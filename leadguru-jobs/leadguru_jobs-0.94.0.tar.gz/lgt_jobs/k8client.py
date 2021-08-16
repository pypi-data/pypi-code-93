import time
import yaml

from kubernetes import client, config
from kubernetes.client import AppsV1Api,  CoreV1Api, ApiException, V1Deployment
from typing import Dict, List

from lgt_data.model import BaseBotModel, DedicatedBotModel

from lgt_jobs.env import k8config, environment

print(f"KUBE_CONFIG_LOCATION: {k8config}")
config.load_kube_config(k8config)

class KubernetesAppsClient:
    def __init__(self, client: AppsV1Api):
        self.__client = client

    def remove_deployments(self, namespace: str, labels: Dict[str, str]):
        deployments_list = self.__client.list_namespaced_deployment(namespace=f'{namespace}')

        for dep in deployments_list.items:
            for label_name in labels:
                if dep.metadata.labels and dep.metadata.labels.get(label_name, "") == labels[label_name]:
                    self.__client.delete_namespaced_deployment(dep.metadata.name, dep.metadata.namespace)

        time.sleep(15)

    def create_namespaced_deployment(self, namespace: str, name: str, template: dict) -> V1Deployment:
        exists = True
        try:
            self.__client.read_namespaced_deployment(name, namespace)
        except ApiException as e:
            if e.status == 404:
                exists = False

        if exists:
            print(f'{name} deleting the old deployment')
            self.__client.delete_namespaced_deployment(name, namespace=f'{namespace}')
            time.sleep(20)

        print(f'{name} creating new deployment')
        return self.__client.create_namespaced_deployment(namespace=f'{namespace}', body=template)


    def create_slack_bots_deployment(self, namespace: str,
                                     name: str,
                                     backend_uri: str,
                                     aggregator_topic: str,
                                     project_id: str,
                                     google_app_credentials: str,
                                     bots: List[BaseBotModel],
                                     labels: Dict[str, str]) -> V1Deployment:

        bot_tag = "prod" if environment == "prod" else "latest"
        with open("lgt_jobs/templates/bots_service_template.yaml") as f:
            template = yaml.safe_load(f)
            containers = list()

            for bot in bots:
                if not bot.token or bot.invalid_creds:
                    continue

                container = {
                    'name': bot.name,
                    'image': f'gcr.io/lead-tool-generator/lgt-slack-aggregator:{bot_tag}',
                    'volumeMounts': [{
                        'name': 'google-cloud-key',
                        'mountPath': '/var/secrets/google'
                    }],
                    'imagePullPolicy': 'Always',
                    'resources': {
                        'requests': {
                            'memory': '32Mi',
                            'cpu': '10m'
                        },
                        'limits': {
                            'memory': '72Mi',
                            'cpu': '10m'
                        }
                    },
                    'env': [
                        {'name': 'PUBSUB_PROJECT_ID', 'value': project_id},
                        {'name': 'PUBSUB_TOPIC_OUT', 'value': aggregator_topic},
                        {'name': 'SLACKBOT_TOKEN', 'value': bot.token},
                        {'name': 'SLACKBOT_NAME', 'value': bot.name},
                        {'name': 'COUNTRY', 'value': bot.country},
                        {'name': 'REGISTRATION_LINK', 'value': bot.registration_link},
                        {'name': 'GOOGLE_APPLICATION_CREDENTIALS', 'value': google_app_credentials},
                        {'name': 'BACKEND_URI', 'value': backend_uri}
                    ]
                }

                if bot.is_dedicated():
                    container["env"].append({"name": "DEDICATED_BOT_ID", "value": f"{bot.id}"})

                containers.append(container)

            template['spec']['template']['spec']['containers'] = containers
            template['metadata']['name'] = name
            template['spec']['selector']['matchLabels']['app'] = name
            template['spec']['template']['metadata']['labels']['app'] = name

            for label_name in labels:
                template["metadata"]["labels"][label_name] = labels[label_name]

            return self.create_namespaced_deployment(namespace, name, template)



class KubernetesClientFactory:
    @staticmethod
    def create_core() -> CoreV1Api:
        kubernetes_client = client.CoreV1Api()
        kubernetes_client.api_client.configuration.verify_ssl = False
        kubernetes_client.api_client.configuration.ssl_ca_cert = None
        return kubernetes_client

    @staticmethod
    def create() -> KubernetesAppsClient:
        kubernetes_client = client.AppsV1Api()
        kubernetes_client.api_client.configuration.verify_ssl = False
        kubernetes_client.api_client.configuration.ssl_ca_cert = None
        return KubernetesAppsClient(kubernetes_client)
