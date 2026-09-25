# Acquisition and processing

The reported bench comparison used a plano-convex lens with nominal curvature radius 1.0 m, a teaching sodium lamp, a Shanghai Optical Instrument Factory JCD3 measuring microscope and a Redmi K60 Ultra smartphone. The phone used the stock camera application, the 1x main camera, fixed bench geometry and a rigid support. Digital zoom and beautification filters were disabled. A calibration reticle with 0.1 mm spacing was recorded at the same focal height as the fringe image.

Xiaomi 14 was also used during testing and development. It is documented here for completeness; the ten repeated acquisitions and the reported error comparison use the Redmi K60 Ultra arrangement.

The robustness audit scales each image to a maximum dimension of 1000 pixels. The radial routine estimates a centre from the dark cross-hair, smooths the radial intensity profile with a Gaussian filter and identifies candidate minima. OpenCV Hough-circle detection provides a comparison radius set. Radius matches use an 8-pixel tolerance. Perturbations multiply brightness by 0.75 or 1.25, or apply Gaussian blur with sigma 1.5 or 3.0 pixels.

These settings define the supplied audit. They do not constitute an independent accuracy standard or a complete uncertainty budget.
