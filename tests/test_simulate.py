"""trano-simulate on its own: it does not import trano and simulates any Modelica package (hand-written here)."""

import ast
import math
import shutil
import subprocess
import sys
from pathlib import Path, PurePath

import pytest

from tests.fixtures.fake_omc import FakeOmc
from trano_simulate.result import SimulationErrorKind
from trano_simulate.simulate import (
    MODELICA_ENVIRONMENT,
    ModelicaEnvironment,
    ModelPackage,
    ModelSource,
    SimulationOptions,
    create_mos_file,
    mos_script,
    render_model,
    run_simulation,
)

PACKAGE = Path(__file__).parents[1] / "trano_simulate"
DECAY = """package Decay
  model building
    Real x(start=1, fixed=true);
  equation
    der(x) = -x;
  end building;
end Decay;
"""
RATES = """within;
package Rates
  constant Real decay = 1 "Rate of the decay of Plant";
end Rates;
"""
PLANT = """package Plant
  model building
    Real x(start=1, fixed=true);
  equation
    der(x) = -Rates.decay*x;
  end building;
end Plant;
"""
BROKEN = """package Broken
  model building
    Real x;
  equation
    der(x) = -undefinedThing;
  end building;
end Broken;
"""


class FakeSource:
    """A ``ModelSource`` without trano: records what the runtime asks of it."""

    name = "Decay"

    def __init__(self) -> None:
        self.calls: list[tuple[Path, PurePath]] = []

    def set_weather_path(self, project_path: Path, model_dir: PurePath) -> None:
        self.calls.append((project_path, model_dir))
        (project_path / "weather.mos").write_text("weather")

    def model(self) -> str:
        return DECAY


def test_the_package_does_not_import_trano() -> None:
    """Importing every module of the package in a fresh interpreter loads no module of trano."""
    modules = [
        ".".join(path.relative_to(PACKAGE.parent).with_suffix("").parts).removesuffix(".__init__")
        for path in PACKAGE.rglob("*.py")
    ]
    code = (
        f"import importlib, sys\nfor m in {modules!r}: importlib.import_module(m)\n"
        "print(sorted(m for m in sys.modules if m == 'trano' or m.startswith('trano.')))"
    )
    loaded = subprocess.run(  # noqa: S603 - the interpreter running the tests, on code written above
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    ).stdout.strip()
    assert loaded == "[]"


def test_no_module_of_the_package_imports_trano() -> None:
    """The same, read from the sources: also imports inside functions, which the import above does not run."""
    imports = []
    for path in PACKAGE.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            names = (
                [node.module or ""]
                if isinstance(node, ast.ImportFrom)
                else [alias.name for alias in node.names]
                if isinstance(node, ast.Import)
                else []
            )
            imports += [f"{path.name}: {name}" for name in names if name.split(".")[0] == "trano"]
    assert imports == []


def test_a_model_package_is_used_as_it_is(tmp_path: Path) -> None:
    package = ModelPackage(name="Decay", source=DECAY)

    assert render_model(package, tmp_path) == DECAY
    assert list(tmp_path.iterdir()) == []  # nothing to copy: the package is rendered already


def test_a_model_source_copies_its_files_and_renders_for_the_directory_omc_sees(tmp_path: Path) -> None:
    source = FakeSource()

    assert render_model(source, tmp_path, PurePath("/simulation")) == DECAY
    assert source.calls == [(tmp_path, PurePath("/simulation"))]
    assert (tmp_path / "weather.mos").exists()


def test_a_source_rendered_already_is_not_rendered_again(tmp_path: Path) -> None:
    source = FakeSource()

    assert render_model(source, tmp_path, text="package Given end Given;") == "package Given end Given;"
    assert source.calls == []


def test_a_fake_source_is_a_model_source() -> None:
    assert isinstance(FakeSource(), ModelSource)
    assert not isinstance(ModelPackage(name="Decay", source=DECAY), ModelSource)


def test_the_script_simulates_the_top_model_of_the_package() -> None:
    options = SimulationOptions(end_time=3600, number_of_intervals=60, variable_filter="x")

    script = mos_script("Decay", "model.mo", DECAY, options)

    assert 'loadFile("/simulation/model.mo");' in script
    assert "checkModel(Decay.building);" in script
    assert (
        "simulate(Decay.building, startTime = 0, stopTime = 3600, tolerance = 0.0001, numberOfIntervals = 60, "
        'variableFilter = "x");'
    ) in script
    assert f'loadModel(Modelica, {{"{MODELICA_ENVIRONMENT.modelica_version}"}});' in script
    assert "AixLib" not in script


def test_a_check_only_script_does_not_simulate() -> None:
    options = SimulationOptions(check_only=True)

    assert "simulate(" not in mos_script("Decay", "model.mo", DECAY, options)
    assert "getErrorString();" not in mos_script("Decay", "model.mo", DECAY, options)
    assert (
        mos_script("Decay", "model.mo", DECAY, options, report_check_errors=True).rstrip().endswith("getErrorString();")
    )


