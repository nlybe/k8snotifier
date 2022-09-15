#!/usr/bin/python3

from concurrent.futures import TimeoutError
from traceback import print_tb
from google.cloud import pubsub_v1
from zoneinfo import ZoneInfo
from datetime import datetime, date, time, timezone
import requests, os, sys, logging, json

# get params from env
gcp_project_id = os.getenv('GCP_PROJECT_ID')
pubsub_subscription_id = os.getenv('PUBSUB_SUBSCRIPTION_ID')
pubsub_timeout = os.getenv('PUBSUB_TIMEOUT')        # Number of seconds the subscriber should listen for messages
slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
gcp_console_cluster_url = "https://console.cloud.google.com/kubernetes/clusters/details"

# initialize logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(levelname)s: %(message)s')
logging.getLogger().info('Welcome to K8s Notifier')

def is_var_set(var_name, var_value):
    if var_value is None:
        logging.getLogger().error(f'The env variable {var_name} is not set')
        sys.exit()


def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    logging.getLogger().info(f"Received {message}.")
    
    myobj = {
        "blocks": [
            { "type": "section", "text": { "type": "mrkdwn", "text": "*"+message.data.decode("utf-8")+"*" } }
        ]
    }
    fields = []

    cluster_location = None
    if 'cluster_location' in message.attributes:
        cluster_location = message.attributes["cluster_location"]        
    if 'cluster_name' in message.attributes:
        if cluster_location is not None:
            fields.append({ "type": "mrkdwn", "text": "*Cluster name*: <"+gcp_console_cluster_url+"/"+cluster_location+"/"+message.attributes["cluster_name"]+"?project="+gcp_project_id+"|"+message.attributes["cluster_name"]+">" })
            fields.append({ "type": "mrkdwn", "text": "*Cluster location*: "+ cluster_location})
        else:
            fields.append({ "type": "mrkdwn", "text": "*Cluster name*: "+message.attributes["cluster_name"] })
    if 'payload' in message.attributes:
        payload = json.loads(message.attributes["payload"])
        if 'resourceType' in payload: 
            fields.append({ "type": "mrkdwn", "text": "*Resource type*: "+payload["resourceType"] })
        if 'operationStartTime' in payload: 
            fields.append({ "type": "mrkdwn", "text": "*Start time*: "+datetime.strptime(payload["operationStartTime"].split(".")[0], "%Y-%m-%dT%H:%M:%S").astimezone(ZoneInfo('Europe/Athens')).strftime('%d/%m/%Y %H:%M:%S') })
        if 'currentVersion' in payload: 
            fields.append({ "type": "mrkdwn", "text": "*Current version*: "+payload["currentVersion"] })
        if 'targetVersion' in payload: 
            fields.append({ "type": "mrkdwn", "text": "*Target version*: "+payload["targetVersion"] })

    if len(fields) > 0:
        myobj["blocks"].append({ "type": "section", "fields": fields} )

    wh = requests.post(slack_webhook_url, json = myobj)
    logging.getLogger().info(wh.text)
    message.ack()

def main():
    subscriber = pubsub_v1.SubscriberClient()

    # The `subscription_path` method creates a fully qualified identifier in the form `projects/{project_id}/subscriptions/{subscription_id}`
    subscription_path = subscriber.subscription_path(gcp_project_id, pubsub_subscription_id)

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    logging.getLogger().info(f"Listening for messages on {subscription_path}...\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber:
        try:
            # When `pubsub_timeout` is not set, result() will block indefinitely, unless an exception is encountered first.
            timeout = None
            if (pubsub_timeout is not None):
                timeout = float(pubsub_timeout)
            streaming_pull_future.result(timeout=timeout)
        except TimeoutError:
            streaming_pull_future.cancel()  # Trigger the shutdown.
            streaming_pull_future.result()  # Block until the shutdown is complete.


# Check if basic var have been set
is_var_set("GCP_PROJECT_ID", gcp_project_id)
is_var_set("PUBSUB_SUBSCRIPTION_ID", pubsub_subscription_id)
is_var_set("SLACK_WEBHOOK_URL", slack_webhook_url)

main()
