# Docker howto
This is a quick guide on how to inteteract with the Docker written in a form of howto's.

## What is ECR
**ECR** is stands as EC2 Container Registry. Here we keep our container images. In terms of ECR, every container image is a **Repository**. In every repository we can keep one or more versions of some image. Every version has it own **tag**.

So, name of every image can be written in the next form: `ECR name/repo:tag`, where ECR name every time is `491722570113.dkr.ecr.us-east-1.amazonaws.com`.

For example, latest version of our basic development image has a name: `491722570113.dkr.ecr.us-east-1.amazonaws.com/development:latest`

## How to pull an image from ECR
`docker pull 491722570113.dkr.ecr.us-east-1.amazonaws.com/repo:tag`

Please keep in mind, that ECR is a private regisrty, so before pulling an image, you have to authenticate first. 

## How to autenticate against ECR
There are two ways to authentiacate - using your personal key pair, or using an instance role. For AWS instance, preferred way is to use an IAM instance role called `ecsInstanceRole`. This role has permission to access ECR, so having this role attached to the instance, you do not have to use your personal keys. If you're going to use ECR from your laptop - personal keys is the only way.

Regardless, are you using your personal keys or an Instance role - you have to install the `aws` tool to authenticate. You can do it by pip: `pip install awscli`. After that, create `~/.aws` directory, and put the `config` file there with a following content:

```
[default]
region=us-east-1
```
If you're going to use your personal keys, create `~/.aws/credentials` file, and put your keys there:

```
aws_access_key_id = AKIAxxxxxx
aws_secret_access_key = XxXxXxXxXxXxXxX
```
If you're going to use an Instance role - you do not need credentials file.

To authenticate against ECR, type `aws ecr get-login`
## How to start container
Every container must have at least one process running inside. If there are no running processes - the container does not running itself. 

For example, our **development** image does not contain any daemons inside. Because of that, you can run the conainer out of this image in interactive mode only:

`docker run -it 491722570113.dkr.ecr.us-east-1.amazonaws.com/development:latest /bin/bash`

This command will start a `bash` process inside a container. To exit from that container - just press Ctrl+D.

If you want to run a container as a daemon (non-interactive), you have to swap `-it` with `-d` and bypass the shell:

`docker run -d some_image:latest`

## How to stop container

`docker kill <id>`

where **id** is a container id

## How to enter running container

`docker exec -it <id> /bin/bash`

where **id** is a container id. This command just run a `bash` process inside a running container. To exit, just press Ctrl+D.

## How to get a container id

`docker ps` shows a list of running containers. Add `-a` to also show stopped containers.