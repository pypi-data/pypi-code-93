from kubernetes.client import V1ObjectMeta, V1ServiceSpec, V1ServicePort
from k8kat.auth.kube_broker import broker


def create(**subs):
  default_labels = dict(app=subs['name'])
  labels = {**subs.get('labels', {}), **default_labels}
  def_match_labels = {**labels, **subs.get('selector', {})}
  force_match_labels = subs.get('force_selector', None)
  coerce_sel = force_match_labels is not None
  match_labels = force_match_labels if coerce_sel else def_match_labels

  svc = broker.client.V1Service(
    api_version='v1',
    metadata=V1ObjectMeta(
      name=subs.get('name'),
      labels=labels
    ),
    spec=V1ServiceSpec(
      type=subs.get('type', 'ClusterIP'),
      selector=match_labels,
      ports=[
        V1ServicePort(
          port=subs.get('from_port', 80),
          target_port=subs.get('to_port', 80)
        )
      ]
    )
  )

  return broker.coreV1.create_namespaced_service(
    body=svc,
    namespace=subs['ns']
  )
