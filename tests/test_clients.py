import httpx
import pytest
from unittest.mock import patch, call
from apiruns.exceptions import ErrorDockerEngineAPI
from apiruns.exceptions import ErrorCreatingNetwork
from apiruns.exceptions import ErrorPullingImage
from apiruns.exceptions import ErrorGettingContainerStatus
from apiruns.exceptions import ErrorListingContainers
from apiruns.exceptions import ErrorDeletingContainers
from apiruns.exceptions import ErrorCreatingContainer
from apiruns.exceptions import ErrorStartingAContainer
from apiruns.exceptions import ErrorContainerExited
from apiruns.clients import ContainerConfig
from apiruns.clients import DockerClient
from dataclasses import dataclass
from dataclasses import field


@dataclass
class MockResponse:
    status_code: int = 200
    data: dict = field(default_factory=dict)
    text: str = ""

    def json(self) -> dict:
        return self.data


class TestContainerConfig:
    def init(self) -> ContainerConfig:
        return ContainerConfig(
            image="mongo",
            port="27017",
            network_id="N123",
            labels={"service": "apiruns"},
            environment=["PORT=27017"],
        )

    def test_build_ports(self):
        obj = self.init()
        expec = obj._build_ports()
        assert expec == {"27017/tcp": {}}

    def test_build_port_bind(self):
        obj = self.init()
        expec = obj._build_port_bind()
        assert expec == {"27017/tcp": [{"HostIp": "", "HostPort": "27017"}]}

    def test_to_json(self):
        obj = self.init()
        resp = obj.to_json()
        expec = {
            "Env": ["PORT=27017"],
            "ExposedPorts": {"27017/tcp": {}},
            "Image": "mongo",
            "Labels": {"service": "apiruns"},
            "NetworkingConfig": {"EndpointsConfig": {"apiruns": {"NetworkID": "N123"}}},
            "PortBindings": {"27017/tcp": [{"HostIp": "", "HostPort": "27017"}]},
        }
        assert resp == expec


