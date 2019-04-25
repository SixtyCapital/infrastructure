"""
Inherits the standard config with one change - log task logs to
stdout
ref https://github.com/GoogleCloudPlatform/airflow-operator/issues/72#issuecomment-486509956
"""

from airflow.config_templates.airflow_local_settings import *

DEFAULT_LOGGING_CONFIG['loggers']['airflow.task']['propagate'] = True
