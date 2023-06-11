class APIError(Exception):
    """All custom API Exceptions"""

    pass


class ParserNotFoundError(APIError):
    """Error when a valid parser is not found."""

    code = 404
    description = "Parser not found."


class UnusualTrafficError(APIError):
    """Error when article source states "unusual traffic from your account" rather than author data."""

    code = 403
    description = "Unusual traffic error."


class S3FileNotFoundError(APIError):
    """Error when file does not exist in S3."""

    code = 404
    description = "Source file not found on S3. Nothing to parse."


class BadLandingPageError(APIError):
    code = 400
    description = "Bad landing page contents. No data available to parse."


class WrongFormatLandingPageError(APIError):

    def __init__(self, format_):
        self.format_ = format_
        self.description = f'Wrong format landing page ({self.format_} format). Unable to parse.'

    code = 400
