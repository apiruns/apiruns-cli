import time
import httpx
from typing import Tuple, Any
from .exceptions import ErrorDockerEngineAPI
from .exceptions import ErrorCreatingNetwork
from .exceptions import ErrorPingDocker
from .exceptions import ErrorGettingContainerStatus
from .exceptions import ErrorCreatingContainer
from .exceptions import ErrorStartingAContainer
from .exceptions import ErrorContainerExited
from .exceptions import ErrorAPIClient
from .exceptions import ErrorPullingImage
from .exceptions import ErrorListingContainers
from .exceptions import ErrorDeletingContainers
from rich import print
import requests
from dataclasses import dataclass
from dataclasses import field


transport = httpx.HTTPTransport(uds="/var/run/docker.sock")
client = httpx.Client(transport=transport)


@dataclass
class ContainerConfig:
    """Container configuration."""
    image: str
    port: str
    network_id: str
    labels: list
    environment: list = field(default_factory=dict)

    def _build_ports(self) -> dict:
        """Build ports.

        Returns:
            example:
                {'8000/tcp': {}}
        """
        return {f"{self.port}/tcp": {}}

    def _build_port_bind(self) -> dict:
        """Build json port bind.

        Returns:
            example:
                {'8000/tcp': [{'HostIp': '', 'HostPort': '8000'}]}
        """
        return {
            f"{self.port}/tcp": [
                {"HostIp": "", "HostPort": self.port}
            ]
        }

    def to_json(self) -> dict:
        """ContainerConfig to json object.

        Returns:
            dict: Json for create a container.
            example:
                {
                    'Image': 'josesalasdev/apiruns',
                    'NetworkingConfig': {
                        'EndpointsConfig': {'apiruns': {'NetworkID': '4cb8b69e'}}
                    },
                    'Labels': {'name': 'apiruns_offline'},
                    'ExposedPorts': {'8000/tcp': {}},
                    'PortBindings': {'8000/tcp': [
                        {'HostIp': '', 'HostPort': '8000'}
                    ]},
                    'Env': ['ENGINE_URI=mongodb://dbmongo:27017/']
                }
        """
        data = {
            "Image": self.image,
            "NetworkingConfig": {
                "EndpointsConfig": {"apiruns": {"NetworkID": self.network_id}}
            },
            "Labels": self.labels,
            "ExposedPorts": self._build_ports(),
            "PortBindings": self._build_port_bind()
        }
        if self.environment:
            data["Env"] = self.environment
        return data


