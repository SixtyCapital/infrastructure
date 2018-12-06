#!/bin/bash

cd /home/ubuntu/build_deploy

cd banks
git reset --hard origin/master
git pull origin master
git push --delete origin daily
git tag --delete daily
git tag -a daily -m "daily build"
git push origin daily

cd ..
cd commodity
git reset --hard origin/master
git pull origin master
git push --delete origin daily
git tag --delete daily
git tag -a daily -m "daily build"
git push origin daily

cd ..
cd conductor
git reset --hard origin/master
git pull origin master
git push --delete origin daily
git tag --delete daily
git tag -a daily -m "daily build"
git push origin daily

cd ..
cd investment
git reset --hard origin/master
git pull origin master
git push --delete origin daily
git tag --delete daily
git tag -a daily -m "daily build"
git push origin daily

cd ..
cd nursery
git reset --hard origin/master
git pull origin master
git push --delete origin daily
git tag --delete daily
git tag -a daily -m "daily build"
git push origin daily

cd ..
cd sector
git reset --hard origin/master
git pull origin master
git push --delete origin daily
git tag --delete daily
git tag -a daily -m "daily build"
git push origin daily

cd ..
cd sixty
git reset --hard origin/master
git pull origin master
git push --delete origin daily
git tag --delete daily
git tag -a daily -m "daily build"
git push origin daily

cd ..

sleep 20m
gcloud container clusters get-credentials --project=sixty-capital-test --zone=us-east4-c sixty-capital-test && kubectl config set-context $(kubectl config current-context) --namespace=airflow
kubectl delete pod -l stack=airflow
sleep 2m
kubectl set image deployments --selector=stack=airflow airflow=gcr.io/sixty-secure/conductor:daily
