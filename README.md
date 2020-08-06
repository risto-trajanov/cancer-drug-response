# Cancer Drug Response

## Getting started with airflow
### Get the data ready
```
cd airflow
docker-compose up -d
```
Then visit `localhost:8080`

Place DAG files in `airflow\dags`. See examples at https://airflow.apache.org/docs/stable/tutorial.html#example-pipeline-definition .


Place python requirements at `airflow\requirements.txt` and then restart the containers with
`docker-compose up -d --force-recreate`
