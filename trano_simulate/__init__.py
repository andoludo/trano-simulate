"""Simulation of Modelica models with OpenModelica, and reports of their results.

A model is a ``ModelPackage`` (the name and the Modelica text of a package whose top model is ``building``), or
any ``ModelSource`` that renders one for a run, such as trano's ``Network``.
"""

from trano_simulate.exceptions import DockerClientError, DockerNotInstalledError, OpenModelicaNotFoundError
from trano_simulate.result import SimulationErrorKind, SimulationResult
from trano_simulate.simulate import (
    CONTAINER_MODEL_DIR,
    MODELICA_ENVIRONMENT,
    Model,
    ModelicaEnvironment,
    ModelPackage,
    ModelSource,
    PhaseCallback,
    SimulationOptions,
    SimulationPhase,
    SimulationRuntime,
    client,
    container,
    load_statements,
    model_directory,
    resolve_runtime,
    run_simulation,
    simulate,
)

__all__ = [
    "CONTAINER_MODEL_DIR",
    "MODELICA_ENVIRONMENT",
    "DockerClientError",
    "DockerNotInstalledError",
    "Model",
    "ModelPackage",
    "ModelSource",
    "ModelicaEnvironment",
    "OpenModelicaNotFoundError",
    "PhaseCallback",
    "SimulationErrorKind",
    "SimulationOptions",
    "SimulationPhase",
    "SimulationResult",
    "SimulationRuntime",
    "client",
    "container",
    "load_statements",
    "model_directory",
    "resolve_runtime",
    "run_simulation",
    "simulate",
]
