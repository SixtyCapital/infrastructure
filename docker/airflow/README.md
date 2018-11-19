## Airflow Infrastructure Setup

```sh
gcloud container clusters get-credentials airflow

kubectl config set-context $(kubectl config current-context) --namespace airflow

kubectl create secret generic airflow-dev \
  --namespace airflow \
  --from-literal=postgres-ip=[IP] \
  --from-literal=postgres-user=[USER] \
  --from-literal=postgres-password=[PASSWORD]

# create cluster
kubectl create -f airflow.yaml

# update cluster
kubectl apply -f airflow.yaml

# helpful to have as a bash script locally
function get-pod {
  kubectl get pod -o=name | grep $1 | awk -F/ '{print $2}' | head -1
}

# to access the kubernetes web ui
kubectl port-forward svc/airflow-web 8080

gcloud container node-pools create airflow-worker \
  --num-nodes=2 --scopes=https://www.googleapis.com/auth/bigquery,https://www.googleapis.com/auth/compute,https://www.googleapis.com/auth/devstorage.read_write,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring \
  --disk-size=300 --machine-type=n1-standard-8 --image-type=CONTAINER_VM \
  --preemptible
```
