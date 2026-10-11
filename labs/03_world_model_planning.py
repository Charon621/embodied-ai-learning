#!/usr/bin/env python3
"""CPU/stdlib lab: learn a toy world model, evaluate rollout, then control.

This is an affine dynamics/MPC teaching experiment, not a Dreamer, JEPA,
video-model, or robot benchmark reproduction. No network or dependencies.
"""

import argparse
import csv
import json
import math
from pathlib import Path
import random
import statistics
import sys


def clip(value, low=-1.0, high=1.0):
    return max(low, min(high, value))


def real_step(state, action, impulse=0.0):
    """The plant is known to the experimenter, hidden from the fitted model.

    Position-dependent gain changes outside the data collection region.
    The optional impulse changes velocity *after* the chosen action.
    """
    p, v = state
    gain = 0.20 + 0.10 * math.tanh(max(abs(p) - 2.0, 0.0))
    vn = 0.90 * v + gain * action - 0.015 * math.sin(p) + impulse
    return (p + vn, vn)


def solve_linear(matrix, rhs):
    """Gaussian elimination with partial pivoting; the matrix is only 4x4."""
    augmented = [list(row) + [b] for row, b in zip(matrix, rhs)]
    size = len(rhs)
    for i in range(size):
        pivot = max(range(i, size), key=lambda k: abs(augmented[k][i]))
        augmented[i], augmented[pivot] = augmented[pivot], augmented[i]
        if abs(augmented[i][i]) < 1e-12:
            raise ValueError("Singular fitting problem; collect richer actions.")
        divisor = augmented[i][i]
        augmented[i] = [x / divisor for x in augmented[i]]
        for k in range(size):
            if k != i:
                scale = augmented[k][i]
                augmented[k] = [x - scale * y for x, y in zip(augmented[k], augmented[i])]
    return [row[-1] for row in augmented]


def collect_episodes(seed, count, steps, ood=False):
    rng = random.Random(seed)
    episodes, rows = [], []
    for episode in range(count):
        center = 3.5 if ood else 0.0
        state = (center + rng.uniform(-0.6, 0.6), rng.uniform(-0.15, 0.15))
        states, actions = [state], []
        for step in range(steps):
            # Feedback keeps each collection policy around its own region.
            action = clip(-0.55 * (state[0] - center) - 0.85 * state[1] + rng.uniform(-0.75, 0.75))
            following = real_step(state, action)
            rows.append([episode, step, *state, action, *following])
            actions.append(action)
            states.append(following)
            state = following
        episodes.append((states, actions))
    return episodes, rows


def fit_model(rows):
    # Fit v_next = cp*p + cv*v + ca*a + c0; integrate p_next = p + v_next.
    normal = [[0.0] * 4 for _ in range(4)]
    rhs = [0.0] * 4
    for _, _, p, v, action, _, vn in rows:
        features = [p, v, action, 1.0]
        for i in range(4):
            rhs[i] += features[i] * vn
            for j in range(4):
                normal[i][j] += features[i] * features[j]
    # Tiny ridge improves conditioning; no holdout values are used for tuning.
    for i in range(4):
        normal[i][i] += 1e-8
    return solve_linear(normal, rhs)


def model_step(state, action, coefficients):
    p, v = state
    cp, cv, ca, c0 = coefficients
    vn = cp * p + cv * v + ca * action + c0
    return (p + vn, vn)


def rmse(errors):
    return math.sqrt(statistics.fmean(x * x for x in errors))


