# Docker Commands Quick Reference

## 🚀 Quick Start

**IMPORTANT:** Always use the `docker-safe.sh` script, never run Docker commands directly!

### Basic Commands

```bash
# Start all services (Redis & ChromaDB)
./docker-safe.sh start

# Check if services are running
./docker-safe.sh status

# Stop all services
./docker-safe.sh stop

# Restart services
./docker-safe.sh restart
```

### Troubleshooting Commands

```bash
# View Redis logs
./docker-safe.sh logs redis

# View ChromaDB logs
./docker-safe.sh logs chromadb

# Clean everything (removes all data!)
./docker-safe.sh clean
```

### What Each Service Does

- **Redis** (Port 6379): Coordinates agents and stores temporary data
- **ChromaDB** (Port 8000): Vector database for semantic search

## 🛡️ Security Features

This script includes:
- ✅ No privilege escalation
- ✅ Memory limits (Redis: 512MB, ChromaDB: 1GB)
- ✅ CPU limits (Redis: 0.5 cores, ChromaDB: 1 core)
- ✅ Isolated network
- ✅ Read-only filesystem for Redis
- ✅ No arbitrary Docker commands allowed

## ❌ What NOT to Do

- Don't give VSCode Docker permissions
- Don't run `docker` commands directly
- Don't modify the script without understanding security implications

## 📋 Daily Workflow

1. **Morning**: `./docker-safe.sh start`
2. **During work**: Services run in background
3. **Check status**: `./docker-safe.sh status`
4. **End of day**: `./docker-safe.sh stop`

## 🚨 If Something Goes Wrong

1. Check status: `./docker-safe.sh status`
2. View logs: `./docker-safe.sh logs redis` or `./docker-safe.sh logs chromadb`
3. Restart: `./docker-safe.sh restart`
4. Last resort: `./docker-safe.sh clean` (deletes all data!)

## 📝 Notes

- Services auto-restart if they crash
- Data is preserved between stops/starts
- Only `clean` command removes data
- No VSCode permissions needed!
