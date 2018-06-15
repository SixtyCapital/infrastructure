from __future__ import unicode_literals
from __future__ import absolute_import
from tempfile import mkstemp
from os import unlink
from kubernetes.config.kube_config import new_client_from_config
from kubernetes.client import CoreV1Api
from sixtyctl.config import (
    DEFAULT_CONFIG, PRODUCTION_CONFIG, PRODUCTION_PROJECT)
from sixtyctl.gcp import (
    describe_container_cluster,
    describe_db_instance,
    ZONE)
from sixtyctl.util import ordered_dump, getLogger

SIXTY_NAMESPACES = ['airflow']
logger = getLogger(__name__)


def get_kube_config_object(project_id, cluster_name, zone):
    cluster_info = describe_container_cluster(project_id, cluster_name)
    kube_name = 'gke_{project_id}_{zone}_{cluster_name}'.format(
        project_id=project_id, zone=zone, cluster_name=cluster_name)
    host = 'https://{}'.format(cluster_info['endpoint'])
    client_cert = cluster_info['masterAuth']['clientCertificate']
    client_key = cluster_info['masterAuth']['clientKey']
    cluster_ca = cluster_info['masterAuth']['clusterCaCertificate']
    username = cluster_info['masterAuth']['username']
    password = cluster_info['masterAuth']['password']
    return {
        'apiVersion': 'v1',
        'kind': 'Config',
        'preferences': {},
        'clusters': [{
            'name': kube_name,
            'cluster': {
                'certificate-authority-data': cluster_ca,
                'server': host}
        }],
        'contexts': [{
            'name': kube_name,
            'context': {
                'cluster': kube_name,
                'user': kube_name}}],
        'current-context': kube_name,
        'users': [{
            'name': kube_name,
            'user': {
                'client-certificate-data': client_cert,
                'client-key-data': client_key,
                'password': password,
                'username': username}}]}


def get_api_client(project_id, cluster_name, zone=None):
    if not zone:
        zone = ZONE
    config = get_kube_config_object(project_id, cluster_name, zone)
    fd, path = mkstemp('.yaml')
    with open(path, 'w') as fstream:
        ordered_dump(config, fstream)
    kube_rest_api_client = new_client_from_config(path)
    client = CoreV1Api(api_client=kube_rest_api_client)
    unlink(path)
    return client


def create_namespaces(project_id, cluster_name):
    client = get_api_client(project_id, cluster_name)
    namespaces = {x.metadata.name for x in client.list_namespace().items}
    for namespace in SIXTY_NAMESPACES:
        if namespace in namespaces:
            logger.warn('Namespace {} already exists!'.format(namespace))
            continue
        client.create_namespace({'metadata': {'name': namespace}})
        logger.info('Created namespace {}'.format(namespace))


def create_airflow_configmap(project_id, cluster_name, db_instance_name):
    from kubernetes.client.models import V1ConfigMap

    namespace = 'airflow'
    configmap_name = 'airflow-env'
    db_info = describe_db_instance(project_id, db_instance_name)
    data = dict(
        GOOGLE_CLOUD_PROJECT=project_id,
        SIXTY_CONFIG_FILE=(
            PRODUCTION_CONFIG if project_id == PRODUCTION_PROJECT
            else DEFAULT_CONFIG),
        AIRFLOW__CORE__LOGGING_CONFIG_CLASS=''
        'sixty.production.airflow_config.logging_config.LOGGING_CONFIG',
        AIRFLOW__CORE__REMOTE_LOG_CONN_ID='sixty_gcp',
        AIRFLOW__CORE__REMOTE_BASE_LOG_FOLDER=''
        'gs://{}/logs/airflow'.format(project_id),
        AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT=''
        ';?extra__google_cloud_platform__project={}'.format(project_id),
        AIRFLOW_CONN_BIGQUERY_DEFAULT=''
        ';?extra__google_cloud_platform__project={}'.format(project_id),
        AIRFLOW__CORE__TASK_LOG_READER='gcs.task',
        FERNET_KEY='Yd02MB6W0KXvklEG1FPxOJt_A-V3ARvnvp1TMfdPivc=',
        REDIS_HOST='celery-redis',
        POSTGRES_DB='airflow',
        POSTGRES_HOST='localhost',
        POSTGRES_USER='postgres',
        POSTGRES_PASSWORD=project_id,
        DB_CONNECTION_NAME=db_info['connectionName'],
    )
    client = get_api_client(project_id, cluster_name)
    if next((x for x in client.list_namespaced_config_map(namespace).items
             if x.metadata.name == configmap_name), None):
        logger.warn('Deleting configmap {} in cluster {} ns {}'.format(
            configmap_name, cluster_name, namespace))
        client.delete_namespaced_config_map(configmap_name, namespace, {})
    client.create_namespaced_config_map(
        namespace, V1ConfigMap(data=data, metadata=dict(name=configmap_name)))
    logger.info('Created configmap {} in cluster {} ns {}'.format(
        configmap_name, cluster_name, namespace))
