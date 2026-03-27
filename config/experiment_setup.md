# Experimental Setup

This document records the representative experimental configuration used in the manuscript-associated reproducibility package for the AI-assisted Newton's rings experiment.

## 1. Hardware and optical components

### Smartphone
- Model: Xiaomi 14
- Release year: 2023
- Manufacturer category: mid-to-high-end smartphone from a Chinese manufacturer
- Camera app: stock/original system camera app only
- Third-party camera apps: not used

### Light sources
- Main monochromatic source: standard sodium lamp commonly used in undergraduate teaching laboratories
- Extension source for mixed-colour exploration: RGB LED board
- LED type: WS2818-5050

### Optical element
- Lens type: plano-convex lens
- Nominal radius of curvature: 1.0 m

### Reading instrument for manual baseline method
- Instrument: measuring microscope
- Model: JCD3
- Manufacturer: Shanghai Optical Instrument Factory

## 2. Imaging conditions

- The smartphone was used with the stock camera app only.
- No beauty filter, enhancement filter, or third-party computational photography app was used.
- Digital zoom was avoided during image acquisition whenever possible.
- The phone was positioned above the eyepiece using a simple clamp or stable support to reduce tilt and hand motion.
- Calibration images and fringe images were recorded under comparable focal conditions.

## 3. Recommended acquisition practice

- Ensure that the ring pattern is clearly visible before capture.
- Avoid obvious motion blur.
- Avoid clipped highlights and severe underexposure.
- Keep the optical axis approximately aligned with the eyepiece axis.
- Record raw fringe images before any later processing.
- Archive calibration images separately from processed outputs.

## 4. Image-analysis main workflow

The main workflow follows the manuscript protocol and consists of:

1. image capture
2. grayscale conversion
3. contrast normalization
4. approximate center detection
5. radial intensity profiling
6. fringe minimum detection
7. boundary refinement
8. circle fitting
9. pixel-to-length calibration
10. diameter export
11. calculation of the radius of curvature from the ring-diameter relation

## 5. Reproducibility note

This setup description is intended to support reproducibility of the reported workflow. Small changes in smartphone imaging behaviour, illumination stability, focus, alignment, and calibration may affect the extracted ring diameters and the final estimated radius of curvature. Therefore, raw images, calibration records, and processing parameters should be archived together whenever possible.