def evaluate_predictions(episodes, model, split, name, horizon):
    per_step = [[] for _ in range(horizon)]
    prediction_rows, one_p, one_v = [], [], []
    for episode, (states, actions) in enumerate(episodes):
        # One-step predictions use the actual preceding state (teacher forcing).
        for state, action, target in zip(states[:-1], actions, states[1:]):
            predicted = model_step(state, action, model)
            one_p.append(predicted[0] - target[0])
            one_v.append(predicted[1] - target[1])
        # Free rollout starts once per independent holdout episode, then uses
        # its own predicted states and the same logged ground-truth actions.
        predicted = states[0]
        for k in range(horizon):
            predicted = model_step(predicted, actions[k], model)
            actual = states[k + 1]
            errors = (predicted[0] - actual[0], predicted[1] - actual[1])
            per_step[k].append(errors)
            prediction_rows.append([split, name, episode, k + 1, *actual, *predicted, *errors])
    one_step = {
        "position_rmse": rmse(one_p), "velocity_rmse": rmse(one_v),
        "state_rmse": math.sqrt((rmse(one_p) ** 2 + rmse(one_v) ** 2) / 2),
        "transitions": len(one_p), "uses_actual_preceding_state": True,
    }
    curve = []
    for k, errors in enumerate(per_step):
        pr = rmse([x[0] for x in errors])
        vr = rmse([x[1] for x in errors])
        curve.append({"horizon": k + 1, "position_rmse": pr, "velocity_rmse": vr,
                      "state_rmse": math.sqrt((pr * pr + vr * vr) / 2), "episodes": len(errors)})
    return {"one_step": one_step, "free_rollout": curve}, prediction_rows


class QuadraticPlanner:
    """Bounded finite-horizon quadratic planning using the *learned* model.

    Coordinate descent solves a convex action problem for this affine model.
    It is deliberately simpler than neural-model CEM or learned actors.
    Both controllers use identical objective, optimizer, and remaining horizon.
    """

    def __init__(self, coefficients):
        self.coefficients = coefficients
        self.cache = {}

    def responses(self, horizon):
        if horizon in self.cache:
            return self.cache[horizon]
        cp, cv, ca, _ = self.coefficients
        p_effects, v_effects = [], []
        p_effect, v_effect = [0.0] * horizon, [0.0] * horizon
        for k in range(horizon):
            for j in range(k):
                v_effect[j] = cp * p_effect[j] + cv * v_effect[j]
                p_effect[j] += v_effect[j]
            p_effect[k] = v_effect[k] = ca
            p_effects.append(p_effect.copy())
            v_effects.append(v_effect.copy())
        hessian = [[0.0] * horizon for _ in range(horizon)]
        for k in range(horizon):
            q = 4.0 if k == horizon - 1 else 1.0
            for i in range(k + 1):
                for j in range(k + 1):
                    hessian[i][j] += q * p_effects[k][i] * p_effects[k][j] + 0.10 * v_effects[k][i] * v_effects[k][j]
        for i in range(horizon):
            hessian[i][i] += 0.03
        answer = (p_effects, v_effects, hessian)
        self.cache[horizon] = answer
        return answer

    def plan(self, state, goal, horizon, warm=None):
        p_effects, v_effects, hessian = self.responses(horizon)
        linear = [0.0] * horizon
        baseline = state
        for k in range(horizon):
            baseline = model_step(baseline, 0.0, self.coefficients)
            q = 4.0 if k == horizon - 1 else 1.0
            for i in range(k + 1):
                linear[i] += q * (baseline[0] - goal) * p_effects[k][i] + 0.10 * baseline[1] * v_effects[k][i]
        actions = [clip(a) for a in warm[:horizon]] if warm else [0.0] * horizon
        actions += [0.0] * (horizon - len(actions))
        sweeps = 0
        for sweeps in range(1, 161):
            max_change = 0.0
            for i in range(horizon):
                residual = linear[i] + sum(hessian[i][j] * actions[j] for j in range(horizon) if j != i)
                following = clip(-residual / hessian[i][i])
                max_change = max(max_change, abs(following - actions[i]))
                actions[i] = following
            if max_change < 1e-6:
                break
        # Projected gradient/KKT residual reveals optimizer imperfections.
        residual = max(abs(actions[i] - clip(actions[i] - (linear[i] + sum(hessian[i][j] * actions[j] for j in range(horizon))) / hessian[i][i])) for i in range(horizon))
        return actions, sweeps, residual


