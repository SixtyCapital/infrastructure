# SSH agent howto

Ok, here a brief overview on how to not keep your access keys in the repo.
 
##The most easier part is AWS keys.
 
To set AWS keys on Tower, you have to setup them in the *Credentials* section (Add *Amazon Web Services Key*), then define these keys on the Job Template (*Cloud Credential*).

To use AWS key from command line, you have to set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` shell variables. A good place to set these files is `~/.bash_profile` file.
 
##Next, a GitHub key.

Since we're using SSH keys to access GitHub, we will use SSH-generated keypairs. 

At first, you have togenerate your keypair. Default keypair is stored in `~/.ssh` directory (`id_rsa` & `id_rsa.pub` files). Almost all of you already have default keys generated. You can use your default keys to access GitHub repositories. But if you don't like to upload your default private key into Ansible Tower - feel free to generate a new keypair with `ssh-keygen` command.
 
If you working with the Tower - then you just have to upload your private SSH key into Credentials section (*Machine Key*), then define this key on the Job Template (*Machine Credential*). This is all for the Tower.
 
If you are working with console - the next thing that you have to do is to add your key to the agent with `ssh-add` command. You can add more than one key. Please use `ssh-add -l` command to list all added keys.
 
And the last thing (you have to do it once) - please check that next configuration strings are exist in your local `ansible.cfg`:

```
[ssh_connection]
ssh_args=-o ForwardAgent=yes
```

That's all. Do not forget to add a corresponding public key to your GitHub profile to access private repositories. And make sure you're not using `sudo` when checking GitHub repository from Ansible task.