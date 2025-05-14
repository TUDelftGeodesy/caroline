# System Deployment

This document describes how Caroline components are currently deployed and configured. The deployment is in a pilot phase, and there is plenty of room for improvements.


## Download Engine

The download engine is installed in a virtual environment in Spider: `/project/caroline/Software/caroline/caroline-venv`

System-level dependencies should be loaded using `module`. For the **Download Engine**, the following modules are required:

- python/3.9.6
- gdal/3.4.1

Package configurations are set in `/project/caroline/Software/caroline/download/.env`
  
## Processing Engine

The processing engine is installed in a virtual environment in Spider: `/project/caroline/Software/caroline/caroline-venv`

Package configurations are set in `/project/caroline/Software/caroline/processing/.env` and `/project/caroline/Software/caroline/rippl/rippl/user_settings.txt/`

System-level dependencies should be loaded using `module`. For the **Processing Engine**, the following modules are required:

- python/3.9.6
- gdal/3.4.1
- proj/8.2.1

## Workflow Manager: Airflow

Apache Airflow was deployed using `docker-compose` in the Virtual Machine. The root installation directory is in `/opt/airflow`, and the web interface is available at: http://caroline.citg.tudelft.nl:8080/

- DAGs are deployed in `/opt/airflow/dags`
- Custom operator are deployed in `/opt/airflow/plugins`
- SSH key are deployed in `/opt/airflow/ssh/`
- Other files that need to be accessed by the Airlfow are be deployed in `/opt/airflow/data/`
  