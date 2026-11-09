# Reproducibility notes

The package supports three checks made in the manuscript:

1. Figure 5 and Figure 6 can be regenerated from the retained source panels with square crops and equal horizontal and vertical pixel scales.
2. Figure 7 can be regenerated from the aggregate questionnaire counts without exposing individual responses.
3. The archived-frame audit can be rerun under the stated brightness and blur perturbations.

The reported ten-acquisition error summary is a study-level result; the complete acquisition log is not included in this public package. The predictor training archive and full classroom application are also outside scope. These limitations are stated in the manuscript.

## Reproduction check on 9 November 2026

The two documented scripts were run in a local copy of the v2.0.0 code and inputs (commit `ee9548321d09a9590c008fbc84f0c55fcb8d8a94`) on Windows. Both completed successfully.

| Component | Observed runtime version |
| --- | --- |
| Python | 3.12.5 (conda-forge) |
| NumPy | 2.2.0 |
| SciPy | 1.13.1 |
| OpenCV (`cv2`) | 4.13.0 |
| Matplotlib | 3.10.3 |
| Pillow | 12.3.0 |

These are the versions used for this later check, not a record of the original study environment. They describe an existing environment, not a tested clean-install lockfile. In particular, its `opencv-python` distribution metadata reported `4.12.0.88` while the imported `cv2` reported `4.13.0`; the runtime version above records the module actually used. The unpinned `requirements.txt` remains the general dependency list.

Verification results:

- Generated Figure 5, Figure 6 and Figure 7 PNGs had identical dimensions and RGBA pixel arrays to `results/figure5_equal_scale.png`, `results/figure6_equal_scale.png` and `results/figure7_questionnaire.png`, respectively.
- All 20 rows of the regenerated `robustness_results.csv` matched the archived CSV. Text fields were compared exactly, numeric fields with relative and absolute tolerances of `1e-10`, and missing numeric values were matched as NaN.
- These checks cover the supplied figure and robustness scripts. They do not independently validate the unpublished acquisition records, predictor training archive or full classroom application.

Run the scripts in a working copy: `robustness_audit.py` overwrites the CSV and overlay under `results/`. Preserve a separate copy of the release outputs if comparing a new run with the archive.