class TestDockerClient:

    headers = {"Content-Type": "application/json"}

    @patch("apiruns.clients.client.get")
    def test_create_network_error_with_docker(self, mock_client):
        # Mocks
        mock_client.side_effect = httpx.RequestError("error")
        # Asserts
        with pytest.raises(ErrorDockerEngineAPI):
            DockerClient._create_network()

    @patch("apiruns.clients.client.get")
    def test_create_network_exists(self, mock_client):
        mock_client.return_value = MockResponse(data={"Id": "123"})
        resp = DockerClient._create_network()

        # Asserts
        assert resp == "123"
        mock_client.assert_called_once_with(
            "http://localhost/networks/apiruns", headers=self.headers
        )

    @patch("apiruns.clients.client")
    def test_create_network_new(self, mock_client):
        mock_client.get.return_value = MockResponse(status_code=404)
        mock_client.post.return_value = MockResponse(
            status_code=201, data={"Id": "1234"}
        )
        resp = DockerClient._create_network()

        # Asserts
        assert resp == "1234"
        mock_client.get.assert_called_once_with(
            "http://localhost/networks/apiruns", headers=self.headers
        )
        mock_client.post.assert_called_once_with(
            "http://localhost/networks/create",
            headers=self.headers,
            json={"name": "apiruns"},
        )

    @patch("apiruns.clients.client")
    def test_create_network_error_with_post_request(self, mock_client):
        mock_client.get.return_value = MockResponse(status_code=404)
        mock_client.post.return_value = MockResponse(
            status_code=500,
        )
        with pytest.raises(ErrorCreatingNetwork):
            DockerClient._create_network()

    @patch("apiruns.clients.client.get")
    def test_pull_image_error(self, mock_client):
        # Mocks
        mock_client.side_effect = httpx.RequestError("error")
        # Asserts
        with pytest.raises(ErrorDockerEngineAPI):
            DockerClient._create_network()

    @patch("apiruns.clients.client.get")
    def test_pull_image_with_image_exists(self, mock_client):
        mock_client.return_value = MockResponse(status_code=200)
        resp = DockerClient._pull_image("mongo")

        # Asserts
        assert resp == None
        mock_client.assert_called_once_with(
            "http://localhost/images/mongo:latest/json", headers=self.headers
        )

    @patch("apiruns.clients.client")
    def test_pull_image_with_image_not_found_and_error_docker(self, mock_client):
        mock_client.get.return_value = MockResponse(status_code=404)
        mock_client.post.side_effect = httpx.RequestError("error")
        with pytest.raises(ErrorDockerEngineAPI):
            DockerClient._pull_image("mongo")

    @patch("apiruns.clients.client")
    def test_pull_image_with_image_not_found_and_bad_request(self, mock_client):
        mock_client.get.return_value = MockResponse(status_code=404)
        mock_client.post.return_value = MockResponse(status_code=400)
        with pytest.raises(ErrorPullingImage):
            DockerClient._pull_image("mongo")

    @patch("apiruns.clients.typer.echo")
    @patch("apiruns.clients.client")
    def test_pull_image_with_image_not_found_and_bad_request(
        self, mock_client, mock_echo
    ):
        mock_client.get.return_value = MockResponse(status_code=404)
        mock_client.post.return_value = MockResponse(status_code=200)
        DockerClient._pull_image("mongo")

        # Assserts
        mock_echo.assert_called_once_with("Pulling `mongo` image.")
        mock_client.get.assert_called_once_with(
            "http://localhost/images/mongo:latest/json", headers=self.headers
        )
        mock_client.post.assert_called_once_with(
            "http://localhost/images/create?fromImage=mongo&tag=latest",
            headers=self.headers,
            json={},
        )

    @patch("apiruns.clients.client.get")
    def test_ping_with_docker_error(self, mock_client):
        # Mocks
        mock_client.side_effect = httpx.RequestError("error")
        # Asserts
        with pytest.raises(ErrorDockerEngineAPI):
            DockerClient._ping()

    @patch("apiruns.clients.client.get")
    def test_ping_with_unsuccesful_request(self, mock_client):
        # Mocks
        mock_client.return_value = MockResponse(status_code=500)
        # Asserts
        with pytest.raises(ErrorDockerEngineAPI):
            DockerClient._ping()
        mock_client.assert_called_once_with(
            "http://localhost/_ping", headers=self.headers
        )

    @patch("apiruns.clients.client.get")
    def test_ping_with_success(self, mock_client):
        # Mocks
        mock_client.return_value = MockResponse(status_code=200)
        DockerClient._ping()
        # Asserts
        mock_client.assert_called_once_with(
            "http://localhost/_ping", headers=self.headers
        )

    @patch("apiruns.clients.client.get")
    def test_container_status_with_docker_error(self, mock_client):
        # Mocks
        mock_client.side_effect = httpx.RequestError("error")
        # Asserts
        with pytest.raises(ErrorDockerEngineAPI):
            DockerClient._get_container_status("ID123")

    @patch("apiruns.clients.client.get")
    def test_container_status_with_unsuccesful_request(self, mock_client):
        # Mocks
        mock_client.return_value = MockResponse(status_code=500)
        # Asserts
        with pytest.raises(ErrorGettingContainerStatus):
            DockerClient._get_container_status("ID123")
        mock_client.assert_called_once_with(
            "http://localhost/containers/ID123/json", headers=self.headers
        )

    @patch("apiruns.clients.client.get")
    def test_container_status_with_success(self, mock_client):
        # Mocks
        mock_client.return_value = MockResponse(
            status_code=200, data={"State": {"Status": "exited"}}
        )
        DockerClient._get_container_status("ID123")
        # Asserts
        mock_client.assert_called_once_with(
            "http://localhost/containers/ID123/json", headers=self.headers
        )

    @patch("apiruns.clients.client.get")
    def test_list_containers_by_name_with_docker_error(self, mock_client):
        # Mocks
        mock_client.side_effect = httpx.RequestError("error")
        # Asserts
        with pytest.raises(ErrorDockerEngineAPI):
            DockerClient._list_containers_by_name("MyAPI")

    @patch("apiruns.clients.client.get")
    def test_list_containers_by_name_with_unsuccesful_request(self, mock_client):
        # Mocks
        mock_client.return_value = MockResponse(status_code=500)
        # Asserts
        with pytest.raises(ErrorListingContainers):
            DockerClient._list_containers_by_name("MyAPI")

        filters = DockerClient._build_labels_filters("MyAPI")
        url = f"http://localhost/containers/json?filters={filters}"
        mock_client.assert_called_once_with(url, headers=self.headers)

    @patch("apiruns.clients.client.get")
    def test_list_containers_by_name_with_success(self, mock_client):
        # Mocks
        mock_client.return_value = MockResponse(status_code=200, data=[])
        response = DockerClient._list_containers_by_name("MyAPI")
        # Asserts
        filters = DockerClient._build_labels_filters("MyAPI")
        url = f"http://localhost/containers/json?filters={filters}"
        mock_client.assert_called_once_with(url, headers=self.headers)
        assert response == []

    @patch("apiruns.clients.client.delete")
    def test_delete_container_with_docker_error(self, mock_client):
        # Mocks
        mock_client.side_effect = httpx.RequestError("error")
        # Asserts
        with pytest.raises(ErrorDockerEngineAPI):
            DockerClient._delete_container("ID123")

    @patch("apiruns.clients.client.delete")
    def test_delete_container_with_unsuccesful_request(self, mock_client):
        # Mocks
        mock_client.return_value = MockResponse(status_code=500)
        # Asserts
        with pytest.raises(ErrorDeletingContainers):
            DockerClient._delete_container("ID123")
        mock_client.assert_called_once_with(
            "http://localhost/containers/ID123?force=true", headers=self.headers
        )

    @patch("apiruns.clients.client.delete")
    def test_delete_container_with_success(self, mock_client):
        # Mocks
        mock_client.return_value = MockResponse(
            status_code=204,
        )
        DockerClient._delete_container("ID123")
        # Asserts

        mock_client.assert_called_once_with(
            "http://localhost/containers/ID123?force=true", headers=self.headers
        )

    @patch("apiruns.clients.client.post")
    def test_run_container_with_docker_error(self, mock_client):
        # Mocks
        mock_client.side_effect = httpx.RequestError("error")
        # Asserts
        with pytest.raises(ErrorDockerEngineAPI):
            DockerClient._run_container(
                image="mongo",
                name="mongodb",
                environment=["PORT=27017"],
                port="27017",
                network_id="n123",
                labels={"service": "apiruns"},
            )

    @patch("apiruns.clients.client.post")
    def test_run_container_with_unsuccesful_request(self, mock_client):
        # Mocks
        mock_client.return_value = MockResponse(status_code=500)
        # Asserts
        with pytest.raises(ErrorCreatingContainer):
            DockerClient._run_container(
                image="mongo",
                name="mongodb",
                environment=["PORT=27017"],
                port="27017",
                network_id="n123",
                labels={"service": "apiruns"},
            )
        response = ContainerConfig(
            image="mongo",
            port="27017",
            network_id="n123",
            labels={"service": "apiruns"},
            environment=["PORT=27017"],
        )
        mock_client.assert_called_once_with(
            "http://localhost/containers/create?name=mongodb",
            headers=self.headers,
            json=response.to_json(),
        )

    @patch("apiruns.clients.client.post")
    def test_run_container_with_success(self, mock_client):
        # Mocks
        mock_client.return_value = MockResponse(status_code=201, data={"Id": "C123"})
        _id = DockerClient._run_container(
            image="mongo",
            name="mongodb",
            environment=["PORT=27017"],
            port="27017",
            network_id="n123",
            labels={"service": "apiruns"},
        )
        # Asserts
        response = ContainerConfig(
            image="mongo",
            port="27017",
            network_id="n123",
            labels={"service": "apiruns"},
            environment=["PORT=27017"],
        )
        mock_client.assert_called_once_with(
            "http://localhost/containers/create?name=mongodb",
            headers=self.headers,
            json=response.to_json(),
        )
        assert _id == "C123"

    @patch("apiruns.clients.client.post")
    def test_start_container_with_docker_error(self, mock_client):
        # Mocks
        mock_client.side_effect = httpx.RequestError("error")
        # Asserts
        with pytest.raises(ErrorDockerEngineAPI):
            DockerClient._start_container("C123")
        mock_client.assert_called_once_with(
            "http://localhost/containers/C123/start", headers=self.headers, json={}
        )

    @patch("apiruns.clients.client.post")
    def test_start_container_with_unsuccesful_request(self, mock_client):
        # Mocks
        mock_client.return_value = MockResponse(status_code=500)
        # Asserts
        with pytest.raises(ErrorStartingAContainer):
            DockerClient._start_container("C123")

        mock_client.assert_called_once_with(
            "http://localhost/containers/C123/start", headers=self.headers, json={}
        )

    @patch("apiruns.clients.client.post")
    def test_start_container_with_success(self, mock_client):
        # Mocks
        mock_client.return_value = MockResponse(
            status_code=204,
        )
        DockerClient._start_container("C123")
        # Asserts
        mock_client.assert_called_once_with(
            "http://localhost/containers/C123/start", headers=self.headers, json={}
        )

    @patch("apiruns.clients.DockerClient._get_container_status")
    @patch("apiruns.clients.time.sleep")
    def test_wait_container_with_exited_status(self, mock_sleep, mock_container):
        # Mocks
        mock_sleep.return_value = None
        mock_container.return_value = "exited"
        # Asserts
        with pytest.raises(ErrorContainerExited):
            DockerClient._wait("C123")

        mock_sleep.assert_called_once_with(1)
        mock_container.assert_called_once_with("C123")

    @patch("apiruns.clients.DockerClient._get_container_status")
    @patch("apiruns.clients.time.sleep")
    def test_wait_container_with_exited_status(self, mock_sleep, mock_container):
        # Mocks
        mock_sleep.return_value = None
        mock_container.return_value = "running"
        DockerClient._wait("C123")
        # Asserts
        mock_sleep.assert_called_once_with(1)
        mock_container.assert_called_once_with("C123")

    def test_build_labels(self):
        # Asserts
        resp = DockerClient._build_labels("apiruns")

        assert resp == {"service": "apiruns_offline-apiruns"}

    @patch("apiruns.clients.DockerClient._ping")
    @patch("apiruns.clients.DockerClient._create_network")
    @patch("apiruns.clients.DockerClient._start_container")
    @patch("apiruns.clients.DockerClient._wait")
    @patch("apiruns.clients.DockerClient._run_container")
    @patch("apiruns.clients.typer.echo")
    def test_compose_service_success(
        self,
        mock_echo,
        mock_run_container,
        mock_wait,
        mock_start_container,
        mock_create_network,
        mock_ping,
    ):
        # Mocks
        mock_create_network.return_value = "N123"
        mock_run_container.side_effect = ["C123", "C1234"]

        # Proccess
        DockerClient.compose_service("MyAPI", start=True)
        # Asserts
        mock_ping.assert_called_once_with()
        mock_create_network.assert_called_once_with()
        calls_echo = [call("Creating DB container."), call("Creating API container.")]
        mock_echo.assert_has_calls(calls_echo, any_order=False)
        calls_containers = [
            call(
                environment=[],
                image="mongo",
                labels={"service": "apiruns_offline-MyAPI"},
                name="dbmongo",
                network_id="N123",
                port="27017",
            ),
            call(
                environment=[
                    "PORT=8000",
                    "MODULE_NAME=api.main",
                    "ENGINE_DB_NAME=apiruns",
                    "ENGINE_URI=mongodb://dbmongo:27017/",
                ],
                image="josesalasdev/apiruns",
                labels={"service": "apiruns_offline-MyAPI"},
                name="MyAPI",
                network_id="N123",
                port="8000",
            ),
        ]
        mock_run_container.assert_has_calls(calls_containers, any_order=False)
