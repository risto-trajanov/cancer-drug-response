
# Cancer Drug Response

## Airflow
### Get the data ready
```
cd airflow
docker-compose up -d
```
Then visit `localhost:8080`

Place DAG files in `airflow\dags`. See examples at https://airflow.apache.org/docs/stable/tutorial.html#example-pipeline-definition .


Place python requirements at `airflow\requirements.txt` and then restart the containers with
`docker-compose up -d --force-recreate`

## API for Drug Response in local enviorment
### Install 

Requirements from `requirements.txt`

Run `main.py`

Go to `localhost:8000`

### Data Input

3 CSV files:

 1. Gene CNV `gene_CNV.csv`
 2. Gene Expression `gene_Expression.csv`
 3. Gene Mutation `gene_Mutation.csv`

Data Collected From 
[https://amp.pharm.mssm.edu/Harmonizome/dataset/CCLE+Cell+Line+Gene+Expression+Profiles](https://amp.pharm.mssm.edu/Harmonizome/dataset/CCLE+Cell+Line+Gene+Expression+Profiles)

**The format of the input data must be in the provided format from the gathered data**
