# Makefile for Brussels' Hotspots app

.PHONY: help install run clean test

help:
	@echo "  Makefile for Brussels' Hotspots app"
	@echo "  Usage:"
	@echo "  make install   - Install the project dependencies"
	@echo "  make run       - Run the application"
	@echo "  make clean     - Clean the project"
	@echo "  make test      - Run the tests"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

run:
	@echo "Running application..."
	streamlit run src/app.py

clean:
	@echo "Cleaning project..."
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	rm -rf build dist *.egg-info

test:
	@echo "Running tests..."
	pytest
