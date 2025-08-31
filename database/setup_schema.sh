#!/bin/bash
# =============================================================================
# Setup Advanced Database Schema
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🗄️  Setting up TTKi Advanced Database Schema${NC}"
echo "================================================"

# Load credentials
CREDENTIALS_FILE="/home/ttki/Pobrane/Jak stworzyć aplikację terminala AI w stylu Bolt/database/.db_credentials"
source "$CREDENTIALS_FILE"

DB_NAME="ttki_advanced"
DB_USER="ttki_admin"
DB_PASSWORD="$(openssl rand -base64 32)"
DB_READONLY_USER="ttki_readonly"
DB_READONLY_PASSWORD="$(openssl rand -base64 32)"

# Function to execute SQL
execute_sql() {
    local sql="$1"
    local database="${2:-postgres}"
    docker exec -i "$CONTAINER_ID" psql -U postgres -d "$database" -c "$sql"
}

# Create database and users
echo -e "${YELLOW}🏗️  Creating database and users...${NC}"

execute_sql "CREATE DATABASE $DB_NAME OWNER postgres;"
execute_sql "CREATE USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASSWORD';"
execute_sql "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
execute_sql "CREATE USER $DB_READONLY_USER WITH ENCRYPTED PASSWORD '$DB_READONLY_PASSWORD';"
execute_sql "GRANT CONNECT ON DATABASE $DB_NAME TO $DB_READONLY_USER;"

echo -e "${GREEN}✅ Database and users created${NC}"

# Install schema
echo -e "${YELLOW}📋 Installing database schema...${NC}"
SCHEMA_FILE="/home/ttki/Pobrane/Jak stworzyć aplikację terminala AI w stylu Bolt/database/schema/advanced_systems_schema.sql"

docker exec -i "$CONTAINER_ID" psql -U postgres -d "$DB_NAME" < "$SCHEMA_FILE"
echo -e "${GREEN}✅ Schema installed successfully${NC}"

# Update credentials file
echo "" >> "$CREDENTIALS_FILE"
echo "# Database Details" >> "$CREDENTIALS_FILE"
echo "DB_NAME=$DB_NAME" >> "$CREDENTIALS_FILE"
echo "DB_USER=$DB_USER" >> "$CREDENTIALS_FILE"
echo "DB_PASSWORD=$DB_PASSWORD" >> "$CREDENTIALS_FILE"
echo "DB_READONLY_USER=$DB_READONLY_USER" >> "$CREDENTIALS_FILE"
echo "DB_READONLY_PASSWORD=$DB_READONLY_PASSWORD" >> "$CREDENTIALS_FILE"

echo -e "${GREEN}✅ Database setup complete!${NC}"
echo "📋 Database: $DB_NAME"
echo "👤 Admin User: $DB_USER"
echo "👁️  Readonly User: $DB_READONLY_USER"
