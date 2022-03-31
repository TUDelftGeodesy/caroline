# Developer's Documentation.




## download Engine

1. Create virtual environment
2. Install download package must be install in venv
3. instal doris-rippl


## Pending matters
Upgrade PROJ in Spider, then install cartopy 


## Examples

"2021-12-19" "2021-12-22" "POLYGON((-155.75 18.90,-155.75 20.2,-154.75 19.50,-155.75 18.90))"

{"start_date":"2021-12-19", "end_date":"2021-12-22", "geometry":"POLYGON((-155.75 18.90,-155.75 20.2,-154.75 19.50,-155.75 18.90))"}

Templating
What I have at the moment is a DAG that accepts the start/end dates and geometry as parameters, when a dag is triggered from the airflow CLI. I think this is the idea for the long run, isn't it?

For example, for a DAG called 'template' : 

$ airflow dags trigger 'template' --conf '{"start_date":"2021-12-19", "end_date":"2021-12-22", "geometry":"POLYGON((-155.75 18.90,-155.75 20.2,-154.75 19.50,-155.75 18.90))"}'

The --conf flag passes a JSON string with all values for the parameters (templated) in the DAG definition. See: https://bitbucket.org/grsradartudelft/caroline/src/90205364f241b5cbff2af27e1270e2136ced1479/dags/interferogram.py?at=feature%2FCAR-16-dag-for-interferogram


## Activate virtual environment in Spider interactive Job

1. Load modules, with `module load`
2. Activate virtual environment
3. Start interactive session with `srun`

    ```shell
    srun --partition=normal --time=00:60:00 -c 1 --ntasks-per-node=1 --pty bash -i -l

    ```
4. run job
