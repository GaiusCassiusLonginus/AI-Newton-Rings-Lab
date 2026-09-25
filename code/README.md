# Code

## Current manuscript audit

- `reproduce_figures.py` regenerates Figures 5-7 from the retained source panels and aggregate questionnaire counts. Outputs are written to `code/generated/`.
- `robustness_audit.py` reruns the archived-frame brightness and blur audit. Outputs are written to `results/`.
- `fig5_source_1.png` to `fig5_source_3.png` and `fig6_source_1.jpeg` to `fig6_source_4.jpeg` are the retained source panels used by the figure script.

Install the dependencies required by these two audit scripts from the repository root with `python -m pip install -r requirements.txt`.

## Historical development tools

- `auto_ring_detection.py` is an earlier automatic ring-detection implementation.
- `manual_three_point_circle.py` is an earlier manual three-point circle measurement tool.
- `prediction_gui.py` records an earlier prediction and validation interface. It depends on model modules and a training archive that are not included in this public package, so it is retained as a development artefact rather than a standalone reproducibility script.

These historical tools document the development of the workflow. They are not used to generate the figures, questionnaire results or numerical comparisons reported in the current manuscript.
