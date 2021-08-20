from model_bakery import baker

from huscy.projects.serializer import ExperimentSerializer, SessionSerializer


def test_sessions_are_serialized_in_experiment_serializer(client, experiment):
    sessions = baker.make('projects.Session', experiment=experiment, _quantity=2)

    serialized_experiment = ExperimentSerializer(experiment).data

    assert serialized_experiment['sessions'] == SessionSerializer(sessions, many=True).data
