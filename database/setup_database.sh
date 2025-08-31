#!/bin/bash
# =============================================================================
# TTKi Database Setup and Security Configuration
# PostgreSQL 17 + pgvector initialization script
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🗄️  TTKi Advanced Database Setup${NC}"
echo "=============================================="

# Configuration
CONTAINER_ID="ed0339295396fec2ec6dbd41f8df4fc6a5fcb3fe9fa489a474e26f927bfd952d"
DB_NAME="ttki_advanced"
DB_USER="ttki_admin"
DB_PASSWORD="$(openssl rand -base64 32)"
DB_READONLY_USER="ttki_readonly"
DB_READONLY_PASSWORD="$(openssl rand -base64 32)"
DB_PORT="5432"

# Save credentials to secure file
CREDENTIALS_FILE="/home/ttki/Pobrane/Jak stworzyć aplikację terminala AI w stylu Bolt/database/.db_credentials"
echo "# TTKi Database Credentials - Generated $(date)" > "$CREDENTIALS_FILE"
echo "DB_HOST=localhost" >> "$CREDENTIALS_FILE"
echo "DB_PORT=$DB_PORT" >> "$CREDENTIALS_FILE"
echo "DB_NAME=$DB_NAME" >> "$CREDENTIALS_FILE"
echo "DB_USER=$DB_USER" >> "$CREDENTIALS_FILE"
echo "DB_PASSWORD=$DB_PASSWORD" >> "$CREDENTIALS_FILE"
echo "DB_READONLY_USER=$DB_READONLY_USER" >> "$CREDENTIALS_FILE"
echo "DB_READONLY_PASSWORD=$DB_READONLY_PASSWORD" >> "$CREDENTIALS_FILE"
chmod 600 "$CREDENTIALS_FILE"

echo -e "${GREEN}✅ Generated secure credentials${NC}"

# Function to execute SQL in container
execute_sql() {
    local sql="$1"
    local database="${2:-postgres}"
    docker exec -i "$CONTAINER_ID" psql -U postgres -d "$database" -c "$sql"
}

# Function to execute SQL file in container
execute_sql_file() {
    local sql_file="$1"
    local database="${2:-postgres}"
    docker exec -i "$CONTAINER_ID" psql -U postgres -d "$database" < "$sql_file"
}

# Start the container if not running
echo -e "${YELLOW}🚀 Starting PostgreSQL container...${NC}"
docker start "$CONTAINER_ID" || {
    echo -e "${RED}❌ Failed to start container${NC}"
    exit 1
}

# Wait for PostgreSQL to be ready
echo -e "${YELLOW}⏳ Waiting for PostgreSQL to be ready...${NC}"
sleep 10

max_attempts=30
attempt=1
while [ $attempt -le $max_attempts ]; do
    if docker exec "$CONTAINER_ID" pg_isready -U postgres >/dev/null 2>&1; then
        echo -e "${GREEN}✅ PostgreSQL is ready${NC}"
        break
    fi
    echo "  Attempt $attempt/$max_attempts..."
    sleep 2
    ((attempt++))
done

if [ $attempt -gt $max_attempts ]; then
    echo -e "${RED}❌ PostgreSQL failed to start${NC}"
    exit 1
fi

# Create database and users
echo -e "${YELLOW}🏗️  Creating database and users...${NC}"

execute_sql "CREATE DATABASE $DB_NAME OWNER postgres;"
echo -e "${GREEN}✅ Database '$DB_NAME' created${NC}"

execute_sql "CREATE USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASSWORD';"
execute_sql "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
execute_sql "ALTER USER $DB_USER CREATEDB;"
echo -e "${GREEN}✅ Admin user '$DB_USER' created${NC}"

execute_sql "CREATE USER $DB_READONLY_USER WITH ENCRYPTED PASSWORD '$DB_READONLY_PASSWORD';"
execute_sql "GRANT CONNECT ON DATABASE $DB_NAME TO $DB_READONLY_USER;"
echo -e "${GREEN}✅ Readonly user '$DB_READONLY_USER' created${NC}"

