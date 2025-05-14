# Airflow

Airflow provides a way to automate the processing workflow required for the productio of data pruducts in Caroline.

We are running version *2.2.4* of Apache Airflow using Docker. 

## Installing Apache Airflow

When running apache airflow for the very firts time, do the following:

1. Copy the [docker-compose.yalm](assets/scripts/docker-compose.yalm) file to the directory that will serve as root directory.
2. Create the following directories: `dags, logs, plugins, ssh`
3. Change the permisions of directories with `chmod -R 777 dags/ logs/ plugins/ ssh/`
4. Create an `.env` file with the user id: `echo -e "AIRFLOW_UID=$(id -u)" > .env`
5. Define and set the values for the following variable in `.env`:
   
    ```shell
    AIRFLOW_UID=552041
    AIRFLOW__WEBSERVER__BASE_URL=http://caroline.citg.tudelft.nl:8080 
    AIRFLOW__SMTP__SMTP_HOST=<require only for the Email Operator> 
    AIRFLOW__SMTP__SMTP_USER=<require only for the Email Operator> 
    AIRFLOW__SMTP__SMTP_PASSWORD=<require only for the Email Operator> 
    AIRFLOW__SMTP__SMTP_PORT=<require only for the Email Operator> 
    AIRFLOW__SMTP__SMTP_MAIL_FROM=<require only for the Email Operator> 
    _AIRFLOW_WWW_USERNAME=<initial admin username> 
    _AIRFLOW_WWW_PASSWORD=<initial admin password> 
    ```

6. Initialize the services with `docker-compose up airflow-init`
7. Start up the containers in detached mode: `docker-compose up -d`

### Reinstalling Apache Airflow

> Warning: this will permanently delete all configurations, DAGs and execution histories.

1. Stop the contatiners.
2. Run `docker-compose down --volumes --remove-orphans`
3. Delete all directories with `rm -rf '<DIRECTORY>'`
4. Follow the instruction in the previous section to install Apache Airflow.

