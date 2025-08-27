#!/bin/bash

# Quick Docker Run Script for AI-Driven Digital Twin Demo
# Author: Rahul Vishwakarma
# SNIA SDC 2025

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 AI-Driven Digital Twin Demo - Quick Docker Run${NC}"
echo "=================================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ .env file not found. Creating from environment variables...${NC}"
    ./docker-setup.sh
fi

# Function to run demo
run_demo() {
    local mode=$1
    local description=$2
    
    echo -e "${GREEN}🎯 Running $description...${NC}"
    echo "Command: $3"
    echo ""
    
    eval "$3"
}

# Show menu
echo "Choose your demo mode:"
echo "1. Automated Demo (presentation mode)"
echo "2. Interactive Menu"
echo "3. Custom Command"
echo "4. Build and Run"
echo "5. Exit"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        run_demo "automated" "Automated Demo" \
            "docker run --rm -it --env-file .env ai-digital-twin-demo:latest python demo_fixed.py"
        ;;
    2)
        echo ""
        run_demo "interactive" "Interactive Menu" \
            "docker run --rm -it --env-file .env ai-digital-twin-demo:latest python main.py"
        ;;
    3)
        echo ""
        read -p "Enter custom command (e.g., 'python demo.py'): " custom_cmd
        if [ ! -z "$custom_cmd" ]; then
            run_demo "custom" "Custom Command" \
                "docker run --rm -it --env-file .env ai-digital-twin-demo:latest $custom_cmd"
        else
            echo "No command provided. Exiting."
        fi
        ;;
    4)
        echo ""
        echo -e "${GREEN}🔨 Building and running with Docker Compose...${NC}"
        docker-compose up --build
        ;;
    5)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
