
# Validations
class ErrorValidatingSchema(Exception):
    """Error validating schema."""

    def __init__(self, errors: dict = {}):
        self.message = "Error validating schema."
        self.errors = errors

class ErrorReadingFile(Exception):
    """Error reading configuration file."""

    def __init__(self, errors: dict = {}):
        self.message = "Error reading configuration file."
        self.errors = errors


# Docker Client

class ErrorDockerEngineAPI(Exception):
    """Error with request to Docker Engine API."""
    def __init__(self, errors: str = None):
        self.message = "Error with request to Docker Engine API."
        self.errors = errors

class ErrorCreatingNetwork(Exception):
    """Error creating network."""
    def __init__(self, errors: str = None):
        self.message = "Error creating network."
        self.errors = errors

class ErrorPingDocker(Exception):
    """Docker API not responding."""
    def __init__(self, errors: str = None):
        self.message = "Docker API not is responding."
        self.errors = errors

class ErrorGettingContainerStatus(Exception):
    """Error getting container status."""
    def __init__(self, errors: str = None):
        self.message = "Error getting container status."
        self.errors = errors

class ErrorCreatingContainer(Exception):
    """Error creating container."""
    def __init__(self, errors: str = None):
        self.message = "Error creating container."
        self.errors = errors

class ErrorStartingAContainer(Exception):
    """Error starting a container."""
    def __init__(self, errors: str = None):
        self.message = "Error starting a container."
        self.errors = errors

class ErrorContainerExited(Exception):
    """There is a container exited."""
    def __init__(self, errors: str = None):
        self.message = "There is a container exited."
        self.errors = errors

class ErrorListingContainers(Exception):
    """Error listing containers."""
    def __init__(self, errors: str = None):
        self.message = "Error listing containers."
        self.errors = errors

class ErrorDeletingContainers(Exception):
    """Error deleting containers."""
    def __init__(self, errors: str = None):
        self.message = "Error deleting containers."
        self.errors = errors

class ErrorPullingImage(Exception):
    """Error pulling image."""
    def __init__(self, errors: str = None):
        self.message = "Error pulling image."
        self.errors = errors

# Apiruns client

class ErrorAPIClient(Exception):
    """Error with request to API rest local."""
    def __init__(self, errors: str = None):
        self.message = "Error with request to API rest local."
        self.errors = errors