# Install extensions in the new database
echo -e "${YELLOW}🔧 Installing PostgreSQL extensions...${NC}"

execute_sql "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";" "$DB_NAME"
execute_sql "CREATE EXTENSION IF NOT EXISTS \"pgcrypto\";" "$DB_NAME"
execute_sql "CREATE EXTENSION IF NOT EXISTS \"vector\";" "$DB_NAME"
execute_sql "CREATE EXTENSION IF NOT EXISTS \"pg_stat_statements\";" "$DB_NAME"

echo -e "${GREEN}✅ Extensions installed:${NC}"
echo "   - uuid-ossp (UUID generation)"
echo "   - pgcrypto (Encryption)"
echo "   - vector (Vector embeddings)"
echo "   - pg_stat_statements (Query analytics)"

# Execute the schema
echo -e "${YELLOW}📋 Installing database schema...${NC}"
SCHEMA_FILE="/home/ttki/Pobrane/Jak stworzyć aplikację terminala AI w stylu Bolt/database/schema/advanced_systems_schema.sql"

if [ -f "$SCHEMA_FILE" ]; then
    execute_sql_file "$SCHEMA_FILE" "$DB_NAME"
    echo -e "${GREEN}✅ Database schema installed successfully${NC}"
else
    echo -e "${RED}❌ Schema file not found: $SCHEMA_FILE${NC}"
    exit 1
fi

# Set up permissions for readonly user
echo -e "${YELLOW}🔒 Setting up permissions...${NC}"

execute_sql "GRANT USAGE ON SCHEMA public TO $DB_READONLY_USER;" "$DB_NAME"
execute_sql "GRANT SELECT ON ALL TABLES IN SCHEMA public TO $DB_READONLY_USER;" "$DB_NAME"
execute_sql "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO $DB_READONLY_USER;" "$DB_NAME"

echo -e "${GREEN}✅ Permissions configured${NC}"

# Configure PostgreSQL for performance
echo -e "${YELLOW}⚡ Configuring PostgreSQL for performance...${NC}"

execute_sql "ALTER SYSTEM SET shared_buffers = '512MB';" "$DB_NAME"
execute_sql "ALTER SYSTEM SET effective_cache_size = '2GB';" "$DB_NAME"
execute_sql "ALTER SYSTEM SET work_mem = '256MB';" "$DB_NAME"
execute_sql "ALTER SYSTEM SET maintenance_work_mem = '512MB';" "$DB_NAME"
execute_sql "ALTER SYSTEM SET random_page_cost = 1.1;" "$DB_NAME"
execute_sql "ALTER SYSTEM SET checkpoint_completion_target = 0.9;" "$DB_NAME"
execute_sql "ALTER SYSTEM SET wal_buffers = '64MB';" "$DB_NAME"
execute_sql "ALTER SYSTEM SET max_connections = 200;" "$DB_NAME"

# Reload configuration
execute_sql "SELECT pg_reload_conf();" "$DB_NAME"

echo -e "${GREEN}✅ Performance configuration applied${NC}"

# Security hardening
echo -e "${YELLOW}🛡️  Applying security hardening...${NC}"

# Password policy
execute_sql "ALTER SYSTEM SET password_encryption = 'scram-sha-256';" "$DB_NAME"

# Connection security
execute_sql "ALTER SYSTEM SET ssl = 'on';" "$DB_NAME"
execute_sql "ALTER SYSTEM SET log_connections = 'on';" "$DB_NAME"
execute_sql "ALTER SYSTEM SET log_disconnections = 'on';" "$DB_NAME"
execute_sql "ALTER SYSTEM SET log_statement = 'mod';" "$DB_NAME"

# Query monitoring
execute_sql "ALTER SYSTEM SET pg_stat_statements.track = 'all';" "$DB_NAME"
execute_sql "ALTER SYSTEM SET pg_stat_statements.max = 10000;" "$DB_NAME"

execute_sql "SELECT pg_reload_conf();" "$DB_NAME"

echo -e "${GREEN}✅ Security configuration applied${NC}"

