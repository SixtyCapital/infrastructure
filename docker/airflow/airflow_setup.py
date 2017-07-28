from airflow.models import Connection
from airflow.settings import Session

session = Session()
gcp_conn = Connection(
    conn_id='sixty_gcp',
    conn_type='google_cloud_platform',
    extra='{"extra__google_cloud_platform__project":"sixty-capital"}')
if not session.query(Connection).filter(
        Connection.conn_id == gcp_conn.conn_id).first():
    session.add(gcp_conn)
    session.commit()
