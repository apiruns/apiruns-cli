import time
import httpx
from typing import Tuple, Any
from .exceptions import ErrorCreatingContainer
from rich import print
import requests

transport = httpx.HTTPTransport(uds="/var/run/docker.sock")
client = httpx.Client(transport=transport)


class DockerClient:
    """Docker Client"""

    DOCKER_HOST = "http://localhost/v1.41"
    DOCKER_HEADERS = {"Content-Type": "application/json"}
    APIRUNS_API_IMAGE = "josesalasdev/apiruns"
    APIRUNS_API_PORTS = {"8000/tcp": {}}
    APIRUNS_DEFAULT_NETWORK = {"name": "apiruns"}
    APIRUNS_DB_IMAGE = "mongo"
    APIRUNS_DB_NAME = "dbmongo"
    APIRUNS_DB_PORTS = {"27017/tcp": {}}
    APIRUNS_LABELS = {"name": "apiruns_offline"}
    DOCKER_STATE_RUNNING = "running"
    DOCKER_STATE_EXITED = "exited"
    APIRUNS_API_ENVS = [
        "PORT=8000",
        "MODULE_NAME=api.main",
        "ENGINE_DB_NAME=apiruns",
        "ENGINE_URI=mongodb://db-mongo:27017/"
    ]

    @classmethod
    def _create_network(cls) -> None:
        """Create a deafult network if no exist."""
        create = f"{cls.DOCKER_HOST}/networks/create"
        retrevier = f"{cls.DOCKER_HOST}/networks/apiruns"
        try:
            response = client.get(retrevier, headers=cls.DOCKER_HEADERS)
            if response.status_code > 299:
                client.post(create, json=cls.APIRUNS_DEFAULT_NETWORK, headers=cls.DOCKER_HEADERS)

        except httpx.RequestError as e:
            raise ErrorCreatingContainer

    @classmethod
    def _run_container(
        cls,
        image: str,
        name: str,
        environment: list,
        ports: dict,
        detach: bool = False,
    ) -> Tuple[None, dict]:
        """Execute a docker container.

        Args:
            image (str): Image name.
            name (str): Container name
            environment (list): Container Environments.
            ports (dict): Container Ports.
            detach (bool, optional): True if is detach. Defaults to False.

        Returns:
            Tuple[None, Container]: Container Object or None.
        """
        url = f"{cls.DOCKER_HOST}/containers/create?name={name}"
        data = {
            "Image": image,
            "NetworkingConfig": cls.APIRUNS_DEFAULT_NETWORK,
            "Labels": cls.APIRUNS_LABELS,
            "ExposedPorts": ports
        }
        if environment:
            data["Env"] = environment

        try:
            response = client.post(url, json=data, headers=cls.DOCKER_HEADERS)
            print(response.json())
            if response.status_code > 299:
                raise ErrorCreatingContainer
            return response.json()
        except httpx.RequestError:
            return None

    # @classmethod
    # def _wait(cls, container_name: str):
    #     while True:
    #         time.sleep(1)
    #         container = client.containers.get(container_name)
    #         if container and container.status == cls.DOCKER_STATE_RUNNING:
    #             break

    #         if not container or container.status == cls.DOCKER_STATE_EXITED:
    #             raise ErrorCreatingContainer

    @classmethod
    def compose_service(cls, name: str):
        """Build services.

        Args:
            name (str): API name.
        """
        # Create apiruns network.
        cls._create_network()
        # Create db container.
        print("Creating DB container.")
        d_container = cls._run_container(
            image=cls.APIRUNS_DB_IMAGE,
            name=cls.APIRUNS_DB_NAME,
            environment={},
            ports=cls.APIRUNS_DB_PORTS,
            detach=True
        )
        print(d_container)
        #cls._wait(d_container.name)

        # Create API container.
        print("Creating API container.")
        api_container = cls._run_container(
            image=cls.APIRUNS_API_IMAGE,
            name=name,
            environment=cls.APIRUNS_API_ENVS,
            ports=cls.APIRUNS_API_PORTS,
            detach=True
        )
        print(api_container)
        #cls._wait(api_container.name)


class APIClient:
    """API local Client"""

    HOST = "http://localhost:8000"

    @classmethod
    def _get(cls, path: str, headers: dict) -> Tuple[None, Any]:
        """Get method http.

        Args:
            path (str): Path name.
            headers (dict): Headers request.

        Returns:
            Tuple[None, Any]: Json if was success else None.
        """
        url = f"{cls.HOST}{path}"
        response = requests.get(url, headers=headers)
        if response.status_code > 299:
            return None
        return response.json()

    @classmethod
    def _post(cls, path: str, data: dict, headers: dict) -> Tuple[None, Any]:
        """Post method http.

        Args:
            path (str): Path name.
            headers (dict): Headers request.
            data (dict): Data to send.

        Returns:
            Tuple[None, Any]: Json if was success else None.
        """
        url = f"{cls.HOST}{path}"
        response = requests.post(url, json=data, headers=headers)
        if response.status_code > 299:
            return None
        return response.json()

    @classmethod
    def ping(cls) -> None:
        """Ping to health services"""
        path = "/ping"
        while True:
            response = cls._get(path, headers={})
            if response:
                break
            time.sleep(1)

    @classmethod
    def create_models(cls, model_list: list) -> None:
        """Create models in the service.

        Args:
            model_list (list): Model list.
        """
        path = "/admin/models"
        for m in model_list:
            cls._post(path, data=m, headers={})
