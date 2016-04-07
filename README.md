# Ansible cookbooks


## Plain deployment cookbooks

### `deploy_ec2_celery_machine.yml`

Build & deploy Celery machine on EC2 instance

### `deploy_ec2_development_machine.yml`

Build & deploy Development machine on EC2 instance

## Docker deployment cookbooks

### `deploy_ec2_celery_docker.yml`

Deploy Celery machine on EC2 using prebuilt Docker container

### `deploy_ec2_development_docker.yml`

Deploy Development machine on EC2 using prebuilt Docker container

### `deploy_ec2_notebook_docker.yml`

Deploy iPython Notebook on EC2 using prebuilt Docker container

## Build cookbooks

###  `build_development.yml`

Builds basis Docker container (APT & PIP installs) and pushes it to ECR

### `build_celery.yml`

Builds Docker container for Celery machine and pushes it to ECR

### `build_notebook.yml`

Builds Docker container for iPython notebook and pushes it to ECR

## Other cookbooks

### `docker_celery.yml`
Used by `build_celery.yml`
### `docker_development.yml`
Used by `build_development.yml`
### `docker_notebook.yml`
Used by `build_notebook.yml`





