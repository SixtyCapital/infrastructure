# SSH agent howto

##GitHub keys.

Since we're using SSH keys to access GitHub, we will use SSH-generated keypairs - either your default or one you generate. 

At first, you have to generate your keypair. Default keypair is stored in `~/.ssh` directory (`id_rsa` & `id_rsa.pub` files). Almost all of you already have default keys generated. You can use your default keys to access GitHub repositories. But if you don't like to upload your default private key into Ansible Tower - feel free to generate a new keypair with `ssh-keygen` command. (Below)

####This creates a new ssh key
https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/

####This uploads the SSH key to git and allows that key to be used to download all repositories that your account has access to.
https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account/

####In order to boot machines with this key - you need to provide it to amazon:
http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#how-to-generate-your-own-key-and-import-it-to-aws

####Finally - In order to for tower to run jobs on your machine - it must have this key as well
Click on the wrench/screwdriver icon in the top right to access the settings menu.
Upload your private SSH key into Credentials section - using 'ubuntu' for the username, and 'Machine' for the type.
For 'Who owns this key' - select user - then admin. This restricts who can run playbooks with this key.
Then to setup the ansible job - you can either modify an existing Job Template - e.g. https://52.6.98.70/#/job_templates/69 and select your key under (*Machine Credential*) - or you can copy an existing job and and modify the copied job.

Lastly - provide keyname: *yourkeyname* in the extra_args section when you start a job. (Similar to how we provide instance types)
 
###Below is if you are not using ansible tower
If you are working with console - the next thing that you have to do is to add your key to the agent with `ssh-add` command. You can add more than one key. Please use `ssh-add -l` command to list all added keys.
 
And the last thing (you have to do it once) - please check that next configuration strings are exist in your local `ansible.cfg`:

```
[ssh_connection]
ssh_args=-o ForwardAgent=yes
```

That's all. Do not forget to add a corresponding public key to your GitHub profile to access private repositories. And make sure you're not using `sudo` when checking GitHub repository from Ansible task.
