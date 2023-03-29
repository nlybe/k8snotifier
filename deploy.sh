#!/usr/bin/env bash
# Use this script to run locally the python app or build and run app with docker

# set the variables below
export GCP_PROJECT_ID='<GCP_PROJECT_ID>'
export PUBSUB_SUBSCRIPTION_ID='<GCP_PUBSUB_SUB>'
export PUBSUB_TIMEOUT=300
export SLACK_WEBHOOK_URL='<SLACK_WEBHOOK_URL>'
export GCP_CREDENTIALS_FILE_NAME="<PATH_TO_CREDENTIALS_FILE>"
export GCP_CREDENTIALS_FILE_PATH="$(pwd)/${GCP_CREDENTIALS_FILE_NAME}"
export GCP_CREDENTIALS_CONTAINER_PATH="/tmp/${GCP_CREDENTIALS_FILE_NAME}"
export REGISTRY_URL='<REGISTRY_URL>'


if [[ ${1} == "app" ]]; then
    ./app/main.py
else    # use param as image tag
    appname=k8snotifier
        
    echo "+ Build the docker image ${appname}:${1}" 
    docker build -t $appname:$1 .

    echo "+ Tag the docker image ${appname}:${1}" 
    docker image tag $appname:$1 $REGISTRY_URL/$appname:$1

    echo "+ Push the docker image ${appname}:${1} to registry" 
    docker push $REGISTRY_URL/$appname:$1 

    # add the " -e PUBSUB_TIMEOUT=$PUBSUB_TIMEOUT \ " if need to set the PUBSUB_TIMEOUT
    echo "+ Run the docker container ${appname}:${1}" 
    docker run  --rm --name $appname \
        -e GCP_PROJECT_ID=$GCP_PROJECT_ID \
        -e PUBSUB_SUBSCRIPTION_ID=$PUBSUB_SUBSCRIPTION_ID \
        -e SLACK_WEBHOOK_URL=$SLACK_WEBHOOK_URL \
        -v ${GCP_CREDENTIALS_FILE_PATH}:/${GCP_CREDENTIALS_CONTAINER_PATH}:ro \
        -e GOOGLE_APPLICATION_CREDENTIALS=${GCP_CREDENTIALS_CONTAINER_PATH} \
        $REGISTRY_URL/$appname:$1

fi
exit 0
