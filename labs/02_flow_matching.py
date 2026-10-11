#!/usr/bin/env python3
"""CPU-only conditional flow matching on one-dimensional Gaussian data.

Uses only the Python standard library. The fitted field is affine in x at each
time knot; least squares learns it from independently sampled endpoint pairs.
The analytic field is a reference, never used to fit the learned field.
"""

import argparse
import bisect
import csv
import json
import math
from pathlib import Path
import random
import statistics
import sys


TARGET_MEAN = 2.0
TARGET_STD = 0.5


def analytic_coefficients(t):
    variance = (1.0 - t) ** 2 + (t * TARGET_STD) ** 2
    a = (t * TARGET_STD**2 - (1.0 - t)) / variance
    return a, TARGET_MEAN - a * t * TARGET_MEAN


def fit_field(seed, knots, train_per_knot):
    rng = random.Random(seed)
    model = []
    for index in range(knots):
        t = index / (knots - 1)
        sum_x = sum_u = sum_xx = sum_xu = sum_uu = 0.0
        for _ in range(train_per_knot):
            x0 = rng.gauss(0.0, 1.0)
            x1 = rng.gauss(TARGET_MEAN, TARGET_STD)
            x = (1.0 - t) * x0 + t * x1
            u = x1 - x0
            sum_x += x
            sum_u += u
            sum_xx += x * x
            sum_xu += x * u
            sum_uu += u * u
        mean_x = sum_x / train_per_knot
        mean_u = sum_u / train_per_knot
        var_x = sum_xx / train_per_knot - mean_x**2
        cov_xu = sum_xu / train_per_knot - mean_x * mean_u
        if var_x <= 1e-12:
            raise ValueError("Degenerate training variance; increase sample count.")
        a = cov_xu / var_x
        b = mean_u - a * mean_x
        # Residual MSE includes irreducible conditional variance.
        mse = max(0.0, sum_uu / train_per_knot - mean_u**2 - a * cov_xu)
        model.append({"t": t, "a": a, "b": b, "training_mse": mse})
    return model


def learned_coefficients(model, t):
    times = [row["t"] for row in model]
    index = min(max(bisect.bisect_right(times, t) - 1, 0), len(model) - 2)
    left, right = model[index], model[index + 1]
    weight = (t - left["t"]) / (right["t"] - left["t"])
    return tuple(left[key] + weight * (right[key] - left[key]) for key in ("a", "b"))


def integrate(initial, steps, coefficients):
    values = list(initial)
    trajectories = [[value] for value in initial[:8]]
    dt = 1.0 / steps
    for index in range(steps):
        a, b = coefficients(index * dt)
        values = [x + dt * (a * x + b) for x in values]
        for trace, x in zip(trajectories, values):
            trace.append(x)
    return values, trajectories


def moments(values):
    return statistics.mean(values), statistics.pstdev(values)


def metrics(values):
    mean, std = moments(values)
    # This is W2 between moment-matched Gaussians, not empirical distribution W2.
    gaussian_w2 = math.hypot(mean - TARGET_MEAN, std - TARGET_STD)
    return {
        "mean": mean,
        "std": std,
        "mean_abs_error": abs(mean - TARGET_MEAN),
        "std_abs_error": abs(std - TARGET_STD),
        "moment_matched_gaussian_w2": gaussian_w2,
    }


def normal_pdf(x, mean, std):
    return math.exp(-0.5 * ((x - mean) / std) ** 2) / (std * math.sqrt(2.0 * math.pi))


