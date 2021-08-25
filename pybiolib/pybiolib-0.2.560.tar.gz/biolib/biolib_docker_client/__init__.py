import docker  # type: ignore


class BiolibDockerClient:
    docker_client = None

    @staticmethod
    def get_docker_client():
        if BiolibDockerClient.docker_client is None:
            try:
                # the final step of docker push can take a long time,
                # so set a long timeout for operations performed by the docker client
                # 15 min (900s) is the maximum supported by AWS load balancers
                BiolibDockerClient.docker_client = docker.from_env(timeout=900)
            except Exception as exception:
                raise Exception(
                    'Failed to connect to Docker, please make sure it is installed and running'
                ) from exception
        return BiolibDockerClient.docker_client

    @staticmethod
    def is_docker_running():
        try:
            BiolibDockerClient.get_docker_client()
            return True
        except Exception:  # pylint: disable=broad-except
            return False
