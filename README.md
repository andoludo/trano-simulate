# trano-simulate

Simulate Modelica models with [OpenModelica](https://openmodelica.org), in a Docker container of the
OpenModelica image or with the `omc` of your machine, and report their results.

It is the simulation backend of [trano](https://github.com/andoludo/trano), and does not depend on it:
a model is the name and the Modelica text of a package whose top model is `building`.

```python
from pathlib import Path

from trano_simulate import ModelPackage, SimulationOptions, run_simulation

package = ModelPackage(name="Decay", source=Path("decay.mo").read_text())
result = run_simulation(Path("run"), package, options=SimulationOptions(end_time=3600), runtime="docker")
result.success, result.result_path, result.error_kind, result.error_message
```

`runtime="docker"` needs Docker; `runtime="local"` needs OpenModelica's `omc` on the PATH, with the Modelica
libraries installed (`trano-install-libraries`).

A package that uses a Modelica library without holding it names the folder of that library: it is loaded before
the package (mounted read-only in the container with `runtime="docker"`).

```python
import fastsmoothbuildings

package = ModelPackage(name="house", source=source, libraries=(fastsmoothbuildings.LIBRARY,))
```

A `ModelSource` (trano's `Network`) may give the same folders as its attribute `libraries`.

## Reports

A report needs two files: the description of the model, which trano writes next to the model it generates
(`<name>.description.json`: its spaces, constructions and systems, and the result variables to plot), and the result
file of the simulation.

```python
from trano_simulate.reporting import ModelDocumentation, to_docx, to_html_reporting

documentation = ModelDocumentation.from_files(Path("house.description.json"), Path("run/results/house.building_res.mat"))
Path("house.html").write_text(to_html_reporting(documentation))
to_docx(documentation, Path("house.docx"))
```

## Development

```bash
uv sync
make linting
make tests      # unit tests
make simulate   # simulations in Docker
```