class DockerClient:
    """Docker Client"""

    DOCKER_HOST = "http://localhost/v1.41"
    DOCKER_HEADERS = {"Content-Type": "application/json"}
    APIRUNS_API_IMAGE = "josesalasdev/apiruns"
    APIRUNS_API_PORTS = "8000"
    APIRUNS_DEFAULT_NETWORK = {"name": "apiruns"}
    APIRUNS_DB_IMAGE = "mongo"
    APIRUNS_DB_NAME = "dbmongo"
    APIRUNS_DB_PORTS = "27017"
    APIRUNS_LABEL = "apiruns_offline"
    DOCKER_STATE_RUNNING = "running"
    DOCKER_STATE_EXITED = "exited"
    APIRUNS_API_ENVS = [
        "PORT=8000",
        "MODULE_NAME=api.main",
        "ENGINE_DB_NAME=apiruns",
        "ENGINE_URI=mongodb://dbmongo:27017/"
    ]

    @classmethod
    def _create_network(cls) -> str:
        """Create default newtwork.

        Raises:
            ErrorCreatingNetwork: Error of creation.
            ErrorDockerEngineAPI: Error of Docker API.

        Returns:
            str: Returns network ID.
        """
        create = f"{cls.DOCKER_HOST}/networks/create"
        retrieve = f"{cls.DOCKER_HOST}/networks/apiruns"
        try:
            response = client.get(retrieve, headers=cls.DOCKER_HEADERS)
            if response.status_code != 200:
                response = client.post(
                    create,
                    json=cls.APIRUNS_DEFAULT_NETWORK,
                    headers=cls.DOCKER_HEADERS
                )
                if response.status_code != 201:
                    raise ErrorCreatingNetwork
                return response.json().get("Id")
            return response.json().get("Id")

        except httpx.RequestError as e:
            raise ErrorDockerEngineAPI(errors=e)

    @classmethod
    def _pull_image(cls, image: str) -> None:
        """Pull Image from docker hub.

        Args:
            image (str): Image name.

        Raises:
            ErrorPullingImage: Image not found.
            ErrorPingDocker: Error of Docker API.
        """
        if not cls._get_image(image):
            print(f"Pulling `{image}` image.")
            url = f"{cls.DOCKER_HOST}/images/create?fromImage={image}&tag=latest"
            try:
                response = client.post(url, json={}, headers=cls.DOCKER_HEADERS)
                if response.status_code != 200:
                    raise ErrorPullingImage(errors=response.text)
            except httpx.RequestError as e:
                raise ErrorPingDocker(errors=e)

    @classmethod
    def _get_image(cls, image: str) -> Any:
        """Get image info.

        Args:
            image (str): Image name.

        Returns:
            Any: Json if was success else None.
        """
        url = f"{cls.DOCKER_HOST}/images/{image}:latest/json"
        try:
            response = client.get(url, headers=cls.DOCKER_HEADERS)
            if response.status_code != 200:
                return None
            return response.json()
        except httpx.RequestError:
            return None

    @classmethod
    def _ping(cls) -> None:
        """Ping to DockerEngineAPI.

        Raises:
            ErrorPingDocker: Docker API not is responding.
        """
        url = f"{cls.DOCKER_HOST}/_ping"
        try:
            response = client.get(url, headers=cls.DOCKER_HEADERS)
            if response.status_code != 200:
                raise ErrorPingDocker(errors=response.text)
        except httpx.RequestError as e:
            raise ErrorPingDocker(errors=e)

    @classmethod
    def _get_container_status(cls, _id) -> str:
        """Get container status.

        Raises:
            ErrorGettingContainerStatus: Error getting status.
            ErrorDockerEngineAPI: Docker API not is responding.

        Returns:
            str: Returns container status.
        """
        url = f"{cls.DOCKER_HOST}/containers/{_id}/json"
        try:
            response = client.get(url, headers=cls.DOCKER_HEADERS)
            if response.status_code != 200:
                raise ErrorGettingContainerStatus
            return response.json()["State"].get("Status")
        except httpx.RequestError as e:
            raise ErrorDockerEngineAPI(errors=e)

    @classmethod
    def _list_containers_by_name(cls, name: str) -> list:
        """List containers by service name.

        Args:
            name (str): API name.

        Raises:
            ErrorListingContainers: Error listing containers.
            ErrorDockerEngineAPI: Docker API not is responding.

        Returns:
            list: Container list.
        """
        label = f"{cls.APIRUNS_LABEL}-{name}"
        url = f"{cls.DOCKER_HOST}/containers/json?label={label}"
        try:
            response = client.get(url, headers=cls.DOCKER_HEADERS)
            if response.status_code != 200:
                raise ErrorListingContainers
            return response.json()
        except httpx.RequestError as e:
            raise ErrorDockerEngineAPI(errors=e)

    @classmethod
    def _delete_container(cls, _id: str):
        url = f"{cls.DOCKER_HOST}/containers/{_id}?force=true"
        try:
            response = client.delete(url, headers=cls.DOCKER_HEADERS)
            if response.status_code != 204:
                raise ErrorDeletingContainers
        except httpx.RequestError as e:
            raise ErrorDockerEngineAPI(errors=e)

    @classmethod
    def _run_container(
        cls,
        image: str,
        name: str,
        environment: list,
        port: str,
        network_id: str,
        labels: list
    ) -> str:
        """Run a container.

        Args:
            image (str): docker image.
            name (str): container name.
            environment (list): list of environment.
            port (str): port to expose.
            network_id (str): Network ID.
            labels (list): List of labels.

        Raises:
            ErrorCreatingContainer: Error creating container.
            ErrorDockerEngineAPI: Docker API not is responding.

        Returns:
            str: Container ID.
        """
        cls._pull_image(image)
        url = f"{cls.DOCKER_HOST}/containers/create?name={name}"
        obj = ContainerConfig(
            image=image,
            port=port,
            network_id=network_id,
            labels=labels,
            environment=environment,
        )
        try:
            response = client.post(url, json=obj.to_json(), headers=cls.DOCKER_HEADERS)
            if response.status_code > 299:
                raise ErrorCreatingContainer
            _id = response.json().get("Id")
            return _id
        except httpx.RequestError as e:
            raise ErrorDockerEngineAPI(errors=e)

    @classmethod
    def _start_container(cls, _id: str):
        """Start a container.

        Args:
            _id (str): Container ID.

        Raises:
            ErrorStartingAContainer: Error starting container.
            ErrorDockerEngineAPI: Docker API not is responding.
        """
        url = f"{cls.DOCKER_HOST}/containers/{_id}/start"
        try:
            response = client.post(url, json={}, headers=cls.DOCKER_HEADERS)
            if response.status_code != 204:
                raise ErrorStartingAContainer
        except httpx.RequestError as e:
            raise ErrorDockerEngineAPI(errors=e)

    @classmethod
    def _wait(cls, container_id: str):
        """Wait by container.

        Args:
            container_id (str): Container ID.

        Raises:
            ErrorContainerExited: Container was exited.
        """
        while True:
            time.sleep(1)
            status = cls._get_container_status(container_id)
            if status == cls.DOCKER_STATE_RUNNING:
                break

            if status == cls.DOCKER_STATE_EXITED:
                raise ErrorContainerExited

    @classmethod
    def _build_labels(cls, name: str) -> dict:
        """Build docker labels.

        Args:
            name (str): API name.

        Returns:
            dict: Labels.
        """
        lable = f"{cls.APIRUNS_LABEL}-{name}"
        return {"name": lable}

    @classmethod
    def compose_service(cls, name: str, start: bool):
        """Compose services.

        Args:
            name (str): Service main name.
            start (bool): Start services.
        """
        # Ping to docker.
        cls._ping()
        # Create apiruns network.
        network = cls._create_network()
        # Create labels
        labels = cls._build_labels(name)
        # Create db container.
        print("Creating DB container.")
        container_id = cls._run_container(
            image=cls.APIRUNS_DB_IMAGE,
            name=cls.APIRUNS_DB_NAME,
            environment={},
            port=cls.APIRUNS_DB_PORTS,
            network_id=network,
            labels=labels,
        )
        if start:
            cls._start_container(container_id)
            cls._wait(container_id)

        # Create API container.
        print("Creating API container.")
        container_id = cls._run_container(
            image=cls.APIRUNS_API_IMAGE,
            name=name,
            environment=cls.APIRUNS_API_ENVS,
            port=cls.APIRUNS_API_PORTS,
            network_id=network,
            labels=labels,
        )
        if start:
            cls._start_container(container_id)
            cls._wait(container_id)

    @classmethod
    def service_down(cls, name: str):
        """Service down.

        Args:
            name (str): Service name.
        """
        containers = cls._list_containers_by_name(name)
        for c in containers:
            print(f"Removing {c['Names']}")
            cls._delete_container(c["Id"])


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
        try:
            response = requests.get(url, headers=headers)
            if response.status_code > 299:
                return None
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ErrorAPIClient(errors=e)

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
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code > 299:
                return None
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ErrorAPIClient(errors=e)

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
