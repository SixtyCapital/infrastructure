from __future__ import absolute_import, unicode_literals

from googleapiclient.discovery import build

from sixtyctl.config import (
    EXTERNAL_PROJECTS,
    KMS_PROJECT,
    SCRATCH_PROJECTS,
    STRATEGY_PROJECTS,
)
from sixtyctl.util import getLogger

logger = getLogger(__name__)
REGION = "us-east4"
ZONE = "{}-c".format(REGION)

# by default, the quota for CPUs is 24 for a new project so we cannot
# add the third region.
BACKUP_ZONES = ["{}-a".format(REGION)]


def create_project(project_id):
    logger.info("Creating project {}".format(project_id))
    svc = build("cloudresourcemanager", "v1")
    project_list = svc.projects().list().execute()["projects"]
    if [x for x in project_list if x["name"] == project_id]:
        logger.warn("Project {} already exists!".format(project_id))
        return lambda: True
    req = svc.projects().create(body=dict(project_id=project_id, name=project_id))
    operation_id = req.execute()["name"]

    def check_status():
        res = svc.operations().get(name=operation_id).execute()
        return "done" in res and res["done"]

    return check_status


def attach_billing(project_id, billing_account):
    logger.info(
        "Attaching billing account {} to project {}".format(billing_account, project_id)
    )
    svc = build("cloudbilling", "v1")
    # this returns something like 'billingAccounts/013B3C-CBCAC6-1DF6AE'
    billing_account_name = next(
        b["name"]
        for b in svc.billingAccounts().list().execute()["billingAccounts"]
        if b["displayName"] == billing_account
    )
    return (
        svc.projects()
        .updateBillingInfo(
            name="projects/{}".format(project_id),
            body={
                "billingAccountName": billing_account_name,
                "billingEnabled": True,
                "name": "projects/{}/billingInfo".format(project_id),
                "projectId": project_id,
            },
        )
        .execute()
    )


def enable_services(project_id):
    svc = build("servicemanagement", "v1")
    service_names = [
        "bigquery-json.googleapis.com",
        "cloudapis.googleapis.com",
        "cloudbuild.googleapis.com",
        "clouddebugger.googleapis.com",
        "cloudtrace.googleapis.com",
        "cloudkms.googleapis.com",
        "compute.googleapis.com",
        "container.googleapis.com",
        "containerregistry.googleapis.com",
        "datastore.googleapis.com",
        "deploymentmanager.googleapis.com",
        "logging.googleapis.com",
        "ml.googleapis.com",
        "monitoring.googleapis.com",
        "pubsub.googleapis.com",
        "replicapool.googleapis.com",
        "replicapoolupdater.googleapis.com",
        "resourceviews.googleapis.com",
        "servicemanagement.googleapis.com",
        "sourcerepo.googleapis.com",
        "sql-component.googleapis.com",
        "storage-api.googleapis.com",
        "storage-component.googleapis.com",
        "sqladmin.googleapis.com",
    ]
    res = (
        svc.services()
        .list(consumerId="project:{}".format(project_id), pageSize=500)
        .execute()
    )
    enabled_svcs = (
        set(x["serviceName"] for x in res["services"]) if "services" in res else set()
    )
    operations = {}
    for service_name in service_names:
        if service_name in enabled_svcs:
            continue
        req_body = dict(consumerId="project:{}".format(project_id))
        operation = (
            svc.services().enable(serviceName=service_name, body=req_body).execute()
        )
        operations[operation["name"]] = False

    def check_status():
        def check_operation_status(operation_name):
            res = svc.operations().get(name=operation_name).execute()
            return "done" in res and res["done"]

        for operation_name, is_done in operations.items():
            operations[operation_name] = is_done = is_done or check_operation_status(
                operation_name
            )
            if not is_done:
                return False
        return True

    return check_status


