#!/bin/bash
# =============================================================================
# Create and Configure TTKi PostgreSQL + pgvector Container
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 Creating TTKi PostgreSQL + pgvector Container${NC}"
echo "=================================================="

# Configuration
CONTAINER_NAME="ttki-postgres"
DB_PASSWORD="$(openssl rand -base64 32)"
DB_PORT="5432"
VOLUME_NAME="ttki-postgres-data"

echo -e "${YELLOW}🔧 Configuration:${NC}"
echo "  📦 Container: $CONTAINER_NAME"
echo "  🔌 Port: $DB_PORT"
echo "  💾 Volume: $VOLUME_NAME"
echo "  🔒 Password: [GENERATED]"
echo ""

# Create Docker volume
echo -e "${YELLOW}📦 Creating Docker volume...${NC}"
docker volume create "$VOLUME_NAME"
echo -e "${GREEN}✅ Volume '$VOLUME_NAME' created${NC}"

# Start PostgreSQL container with pgvector
echo -e "${YELLOW}🚀 Starting PostgreSQL + pgvector container...${NC}"

CONTAINER_ID=$(docker run -d \
    --name "$CONTAINER_NAME" \
    -e POSTGRES_PASSWORD="$DB_PASSWORD" \
    -e POSTGRES_DB="postgres" \
    -e POSTGRES_USER="postgres" \
    -p "$DB_PORT:5432" \
    -v "$VOLUME_NAME:/var/lib/postgresql/data" \
    --restart unless-stopped \
    tatkowy/postgres-pgvector:17)

echo -e "${GREEN}✅ Container started with ID: ${CONTAINER_ID:0:12}${NC}"

# Save credentials
CREDENTIALS_FILE="/home/ttki/Pobrane/Jak stworzyć aplikację terminala AI w stylu Bolt/database/.db_credentials"
echo "# TTKi Database Credentials - Generated $(date)" > "$CREDENTIALS_FILE"
echo "CONTAINER_ID=$CONTAINER_ID" >> "$CREDENTIALS_FILE"
echo "CONTAINER_NAME=$CONTAINER_NAME" >> "$CREDENTIALS_FILE"
echo "DB_HOST=localhost" >> "$CREDENTIALS_FILE"
echo "DB_PORT=$DB_PORT" >> "$CREDENTIALS_FILE"
echo "POSTGRES_PASSWORD=$DB_PASSWORD" >> "$CREDENTIALS_FILE"
chmod 600 "$CREDENTIALS_FILE"

echo -e "${GREEN}✅ Credentials saved to: $CREDENTIALS_FILE${NC}"

# Wait for PostgreSQL to be ready
echo -e "${YELLOW}⏳ Waiting for PostgreSQL to be ready...${NC}"
sleep 15

max_attempts=30
attempt=1
while [ $attempt -le $max_attempts ]; do
    if docker exec "$CONTAINER_ID" pg_isready -U postgres >/dev/null 2>&1; then
        echo -e "${GREEN}✅ PostgreSQL is ready!${NC}"
        break
    fi
    echo "  Attempt $attempt/$max_attempts..."
    sleep 3
    ((attempt++))
done

if [ $attempt -gt $max_attempts ]; then
    echo -e "${RED}❌ PostgreSQL failed to start properly${NC}"
    docker logs "$CONTAINER_ID" --tail 10
    exit 1
fi

# Test basic functionality
echo -e "${YELLOW}🧪 Testing PostgreSQL functionality...${NC}"

# Test basic connection
docker exec "$CONTAINER_ID" psql -U postgres -c "SELECT version();" > /dev/null
echo -e "${GREEN}✅ PostgreSQL connection: OK${NC}"

# Test pgvector extension
docker exec "$CONTAINER_ID" psql -U postgres -c "CREATE EXTENSION IF NOT EXISTS vector;" > /dev/null
docker exec "$CONTAINER_ID" psql -U postgres -c "SELECT vector('{1,2,3}');" > /dev/null
echo -e "${GREEN}✅ pgvector extension: OK${NC}"

# Show container status
echo ""
echo -e "${BLUE}📊 Container Status:${NC}"
docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo -e "${GREEN}🎉 PostgreSQL + pgvector container ready!${NC}"
echo ""
echo -e "${BLUE}Container Details:${NC}"
echo "  🆔 ID: $CONTAINER_ID"
echo "  📛 Name: $CONTAINER_NAME"
echo "  🔌 Port: localhost:$DB_PORT"
echo "  💾 Volume: $VOLUME_NAME"
echo ""
echo -e "${YELLOW}Next: Run the database schema setup${NC}"
echo "  ./database/setup_advanced_schema.sh"
