from __future__ import unicode_literals
from __future__ import absolute_import
from googleapiclient.discovery import build
from sixtyctl.util import getLogger
from sixtyctl.config import SCRATCH_PROJECTS, STRATEGY_PROJECTS

logger = getLogger(__name__)
REGION = 'us-east4'
ZONE = '{}-c'.format(REGION)


def create_project(project_id):
    logger.info('Creating project {}'.format(project_id))
    svc = build('cloudresourcemanager', 'v1')
    project_list = svc.projects().list().execute()['projects']
    if [x for x in project_list if x['name'] == project_id]:
        logger.warn('Project {} already exists!'.format(project_id))
        return lambda: True
    req = svc.projects().create(body=dict(
        project_id=project_id,
        name=project_id))
    operation_id = req.execute()['name']

    def check_status():
        res = svc.operations().get(name=operation_id).execute()
        return 'done' in res and res['done']
    return check_status


def attach_billing(project_id, billing_account):
    logger.info('Attaching billing account {} to project {}'.format(
        billing_account, project_id))
    svc = build('cloudbilling', 'v1')
    # this returns something like 'billingAccounts/013B3C-CBCAC6-1DF6AE'
    billing_account_name = next(
        b['name']
        for b in svc.billingAccounts().list().execute()['billingAccounts']
        if b['displayName'] == billing_account)
    return svc.projects().updateBillingInfo(
        name='projects/{}'.format(project_id),
        body={
            'billingAccountName': billing_account_name,
            'billingEnabled': True,
            'name': 'projects/{}/billingInfo'.format(project_id),
            'projectId': project_id}
        ).execute()


def enable_services(project_id):
    svc = build('servicemanagement', 'v1')
    service_names = [
        'cloudapis.googleapis.com',
        'servicemanagement.googleapis.com',
        'compute.googleapis.com',
        'clouddebugger.googleapis.com',
        'bigquery-json.googleapis.com',
        'datastore.googleapis.com',
        'storage-component.googleapis.com',
        'pubsub.googleapis.com',
        'container.googleapis.com',
        'storage-api.googleapis.com',
        'logging.googleapis.com',
        'resourceviews.googleapis.com',
        'replicapool.googleapis.com',
        'sourcerepo.googleapis.com',
        'deploymentmanager.googleapis.com',
        'containerregistry.googleapis.com',
        'monitoring.googleapis.com',
        'sql-component.googleapis.com',
        'cloudtrace.googleapis.com',
        'replicapoolupdater.googleapis.com',
        'cloudbuild.googleapis.com',
        "sqladmin.googleapis.com"
    ]
    res = svc.services().list(
        consumerId='project:{}'.format(project_id), pageSize=500).execute()
    enabled_svcs = (
        set(x['serviceName'] for x in res['services'])
        if 'services' in res else set())
    operations = {}
    for service_name in service_names:
        if service_name in enabled_svcs:
            continue
        req_body = dict(consumerId='project:{}'.format(project_id))
        operation = svc.services().enable(
            serviceName=service_name, body=req_body).execute()
        operations[operation['name']] = False

    def check_status():
        def check_operation_status(operation_name):
            res = svc.operations().get(name=operation_name).execute()
            return 'done' in res and res['done']
        for operation_name, is_done in operations.items():
            operations[operation_name] = is_done = (
                is_done or check_operation_status(operation_name))
            if not is_done:
                return False
        return True

    return check_status