def create_db_instance(project_id, db_instance_name):
    logger.info(
        "Creating database {} in project {}".format(db_instance_name, project_id)
    )
    svc = build("sqladmin", "v1beta4")

    res = svc.instances().list(project=project_id).execute()
    if [x for x in res.get("items", []) if x["name"] == db_instance_name]:
        logger.warn("DB instance {} already exists!".format(db_instance_name))
        return lambda: True

    body = {
        "databaseVersion": "POSTGRES_9_6",
        "name": db_instance_name,
        "project": project_id,
        "region": REGION,
        "settings": {
            "activationPolicy": "ALWAYS",
            "backupConfiguration": {"enabled": True, "startTime": "23:00"},
            "dataDiskSizeGb": "10",
            "dataDiskType": "PD_SSD",
            "locationPreference": {"zone": ZONE},
            "maintenanceWindow": {"day": 6, "hour": 20},
            "pricingPlan": "PER_USE",
            "storageAutoResize": True,
            "storageAutoResizeLimit": "0",
            # only need one this large because of the number of connections
            # ideally would be just above 7.5GB (same between 7.5 and 15),
            # but need to check how to send custom reqs
            # Could also use pgbouncer or mysql - vanilla postgres seems to be bad
            # at handling lots of connections
            "tier": "db-custom-4-15360",
        },
    }
    operation = svc.instances().insert(project=project_id, body=body).execute()

    def check_status():
        status = (
            svc.operations()
            .get(project=project_id, operation=operation["name"])
            .execute()["status"]
        )
        if status not in ["PENDING", "RUNNING", "DONE"]:
            raise Exception("Invalid db status: {}".format(status))
        return status == "DONE"

    return check_status


def create_db(project_id, db_instance_name, db_name):
    svc = build("sqladmin", "v1beta4")
    res = svc.databases().list(project=project_id, instance=db_instance_name).execute()
    if [x for x in res.get("items", []) if x["name"] == db_name]:
        logger.warn("Database {} already exists!".format(db_instance_name))
        return True  # short circuit if database already exists
    status = (
        svc.databases()
        .insert(
            project=project_id,
            instance=db_instance_name,
            body=dict(instance=db_instance_name, name=db_name, project=project_id),
        )
        .execute()["status"]
    )
    if status == "DONE":
        return True
    else:
        raise Exception("Error creating db, unknown status {}".format(status))


def describe_db_instance(project_id, db_instance_name):
    svc = build("sqladmin", "v1beta4")
    return svc.instances().get(project=project_id, instance=db_instance_name).execute()


def update_default_db_password(project_id, db_instance_name):
    svc = build("sqladmin", "v1beta4")
    logger.info(
        "Updating default password for user postgres in {}".format(db_instance_name)
    )
    return (
        svc.users()
        .update(
            project=project_id,
            instance=db_instance_name,
            name="postgres",
            # network is secure so set the password to something standard
            # we're using the project name as password to minimize accidents
            body={"password": project_id},
            host="",
        )
        .execute()
    )


def delete_default_subnetworks(project_id):
    svc = build("compute", "v1")
    logger.info("Deleting default subnetworks in project {}".format(project_id))

    # Switch network to custom mode so we can delete default subnets
    svc.networks().switchToCustomMode(project=project_id, network="default").execute()

    subnetworks_map = (
        svc.subnetworks().aggregatedList(project=project_id).execute()["items"]
    )

    for region in subnetworks_map:
        for subnetwork in subnetworks_map[region]["subnetworks"]:
            region_name = region.split("/")[1]
            svc.subnetworks().delete(
                project=project_id, region=region_name, subnetwork="default"
            ).execute()

    def check_status():
        subnetworks = (
            svc.subnetworks().aggregatedList(project=project_id).execute()["items"]
        )
        for region in subnetworks.keys():
            if "subnetworks" in subnetworks[region]:
                return False
        return True

    return check_status


def add_vpc_peering_to_trading(project_id):
    svc = build("compute", "v1")
    logger.info("Adding VPC peering for trading to project {}".format(project_id))

    body_external = {
        "peerNetwork": "https://www.googleapis.com/compute/v1/projects/sixty-trading-test/global/networks/default",  # noqa
        "name": "trading-link-" + project_id,
        "autoCreateRoutes": True,
    }
    svc.networks().addPeering(
        project=project_id, network="default", body=body_external
    ).execute()

    body_current = {
        "peerNetwork": "https://www.googleapis.com/compute/v1/projects/"
        + project_id
        + "/global/networks/default",
        "name": "trading-link-" + project_id,
        "autoCreateRoutes": True,
    }
    svc.networks().addPeering(
        project="sixty-trading-test", network="default", body=body_current
    ).execute()


