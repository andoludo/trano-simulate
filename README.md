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

## Development

```bash
uv sync
make linting
make tests      # unit tests
make simulate   # simulations in Docker
```
