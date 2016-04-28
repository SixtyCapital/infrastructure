# Ansible cookbooks


## Plain deployment cookbooks

### `deploy_ec2_celery_machine.yml`

Build & deploy Celery machine on EC2 instance

### `deploy_ec2_development_machine.yml`

Build & deploy Development machine on EC2 instance

## Docker deployment cookbooks

### `deploy_ec2_celery_docker.yml`

Deploy Celery machine on EC2 using prebuilt Docker container

### `deploy_ec2_celery_grid.yml`

Deploy Celery grid (worker machines + flower machine) on EC2 using prebuilt Docker container

### `deploy_ec2_development_docker.yml`

Deploy Development machine on EC2 using prebuilt Docker container

### `deploy_ec2_notebook_docker.yml`

Deploy iPython Notebook on EC2 using prebuilt Docker container

## Build cookbooks

###  `deploy_ec2_builder.yml`

Deploy Builder machine which builds Docker container and pushes it to ECR. Must be supplied with one of following tags:

#### `--tags development`

Builds a basic Docker container (APT & PIP installs)

#### `--tags celery`

Builds a Docker container for Celery machine

#### `--tags notebook`

Builds a Docker container for iPython notebook

## Other cookbooks

### `docker_celery.yml`
Used by `deploy_ec2_builder.yml --tags celery`
### `docker_development.yml`
Used by `deploy_ec2_builder.yml --tags development`
### `docker_notebook.yml`
Used by `deploy_ec2_builder.yml --tags notebook`





