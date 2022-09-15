# K8s Notifier

A Python-based application for listening to a pubsub subscription for GKE cluster messages and sending notifications to slack.

GKE offers the option to send to a PubSub topic the following notification types:

- Version upgrade available (UpgradeAvailableEvent)
- Version upgrade started (UpgradeEvent)
- Security bulletin issued (SecurityBulletinEvent)

The aim of this tool is to provide a gke-notification-handler, which listen to a pubsub subscription and send notifications to a slack channel.

Read more details on [GCP documentation](https://cloud.google.com/kubernetes-engine/docs/tutorials/cluster-notifications-slack).


## Prerequisites

This is the list of prerequisites required:

On GCP this is the list of prerequisites required for an existing GCP project:

- a PubSub topic and subscription
- a GKE cluster with **Notifications** feature enabled and declaring the **Topic ID**
- a Service Account with **roles/pubsub.subscriber** role to the subscription

You'll need also a Slack application with an incoming Webhook URL for the channel you'd like to receive these notifications. You can get more information at [https://api.slack.com/messaging/webhooks](https://api.slack.com/messaging/webhooks).

## How to use

### Environment Variables

You will have to set the env variables below

| Variable                       | Description                                                 |
| ------------------------------ | ----------------------------------------------------------- |
| GCP_PROJECT_ID                 | The project ID on GCP                                       |
| PUBSUB_SUBSCRIPTION_ID         | The PubSub Subscription ID                                  |
| SLACK_WEBHOOK_URL              | The Webhook URL of the slack channel                        |
| GOOGLE_APPLICATION_CREDENTIALS | A credentials file path for the json key of Service Account |
| PUBSUB_TIMEOUT                 | Optionally set a timeout on subscription listening (in sec) |


### Try locally

For run - test locally set the vars in **run_locally.sh** and run the following:

```bash
# run directly the python script by using the "app" as param
./run_locally.sh app

# run locally as docker container by using an IMAGE_TAG value as param (this will build the image first)
run_locally.sh IMAGE_TAG
```


### Deploy on Kubernetes cluster

Use the following in order to deploy the application to a Kubernetes cluster:

```bash
# create a secret for the Service Account json key
kubectl create secret generic gcp-pubsub-sa-key --from-file=PATH_TO_GCP_PUBSUB_SA_KEY_FILE

# then update the environment variables and the image on deployment.yaml file and run the command:
kubectl apply -f deployment.yaml
```


## Sample message from GKE
```bash
{
   data: 'Master is upgrading to version 1.23.8-gke.1900.'
   ordering_key: ''
   attributes: {
     "cluster_location": "us-east1",
     "cluster_name": "CLUSTER_NAME",
     "payload": "{\"resourceType\":\"MASTER\", \"operation\":\"operation-1662536672793-9f8f675f\", \"operationStartTime\":\"2022-09-07T07:44:32.793341429Z\", \"currentVersion\":\"1.23.7-gke.1400\", \"targetVersion\":\"1.23.8-gke.1900\"}",
     "project_id": "PROJECT_ID",
     "type_url": "type.googleapis.com/google.container.v1beta1.UpgradeEvent"
   }
}

```