def write_svg(path, initial, generated, trajectories):
    width, height = 1000, 600
    x_min, x_max = -4.0, 5.0
    bins = 54
    bin_width = (x_max - x_min) / bins

    def histogram(values):
        counts = [0] * bins
        for value in values:
            index = int((value - x_min) / bin_width)
            if 0 <= index < bins:
                counts[index] += 1
        return [count / (len(values) * bin_width) for count in counts]

    histograms = [(histogram(initial), "#64748b", "source samples"),
                  (histogram(generated), "#2563eb", "learned samples")]
    y_max = max(1.0, max(max(hist) for hist, _, _ in histograms) * 1.1)
    elements = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
                '<rect width="100%" height="100%" fill="#f8fafc"/>',
                '<g font-family="sans-serif" fill="#0f172a">',
                '<text x="48" y="32" font-size="21">Flow matching: N(0,1) to N(2,0.5^2)</text>',
                '<text x="48" y="56" font-size="13">Toy affine field learned from pairs; not image or video generation.</text>']
    chart_x, chart_y, chart_w, chart_h = 60, 88, 875, 255

    def point(x, y):
        return chart_x + (x - x_min) / (x_max - x_min) * chart_w, chart_y + chart_h - y / y_max * chart_h

    for hist, color, _ in histograms:
        for index, density in enumerate(hist):
            x, y = point(x_min + index * bin_width, density)
            elements.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{chart_w / bins:.2f}" height="{chart_y + chart_h - y:.2f}" fill="{color}" opacity="0.40"/>')
    curve = [point(x_min + (x_max - x_min) * index / 250,
                   normal_pdf(x_min + (x_max - x_min) * index / 250, TARGET_MEAN, TARGET_STD))
             for index in range(251)]
    curve_points = " ".join(f"{x:.2f},{y:.2f}" for x, y in curve)
    elements.append(f'<polyline points="{curve_points}" fill="none" stroke="#dc2626" stroke-width="2.5"/>')
    elements.append(f'<line x1="{chart_x}" y1="{chart_y + chart_h}" x2="{chart_x + chart_w}" y2="{chart_y + chart_h}" stroke="#0f172a"/>')
    for value in range(-4, 6):
        x, _ = point(value, 0.0)
        elements.append(f'<text x="{x:.2f}" y="365" font-size="12">{value}</text>')
    elements.extend(['<text x="60" y="387" font-size="13" fill="#64748b">gray: initial samples</text>',
                     '<text x="270" y="387" font-size="13" fill="#2563eb">blue: learned final samples</text>',
                     '<text x="535" y="387" font-size="13" fill="#dc2626">red: target analytic density</text>',
                     '<text x="60" y="414" font-size="15">Eight sample trajectories (time: 0 to 1)</text>'])
    trace_min = min(min(trace) for trace in trajectories) - 0.25
    trace_max = max(max(trace) for trace in trajectories) + 0.25
    for trace in trajectories:
        points = " ".join(f"{60 + index / (len(trace)-1) * 875:.2f},{555 - (value - trace_min) / (trace_max - trace_min) * 115:.2f}" for index, value in enumerate(trace))
        elements.append(f'<polyline points="{points}" fill="none" stroke="#2563eb" stroke-width="1.5" opacity="0.65"/>')
    elements.extend(['<text x="60" y="579" font-size="12">t = 0</text>',
                     '<text x="900" y="579" font-size="12">t = 1</text>', '</g></svg>'])
    path.write_text("\n".join(elements), encoding="utf-8")


