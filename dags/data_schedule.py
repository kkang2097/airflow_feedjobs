from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator as bo
from airflow.operators.empty import EmptyOperator as eo
from datetime import datetime