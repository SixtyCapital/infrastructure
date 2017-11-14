from airflow.models import Connection
from airflow.settings import Session
import os
import requests
import json

project_id = os.getenv('GOOGLE_CLOUD_PROJECT')

if not project_id:
    # use project id from instance metadata
    project_id = requests.get(
        'http://metadata.google.internal'
        '/computeMetadata/v1//project/project-id',
        headers={'Metadata-Flavor': 'Google'}).content
conn_extras = json.dumps({
    'extra__google_cloud_platform__project': project_id
})
session = Session()
gcp_conn = Connection(
    conn_id='sixty_gcp',
    conn_type='google_cloud_platform',
    extra=conn_extras)
if not session.query(Connection).filter(
        Connection.conn_id == gcp_conn.conn_id).first():
    session.add(gcp_conn)
    session.commit()
