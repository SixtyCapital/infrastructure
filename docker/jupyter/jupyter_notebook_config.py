# from https://github.com/jupyter/docker-stacks/blob/master/base-notebook/jupyter_notebook_config.py

from jupyter_core.paths import jupyter_data_dir
import subprocess
import os
import errno
import stat
from notebook.auth import passwd


PEM_FILE = os.path.join(jupyter_data_dir(), 'notebook.pem')

c = get_config()
c.NotebookApp.ip = '*'
c.NotebookApp.port = 8888
c.NotebookApp.open_browser = False

# Set a certificate if USE_HTTPS is set to any value
if 'USE_HTTPS' in os.environ:
    if not os.path.isfile(PEM_FILE):
        # Ensure PEM_FILE directory exists
        dir_name = os.path.dirname(PEM_FILE)
        try:
            os.makedirs(dir_name)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(dir_name):
                pass
            else: raise
        # Generate a certificate if one doesn't exist on disk
        subprocess.check_call(['openssl', 'req', '-new',
            '-newkey', 'rsa:2048', '-days', '365', '-nodes', '-x509',
            '-subj', '/C=XX/ST=XX/L=XX/O=generated/CN=generated',
            '-keyout', PEM_FILE, '-out', PEM_FILE])
        # Restrict access to PEM_FILE
        os.chmod(PEM_FILE, stat.S_IRUSR | stat.S_IWUSR)
    c.NotebookApp.certfile = PEM_FILE

# Set a password if PASSWORD is set (only second branch is in official jupter version)
if 'PASSWORD' in os.environ:
    c.NotebookApp.password = passwd(os.environ['PASSWORD'])
    # not even sure if this deletes it from the shell env?
    del os.environ['PASSWORD']
elif 'PASSWORD_HASH' in os.environ:
    c.NotebookApp.password = os.environ['PASSWORD_HASH']

# not from the link above
notebook_dir = os.environ.get('NOTEBOOK_DIR')

if notebook_dir:
    try:
        os.makedirs(notebook_dir)
    except:
        pass
    c.NotebookApp.notebook_dir = notebook_dir
