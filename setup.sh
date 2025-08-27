#!/bin/bash

# AI-Driven Digital Twin Demo Setup Script
# Author: Rahul Vishwakarma
# SNIA SDC 2025 - Leveraging DMTF Redfish 2025.2 Specifications

echo "Setting up AI-Driven Digital Twin Demo..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Found Python version: $PYTHON_VERSION"

# Create Python virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file
echo "Creating .env file..."
cat > .env << 'EOF'
# AI-Driven Digital Twin Demo Environment Configuration

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-04-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1
AZURE_OPENAI_EMBED_DEPLOYMENT_NAME=text-embedding-3-large

# Legacy Google Gemini (optional)
GOOGLE_API_KEY=your_gemini_api_key_here

# Generation Parameters
MAX_RETRIES=3
TEMPERATURE=0.7

# Demo Configuration
DEMO_MODE=interactive
DEMO_SPEED=1.0

# Redfish Configuration
REDFISH_VERSION=1.19.0
SCHEMA_VERSION=2025.2
STRICT_VALIDATION=true

# Paths (usually don't need to change)
SPECS_DIR=specifications
TEMPLATES_DIR=templates
EXAMPLES_DIR=examples
OUTPUT_DIR=output/recordings
REDFISH_MOCKUPS_DIR=DSP2043_2025.2
EOF

echo ""
echo "✅ Setup complete!"
echo ""
echo "⚠️  IMPORTANT: Edit the .env file and add your Azure OpenAI API key and endpoint"
echo ""
echo "To get Azure OpenAI API key:"
echo "1. Go to https://oai.azure.com/"
echo "2. Create a new resource or use existing one"
echo "3. Get your API key and endpoint from the resource"
echo "4. Copy the key and endpoint to .env file"
echo ""
echo "Available Demo Modes:"
echo "1. Automated Demo (presentation mode): python demo.py"
echo "2. Interactive Menu: python main.py"
echo ""
echo "Demo Scenarios Available:"
echo "• Storage Infrastructure (controllers, drives, volumes)"
echo "• Compute Infrastructure (systems, processors, memory)"
echo "• Networking Infrastructure (adapters, fabrics, switches)"
echo "• Comprehensive Infrastructure (full data center)"
echo ""
echo "Redfish Profiles Available:"
echo "• public-localstorage, public-bladed, public-rackmount1"
echo "• public-composability, public-cxl, public-nvmeof-jbof"
echo "• public-smartnic, public-telemetry, public-sasfabric"
echo ""
echo "To run the demo:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Edit .env file with your API key"
echo "3. Run automated demo: python demo.py"
echo "4. Run interactive demo: python main.py"
echo ""
echo "🎯 Ready for SNIA SDC 2025 presentation!"
