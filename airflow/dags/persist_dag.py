from datetime import timedelta

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to operate!
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import downloader
import extract_drug_data

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}

dag = DAG(
    'Persist',
    default_args=default_args,
    description='Cell data download and persist with right format',
    schedule_interval=timedelta(days=1),
)


def downloader_function():
    print("start")
    downloader.main()
    print("end")


def drug_data_function():
    print("start")
    extract_drug_data.main()
    print("end")


download_task = PythonOperator(
    task_id='download_task',
    python_callable=downloader_function,
    dag=dag
)

drug_data_task = PythonOperator(
    task_id='drug_data_task',
    python_callable=drug_data_function,
    dag=dag
)

#download_task >> \
drug_data_task
