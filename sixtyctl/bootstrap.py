from __future__ import unicode_literals
from __future__ import absolute_import
from time import sleep
from sixtyctl.gcp import (
    add_vpc_peering_to_trading,
    create_project,
    attach_billing,
    enable_services,
    create_project_buckets,
    create_db_instance,
    create_db,
    create_container_cluster,
    delete_default_subnetworks,
    update_default_db_password,
    grant_bucket_access,
    grant_bigquery_access,
    grant_kms_access,
)
from sixtyctl.kubernetes import create_namespaces, create_airflow_configmap
from sixtyctl.util import getLogger

logger = getLogger(__name__)


def run(project_id):
    billing_account = "sixty-invoice-billing"
    db_instance_name = "airflow-postgres-119"
    db_name = "airflow"
    cluster_name = project_id

    is_project_created = create_project(project_id)
    while not is_project_created():
        logger.info("Waiting for project to be created...")
        sleep(3)
    sleep(3)  # project sometimes not immediately available
    attach_billing(project_id, billing_account)
    are_services_enabled = enable_services(project_id)
    while not are_services_enabled():
        logger.info("Waiting for services to be enabled")
        sleep(3)
    create_project_buckets(project_id)

    is_subnetworks_ready = delete_default_subnetworks(project_id)
    while not is_subnetworks_ready():
        logger.info("Waiting for subnetworks to be deleted...")
        sleep(3)

    add_vpc_peering_to_trading(project_id)

    is_db_ready = create_db_instance(project_id, db_instance_name)
    is_cluster_ready = create_container_cluster(project_id, cluster_name)
    while not is_db_ready():
        logger.info("Waiting for db to launch...")
        sleep(3)
    create_db(project_id=project_id, db_instance_name=db_instance_name, db_name=db_name)
    update_default_db_password(project_id, db_instance_name)
    while not is_cluster_ready():
        logger.info("Waiting for cluster to launch...")
        sleep(3)
    grant_bucket_access(project_id)
    grant_bigquery_access(project_id)
    grant_kms_access(project_id)
    create_namespaces(project_id, cluster_name)
    create_airflow_configmap(project_id, cluster_name, db_instance_name)


def test():
    import random

    project_id = "integration-test-%x" % random.getrandbits(32)
    logger.info("Integration run started for {}".format(project_id))
    run(project_id)