# Test database connection and functionality
echo -e "${YELLOW}🧪 Testing database functionality...${NC}"

# Test basic connectivity
AGENT_COUNT=$(execute_sql "SELECT COUNT(*) FROM agents;" "$DB_NAME" | grep -o '[0-9]*' | head -1)
echo -e "${GREEN}✅ Database connectivity: OK${NC}"

# Test vector extension
execute_sql "SELECT vector_dims(vector(1536));" "$DB_NAME" > /dev/null
echo -e "${GREEN}✅ Vector extension: OK${NC}"

# Test UUID generation
execute_sql "SELECT uuid_generate_v4();" "$DB_NAME" > /dev/null
echo -e "${GREEN}✅ UUID generation: OK${NC}"

# Create connection test script
cat > "/home/ttki/Pobrane/Jak stworzyć aplikację terminala AI w stylu Bolt/database/test_connection.py" << 'EOF'
#!/usr/bin/env python3
"""
Database connection test script
"""
import psycopg2
import sys
import os

# Load credentials
credentials_file = "/home/ttki/Pobrane/Jak stworzyć aplikację terminala AI w stylu Bolt/database/.db_credentials"
creds = {}

with open(credentials_file, 'r') as f:
    for line in f:
        if line.startswith('#') or '=' not in line:
            continue
        key, value = line.strip().split('=', 1)
        creds[key] = value

try:
    # Test admin connection
    admin_conn = psycopg2.connect(
        host=creds['DB_HOST'],
        port=creds['DB_PORT'],
        database=creds['DB_NAME'],
        user=creds['DB_USER'],
        password=creds['DB_PASSWORD']
    )
    
    with admin_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM agents;")
        count = cur.fetchone()[0]
        print(f"✅ Admin connection: OK (agents table has {count} records)")
    
    admin_conn.close()
    
    # Test readonly connection
    readonly_conn = psycopg2.connect(
        host=creds['DB_HOST'],
        port=creds['DB_PORT'],
        database=creds['DB_NAME'],
        user=creds['DB_READONLY_USER'],
        password=creds['DB_READONLY_PASSWORD']
    )
    
    with readonly_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM system_config;")
        count = cur.fetchone()[0]
        print(f"✅ Readonly connection: OK (system_config has {count} records)")
    
    readonly_conn.close()
    
    print("\n🎉 Database setup completed successfully!")
    print("📋 Connection details saved to:", credentials_file)
    
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)
EOF

chmod +x "/home/ttki/Pobrane/Jak stworzyć aplikację terminala AI w stylu Bolt/database/test_connection.py"

# Final status
echo ""
echo -e "${BLUE}=============================================="
echo -e "🎉 TTKi Advanced Database Setup Complete!"
echo -e "==============================================\n${NC}"

echo -e "${GREEN}Database Information:${NC}"
echo "  📛 Name: $DB_NAME"
echo "  🌐 Host: localhost:$DB_PORT"
echo "  👤 Admin User: $DB_USER"
echo "  👁️  Readonly User: $DB_READONLY_USER"
echo ""

echo -e "${GREEN}Features Enabled:${NC}"
echo "  ✅ Vector embeddings (pgvector)"
echo "  ✅ UUID generation"
echo "  ✅ Encryption support"
echo "  ✅ Query analytics"
echo "  ✅ Cross-agent learning tables"
echo "  ✅ Shared memory system"
echo "  ✅ Advanced analytics"
echo "  ✅ Self-improvement framework"
echo ""

echo -e "${YELLOW}Security:${NC}"
echo "  🔒 Encrypted passwords"
echo "  🛡️  Connection logging"
echo "  👥 Role-based access"
echo "  📊 Query monitoring"
echo ""

echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Run connection test: python3 database/test_connection.py"
echo "  2. Start implementing cross-agent learning"
echo "  3. Configure analytics dashboard"
echo ""

echo -e "${GREEN}🔐 Credentials saved securely to: $CREDENTIALS_FILE${NC}"
echo -e "${YELLOW}⚠️  Keep this file secure - contains database passwords!${NC}"
