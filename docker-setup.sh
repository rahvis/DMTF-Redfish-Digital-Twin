#!/bin/bash

# AI-Driven Digital Twin Demo - Docker Setup Script
# Author: Rahul Vishwakarma
# SNIA SDC 2025 - Leveraging DMTF Redfish 2025.2 Specifications

set -e

echo "🚀 AI-Driven Digital Twin Demo - Docker Setup"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    print_status "Docker is installed and running"
}

# Check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker Compose is available"
}

# Check environment variables
check_environment() {
    print_info "Checking environment variables..."
    
    if [ -z "$AZURE_OPENAI_API_KEY" ]; then
        print_warning "AZURE_OPENAI_API_KEY is not set"
        echo "Please set it: export AZURE_OPENAI_API_KEY=your_key_here"
    else
        print_status "AZURE_OPENAI_API_KEY is set"
    fi
    
    if [ -z "$AZURE_OPENAI_ENDPOINT" ]; then
        print_warning "AZURE_OPENAI_ENDPOINT is not set"
        echo "Please set it: export AZURE_OPENAI_ENDPOINT=your_endpoint_here"
    else
        print_status "AZURE_OPENAI_ENDPOINT is set"
    fi
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        print_info "Creating .env file from environment variables..."
        cat > .env << EOF
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY:-your_azure_openai_api_key_here}
AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT:-your_azure_openai_endpoint_here}
AZURE_OPENAI_API_VERSION=2024-04-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1
AZURE_OPENAI_EMBED_DEPLOYMENT_NAME=text-embedding-3-large

# General Configuration
MAX_RETRIES=3
TEMPERATURE=0.7
DEMO_MODE=interactive
DEMO_SPEED=1.0

# Redfish Configuration
REDFISH_VERSION=1.19.0
SCHEMA_VERSION=2025.2
STRICT_VALIDATION=true
EOF
        print_status ".env file created"
    else
        print_status ".env file already exists"
    fi
}

# Build Docker image
build_image() {
    print_info "Building Docker image..."
    docker build -t ai-digital-twin-demo:latest .
    print_status "Docker image built successfully"
}

# Show usage information
show_usage() {
    echo ""
    echo "🎯 Usage Examples:"
    echo "=================="
    echo ""
    echo "1. Run automated demo:"
    echo "   docker run --rm -it --env-file .env ai-digital-twin-demo:latest"
    echo ""
    echo "2. Run interactive menu:"
    echo "   docker run --rm -it --env-file .env ai-digital-twin-demo:latest python main.py"
    echo ""
    echo "3. Run with Docker Compose (automated demo):"
    echo "   docker-compose --profile demo up demo-runner"
    echo ""
    echo "4. Run with Docker Compose (interactive):"
    echo "   docker-compose --profile interactive up interactive"
    echo ""
    echo "5. Run with Docker Compose (all services):"
    echo "   docker-compose --profile demo --profile interactive up"
    echo ""
    echo "6. Build and run in one command:"
    echo "   docker-compose up --build"
    echo ""
}

# Main setup function
main() {
    echo "Starting Docker setup..."
    echo ""
    
    # Check prerequisites
    check_docker
    check_docker_compose
    check_environment
    
    echo ""
    print_info "Building Docker image..."
    build_image
    
    echo ""
    print_status "Docker setup completed successfully!"
    print_status "Your AI-Driven Digital Twin Demo is ready to run!"
    
    show_usage
}

# Run main function
main "$@"