def create_container_cluster(project_id, cluster_name, zone=None):
    if not zone:
        zone = ZONE
    logger.info(
        "Creating container cluster {} in project {}".format(cluster_name, project_id)
    )
    svc = build("container", "v1")
    list_res = (
        svc.projects()
        .zones()
        .clusters()
        .list(projectId=project_id, zone=ZONE)
        .execute()
        .get("clusters", [])
    )
    if [x for x in list_res if x["name"] == cluster_name]:
        logger.warn("Container cluster {} already exists!".format(cluster_name))
        return lambda: True  # short circuit if cluster exists
    node_oauth_scopes = [
        "https://www.googleapis.com/auth/bigquery",
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/compute",
        "https://www.googleapis.com/auth/devstorage.read_write",
        "https://www.googleapis.com/auth/service.management.readonly",
        "https://www.googleapis.com/auth/servicecontrol",
        "https://www.googleapis.com/auth/logging.write",
        "https://www.googleapis.com/auth/monitoring",
        "https://www.googleapis.com/auth/sqlservice.admin",
        "https://www.googleapis.com/auth/datastore",
    ]

    zones = [ZONE]
    zones.extend(BACKUP_ZONES)

    body = {
        "locations": zones,
        # TODO: upgrade to newer stackdriver
        # (done manually to existing projects)
        "loggingService": "logging.googleapis.com",
        "monitoringService": "monitoring.googleapis.com",
        "name": cluster_name,
        "nodePools": [
            {
                "name": "small",
                "autoscaling": {"enabled": True, "maxNodeCount": 20, "minNodeCount": 0},
                "management": {"autoUpgrade": True, "autoRepair": True},
                "config": {
                    "diskSizeGb": 100,
                    "imageType": "cos",
                    "machineType": "n1-standard-1",
                    "oauthScopes": node_oauth_scopes,
                },
                "initialNodeCount": 1,
            },
            {
                "name": "large-preemptible",
                "autoscaling": {"enabled": True, "maxNodeCount": 20, "minNodeCount": 0},
                "management": {"autoUpgrade": True, "autoRepair": True},
                "config": {
                    "diskSizeGb": 300,
                    "imageType": "cos",
                    "machineType": "n1-standard-8",
                    "oauthScopes": node_oauth_scopes,
                    "preemptible": True,
                },
                "initialNodeCount": 1,
            },
        ],
        "ipAllocationPolicy": {"useIpAliases": True, "createSubnetwork": True},
    }
    operation = (
        svc.projects()
        .zones()
        .clusters()
        .create(projectId=project_id, zone=ZONE, body={"cluster": body})
        .execute()
    )

    def check_status():
        status = (
            svc.projects()
            .zones()
            .operations()
            .get(projectId=project_id, zone=ZONE, operationId=operation["name"])
            .execute()["status"]
        )
        if status not in ["PENDING", "RUNNING", "DONE"]:
            raise Exception("Invalid cluster status: {}".format(status))
        return status == "DONE"

    return check_status


def describe_container_cluster(project_id, cluster_name):
    svc = build("container", "v1")
    return (
        svc.projects()
        .zones()
        .clusters()
        .get(projectId=project_id, zone=ZONE, clusterId=cluster_name)
        .execute()
    )


def describe_default_compute_service_account(project_id):
    svc = build("iam", "v1")
    default_name = "Compute Engine default service account"
    svc_accounts = (
        svc.projects()
        .serviceAccounts()
        .list(name="projects/{}".format(project_id), pageSize=100)
        .execute()["accounts"]
    )
    return next(x for x in svc_accounts if x.get("displayName") == default_name)


