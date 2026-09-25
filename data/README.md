# Data files

- `questionnaire_counts.csv`: aggregate A-E counts for the eight anonymous questionnaire items; no individual response is included.
- `measurement_summary.csv`: the summary values reported in the manuscript for the ten-acquisition bench comparison and the representative timing and uncertainty comparisons.
- `raw_frame_01.jpg` to `raw_frame_04.jpg`: archived fringe frames used in the robustness audit.
- `image_provenance.json`: source-panel hashes, dimensions and crop operations for Figures 5 and 6.

The generated radius-matching table is stored as `results/robustness_results.csv`.

The questionnaire counts use a denominator of 54 complete responses for every item. Individual responses, class metadata and student laboratory reports are not part of this public package.

## Historical development material

- `sample_images/` contains image examples retained from the initial development package. They are not additional independent acquisitions for the current robustness audit.
- `sample_tables/sample_measurements.csv` is a small demonstration table retained from the initial repository release. It is not part of the ten-acquisition comparison and is not a source for numerical claims in the current manuscript.