def control_trial(model, initial, goal, steps, controller, impulse_step=None):
    planner = QuadraticPlanner(model)
    state, actions, rows, cost = initial, [], [], 0.0
    plan_count, largest_residual = 0, 0.0
    last_plan = None
    if controller == "open_loop":
        actions, _, residual = planner.plan(initial, goal, steps)
        plan_count, largest_residual = 1, residual
    for k in range(steps):
        if controller == "receding_horizon":
            warm = last_plan[1:] if last_plan else None
            last_plan, _, residual = planner.plan(state, goal, steps - k, warm)
            action = last_plan[0]
            plan_count += 1
            largest_residual = max(largest_residual, residual)
        else:
            action = actions[k]
        predicted = model_step(state, action, model)
        impulse = 0.45 if k == impulse_step else 0.0
        following = real_step(state, action, impulse)
        q = 4.0 if k == steps - 1 else 1.0
        stage_cost = q * (following[0] - goal) ** 2 + 0.10 * following[1] ** 2 + 0.03 * action ** 2
        cost += stage_cost
        rows.append([k, *state, action, impulse, *following, *predicted, stage_cost])
        state = following
    result = {"cost": cost, "final_position_error": abs(state[0] - goal),
              "final_velocity": state[1], "plan_calls": plan_count,
              "max_projected_gradient_residual": largest_residual}
    return result, rows