def create_project_buckets(project_id):
    svc = build("storage", "v1")
    # see https://cloud.google.com/storage/docs/managing-lifecycles
    buckets = [
        {
            "name": project_id,
            "storageClass": "REGIONAL",
            "location": REGION,
            "lifecycle": {
                "rule": [
                    {
                        # downgrade storange class after 1 month
                        "action": {
                            "type": "SetStorageClass",
                            "storageClass": "NEARLINE",
                        },
                        "condition": {"age": 31},
                    }
                ]
            },
        },
        {
            "name": "{}-temp".format(project_id),
            "storageClass": "REGIONAL",
            "location": REGION,
            "lifecycle": {
                "rule": [
                    {
                        # delete gcs objects after 2 weeks
                        "action": {"type": "Delete"},
                        "condition": {"age": 14},
                    }
                ]
            },
        },
    ]
    existing_buckets = svc.buckets().list(project=project_id).execute().get("items", [])
    for bucket in buckets:
        bucket_name = bucket["name"]
        if next(
            (bucket for bucket in existing_buckets if bucket["name"] == bucket_name),
            None,
        ):
            logger.warn(
                "Bucket {} already exists for project {}".format(
                    bucket_name, project_id
                )
            )
        else:
            svc.buckets().insert(project=project_id, body=bucket).execute()
            logger.info(
                "Bucket {} created in project {}".format(bucket_name, project_id)
            )


def grant_bucket_access(project_id):
    # TODO: we now use groups for this access; replace with group membership
    svc_email = describe_default_compute_service_account(project_id)["email"]
    # grant access to GCR buckets
    gcr_projects = SCRATCH_PROJECTS
    if project_id not in SCRATCH_PROJECTS:
        gcr_projects += STRATEGY_PROJECTS
    svc = build("storage", "v1")
    member = "serviceAccount:{}".format(svc_email)
    role_name = "roles/storage.objectViewer"
    buckets = [
        # GCR buckets
        "artifacts.{}.appspot.com".format(p)
        for p in gcr_projects
    ]
    buckets += EXTERNAL_PROJECTS
    for bucket in buckets:
        iam_bindings = svc.buckets().getIamPolicy(bucket=bucket).execute()["bindings"]
        role = next((x for x in iam_bindings if x["role"] == role_name), None)
        if not role:
            role = {"role": role_name, "members": []}
            iam_bindings.append(role)
        if member in role["members"]:
            logger.warn("{} already has access to bucket: {}".format(member, bucket))
        else:
            role["members"].append(member)
            svc.buckets().setIamPolicy(
                bucket=bucket, body={"bindings": iam_bindings}
            ).execute()
            logger.info("{} granted access to GCR for {}".format(member, bucket))


def grant_bigquery_access(project_id):
    # TODO: we now use groups for this access; replace with group membership
    # of service accounts
    if project_id in SCRATCH_PROJECTS:
        logger.info("Access not granted to ext data: {} is a scratch project")
        return
    for ext_project in EXTERNAL_PROJECTS:
        member = "serviceAccount:{}".format(
            describe_default_compute_service_account(project_id)["email"]
        )
        svc = build("cloudresourcemanager", "v1")
        policy_bindings = (
            svc.projects()
            .getIamPolicy(resource=ext_project, body={})
            .execute()["bindings"]
        )
        role_name = "roles/bigquery.admin"
        role = next((x for x in policy_bindings if x["role"] == role_name), None)
        if not role:
            role = {"role": role_name, "members": []}
            policy_bindings.append(role)
        if member in role["members"]:
            logger.warn(
                "{} already has bigquery access to {}".format(member, ext_project)
            )
        else:
            role["members"].append(member)
            # return policy_bindings
            svc.projects().setIamPolicy(
                resource=ext_project, body={"policy": {"bindings": policy_bindings}}
            ).execute()
            logger.info("{} granted bigquery access to {}".format(member, ext_project))


def grant_kms_access(project_id):
    # TODO: we now use groups for this access; replace with group membership
    svc_email = describe_default_compute_service_account(project_id)["email"]

    member = "serviceAccount:{}".format(svc_email)
    svc = build("cloudresourcemanager", "v1")

    policy_bindings = (
        svc.projects().getIamPolicy(resource=KMS_PROJECT, body={}).execute()["bindings"]
    )
    role_name = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
    role = next((x for x in policy_bindings if x["role"] == role_name), None)
    if not role:
        role = {"role": role_name, "members": []}
        policy_bindings.append(role)
    if member in role["members"]:
        logger.warn("{} already has KMS access to {}".format(member, KMS_PROJECT))
    else:
        role["members"].append(member)
        # return policy_bindings
        svc.projects().setIamPolicy(
            resource=KMS_PROJECT, body={"policy": {"bindings": policy_bindings}}
        ).execute()
        logger.info("{} granted KMS access to {}".format(member, KMS_PROJECT))
