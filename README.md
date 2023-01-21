# Luigi Workflows for Multilex

## Commands

- luigid --port = 8082 : Runs a luigi vizualizer server on port number 8082
- python -m luigi --module [file_name] [ClassName-Task] --local-scheduler
  - file_name : Enter the name of the file without .py extension
  - ClassName : Enter the name of the class

## Initial setup

- git clone [url of repo]
- pip install -r requirements.txt
- morning.bat
- evening.bat
- Paste final xlsx file into Output folder
- night.bat

## Workflows

- LoggingWf : S1 data workflow
- SecS1WF : Union of two daily log reports and automated mail

## News assigner + data upload

- form
- take final report as input
- file will be sent to the backend
- read this file, and upload to database
- upload to drive

## deals with deep learning

- train
- predicts
