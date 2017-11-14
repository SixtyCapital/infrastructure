from __future__ import unicode_literals
from __future__ import absolute_import
from tempfile import mkstemp
from os import unlink
from kubernetes.config.kube_config import new_client_from_config
from kubernetes.client import CoreV1Api
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


def create_airflow_secrets(project_id, cluster_name, db_instance_name):
    namespace = 'airflow'
    secrets_name = 'airflow-secrets'
    db_info = describe_db_instance(project_id, db_instance_name)
    secrets = {
        'db-connection-name': db_info['connectionName'],
        'db-user': 'postgres',
        'db-password': project_id,
        'db-airflow-database': 'airflow',
        'airflow-log-folder': 'gs://{}/logs/airflow'.format(project_id),
        'project-id': project_id
    }
    client = get_api_client(project_id, cluster_name)
    client.list_namespaced_secret(namespace)
    if next((x for x in client.list_namespaced_secret(namespace).items
             if x.metadata.name == secrets_name), None):
        logger.warn('Deleting secret {} in cluster {} ns {}'.format(
            secrets_name, cluster_name, namespace))
        client.delete_namespaced_secret(
            name=secrets_name, namespace=namespace, body={})
    client.create_namespaced_secret(
        namespace=namespace,
        body={'stringData': secrets,
              'metadata': {'name': secrets_name}})
    logger.info('Created secret {} in cluster {} ns {}'.format(
        secrets_name, cluster_name, namespace))