def write_csv(path, header, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def svg_chart(path, panels, nonnegative=False):
    """Small dependency-free SVG; each panel is (title, series, x_label)."""
    width, panel_height = 880, 260
    colors = ["#2368a0", "#d16227", "#20806f", "#8b4b9b"]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{panel_height * len(panels)}" viewBox="0 0 {width} {panel_height * len(panels)}">', '<rect width="100%" height="100%" fill="#fbfcfd"/>']
    for panel, (title, series, label) in enumerate(panels):
        top, left, plotw, ploth = panel * panel_height + 42, 76, 730, 145
        xs = [x for _, points in series for x, _ in points]
        ys = [y for _, points in series for _, y in points]
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        pad = max((ymax - ymin) * 0.12, 0.005)
        ymin, ymax = max(0.0, ymin - pad) if nonnegative else ymin - pad, ymax + pad
        def px(x):
            return left + (x - xmin) / max(xmax - xmin, 1e-12) * plotw
        def py(y):
            return top + ploth - (y - ymin) / (ymax - ymin) * ploth
        parts.append(f'<text x="{left}" y="{top - 18}" font-family="sans-serif" font-size="15">{title}</text>')
        for tick in range(5):
            y = ymin + (ymax - ymin) * tick / 4
            parts.append(f'<line x1="{left}" y1="{py(y):.2f}" x2="{left + plotw}" y2="{py(y):.2f}" stroke="#dbe2e9"/>')
            parts.append(f'<text x="{left - 10}" y="{py(y) + 4:.2f}" text-anchor="end" font-family="sans-serif" font-size="11">{y:.3f}</text>')
        for tick in range(5):
            x = xmin + (xmax - xmin) * tick / 4
            parts.append(f'<text x="{px(x):.2f}" y="{top + ploth + 19}" text-anchor="middle" font-family="sans-serif" font-size="11">{x:.0f}</text>')
        for i, (name, points) in enumerate(series):
            coordinates = " ".join(f"{px(x):.2f},{py(y):.2f}" for x, y in points)
            color = colors[i % len(colors)]
            parts.append(f'<polyline points="{coordinates}" fill="none" stroke="{color}" stroke-width="2"/>')
            parts.append(f'<text x="{left + i * 180}" y="{top + ploth + 51}" fill="{color}" font-family="sans-serif" font-size="12">{name}</text>')
        parts.append(f'<text x="{left + plotw / 2}" y="{top + ploth + 35}" text-anchor="middle" font-family="sans-serif" font-size="11">{label}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/03-world-model"))
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--episodes", type=int, default=8, help="Paired control trials per scenario, 1..64.")
    parser.add_argument("--horizon", type=int, default=24, help="Control episode length and initial planning horizon, 8..48.")
    args = parser.parse_args()
    if args.seed < 0:
        parser.error("seed must be nonnegative")
    if not 1 <= args.episodes <= 64 or not 8 <= args.horizon <= 48:
        parser.error("episodes must be 1..64 and horizon 8..48")
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    _, training_rows = collect_episodes(args.seed, 64, 30)
    id_episodes, id_rows = collect_episodes(args.seed + 10001, 32, 24)
    ood_episodes, ood_rows = collect_episodes(args.seed + 20001, 32, 24, ood=True)
    model = fit_model(training_rows)
    biased = model.copy()
    biased[2] *= 0.65
    biased[3] += 0.035
    models = {"fitted": model, "biased": biased}
    prediction, prediction_rows, error_rows = {}, [], []
    for split, episodes in [("in_distribution", id_episodes), ("out_of_distribution", ood_episodes)]:
        prediction[split] = {}
        for name, coefficients in models.items():
            metrics, rows = evaluate_predictions(episodes, coefficients, split, name, 20)
            prediction[split][name] = metrics
            prediction_rows.extend(rows)
            error_rows.extend([split, name, entry["horizon"], entry["position_rmse"], entry["velocity_rmse"], entry["state_rmse"], entry["episodes"]] for entry in metrics["free_rollout"])
    scenarios = {
        "baseline_id": {"model": "fitted", "position": -1.1, "goal": 0.9, "impulse": None},
        "unseen_impulse": {"model": "fitted", "position": -1.1, "goal": 0.9, "impulse": args.horizon // 3},
        "initial_state_ood": {"model": "fitted", "position": 3.6, "goal": -0.9, "impulse": None},
        "deliberately_biased_model": {"model": "biased", "position": -1.1, "goal": 0.9, "impulse": None},
    }
    rng = random.Random(args.seed + 30001)
    control, control_rows, summary_rows, control_panels = {}, [], [], []
    for scenario, specification in scenarios.items():
        control[scenario] = {name: [] for name in ["open_loop", "receding_horizon"]}
        example_series = []
        for trial in range(args.episodes):
            # Paired initial states and impulses are shared by both controllers.
            initial = (specification["position"] + rng.uniform(-0.08, 0.08), rng.uniform(-0.04, 0.04))
            for controller in control[scenario]:
                result, rows = control_trial(models[specification["model"]], initial, specification["goal"], args.horizon, controller, specification["impulse"])
                control[scenario][controller].append(result)
                summary_rows.append([scenario, controller, trial, *initial, specification["goal"], result["cost"], result["final_position_error"], result["final_velocity"], result["plan_calls"], result["max_projected_gradient_residual"]])
                control_rows.extend([scenario, controller, trial, specification["goal"], *row] for row in rows)
                if trial == 0:
                    example_series.append((controller, [(0, initial[0])] + [(row[0] + 1, row[5]) for row in rows]))
        aggregate = {}
        for controller, results in control[scenario].items():
            aggregate[controller] = {
                "mean_cost": statistics.fmean(r["cost"] for r in results),
                "cost_sample_std": statistics.stdev(r["cost"] for r in results) if len(results) > 1 else 0.0,
                "mean_final_position_error": statistics.fmean(r["final_position_error"] for r in results),
                "mean_plan_calls": statistics.fmean(r["plan_calls"] for r in results),
                "max_projected_gradient_residual": max(r["max_projected_gradient_residual"] for r in results),
            }
        paired = [o["cost"] - m["cost"] for o, m in zip(control[scenario]["open_loop"], control[scenario]["receding_horizon"])]
        aggregate["paired_cost_difference_open_minus_receding"] = {
            "mean": statistics.fmean(paired), "positive_count": sum(d > 0 for d in paired), "trials": len(paired),
            "interpretation": "Positive means lower receding-horizon cost in this toy experiment; not a universal theorem.",
        }
        control[scenario] = aggregate
        example_series.append(("goal", [(0, specification["goal"]), (args.horizon, specification["goal"])]))
        control_panels.append((scenario + " / paired trial 0 / position", example_series, "environment step"))
    training_range = {name: [min(row[index] for row in training_rows), max(row[index] for row in training_rows)] for name, index in [("position", 2), ("velocity", 3), ("action", 4)]}
    metrics = {
        "schema_version": 1, "seed": args.seed,
        "scope": "Synthetic fully-observed affine-model experiment; no neural world model, pixels, RL actor, or real robot.",
        "config": {"train_episodes": 64, "train_steps": 30, "holdout_episodes_per_split": 32, "holdout_steps": 24, "free_rollout_horizon": 20, "control_trials_per_scenario": args.episodes, "control_steps": args.horizon, "action_bounds": [-1, 1]},
        "split_protocol": "Separate whole episodes and independent RNG seeds; holdouts are not used for fitting or optimizer tuning.",
        "true_dynamics": "gain(p)=0.20+0.10*tanh(max(abs(p)-2,0)); v'=0.90*v+gain(p)*a-0.015*sin(p)+impulse; p'=p+v'",
        "model_equation": "v'=cp*p+cv*v+ca*a+c0; p'=p+v'",
        "coefficient_order": ["cp", "cv", "ca", "c0"], "models": models, "training_range": training_range,
        "planning_protocol": "Identical bounded quadratic objective and coordinate solver. Open loop plans all steps once; receding horizon replans remaining steps from actual state and executes only the first action. No model is refit during control.",
        "cost_equation": "sum_t q_t*(p_next-goal)^2+0.10*v_next^2+0.03*a^2, q_t=1 except terminal q=4",
        "prediction": prediction, "control": control,
        "limitations": ["Fully observed toy states do not measure representation quality or partial observability.", "Model class is intentionally misspecified; OOD gain and external impulse are not fitted.", "The receding controller uses more planning calls; cost comparison is not compute-matched.", "Finite coordinate-descent sweeps can leave solver residual; inspect the reported residual.", "No hyperparameter sweep, confidence interval, paper reproduction, or hardware claim."],
    }
    write_csv(out / "train.csv", ["episode", "step", "position", "velocity", "action", "next_position", "next_velocity"], training_rows)
    write_csv(out / "holdout.csv", ["split", "episode", "step", "position", "velocity", "action", "next_position", "next_velocity"], [["in_distribution", *row] for row in id_rows] + [["out_of_distribution", *row] for row in ood_rows])
    write_csv(out / "prediction_errors.csv", ["split", "model", "horizon", "position_rmse", "velocity_rmse", "state_rmse", "episodes"], error_rows)
    write_csv(out / "predictions.csv", ["split", "model", "episode", "horizon", "actual_position", "actual_velocity", "predicted_position", "predicted_velocity", "position_error", "velocity_error"], prediction_rows)
    write_csv(out / "control_summary.csv", ["scenario", "controller", "trial", "initial_position", "initial_velocity", "goal", "cost", "final_position_error", "final_velocity", "plan_calls", "max_projected_gradient_residual"], summary_rows)
    write_csv(out / "trajectories.csv", ["scenario", "controller", "trial", "goal", "step", "position", "velocity", "action", "velocity_impulse", "next_position", "next_velocity", "model_next_position", "model_next_velocity", "stage_cost"], control_rows)
    (out / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    prediction_panels = []
    for split in prediction:
        series = [(name, [(entry["horizon"], entry["state_rmse"]) for entry in data["free_rollout"]]) for name, data in prediction[split].items()]
        prediction_panels.append((split + " / free-rollout state RMSE", series, "prediction horizon"))
    svg_chart(out / "prediction_errors.svg", prediction_panels, nonnegative=True)
    svg_chart(out / "control_trajectories.svg", control_panels)
    # Guard output validity without enforcing any preferred performance ranking.
    if not all(math.isfinite(row[-1]) and abs(row[7]) <= 1.0 for row in control_rows):
        raise AssertionError("Non-finite trajectory or action-bound violation")
    print(json.dumps({"output_dir": str(out.resolve()), "seed": args.seed, "fitted_coefficients": model,
                      "control_mean_costs": {s: {c: d[c]["mean_cost"] for c in ["open_loop", "receding_horizon"]} for s, d in control.items()}}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
