# Code

This directory contains the scripts associated with the manuscript workflow.

- `reproduce_figures.py` regenerates Figures 5-7 from the retained source panels and aggregate questionnaire counts. Outputs are written to `code/generated/`.
- `robustness_audit.py` reruns the archived-frame brightness and blur audit. Outputs are written to `results/`.
- `auto_ring_detection.py` is an earlier automatic ring-detection implementation retained for inspection.
- `manual_three_point_circle.py` is the manual three-point circle comparison tool.
- `prediction_gui.py` is a research prototype for prediction and data validation. It is not used as ground truth or for grading, and its training archive is not included in this public package.

Install the dependencies required by the two reproducibility scripts from the repository root with `python -m pip install -r requirements.txt`.
