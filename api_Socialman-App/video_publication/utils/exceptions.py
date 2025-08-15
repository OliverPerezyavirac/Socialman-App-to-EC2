class SocialManBaseException(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.message = message
        self.code = code

class ValidationError(SocialManBaseException):
    def __init__(self, message, code="VALIDATION_ERROR"):
        super().__init__(message, code)

class SocialMediaError(SocialManBaseException):
    def __init__(self, message, code="SOCIAL_MEDIA_ERROR"):
        super().__init__(message, code)

class AWSError(SocialManBaseException):
    def __init__(self, message, code="AWS_ERROR"):
        super().__init__(message, code)

class DatabaseError(SocialManBaseException):
    def __init__(self, message, code="DATABASE_ERROR"):
        super().__init__(message, code)

class ConfigurationError(SocialManBaseException):
    def __init__(self, message, code="CONFIGURATION_ERROR"):
        super().__init__(message, code)

class PublicationError(SocialManBaseException):
    def __init__(self, message, platform=None, code="PUBLICATION_ERROR"):
        super().__init__(message, code)
        self.platform = platform

class CredentialsError(SocialManBaseException):
    def __init__(self, message, platform=None, code="CREDENTIALS_ERROR"):
        super().__init__(message, code)
        self.platform = platform