def create_db_instance(project_id, db_instance_name):
    logger.info('Creating database {} in project {}'.format(
        db_instance_name, project_id))
    svc = build('sqladmin', 'v1beta4')

    res = svc.instances().list(project=project_id).execute()
    if [x for x in res.get('items', []) if x['name'] == db_instance_name]:
        logger.warn('DB instance {} already exists!'.format(db_instance_name))
        return lambda: True

    body = {
        'databaseVersion': 'POSTGRES_9_6',
        'name': db_instance_name,
        'project': project_id,
        'region': REGION,
        'settings': {
            'activationPolicy': 'ALWAYS',
            'backupConfiguration': {
                'binaryLogEnabled': True,
                'enabled': True,
                'startTime': '23:00'},
            'dataDiskSizeGb': '10',
            'dataDiskType': 'PD_SSD',
            'locationPreference': {
                'zone': ZONE},
            'maintenanceWindow': {
                'day': 6,
                'hour': 20},
            'pricingPlan': 'PER_USE',
            'storageAutoResize': True,
            'storageAutoResizeLimit': '0',
            'tier': 'db-custom-1-3840'}}
    operation = svc.instances().insert(project=project_id, body=body).execute()

    def check_status():
        status = svc.operations().get(
            project=project_id,
            operation=operation['name']).execute()['status']
        if status not in ['PENDING', 'RUNNING', 'DONE']:
            raise Exception('Invalid db status: {}'.format(status))
        return status == 'DONE'

    return check_status


def create_db(project_id, db_instance_name, db_name):
    svc = build('sqladmin', 'v1beta4')
    res = svc.databases().list(
        project=project_id, instance=db_instance_name).execute()
    if [x for x in res.get('items', []) if x['name'] == db_name]:
        logger.warn('Database {} already exists!'.format(db_instance_name))
        return True  # short circuit if database already exists
    status = svc.databases().insert(
        project=project_id,
        instance=db_instance_name,
        body=dict(instance=db_instance_name, name=db_name, project=project_id)
        ).execute()['status']
    if status == 'DONE':
        return True
    else:
        raise Exception('Error creating db, unknown status {}'.format(status))


def describe_db_instance(project_id, db_instance_name):
    svc = build('sqladmin', 'v1beta4')
    return svc.instances().get(
        project=project_id, instance=db_instance_name).execute()


def update_default_db_password(project_id, db_instance_name):
    svc = build('sqladmin', 'v1beta4')
    logger.info('Updating default password for user postgres in {}'.format(
        db_instance_name))
    return svc.users().update(
        project=project_id,
        instance=db_instance_name,
        name='postgres',
        # network is secure so set the password to something standard
        # we're using the project name as password to minimize accidents
        body={'password': project_id},
        host='').execute()


def create_container_cluster(project_id, cluster_name, zone=None):
    if not zone:
        zone = ZONE
    logger.info('Creating container cluster {} in project {}'.format(
        cluster_name, project_id))
    svc = build('container', 'v1')
    list_res = svc.projects().zones().clusters().list(
        projectId=project_id, zone=ZONE).execute().get('clusters', [])
    if [x for x in list_res if x['name'] == cluster_name]:
        logger.warn('Container cluster {} already exists!'.format(
            cluster_name))
        return lambda: True  # short circuit if cluster exists
    node_oauth_scopes = [
        'https://www.googleapis.com/auth/bigquery',
        'https://www.googleapis.com/auth/compute',
        'https://www.googleapis.com/auth/devstorage.read_write',
        'https://www.googleapis.com/auth/service.management.readonly',
        'https://www.googleapis.com/auth/servicecontrol',
        'https://www.googleapis.com/auth/logging.write',
        'https://www.googleapis.com/auth/monitoring',
        'https://www.googleapis.com/auth/sqlservice.admin']
    body = {
        'locations': [ZONE],
        'loggingService': 'logging.googleapis.com',
        'monitoringService': 'monitoring.googleapis.com',
        'name': cluster_name,
        'nodePools': [{
            'name': 'small',
            'autoscaling': {
                'enabled': True,
                'maxNodeCount': 20,
                'minNodeCount': 1},
            'config': {
                'diskSizeGb': 100,
                'imageType': 'ubuntu',
                'machineType': 'n1-standard-1',
                'oauthScopes': node_oauth_scopes},
            'initialNodeCount': 1
        }, {
            'name': 'large-preemptible',
            'autoscaling': {
                'enabled': True,
                'maxNodeCount': 20,
                'minNodeCount': 1},
            'config': {
                'diskSizeGb': 300,
                'imageType': 'ubuntu',
                'machineType': 'n1-standard-8',
                'oauthScopes': node_oauth_scopes,
                'preemptible': True},
            'initialNodeCount': 1}]}
    operation = svc.projects().zones().clusters().create(
        projectId=project_id, zone=ZONE, body={'cluster': body}).execute()

    def check_status():
        status = svc.projects().zones().operations().get(
            projectId=project_id, zone=ZONE,
            operationId=operation['name']).execute()['status']
        if status not in ['PENDING', 'RUNNING', 'DONE']:
            raise Exception('Invalid cluster status: {}'.format(status))
        return status == 'DONE'

    return check_status


