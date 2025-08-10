# Licia's Research Lab V2 - Rapid Start Makefile
# One-command setup and management

.PHONY: rapid-start status stop clean test help

# Default target
help:
	@echo "Licia's Research Lab V2 - Command Reference"
	@echo "==========================================="
	@echo "make rapid-start    - Complete setup and launch (30 minutes)"
	@echo "make status        - Check system health"
	@echo "make stop          - Stop all services"
	@echo "make clean         - Clean up containers and data"
	@echo "make test          - Run test suite"
	@echo "make bootstrap     - Extract code from implementation guide"

# Complete rapid setup
rapid-start: check-prerequisites create-dirs pull-images init-db start-services health-check
	@echo "✅ System ready! Access review interface at http://localhost:3000"

# Check prerequisites
check-prerequisites:
	@echo "Checking prerequisites..."
	@command -v docker >/dev/null 2>&1 || { echo "❌ Docker not installed"; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 not installed"; exit 1; }
	@command -v node >/dev/null 2>&1 || { echo "❌ Node.js not installed"; exit 1; }
	@echo "✅ All prerequisites installed"

# Create directory structure
create-dirs:
	@echo "Creating directory structure..."
	@mkdir -p agents/nuance agents/intelligence
	@mkdir -p orchestrators logs/vscode logs/cli logs/agents
	@mkdir -p docker/seccomp
	@mkdir -p tests/unit tests/integration tests/e2e tests/performance
	@mkdir -p review_interface/templates review_interface/static
	@mkdir -p data/redis data/chromadb
	@mkdir -p transcripts outputs samples reference
	@mkdir -p ingestion rag quality_gates
	@mkdir -p security memory workflows
	@echo "✅ Directories created"

# Pull Docker images
pull-images:
	@echo "Pulling Docker images..."
	@docker pull redis:7-alpine
	@docker pull ghcr.io/chroma-core/chroma:latest
	@docker pull python:3.9-slim
	@echo "✅ Images pulled"

# Initialize databases
init-db:
	@echo "Initializing databases..."
	@docker-compose -f docker-compose.secure.yml up -d redis chromadb
	@sleep 5  # Wait for services to start
	@echo "✅ Databases initialized"

# Start all services
start-services:
	@echo "Starting services..."
	@docker-compose -f docker-compose.secure.yml up -d
	@echo "✅ Services started"

# Health check
health-check:
	@echo "Running health checks..."
	@curl -s http://localhost:8000/api/v1/heartbeat >/dev/null 2>&1 && echo "✅ ChromaDB: Running" || echo "❌ ChromaDB: Not responding"
	@redis-cli ping >/dev/null 2>&1 && echo "✅ Redis: Running" || echo "❌ Redis: Not responding"

# Check system status
status:
	@echo "System Status"
	@echo "============="
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@echo "Orchestrators:"
	@ps aux | grep -E "(vscode|cli)_orchestrator.py" | grep -v grep || echo "No orchestrators running"

# Stop all services
stop:
	@echo "Stopping all services..."
	@docker-compose -f docker-compose.secure.yml down
	@pkill -f "orchestrator.py" || true
	@echo "✅ All services stopped"

# Clean up
clean: stop
	@echo "Cleaning up..."
	@docker-compose -f docker-compose.secure.yml down -v
	@rm -rf data/redis/* data/chromadb/*
	@rm -rf logs/*
	@echo "✅ Cleanup complete"

# Run tests
test:
	@echo "Running test suite..."
	@python -m pytest tests/ -v

test-unit:
	@python -m pytest tests/unit/ -v

test-integration:
	@python -m pytest tests/integration/ -v

test-performance:
	@python -m pytest tests/performance/ -v

# Bootstrap from implementation guide
bootstrap:
	@echo "Extracting code from RAPID_IMPLEMENTATION_GUIDE.md..."
	@python scripts/bootstrap_from_guide.py
	@echo "✅ Code extraction complete"

# Install Python dependencies
install-deps:
	@pip install -r requirements.txt
	@npm install -g @modelcontextprotocol/server-sequential-thinking

# Launch orchestrators
start-vscode-orchestrator:
	@python orchestrators/vscode_orchestrator.py &

start-cli-orchestrator:
	@python orchestrators/cli_orchestrator.py --mode cooperative &

# Process content
process-transcript:
	@python -m licia_lab process transcript $(FILE)

ingest-perplexity:
	@python -m licia_lab ingest perplexity $(DIR)

# Development helpers
dev-setup: create-dirs install-deps
	@echo "Development environment ready"

logs-vscode:
	@tail -f logs/vscode/*.log

logs-cli:
	@tail -f logs/cli/*.log

logs-agents:
	@tail -f logs/agents/*.log
