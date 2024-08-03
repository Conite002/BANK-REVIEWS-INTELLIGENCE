from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import subprocess
import os, sys


# UTILS
# ------------------------------------------------------------------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'SrapperService', 'production_standalone', 'scrapper_initialize.py'))

def run_crawler():
    result = subprocess.run([
        'python3', 
        str(BASE_DIR)
    ])
    print(result.stdout)
    if result.stderr:
        print('>>>>>>>>>>>>ERROR<<<<<<<<<<<<<')
        print(result.stderr)


# DAG
# ------------------------------------------------------------------------------------

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'INITIAL-DATA-CRAWLER',
    default_args=default_args,
    description='A simple crawler DAG',
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False
)

# PYTHON OPERATOR
# ------------------------------------------------------------------------------------
run_script_task = PythonOperator(
    task_id='run_script',
    python_callable=run_crawler,
    dag=dag
)

# ORCHESTRATION
# ------------------------------------------------------------------------------------
run_script_task