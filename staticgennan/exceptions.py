from click import ClickException


class staticgennanException(ClickException):
    """Base exceptions for all staticgennan Exceptions"""


class ConfigurationError(staticgennanException):
    """Error in configuration"""
