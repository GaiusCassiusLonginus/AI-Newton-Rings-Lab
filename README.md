# AI-Newton-Rings-Lab

This repository provides the reproducibility package for our manuscript on an AI-assisted Newton's rings undergraduate optics experiment. It is intended to support peer review, post-publication verification, and classroom reuse.

## Repository purpose

This repository is not only a software project. It is a paper-associated reproducibility package that contains the materials needed to understand, inspect, and reproduce the experimental workflow reported in the manuscript.

## Planned contents

- `data/`  
  Raw fringe images, calibration images, and sample datasets used for analysis and demonstration.

- `code/`  
  Image-processing and analysis scripts for extracting ring diameters and estimating the radius of curvature.

- `config/`  
  Experimental setup description, hardware information, acquisition conditions, and processing parameters.

- `docs/`  
  Supporting documents for uncertainty analysis, AI-vs-manual comparison, teaching implementation, and assessment design.

- `results/`  
  Example outputs, intermediate figures, processed tables, and reproducibility demonstrations.

## Experimental setup summary

The reproducibility package corresponds to the manuscript version using the following representative setup:

- Smartphone: Xiaomi 14 (2023 release), stock camera app only
- Main monochromatic source: standard sodium lamp used in undergraduate teaching laboratories
- RGB extension source: WS2818-5050 LED board
- Lens: plano-convex lens, nominal radius of curvature 1.0 m
- Measuring microscope: Shanghai Optical Instrument Factory JCD3 measuring microscope

## Reproducibility principles

To support reproducibility, this repository is being organized around the following principles:

1. Raw data are preserved whenever possible.
2. Calibration information is stored separately from processed results.
3. Image-processing steps are documented and auditable.
4. Manual and AI-assisted measurement routes can be compared.
5. Uncertainty sources are explicitly described rather than hidden.

## Intended use

This repository is intended for:

- journal reviewers and readers
- instructors who want to adapt the experiment
- students learning experimental optics and uncertainty analysis
- researchers interested in AI-assisted laboratory instruction

## Citation

Citation information will be added after the archival release is deposited in Zenodo and a DOI is assigned.

## License

This repository is released under the MIT License unless otherwise specified for individual files or datasets.
