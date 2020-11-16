class UnstableAPIError(RuntimeError):
    """Indicates a failed assumption about an unstable API.

    This whole project is built off of undocumented APIs.
    If raised, this exception indicates that something about the API has changed,
    and the source code should be modified accordingly.
    """
