
class ErrorValidatingSchema(Exception):

    def __init__(self, errors: dict):
        self.message = "Error validating schema."
        self.errors = errors

class ErrorReadingFile(Exception):
    message = "Error reading yaml."

class ErrorCreatingContainer(Exception):
    message = "Error creating container."
