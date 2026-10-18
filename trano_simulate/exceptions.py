"""Errors of the simulation backends; ``trano.exceptions`` re-exports them."""


class DockerNotInstalledError(Exception): ...


class DockerClientError(Exception): ...


class OpenModelicaNotFoundError(Exception):
    """The local simulation runtime is selected but OpenModelica's ``omc`` is not on the PATH."""
