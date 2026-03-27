# Uncertainty Analysis

This document provides a structured description of the uncertainty sources associated with both the manual measurement method and the AI-assisted image-based method in the Newton's rings experiment.

## 1. Comparison: Manual method vs AI-assisted method

### Manual method

Main uncertainty sources:

- Visual judgement of ring boundaries
- Identification of the central fringe
- Parallax and reading error in the measuring microscope
- Mechanical backlash during stage movement
- Repeated measurement variability
- Ring miscounting or incorrect indexing

Characteristics:

- Strong dependence on operator experience
- Higher random uncertainty due to repeated manual readings
- Good transparency (students directly observe the measurement process)

---

### AI-assisted method

Main uncertainty sources:

- Image quality (blur, noise, compression)
- Center detection accuracy
- Thresholding and fringe extraction parameters
- Circle fitting residuals
- Pixel-to-length calibration
- Incorrect ring order assignment

Characteristics:

- Reduced reading noise compared to manual methods
- Improved repeatability under fixed parameters
- Additional model- and calibration-related uncertainties
- Requires validation against manual baseline

---

## 2. Qualitative comparison

| Aspect | Manual method | AI-assisted method |
|------|-------------|------------------|
| Ring edge determination | subjective | algorithm-dependent |
| Center determination | difficult | improved but model-dependent |
| Reading error | high | low |
| Calibration dependence | low | high |
| Repeatability | limited | improved |
| Transparency | high | moderate |

Key observation:

The AI-assisted method does not eliminate uncertainty.  
It redistributes uncertainty from human reading to calibration and model assumptions.

---

## 3. Uncertainty sources in the AI image measurement chain

### 3.1 Image acquisition

- Smartphone tilt relative to optical axis  
  → causes geometric distortion

- Motion blur or focus instability  
  → broadens intensity minima

- Automatic exposure / HDR / compression  
  → alters fringe contrast and position

---

### 3.2 Calibration

- Calibration target not at the same focal plane  
  → systematic scale error

- Limited calibration resolution  
  → pixel-to-length conversion uncertainty

---

### 3.3 Image processing

- Contrast normalization choices  
- Noise filtering parameters  
- Fringe detection threshold  

→ all may shift detected ring positions slightly

---

### 3.4 Geometric fitting

- Center estimation error  
- Circle fitting residuals  

→ errors increase for outer rings

---

### 3.5 Physical modelling

- Incorrect ring order assignment  
- Incorrect wavelength assumption  

→ leads to systematic error in radius estimation

---

## 4. Educational implication

From a teaching perspective:

- The manual method exposes students to observational uncertainty.
- The AI-assisted method exposes students to model and calibration uncertainty.
- Comparing both methods helps students understand that:
  
  > uncertainty is not removed by technology; it is transformed.

Students are therefore required to:

- obtain at least one manual baseline result
- compare it with the AI-assisted result
- identify dominant uncertainty sources
- explain discrepancies

---

## 5. Practical recommendation

For classroom implementation:

- Always retain raw images
- Keep calibration data separate
- Use fixed processing parameters within a dataset
- Report fitting residuals when possible
- Avoid selecting only “good-looking” results without justification

---

## 6. Reproducibility note

Uncertainty evaluation in this repository is qualitative and instructional in nature.  
Quantitative uncertainty propagation may be developed in future work depending on the experimental design and available calibration precision.
