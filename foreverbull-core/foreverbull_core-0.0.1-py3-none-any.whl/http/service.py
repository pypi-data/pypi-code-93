import requests
from .exceptions import RequestError


class Service:
    def __init__(self, host, session=None):
        self.host = host
        if session is None:
            session = requests.Session()
        self.session = session

    def list_services(self):
        rsp = self.session.get(f"http://{self.host}/services")
        if not rsp.ok:
            raise RequestError(f"get call /services gave bad return code: {rsp.status_code}")
        return rsp.json()

    def create_service(self, service):
        rsp = self.session.post(f"http://{self.host}/services", json=service)
        if not rsp.ok:
            raise RequestError(f"post call /services gave bad return code: {rsp.status_code}")
        return rsp.json()

    def get_service(self, service_id):
        rsp = self.session.get(f"http://{self.host}/services/{service_id}")
        if not rsp.ok:
            raise RequestError(f"get call /services/{service_id} gave bad return code: {rsp.status_code}")
        return rsp.json()

    def update_service():
        pass

    def delete_service(self, service_id):
        rsp = self.session.delete(f"http://{self.host}/services/{service_id}")
        if not rsp.ok:
            raise RequestError(f"delete call /services/{service_id} gave bad return code: {rsp.status_code}")
        return True

    def list_instances(self, service_id):
        rsp = self.session.get(f"http://{self.host}/services/{service_id}/instances")
        if not rsp.ok:
            raise RequestError(f"get call /services/{service_id}/instances gave bad return code: {rsp.status_code}")
        return rsp.json()

    def create_instance(self, service_id, instance):
        rsp = self.session.post(f"http://{self.host}/services/{service_id}/instances", json=instance)
        if not rsp.ok:
            raise RequestError(f"post call /services/{service_id}/instances gave bad return code: {rsp.status_code}")
        return rsp.json()

    def get_instance(self, service_id, instance_id):
        rsp = self.session.get(f"http://{self.host}/services/{service_id}/instances/{instance_id}")
        if not rsp.ok:
            raise RequestError(f"get call /services/{service_id}/instances/1 gave bad return code: {rsp.status_code}")
        return rsp.json()

    def update_instance(self, service_id, instance_id, host, port, online):
        rsp = self.session.patch(
            f"http://{self.host}/services/{service_id}/instances/{instance_id}",
            params={"host": host, "port": port, "online": online, "listen": online},
        )
        if not rsp.ok:
            raise RequestError(
                f"get call /services/{service_id}/instances/{instance_id} gave bad return code: {rsp.status_code}"
            )
        return True

    def delete_instance(self, service_id, instance_id):
        rsp = self.session.delete(f"http://{self.host}/services/{service_id}/instances/{instance_id}")
        if not rsp.ok:
            raise RequestError(
                f"delete call /services/{service_id}/instances/{instance_id} gave bad return code: {rsp.status_code}"
            )
        return True

    def list_containers(self):
        rsp = self.session.get(f"http://{self.host}/services/containers")
        if not rsp.ok:
            raise RequestError(f"get call /services/containers gave bad return code: {rsp.status_code}")
        return rsp.json()

    def create_container(self, container):
        rsp = self.session.post(f"http://{self.host}/services/containers", json=container)
        if not rsp.ok:
            raise RequestError(f"post call /services/containers gave bad return code: {rsp.status_code}")
        return rsp.json()

    def get_container(self, container_id):
        rsp = self.session.get(f"http://{self.host}/services/containers/{container_id}")
        if not rsp.ok:
            raise RequestError(f"get call /services/containers/{container_id} gave bad return code: {rsp.status_code}")
        return rsp.json()

    def update_container():
        pass

    def delete_container(self, container_id):
        rsp = self.session.delete(f"http://{self.host}/services/containers/{container_id}")
        if not rsp.ok:
            raise RequestError(
                f"delete call /services/containers/{container_id} gave bad return code: {rsp.status_code}"
            )
        return True
