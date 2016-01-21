### Automated iPython Server

#### Usage:

Connect to a dev linux server: `ssh ubuntu@54.172.16.9 -i keys/temp2014-10-10.pem`

To deploy EC2 instance and tag it with class=notebook:  
`ansible-playbook deploy_ec2.yml`

To install, configure, and run ipython notebook server on the EC2:  
`ansible-playbook -i ec2.py deploy_notebook.yml`

Link to notebook will be displayed on debug message.

To start ipython notebook only, and display link:  
`ansible-playbook -i ec2.py deploy_notebook.yml --tags=run`

To kill ipython notebook:  
`ansible-playbook -i ec2.py kill_notebook.yml`  