def describe_container_cluster(project_id, cluster_name):
    svc = build('container', 'v1')
    return svc.projects().zones().clusters().get(
        projectId=project_id,
        zone=ZONE,
        clusterId=cluster_name).execute()


def describe_default_compute_service_account(project_id):
    svc = build('iam', 'v1')
    default_name = 'Compute Engine default service account'
    svc_accounts = svc.projects().serviceAccounts().list(
        name='projects/{}'.format(project_id),
        pageSize=100).execute()['accounts']
    return next(x for x in svc_accounts
                if x.get('displayName') == default_name)


def create_project_buckets(project_id):
    svc = build('storage', 'v1')
    # see https://cloud.google.com/storage/docs/managing-lifecycles
    buckets = [{
        'name': project_id,
        'storageClass': 'REGIONAL',
        'location': REGION,
        'lifecycle': {
            'rule': [{
                # downgrade storange class after 1 month
                'action': {
                    'type': 'SetStorageClass',
                    'storageClass': 'NEARLINE'
                },
                'condition': {
                    'age': 31
                }
            }]
        }
    }, {
        'name': '{}-temp'.format(project_id),
        'storageClass': 'REGIONAL',
        'location': REGION,
        'lifecycle': {
            'rule': [{
                # delete gcs objects after 2 weeks
                'action': {
                    'type': 'Delete'
                },
                'condition': {'age': 14}
            }, {
                # downgrade storage class after 3 days
                'action': {
                    'type': 'SetStorageClass',
                    'storageClass': 'NEARLINE'
                },
                'condition': {
                    'age': 3
                }
            }]
        }
    }]
    existing_buckets = svc.buckets().list(
        project=project_id).execute().get('items', [])
    for bucket in buckets:
        bucket_name = bucket['name']
        if next((bucket for bucket in existing_buckets
                 if bucket['name'] == bucket_name), None):
            logger.warn('Bucket {} already exists for project {}'.format(
                bucket_name, project_id))
        else:
            svc.buckets().insert(
                project=project_id,
                body=bucket).execute()
            logger.info('Bucket {} created in project {}'.format(
                bucket_name, project_id))


def grant_bucket_access(project_id):
    svc_email = describe_default_compute_service_account(project_id)['email']
    # grant access to GCR buckets
    gcr_projects = SCRATCH_PROJECTS
    if project_id not in SCRATCH_PROJECTS:
        gcr_projects += STRATEGY_PROJECTS
    svc = build('storage', 'v1')
    member = 'serviceAccount:{}'.format(svc_email)
    role_name = 'roles/storage.objectViewer'
    for gcr_project in gcr_projects:
        gcr_bucket = 'artifacts.{}.appspot.com'.format(gcr_project)
        iam_bindings = svc.buckets().getIamPolicy(
            bucket=gcr_bucket).execute()['bindings']
        role = next(
            (x for x in iam_bindings
             if x['role'] == role_name),
            None)
        if not role:
            role = {'role': role_name, 'members': []}
            iam_bindings.append(role)
        if member in role['members']:
            logger.warn('{} already has access to GCR for {}'.format(
                member, gcr_project))
        else:
            role['members'].append(member)
            svc.buckets().setIamPolicy(
                bucket=gcr_bucket, body={'bindings': iam_bindings}).execute()
            logger.info('{} granted access to GCR for {}'.format(
                member, gcr_project))
