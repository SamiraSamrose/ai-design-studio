#!/bin/bash

echo "Starting AI-Driven Industrial Product Design Studio"
echo "=================================================="

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing/updating dependencies..."
pip install -r backend/requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your API keys before running again."
    exit 1
fi

echo "Creating output directories..."
mkdir -p generated_designs refined_designs comparisons nuke_scripts temp exports

echo "Starting Flask server..."
cd backend
python app.py