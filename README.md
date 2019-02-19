## Sixty Capital base repo

This repo contains our base infrastructure code

- A Dockerfile supporting an excellent python data science research & production environment. This includes python & linux libraries, a jupyter notebook config, and an airflow config for running on Kubernetes
- Scripts for creating and configuring a Google Cloud project running a Kubernetes cluster. The current scripts are designed for a cluster to run airflow, but can be easily adjusted for other requirements