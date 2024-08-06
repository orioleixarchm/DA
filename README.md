# AED Coverage and Cardiac Arrest Hotspots in Brussels
Modern Data Analytics App project.

Oriol Eixarch Mejías.

## Objective
The objective of this project is to analyze the current locations of  the occurrences of cardiac related issues in Brussels, the location of Automated External Defibrillators (AEDs) and that of the emergency services. The application aims to provide insights into the accessibility and coverage of AEDs and emergency services to improve emergency response and potentially save lives.
The following kinds of intervention have been used:
- P011 - Chest pain.
- P039 - Cardiac problem (other than thoracic pain).
- P000 - ARCA DEA (stands for Ambulance Réanimation-Catastrophe + Défibrillateur Externe Automatique).
- P003  N05 - HARTSTILSTAND - DOOD - OVERLEDEN. 

## Project Structure
The project consists of several Python scripts and a Streamlit application.
Locally, each program creates data stored locally for the next one untill the app is executed.

The app has been deployed via streamlit and can be checked [here](https://g4ahg4xw73pespmhcipyh8.streamlit.app/).

## Order of execution
If the user is interested in run the data flow and app locally it is worth noting that all programs can retreive data in two ways:
- **Drive**: All programs will retreive the data stored in a drive instead of the newly locally created data, this can be modified by uncomenting portions of existing code in each program. The app program will retrieve by default data from the local directory.
  - The following running order ensures better performance: _Computing Distances.py -> app.py_. Data can be accessed in _app.py_ directly via drive if the specific portion of the code is uncommented.
- **Locally**: All programs (except _AEDs Coordinates.py_) can retrieve the necessary data from the local directory once created by the previous program/s. Portions of the code need to be uncomented in each program.
  - The following running order must be ensured: _AEDs Coordinates.py -> DataBrussels.py -> Clustering.py -> Computing Distances.py -> app.py_.

Please, bear in mind that the first step, running _AEDs Coordinates.py_ can take up to 4 hours, therefore I encourage the user to either follow running option 1 or, at least use the drive to get until the second step of the dataflow and run locally only the following part _DataBrussels.py -> Clustering.py -> Computing Distances.py -> app.py_ skipping the first porogram as the data created therein is stored in the drive.

### Parts and Programs
- **app.py**: Main Streamlit application that visualizes the AED locations, emergency services, and cardiac arrest hotspots on an interactive map, version non-deployed used for testing.
- **app_depl.py**: Deployed application.
- **AEDs Coordinates.py**: Processes and compute the coordinates (latitde and longitude) of each AED based on their address.
- **DataBrussels.py**: Creates the clean datasets for ambulances, interventions and AEDs.
- **Clustering.py**: Performs clustering analysis to identify hotspots and clusters of AEDs and emergency services.
- **Computing Distances.py**: Calculates the distances between all interventions and the closest AED and emergency services.
- **utilities.py**: Contains utility functions used across various scripts.
- **basic_test.py**: Script to download and test the quality of the data.
- **run_app.py**: Runs the non-deployed Streamlit application from within a Python script

### Directory Structure
- **Project directory**
  - **src**: Contains all the source code including the main application and supporting scripts.
  - **tests**: Contains the test script for validating the functionality of the application, which for the sake of simplicity includes only basic tets.
  - Other files: `README.md`, `requirements.txt`, `setup.py`, `setup_tests.py`, `Makefile`, `LICENSE`.

## Mission
The mission of this project is to enhance the emergency response system in Brussels by providing a functional analysis of AED coverage and the spatial relationship between emergency services and cardiac arrest incidents. By identifying areas with insufficient coverage, the project aims to recommend strategic placements of additional AEDs and optimize emergency response routes while offering a certain flexibility to accomodate different scenarios and strategies (critical distances are defined by the user).

## Setup and Installation
To set up and run the project, follow these steps:

### First Step
- Clone repository: `git clone https://github.com/orioleixarchm/DA.git`.
- Set directory: `cd DA`.

### Install Dependencies
- Ensure Python is installed.
- Install the required dependencies.

### Run the Setup Script
- Execute the script to install the project and its dependencies into the Python environment `python setup.py install`. 

### Run the Application
- Run the required programs (at least _Computing Distances.py_).
- Use the Makefile or run the Streamlit application directly from the command line.

## Makefile Contents
The Makefile includes commands to install dependencies, run the application, clean the project and run tests. Specific targets are provided for each script to facilitate execution.

## Running Tests
To run the tests, execute the tests using the Makefile or directly with pytest as the data is accessed through the drive.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contact
For any questions or inquiries, please contact Oriol Eixarch at orioleixarchm@gmail.com.


