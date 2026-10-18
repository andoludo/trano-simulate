Outputs of OpenModelica 1.26.9 (`omc <script>.mos`) for scripts written by
`trano_simulate.simulate.create_mos_file` (then part of trano), used to test how `trano_simulate.result` classifies a run:

- `success.log`: trano's `tests/tutorials/first_model.yaml`, one day with Buildings.
- `translation_error.log`: a model referring to an undefined variable (fails to build).
- `solver_assertion.log`: a model whose assertion is violated during the simulation.
- `solver_missing_weather.log`: `first_model.yaml` with a weather resource the simulation cannot open.