def test_aixlib_is_loaded_only_for_the_models_using_it() -> None:
    environment = ModelicaEnvironment(aixlib="9.9.9")

    script = mos_script("Zone", "model.mo", "AixLib.ThermalZones.Zone zone;", SimulationOptions(), environment)

    assert 'loadModel(AixLib, {"9.9.9", "default"});' in script


def test_the_script_reads_the_model_where_omc_sees_the_project(tmp_path: Path) -> None:
    package = ModelPackage(name="Decay", source=DECAY)

    with create_mos_file(package, SimulationOptions(), tmp_path, model_dir=tmp_path) as script_name:
        script = (tmp_path / script_name).read_text()
        [model_file] = list(tmp_path.glob("*.mo"))
        assert model_file.read_text() == DECAY
        assert f'loadFile("{tmp_path.as_posix()}/{model_file.name}");' in script
    assert list(tmp_path.glob("*.mo*")) == []  # the temporary files are removed


def rates_library(path: Path) -> Path:
    """A Modelica library stored in its folder, which the package ``PLANT`` uses without holding it."""
    library = path / "Rates"
    library.mkdir()
    (library / "package.mo").write_text(RATES)
    return library


def test_the_libraries_a_package_uses_are_loaded_before_it_where_omc_sees_them(tmp_path: Path) -> None:
    library = rates_library(tmp_path)
    package = ModelPackage(name="Plant", source=PLANT, libraries=(library,))
    project = tmp_path / "project"
    project.mkdir()

    with create_mos_file(package, SimulationOptions(), project) as script_name:  # in the container
        script = (project / script_name).read_text()
        assert script.index('loadFile("/libraries/Rates/package.mo");') < script.index('loadFile("/simulation/')
    with create_mos_file(package, SimulationOptions(), project, model_dir=project) as script_name:  # local
        assert f'loadFile("{library.resolve().as_posix()}/package.mo");' in (project / script_name).read_text()


def test_a_source_without_libraries_loads_none(tmp_path: Path) -> None:
    with create_mos_file(FakeSource(), SimulationOptions(), tmp_path) as script_name:
        assert "/libraries/" not in (tmp_path / script_name).read_text()


def test_a_package_simulates_with_the_local_runtime(tmp_path: Path, fake_omc: FakeOmc) -> None:
    result = run_simulation(tmp_path, ModelPackage(name="Decay", source=DECAY), runtime="local")

    assert result.success
    assert result.result_path == tmp_path.resolve() / "results" / "Decay.building_res.mat"
    assert "checkModel(Decay.building);" in str(fake_omc.record["script"])


def test_a_failed_local_run_of_a_package_reports_why(tmp_path: Path, fake_omc: FakeOmc) -> None:
    fake_omc.replay("translation_error.log")

    result = run_simulation(tmp_path, ModelPackage(name="Broken", source=BROKEN), runtime="local")

    assert not result.success
    assert result.error_kind is SimulationErrorKind.translation


def _final_value(result_path: Path, name: str) -> float:
    from buildingspy.io.outputfile import Reader

    _, values = Reader(str(result_path), "dymola").values(name)
    return float(values[-1])


RUNTIMES = [
    pytest.param("docker", marks=pytest.mark.simulate, id="docker"),
    pytest.param(
        "local",
        marks=[
            pytest.mark.simulation,
            pytest.mark.skipif(shutil.which("omc") is None, reason="OpenModelica's omc is not on the PATH"),
        ],
        id="local",
    ),
]


@pytest.mark.parametrize("runtime", RUNTIMES)
def test_a_package_simulates_with_openmodelica(tmp_path: Path, runtime: str) -> None:
    """x' = -x from x(0) = 1: x(1 s) = exp(-1)."""
    options = SimulationOptions(end_time=1, tolerance=1e-8, number_of_intervals=100)

    result = run_simulation(tmp_path, ModelPackage(name="Decay", source=DECAY), options=options, runtime=runtime)

    assert result.success, result.log[-3000:]
    assert result.result_path is not None
    assert _final_value(result.result_path, "x") == pytest.approx(math.exp(-1), rel=1e-5)


@pytest.mark.parametrize("runtime", RUNTIMES)
def test_a_package_simulates_with_a_library_it_uses(tmp_path: Path, runtime: str) -> None:
    """x' = -decay x, the rate from the library loaded beside the package."""
    options = SimulationOptions(end_time=1, tolerance=1e-8, number_of_intervals=100)
    package = ModelPackage(name="Plant", source=PLANT, libraries=(rates_library(tmp_path),))
    project = tmp_path / "project"
    project.mkdir()

    result = run_simulation(project, package, options=options, runtime=runtime)

    assert result.success, result.log[-3000:]
    assert result.result_path is not None
    assert _final_value(result.result_path, "x") == pytest.approx(math.exp(-1), rel=1e-5)


@pytest.mark.parametrize("runtime", RUNTIMES)
def test_a_broken_package_is_a_translation_error(tmp_path: Path, runtime: str) -> None:
    options = SimulationOptions(end_time=1)

    result = run_simulation(tmp_path, ModelPackage(name="Broken", source=BROKEN), options=options, runtime=runtime)

    assert not result.success
    assert result.error_kind is SimulationErrorKind.translation, result.log[-3000:]
    assert result.result_path is None
