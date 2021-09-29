class APIError(Exception):
    """All custom API Exceptions"""

    pass


class ParserNotFoundError(APIError):
    """Error when file does not exist in S3."""

    code = 404
    description = "Parser not found."


class AuthorNotFoundError(APIError):
    """Error when author is not found within a valid document."""

    code = 404
    description = "Authors not found."


class S3FileNotFoundError(APIError):
    """Error when file does not exist in S3."""

    code = 404
    description = "Source file not found on S3. Nothing to parse."
