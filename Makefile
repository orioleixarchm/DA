# Makefile for Brussels' Hotspots app

.PHONY: help install run clean test

help:
	@echo "  Makefile for Brussels' Hotspots app"
	@echo "  Usage:"
	@echo "  make install   - Install the project dependencies"
	@echo "  make aed_coordinates       - Run AEDCoordinates.py"
	@echo "  make data_brussels         - Run DataBrussels.py"
	@echo "  make clustering            - Run Clustering.py"
	@echo "  make computing_distances   - Run ComputingDistances.py"
	@echo "  make run       - Run the application"
	@echo "  make clean     - Clean the project"
	@echo "  make test      - Run the tests"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

aed_coordinates:
	@echo "Running AEDCoordinates.py..."
	python src/AEDCoordinates.py

data_brussels:
	@echo "Running DataBrussels.py..."
	python src/DataBrussels.py

clustering:
	@echo "Running Clustering.py..."
	python src/Clustering.py

computing_distances:
	@echo "Running ComputingDistances.py..."
	python src/ComputingDistances.py

run:
	@echo "Running application..."
	streamlit run src/app.py

clean:
	@echo "Cleaning project..."
	cd %USERPROFILE% && for /d /r . %a in (DA) do if exist "%a" rd /s /q "%a"
	@echo "Cleanup complete."

test:
	@echo "Running tests..."
	pytest
