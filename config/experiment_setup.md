# Experimental setup

This document records the equipment roles in the manuscript-associated reproducibility package.

## Reported ten-acquisition comparison

- smartphone: Redmi K60 Ultra, stock camera application, 1x main camera
- support: rigid fixed bench geometry
- monochromatic source: teaching sodium lamp, treated operationally as the sodium D doublet near 589.0 and 589.6 nm
- optical element: plano-convex lens with nominal curvature radius 1.0 m
- manual instrument: Shanghai Optical Instrument Factory JCD3 measuring microscope
- calibration reticle: 0.1 mm spacing, recorded at the same focal height as the air film

Digital zoom and beautification filters were disabled. The source, lens-plate contact state and camera position were held fixed during the reported repeated acquisitions.

## Additional testing and development

Xiaomi 14 was also used during testing and development. Results from that device are not represented as the ten-acquisition benchmark reported in the manuscript.

The RGB extension activity used a WS2818-5050 LED board. The retained Figure 5 and Figure 6 source panels are documented separately in `data/image_provenance.json`.

## Reproducibility scope

Changes in smartphone processing, focus, alignment, illumination and calibration can affect extracted ring diameters. Raw frames, calibration records and processing settings should therefore be retained together. The supplied audit checks the stability of extracted radii under stated perturbations; it does not provide independent centre or ring-identity ground truth.
