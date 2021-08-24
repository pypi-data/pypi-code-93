# Copyright (c) Qotto, 2021

"""
Kafka admin client
"""

from typing import Dict

from confluent_kafka.admin import AdminClient, ClusterMetadata, TopicMetadata, NewTopic

from .kafka_errors import KafkaTopicCreationError, KafkaTopicDeletionError, KafkaError

__all__ = [
    'KafkaAdmin',
]


class KafkaAdmin:
    """
    Wrapper around a Confluent Kafka AdminClient
    """

    def __init__(
        self,
        admin_config: Dict[str, str],
    ) -> None:
        self._kafka_admin = AdminClient(admin_config)

    def create_topic(self, topic: str, partitions: int = 1, replications: int = 1) -> None:
        """
        Create a topic

        :param topic: topic name to create
        :param partitions: number of partitions, default 1
        :param replications: number of replicas, default 1

        :raise KafkaTopicCreationError: Could not create the topic (e.g. because it already exists)
        """
        try:
            future_topics = self._kafka_admin.create_topics([NewTopic(topic, partitions, replications)])
            for future_topic in future_topics.values():
                future_topic.result()
        except Exception as e:
            raise KafkaTopicCreationError(f"Could not create topic {topic}") from e

    def delete_topic(self, topic: str) -> None:
        """
        Delete a topic

        :param topic: topic name to delete

        :raise KafkaTopicDeletionError: Could not delete the topic (e.g. because it does not exist)
        """
        try:
            future_topics = self._kafka_admin.delete_topics([topic])
            for future_topic in future_topics.values():
                future_topic.result()
        except Exception as e:
            raise KafkaTopicDeletionError(f"Could not delete topic {topic}") from e

    def list_topic(self) -> list[str]:
        """
        List all topics in the broker

        :return: The list of all topic names

        :raise KafkaError: The broker did not answer
        """
        try:
            cluster_meta: ClusterMetadata = self._kafka_admin.list_topics()
            topic_meta: TopicMetadata
            return sorted(cluster_meta.topics.keys())
        except Exception as e:
            raise KafkaError from e
