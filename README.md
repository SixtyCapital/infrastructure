## Security policies

### General access

Three levels:
- **technology** - access to all technology assets, such as the sixty & infrastructure repos
- **investment** - access to all proprietary investment assets apart from investment strategies
- **administrator** - access to everything, including changing permissions. Includes investment strategies by default

Each have a group on AWS.

TODO: align GitHub with these

### Strategy access

Access to investment strategies (sector / commodity) is on a strategy-by-strategy basis.

Each has a group on AWS, which people are added individually to the repos on GitHub

### Circle-CI access

There is a Circle-CI user for each level required:
- circle-technology
- circle-investment
- circle-strategy-*

These need to be added to the relevant Circle-CI project's environment variable

### ECR access

ECR access is explicitly offered through policies attached to the groups.

Nothing is attached to the investment group because there aren't any applicable containers. I think it would make sense to add a 'research' / 'lab' / 'investment' container that had all the investment repos on.

### Remaining TODOs

- Remove S3-Dev user (and the keys in sixty repo), forcing people to supply their own credentials when running stuff
- Prevent lower security users from doing destructive things, such as pushing to ECR repos (particularly master), or deleting from S3
- Currently there are multiple production roles on AWS, not sure what's going on there. Does production actually run under a role?
- DB keys are badly managed now - could put them in a S3 bucket or use KMS
- Google Cloud security is not as developed

# Quick examples

NB: These are a bit out of date. The policy now is to start an empty machine, and then pull the containers you need and start them on the RI

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
