import docker
from typing import Tuple
from docker.client.container import Container

_docker_client = docker.from_env()


class DockerClient:
    """Docker Client"""

    APIRUNS_DEFAULT_NETWORK = "apiruns"
    APIRUNS_LABELS = ["apiruns_containes"]

    def _create_network(self) -> None:
        """Create a deafult network if no exist."""
        try:
            _docker_client.networks.get(self.APIRUNS_DEFAULT_NETWORK)
        except docker.errors.NotFound:
            _docker_client.networks.create(self.APIRUNS_DEFAULT_NETWORK)

    def _run_container(
        self,
        image: str,
        name: str,
        environment: dict,
        ports: dict,
        detach: bool = False,
    ) -> Tuple[None, Container]:
        """Execute a docker container.

        Args:
            image (str): Image name.
            name (str): Container name
            environment (dict): Container Environments.
            ports (dict): Container Ports.
            detach (bool, optional): True if is detach. Defaults to False.

        Returns:
            Tuple[None, Container]: Container Object or None.
        """
        try:
            container = self._client.containers.run(
                image=image,
                name=name,
                detach=detach,
                network=self.APIRUNS_DEFAULT_NETWORK,
                environment=environment,
                labels=self.APIRUNS_LABELS,
                ports=ports,
            )
            return container
        except docker.errors.APIError:
            return None
