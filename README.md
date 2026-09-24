# AI-assisted Newton's rings laboratory

This repository is the public reproducibility package for the manuscript:

> An AI-assisted Newton's rings laboratory for undergraduates: manual-first measurement, transparent feedback and guided inquiry design

It contains the aggregate questionnaire data, archived image examples, figure source panels, processing scripts, configuration notes and representative outputs needed to inspect the workflow reported in the paper.

## Repository map

- `code/` figure-generation and robustness-audit scripts, with the source panels required by the figure script
- `config/` acquisition and processing details
- `data/` anonymised aggregate counts, archived fringe frames and provenance records
- `docs/` scope, privacy and reproducibility notes
- `results/` figures and robustness-audit output used in the manuscript

## Experimental setup

- plano-convex lens with nominal curvature radius 1.0 m
- teaching sodium lamp for the monochromatic measurements
- WS2818-5050 RGB LED board for the colour-extension activity
- Shanghai Optical Instrument Factory JCD3 measuring microscope
- stock smartphone camera application, 1x main-camera setting, fixed bench support, digital zoom and beautification disabled

Xiaomi 14 was used during testing and development. The ten-acquisition comparison reported in the manuscript used a Redmi K60 Ultra with the fixed geometry described in `config/acquisition_and_processing.md`.

## Reproduce the supplied outputs

From the repository root:

```text
python -m pip install -r requirements.txt
python code/reproduce_figures.py
python code/robustness_audit.py
```

`reproduce_figures.py` regenerates the Figure 5-7 panels from the retained source images. `robustness_audit.py` applies the brightness and Gaussian-blur perturbations described in the paper and writes a CSV and overlay image to `results/`.

The scripts are transparent audit tools, not independent ground-truth validators. The radius matching audit does not compare fitted centres or ring identities and its search range depends on the radial estimate.

## Data and privacy

`data/questionnaire_counts.csv` contains only aggregate counts for the eight questionnaire items (`n = 54`). Individual responses, class metadata, student names and electronic student laboratory reports are not included. The reports are retained by the course instructor and can only be shared in anonymised form with appropriate permission.

The complete ten-acquisition timing records, predictor training archive and full classroom application are outside this package. The manuscript identifies these limits and gives the corresponding author as the contact for additional records where sharing is permitted.

## License

Code and documentation are released under the MIT License. Image and dataset reuse should preserve the manuscript citation and the provenance information in `data/image_provenance.json`.
