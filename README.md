#<a name="top"></a>FIWARE Agile scripts
[![License badge](https://img.shields.io/badge/license-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Scripts to generate automatically the sprint closing, sprint planning and retrospective tickets.

These scripts were developed in order to facilitate the SCRUM MASTER tasks in Jira. The 
purpose is to generate automatically the hierarchy of jira tickets per each chapter and per each 
generic enabler.

These scripts were originally develop by Manuel Escriche from Telefónica I+D and now 
is maintained by me. I just try to cover python style reorganize content to separate 
the scripts and generate a separate project for it. Currently these scripts are using
Python3.6

## Description of the scripts

The scripts are divided into 2 subgroups:

- SprintClosing.py: it generates the tickets associated to the sprint clossing and retrospective
 activities per each sprint.
- SprintPlanning.py: it generated the tickets associated to the sprint planning activities per 
each sprint.

[Top](#top)

## Build and Install

### Requirements

The following software must be installed:

- Python 3.6
- pip
- virtualenv


### Installation

The recommend installation method is using a virtualenv. Actually, the installation 
process is only about the python dependencies, because the python code do not need 
installation.

1. Clone this repository.
2. Create virtualenv: 'virtualenv -p python3.6 env
3. Activate the virtualenv: 'source env/bin/activate
4. Install dependencies: 'pip install -r requirements.txt'

[Top](#top)

## Configuration

There is a directory 'site_config' that contains all the configurations files that
are needed to execute the scripts. It contains sensible information and it is not
upload to the github repository. Please contact with the owner of the repository
if you want to use it.

[Top](#top)

## License

These scripts are licensed under Apache License 2.0.