def run(args):
    model = fit_field(args.seed, args.knots, args.train_per_knot)
    eval_rng = random.Random(args.seed + 1)
    initial = [eval_rng.gauss(0.0, 1.0) for _ in range(args.samples)]
    summary = {
        "experiment": "one_dimensional_gaussian_conditional_flow_matching",
        "seed": args.seed,
        "target": {"mean": TARGET_MEAN, "std": TARGET_STD},
        "config": {"knots": args.knots, "train_per_knot": args.train_per_knot,
                   "samples": args.samples, "steps": args.steps},
        "baseline_identity": metrics(initial),
        "training_mse_mean": statistics.mean(row["training_mse"] for row in model),
        "runs": [],
        "limitations": ["Affine Gaussian toy model; no neural network or video.",
                        "Training loss contains conditional variance and need not approach zero.",
                        "W2 shown here is for moment-matched Gaussians, not empirical distributions.",
                        "Only numerical transport properties are checked; no physical causality claim."],
    }
    final_samples = final_trajectories = None
    for steps in args.steps:
        learned, traces = integrate(initial, steps, lambda t: learned_coefficients(model, t))
        oracle, _ = integrate(initial, steps, analytic_coefficients)
        # For these Gaussian marginals the exact ODE endpoint is mu + sigma*x0.
        exact = [TARGET_MEAN + TARGET_STD * value for value in initial]
        summary["runs"].append({
            "steps": steps,
            "learned": metrics(learned),
            "oracle_euler": metrics(oracle),
            "oracle_rmse_to_exact_endpoint": math.sqrt(statistics.mean((a - b) ** 2 for a, b in zip(oracle, exact))),
            "learned_rmse_to_oracle_euler": math.sqrt(statistics.mean((a - b) ** 2 for a, b in zip(learned, oracle))),
        })
        final_samples, final_trajectories = learned, traces
    validation_rng = random.Random(args.seed + 2)
    errors = []
    for _ in range(args.samples):
        t = validation_rng.random()
        std = math.sqrt((1.0 - t) ** 2 + (t * TARGET_STD) ** 2)
        x = validation_rng.gauss(t * TARGET_MEAN, std)
        a, b = learned_coefficients(model, t)
        oracle_a, oracle_b = analytic_coefficients(t)
        errors.append((a * x + b - (oracle_a * x + oracle_b)) ** 2)
    summary["held_out_velocity_rmse_to_analytic"] = math.sqrt(statistics.mean(errors))
    largest = summary["runs"][-1]
    checks = {
        "all_numbers_finite": all(math.isfinite(value) for row in model for value in row.values()) and all(math.isfinite(x) for x in final_samples),
        "learned_improves_over_identity": largest["learned"]["moment_matched_gaussian_w2"] < 0.25 * summary["baseline_identity"]["moment_matched_gaussian_w2"],
        "default_quality_mean_error_below_0_08": largest["learned"]["mean_abs_error"] < 0.08,
        "default_quality_std_error_below_0_06": largest["learned"]["std_abs_error"] < 0.06,
        "default_quality_velocity_rmse_below_0_10": summary["held_out_velocity_rmse_to_analytic"] < 0.10,
        "oracle_refinement_reduces_endpoint_error": summary["runs"][-1]["oracle_rmse_to_exact_endpoint"] < summary["runs"][0]["oracle_rmse_to_exact_endpoint"] if len(args.steps) > 1 else None,
    }
    summary["checks"] = checks
    summary["checks_passed"] = all(value for value in checks.values() if value is not None)
    summary["skipped_checks"] = [key for key, value in checks.items() if value is None]
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "metrics.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (output / "field.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["t", "a", "b", "training_mse", "analytic_a", "analytic_b"])
        writer.writeheader()
        for row in model:
            a, b = analytic_coefficients(row["t"])
            writer.writerow(dict(row, analytic_a=a, analytic_b=b))
    with (output / "samples.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["sample_id", "initial", "learned_final", "exact_reference_final"])
        writer.writerows((index, initial[index], final_samples[index], TARGET_MEAN + TARGET_STD * initial[index]) for index in range(args.samples))
    write_svg(output / "flow.svg", initial, final_samples, final_trajectories)
    print(json.dumps({"output_dir": str(output.resolve()), "checks_passed": summary["checks_passed"],
                      "largest_step_run": largest, "held_out_velocity_rmse": summary["held_out_velocity_rmse_to_analytic"]}, indent=2))
    return 0 if summary["checks_passed"] else 1


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="outputs/02-flow", help="Artifact directory (default: outputs/02-flow)")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--knots", type=int, default=41)
    parser.add_argument("--train-per-knot", type=int, default=6000)
    parser.add_argument("--samples", type=int, default=2048)
    parser.add_argument("--steps", default="8,32,128", help="Comma-separated positive Euler step counts")
    args = parser.parse_args()
    try:
        args.steps = sorted(set(int(value) for value in args.steps.split(",")))
    except ValueError:
        parser.error("--steps must contain integers separated by commas")
    if args.knots < 2 or args.train_per_knot < 10 or args.samples < 10 or not args.steps or min(args.steps) < 1:
        parser.error("Require knots >= 2, train-per-knot/samples >= 10 and positive steps")
    return args


if __name__ == "__main__":
    sys.exit(run(parse_args()))
