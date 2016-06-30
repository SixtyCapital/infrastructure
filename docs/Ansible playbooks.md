# Ansible playbooks

## Deployment playbooks

### `deploy_ec2_celery_worker.yml`

Deploy Celery machine on EC2 using prebuilt Docker container

### `deploy_ec2_celery_grid.yml`

Deploy Celery grid (worker machines + flower machine) on EC2 using prebuilt Docker container

### `deploy_ec2_development_docker.yml`

Deploy Development machine on EC2 using prebuilt Docker container

### `deploy_ec2_jupyter.yml`

Deploy iPython Jupyter on EC2 using prebuilt Docker container

## Build playbook

###  `deploy_ec2_builder.yml`

Deploy Builder machine, which builds Docker container and pushes it to ECR. Can be supplied with one of following tags (without tags builds all of them):

#### `--tags development`

Builds a basic Docker container (APT & PIP installs)

#### `--tags celery`

Builds a Docker container for Celery machine

#### `--tags jupyter`

Builds a Docker container for iPython jupyter

## Other playbooks

### `build_container.yml`
Used by `deploy_ec2_builder.yml` to build containers
### `update_workers.yml`
Update Git repos on running workers and restart workers containers






