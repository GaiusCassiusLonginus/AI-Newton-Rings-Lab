from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
from scipy.optimize import linear_sum_assignment


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)


def load_scaled(path, max_dim=1000):
    rgb = np.asarray(Image.open(path).convert("RGB"))
    scale = min(1.0, max_dim / max(rgb.shape[:2]))
    if scale != 1.0:
        rgb = cv2.resize(rgb, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    return rgb


def disk_geometry(gray):
    threshold = np.percentile(gray, 55)
    mask = (gray >= threshold).astype(np.uint8)
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, 8)
    candidates = [(stats[i, cv2.CC_STAT_AREA], i) for i in range(1, count)]
    _, label = max(candidates)
    x, y, w, h, _ = stats[label]
    cx, cy = centroids[label]
    radius = 0.45 * min(w, h)
    return float(cx), float(cy), float(radius), labels == label


def crosshair_center(gray, cx, cy, radius):
    yy, xx = np.indices(gray.shape)
    disk = (xx - cx) ** 2 + (yy - cy) ** 2 < (0.8 * radius) ** 2
    # The cross-hair is a persistent dark line; use trimmed mean darkness.
    col_score = np.full(gray.shape[1], np.inf)
    row_score = np.full(gray.shape[0], np.inf)
    for x in range(max(0, int(cx - 0.25 * radius)), min(gray.shape[1], int(cx + 0.25 * radius) + 1)):
        vals = gray[:, x][disk[:, x]]
        if len(vals):
            col_score[x] = np.percentile(vals, 25)
    for y in range(max(0, int(cy - 0.25 * radius)), min(gray.shape[0], int(cy + 0.25 * radius) + 1)):
        vals = gray[y, :][disk[y, :]]
        if len(vals):
            row_score[y] = np.percentile(vals, 25)
    return float(np.argmin(col_score)), float(np.argmin(row_score))


def radial_profile(gray, cx, cy, max_radius):
    yy, xx = np.indices(gray.shape)
    rr = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    bins = rr.astype(np.int32)
    valid = bins <= int(max_radius)
    sums = np.bincount(bins[valid].ravel(), weights=gray[valid].ravel())
    counts = np.bincount(bins[valid].ravel())
    profile = sums / np.maximum(counts, 1)
    return gaussian_filter1d(profile, sigma=2.0)


def ring_radii(profile, max_radius):
    lo = max(12, int(0.08 * max_radius))
    hi = min(len(profile), int(0.88 * max_radius))
    prominence = max(1.5, 0.035 * (np.percentile(profile[lo:hi], 95) - np.percentile(profile[lo:hi], 5)))
    peaks, props = find_peaks(-profile[lo:hi], distance=max(8, int(max_radius / 35)), prominence=prominence)
    radii = peaks + lo
    return radii.astype(float)


def opencv_hough(gray, expected_radii):
    if len(expected_radii) == 0:
        return np.array([])
    blurred = cv2.GaussianBlur(gray, (7, 7), 1.5)
    min_r = max(8, int(expected_radii.min() - 10))
    max_r = int(expected_radii.max() + 12)
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.0,
        minDist=6,
        param1=70,
        param2=18,
        minRadius=min_r,
        maxRadius=max_r,
    )
    if circles is None:
        return np.array([])
    return np.sort(circles[0, :, 2])


def match_radii(reference, candidates, tolerance=8):
    # Radius-only comparison: one candidate cannot count as two recovered rings.
    # Minimise differences after maximising the number of admissible pairs.
    reference = np.asarray(reference, dtype=float)
    candidates = np.asarray(candidates, dtype=float)
    if not len(reference) or not len(candidates):
        return []
    distances = np.abs(reference[:, None] - candidates[None, :])
    penalty = (min(len(reference), len(candidates)) + 1) * (tolerance + 1)
    costs = np.where(distances <= tolerance, distances, penalty)
    row_indices, column_indices = linear_sum_assignment(costs)
    return [
        (reference[i], candidates[j])
        for i, j in zip(row_indices, column_indices)
        if distances[i, j] <= tolerance
    ]


def analyse(rgb):
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    cx0, cy0, radius, _ = disk_geometry(gray)
    cx, cy = crosshair_center(gray, cx0, cy0, radius)
    profile = radial_profile(gray, cx, cy, radius)
    radii = ring_radii(profile, radius)
    hough = opencv_hough(gray, radii)
    matches = match_radii(radii, hough)
    return {
        "gray": gray,
        "center": (cx, cy),
        "radius": radius,
        "profile": profile,
        "radii": radii,
        "hough": hough,
        "matches": matches,
    }


def perturb(rgb, mode, value):
    if mode == "brightness":
        return np.clip(rgb.astype(float) * value, 0, 255).astype(np.uint8)
    if mode == "blur":
        k = int(6 * value + 1) | 1
        return cv2.GaussianBlur(rgb, (k, k), value)
    raise ValueError(mode)


rows = []
fig, axes = plt.subplots(4, 2, figsize=(9, 14))
for image_index, path in enumerate(sorted(DATA.glob("raw_frame_*.jpg"))):
    rgb = load_scaled(path)
    base = analyse(rgb)
    matches = base["matches"]
    differences = [abs(b - a) / a * 100 for a, b in matches]
    rows.append(
        {
            "image": path.name,
            "condition": "unperturbed",
            "rings": len(base["radii"]),
            "matched": len(matches),
            "median_difference_percent": np.median(differences) if differences else np.nan,
            "max_difference_percent": np.max(differences) if differences else np.nan,
        }
    )
    ax = axes[image_index, 0]
    ax.imshow(rgb)
    cx, cy = base["center"]
    ax.plot(cx, cy, "+", color="cyan", markersize=12, markeredgewidth=2)
    for radius in base["radii"]:
        ax.add_patch(plt.Circle((cx, cy), radius, fill=False, color="cyan", linewidth=0.7))
    # Use ASCII display labels so the audit image renders consistently without a CJK font.
    ax.set_title(f"raw frame {image_index + 1:02d}")
    ax.axis("off")
    axes[image_index, 1].plot(base["profile"], color="black", linewidth=1)
    axes[image_index, 1].plot(base["radii"], base["profile"][base["radii"].astype(int)], "o", ms=3)
    axes[image_index, 1].set_xlim(0, base["radius"])
    axes[image_index, 1].set_title("radial profile and selected minima")

    base_radii = base["radii"]
    for label, mode, value in [
        ("brightness 0.75", "brightness", 0.75),
        ("brightness 1.25", "brightness", 1.25),
        ("Gaussian blur sigma=1.5", "blur", 1.5),
        ("Gaussian blur sigma=3.0", "blur", 3.0),
    ]:
        test = analyse(perturb(rgb, mode, value))
        matched = match_radii(base_radii, test["radii"], tolerance=8)
        differences = [abs(b - a) / a * 100 for a, b in matched]
        rows.append(
            {
                "image": path.name,
                "condition": label,
                "rings": len(test["radii"]),
                "matched": len(matched),
                "median_difference_percent": np.median(differences) if differences else np.nan,
                "max_difference_percent": np.max(differences) if differences else np.nan,
            }
        )

fig.tight_layout()
fig.savefig(OUT / "robustness_overlay.png", dpi=200)

import csv

with open(OUT / "robustness_results.csv", "w", newline="", encoding="utf-8-sig") as handle:
    writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

for row in rows:
    print(row)



