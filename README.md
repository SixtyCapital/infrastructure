# Quick examples

## How to start a development machine
1. Use the Tower or command line to deploy an instance:
	`ansible-playbook deploy_ec2_development_docker.yml -i hosts`
2. SSH to the instance, and start command shell in Docker container: `docker run -ti 491722570113.dkr.ecr.us-east-1.amazonaws.com/development /bin/bash`
	
### Variables to redefine:
- `keyname`: SSH key name to use
- `tag`: ECR image tag to use
- `name`: tag name for a instance, default is "development"
- `repos`: list of Git repos to clone, in a form of *dict*, default is `sixty: develop`

	
## How to start a Jupyter machine
1. Use the Tower or command line to deploy an instance:
	`ansible-playbook deploy_ec2_jupyter.yml -i hosts`
2. Point your browser to `https://x.x.x.x:8888`, where `x.x.x.x` is IP address of deployed machine.

### Variables to redefine:
- `keyname`: SSH key name to use
- `tag`: ECR image tag to use
- `name`: tag name for a instance, default is "notebook"
- `repos`: list of Git repos to clone, in a form of *dict*, default is `sixty: develop`

## How to start a Celery grid
1. Use the Tower or command line to deploy a grid:
	`ansible-playbook deploy_ec2_celery_grid.yml -i hosts`
2. Point your browser to `https://x.x.x.x:5555`, where `x.x.x.x` is IP address of a master machine.

### Variables to redefine:
- `keyname`: SSH key name to use
- `tag`: ECR image tag to use
- `name`: tag name for a grid, default is "CeleryGrid"
- `count`: count of worker instances, default is 7
- `repos`: list of Git repos to clone, in a form of *dict*, default is `sixty: develop`
- `env`: list of environment variables to set in a form of *dict*
- `etl_start`: line to be passed to ETL script start

## More documentation:

- [Full list of Ansible playbooks](docs/Ansible playbooks.md)
- [Docker how-to](docs/Docker howto.md)
- [SSH agent how-to](docs/SSH agent howto.md)