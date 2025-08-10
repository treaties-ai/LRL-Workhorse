#!/bin/bash

# Licia's Research Lab V2 - Secure Docker Helper
# This script provides restricted Docker operations without broad permissions
# Only pre-defined, safe operations are allowed

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REDIS_CONTAINER="licia-redis-secure"
CHROMADB_CONTAINER="licia-chromadb-secure"
NETWORK_NAME="licia-network-secure"
REDIS_PORT=6379
CHROMADB_PORT=8000

# Function to print colored messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop first."
        exit 1
    fi
}

# Create isolated network if it doesn't exist
create_network() {
    if ! docker network inspect $NETWORK_NAME >/dev/null 2>&1; then
        print_status "Creating isolated network: $NETWORK_NAME"
        docker network create --driver bridge $NETWORK_NAME
        print_success "Network created"
    else
        print_status "Network $NETWORK_NAME already exists"
    fi
}

# Start Redis container
start_redis() {
    if docker ps -a --format '{{.Names}}' | grep -q "^${REDIS_CONTAINER}$"; then
        if docker ps --format '{{.Names}}' | grep -q "^${REDIS_CONTAINER}$"; then
            print_warning "Redis is already running"
        else
            print_status "Starting existing Redis container..."
            docker start $REDIS_CONTAINER
            print_success "Redis started"
        fi
    else
        print_status "Creating and starting Redis container..."
        docker run -d \
            --name $REDIS_CONTAINER \
            --network $NETWORK_NAME \
            -p $REDIS_PORT:6379 \
            --restart unless-stopped \
            --memory="512m" \
            --cpus="0.5" \
            --security-opt no-new-privileges:true \
            --read-only \
            --tmpfs /data:size=100M \
            redis:7-alpine \
            redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
        print_success "Redis container created and started"
    fi
}

# Start ChromaDB container
start_chromadb() {
    if docker ps -a --format '{{.Names}}' | grep -q "^${CHROMADB_CONTAINER}$"; then
        if docker ps --format '{{.Names}}' | grep -q "^${CHROMADB_CONTAINER}$"; then
            print_warning "ChromaDB is already running"
        else
            print_status "Starting existing ChromaDB container..."
            docker start $CHROMADB_CONTAINER
            print_success "ChromaDB started"
        fi
    else
        print_status "Creating and starting ChromaDB container..."
        docker run -d \
            --name $CHROMADB_CONTAINER \
            --network $NETWORK_NAME \
            -p $CHROMADB_PORT:8000 \
            --restart unless-stopped \
            --memory="1g" \
            --cpus="1.0" \
            --security-opt no-new-privileges:true \
            -v "$(pwd)/data/chromadb:/chroma/chroma" \
            ghcr.io/chroma-core/chroma:latest
        print_success "ChromaDB container created and started"
    fi
}

# Start all services
start_services() {
    print_status "Starting all services..."
    check_docker
    create_network
    start_redis
    start_chromadb
    sleep 3  # Give services time to initialize
    print_success "All services started successfully!"
    status_services
}

# Stop all services
stop_services() {
    print_status "Stopping all services..."
    check_docker
    
    if docker ps --format '{{.Names}}' | grep -q "^${REDIS_CONTAINER}$"; then
        docker stop $REDIS_CONTAINER
        print_success "Redis stopped"
    else
        print_warning "Redis was not running"
    fi
    
    if docker ps --format '{{.Names}}' | grep -q "^${CHROMADB_CONTAINER}$"; then
        docker stop $CHROMADB_CONTAINER
        print_success "ChromaDB stopped"
    else
        print_warning "ChromaDB was not running"
    fi
    
    print_success "All services stopped"
}

# Check status of services
status_services() {
    print_status "Checking service status..."
    check_docker
    
    echo ""
    echo "Service Status:"
    echo "==============="
    
    # Check Redis
    if docker ps --format '{{.Names}}' | grep -q "^${REDIS_CONTAINER}$"; then
        echo -e "Redis:     ${GREEN}Running${NC} (Port: $REDIS_PORT)"
        # Test Redis connection
        if docker exec $REDIS_CONTAINER redis-cli ping >/dev/null 2>&1; then
            echo -e "  Health:  ${GREEN}Healthy${NC}"
        else
            echo -e "  Health:  ${RED}Unhealthy${NC}"
        fi
    else
        echo -e "Redis:     ${RED}Stopped${NC}"
    fi
    
    # Check ChromaDB
    if docker ps --format '{{.Names}}' | grep -q "^${CHROMADB_CONTAINER}$"; then
        echo -e "ChromaDB:  ${GREEN}Running${NC} (Port: $CHROMADB_PORT)"
        # Test ChromaDB connection
        if curl -s http://localhost:$CHROMADB_PORT/api/v1/heartbeat >/dev/null 2>&1; then
            echo -e "  Health:  ${GREEN}Healthy${NC}"
        else
            echo -e "  Health:  ${YELLOW}Starting...${NC}"
        fi
    else
        echo -e "ChromaDB:  ${RED}Stopped${NC}"
    fi
    
    echo ""
}

# View logs for a service
view_logs() {
    local service=$1
    check_docker
    
    case $service in
        redis)
            if docker ps -a --format '{{.Names}}' | grep -q "^${REDIS_CONTAINER}$"; then
                print_status "Showing last 50 lines of Redis logs..."
                docker logs --tail 50 $REDIS_CONTAINER
            else
                print_error "Redis container does not exist"
            fi
            ;;
        chromadb)
            if docker ps -a --format '{{.Names}}' | grep -q "^${CHROMADB_CONTAINER}$"; then
                print_status "Showing last 50 lines of ChromaDB logs..."
                docker logs --tail 50 $CHROMADB_CONTAINER
            else
                print_error "ChromaDB container does not exist"
            fi
            ;;
        *)
            print_error "Unknown service: $service"
            print_status "Available services: redis, chromadb"
            exit 1
            ;;
    esac
}

# Clean up containers and data
clean_all() {
    print_warning "This will remove all containers and data. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Cleaning up..."
        check_docker
        
        # Stop and remove containers
        docker rm -f $REDIS_CONTAINER 2>/dev/null || true
        docker rm -f $CHROMADB_CONTAINER 2>/dev/null || true
        
        # Remove network
        docker network rm $NETWORK_NAME 2>/dev/null || true
        
        # Clear data directories
        rm -rf data/redis/* 2>/dev/null || true
        rm -rf data/chromadb/* 2>/dev/null || true
        
        print_success "Cleanup complete"
    else
        print_status "Cleanup cancelled"
    fi
}

# Main command handler
case "${1:-}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    status)
        status_services
        ;;
    restart)
        stop_services
        sleep 2
        start_services
        ;;
    logs)
        if [ -z "${2:-}" ]; then
            print_error "Please specify a service: redis or chromadb"
            exit 1
        fi
        view_logs $2
        ;;
    clean)
        clean_all
        ;;
    help|--help|-h)
        echo "Licia's Research Lab V2 - Secure Docker Helper"
        echo ""
        echo "Usage: $0 <command> [options]"
        echo ""
        echo "Commands:"
        echo "  start    - Start all services (Redis & ChromaDB)"
        echo "  stop     - Stop all services"
        echo "  status   - Check status of all services"
        echo "  restart  - Restart all services"
        echo "  logs <service> - View logs (redis or chromadb)"
        echo "  clean    - Remove all containers and data"
        echo "  help     - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 start"
        echo "  $0 status"
        echo "  $0 logs redis"
        echo "  $0 stop"
        ;;
    *)
        print_error "Invalid command: ${1:-}"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac
