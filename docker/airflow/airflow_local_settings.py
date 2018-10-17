def gen_run_date(execution_date, next_execution_date, run_id):
    date = execution_date
    if next_execution_date and run_id and run_id.startswith('scheduled__'):
        date = next_execution_date
    return date


# Do we use this anywhere?
def sixty_pre_execute(context):
    """
    With the inclusion of the 'run_date' family of macros, our templates now
    require they be rednered a second time.

    Double-render idea from: https://stackoverflow.com/a/45941551/7067569
    """
    context['ti'].render_templates()


# Do we use this anywhere?
def policy(task):
    """
    Manipulate tasks as they are loaded:
    https://github.com/apache/incubator-airflow/blob/667a26ce492d944793eb25c72b9f21e41266c7d9/airflow/models.py#L388
    given task: <Task(BashOperator): load_sge_data>
    isinstance(task, BashOperator) #=> True
    """
    run_date_str = '_run_date(execution_date, next_execution_date, run_id)'
    run_ds_str = run_date_str + '.strftime("%Y-%m-%d")'
    run_ds_nodash_str = run_date_str + '.strftime("%Y%m%d")'
    task.dag.user_defined_macros = task.dag.user_defined_macros or dict(
        _run_date=gen_run_date,
        run_date='{{ ' + run_date_str + ' }}',
        run_ds='{{ ' + run_ds_str + ' }}',
        run_ds_nodash='{{ ' + run_ds_nodash_str + ' }}',
    )

    task.pre_execute = sixty_pre_execute
