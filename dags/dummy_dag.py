from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator as bo
from airflow.operators.empty import EmptyOperator as eo
from datetime import datetime

@dag(start_date= datetime(2021, 1, 1), schedule = "@weekly", catchup=False)
def example_dag():
    #Have a bunch of tasks here
    start = eo(task_id='start')
    end = eo(task_id='end')

    @task
    def a():
        print(1.0)
        return 1.0

    @task
    def b():
        print(2.0)
        return 2.0
    
    a = a()
    b = b()
    also_run = bo(task_id='also_run', bash_command='echo 123')

    #DAG execution flow
    start >> a >> b >> also_run >>  end

if __name__ == "__main__":
    example_dag().test()