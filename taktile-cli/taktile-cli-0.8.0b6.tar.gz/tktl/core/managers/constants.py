TEMPLATE_PROJECT_DIRS = [
    "src/",
    "assets/",
    "tests/",
]

TEMPLATE_PROJECT_FILES = [
    "template/src/endpoints.py",
    "template/assets/model.joblib",
    "template/assets/loans_test.pqt",
    "template/tests/test_accuracy.py",
    "template/tests/test_plausibility.py",
    "template/tests/test_schema.py",
    "template/tests/test_taktile_endpoint_tests.py",
    "template/.gitignore",
    "template/.gitattributes",
    "template/.buildfile",
    "template/.dockerignore",
    "template/README.md",
    "template/requirements.txt",
]


CONFIG_FILE_TEMPLATE = """
# See the full documentation at https://docs.taktile.com/configuring-taktile/deployment-configuration

# If this option is set only commits with a commit message starting
# with the deployment_prefix will be deployed
# deployment_prefix: "#deploy"

# If this option is set commits with a commit message starting
# with the undeployment_prefix will cause an existing Taktile
# deployment to no longer be deployed
# undeployment_prefix: "#undeploy"

service:

  # For the `instance_type` format, use the following: <instance_kind>.<instance_size>
  # and see the documentation: https://docs.taktile.com/configuring-taktile/deployment-configuration#instance-type-rest-arrow

  # Rest deployment scaling parameters
  rest:
    instance_type: gp.small
    # Maximum and minimum number of replicas to which the REST service is allowed to reach
    # by the auto-scaler
    max_replicas: 1
    # Minimum, or starting number of replicas
    replicas: 1

  # Arrow deployment scaling parameters
  arrow:
    instance_type: gp.small
    # Arrow replicas are fixed and don't autoscale
    replicas: 1

version: {version}
"""
