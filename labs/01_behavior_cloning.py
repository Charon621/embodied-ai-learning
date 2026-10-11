"""Toy behavior cloning under distribution shift; standard library only.

Dynamics: next_x = x + 0.25*x**2 + action.
Expert: action = -0.65*x - 0.25*x**2.
Learner: a quadratic ridge regressor, trained near zero, then on visited states.
This is an instructional feedback-data exercise, not a DAgger or robot benchmark.
"""
import argparse
import csv
import json
import math
import random
from pathlib import Path


def features(x):
    return [1.0, x, x * x]


def expert(x):
    return -0.65 * x - 0.25 * x * x


def solve(matrix, target):
    a = [row[:] + [value] for row, value in zip(matrix, target)]
    for col in range(len(target)):
        pivot = max(range(col, len(a)), key=lambda i: abs(a[i][col]))
        a[col], a[pivot] = a[pivot], a[col]
        if abs(a[col][col]) < 1e-12:
            raise ValueError("Singular fit")
        scale = a[col][col]
        a[col] = [v / scale for v in a[col]]
        for i in range(len(a)):
            if i == col:
                continue
            ratio = a[i][col]
            a[i] = [v - ratio * w for v, w in zip(a[i], a[col])]
    return [row[-1] for row in a]


def fit(samples, ridge=0.2):
    matrix = [[0.0] * 3 for _ in range(3)]
    target = [0.0] * 3
    for x, action in samples:
        f = features(x)
        for i in range(3):
            target[i] += f[i] * action
            for j in range(3):
                matrix[i][j] += f[i] * f[j]
    for i in range(1, 3):
        matrix[i][i] += ridge
    matrix[0][0] += 1e-9
    return solve(matrix, target)


def policy(weights, x):
    return sum(w * f for w, f in zip(weights, features(x)))


def rollout(weights, start, steps=20):
    x = start
    rows = []
    failed = False
    for step in range(steps):
        action = expert(x) if weights is None else policy(weights, x)
        rows.append({"step": step, "state": x, "action": action})
        x = x + 0.25 * x * x + action
        if not math.isfinite(x) or abs(x) > 8.0:
            failed = True
            break
    # A failed rollout receives the same stated penalty even if it ends early.
    cost = sum(row["state"] ** 2 for row in rows) + (1000.0 if failed else x * x)
    return rows, cost, failed


def mse(weights, states):
    return sum((policy(weights, x) - expert(x)) ** 2 for x in states) / len(states)


def evaluate(weights, starts):
    results = [rollout(weights, x) for x in starts]
    return {"mean_state_cost": sum(r[1] for r in results) / len(results),
            "failed_episodes": sum(r[2] for r in results),
            "episodes": len(results), "failure_threshold": 8.0,
            "failure_penalty": 1000.0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/bc"))
    args = parser.parse_args()
    rng = random.Random(args.seed)
    train = []
    for _ in range(200):
        x = rng.uniform(-0.15, 0.15)
        train.append((x, expert(x) + rng.gauss(0, 0.01)))
    initial = fit(train)
    iid = [rng.uniform(-0.15, 0.15) for _ in range(200)]
    shifted = [rng.uniform(-3, 3) for _ in range(200)]
    starts = [-3, -2, -1, -0.2, 0.2, 1, 2, 3]
    history = []
    augmented = train[:]
    current = initial
    for iteration in range(3):
        # These are training starts. The held-out evaluation starts are separate.
        query_starts = [rng.uniform(-3, 3) for _ in range(8)]
        before = len(augmented)
        for start in query_starts:
            rows, _, _ = rollout(current, start)
            augmented.extend((r["state"], expert(r["state"])) for r in rows)
        current = fit(augmented)
        history.append({"iteration": iteration + 1, "queried_labels": len(augmented) - before,
                        "weights": current})
    result = {"seed": args.seed, "training_samples": len(train),
              "training_range": [-0.15, 0.15], "ridge": 0.2,
              "expert_weights": [0, -0.65, -0.25],
              "bc_weights": initial, "feedback_weights": current,
              "iid_action_mse": {"bc": mse(initial, iid), "feedback": mse(current, iid)},
              "shifted_action_mse": {"bc": mse(initial, shifted), "feedback": mse(current, shifted)},
              "closed_loop": {"expert": evaluate(None, starts), "bc": evaluate(initial, starts),
                              "feedback": evaluate(current, starts)},
              "feedback_history": history,
              "limitations": ["Toy state observed directly; known polynomial feature class.",
                              "Feedback requires expert labels and increases training data.",
                              "Regularization and narrow training support cause this failure.",
                              "No neural VLA, camera, contact physics, or real robot evaluation."]}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "metrics.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    with (args.output_dir / "rollouts.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["policy", "initial_state", "step", "state", "action"])
        for name, weights in [("expert", None), ("bc", initial), ("feedback", current)]:
            for start in starts:
                rows, _, _ = rollout(weights, start)
                writer.writerows([name, start, r["step"], r["state"], r["action"]] for r in rows)
    lines = ['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="380" viewBox="0 0 760 380">',
             '<rect width="760" height="380" fill="white"/>',
             '<text x="40" y="25" font-family="sans-serif" font-size="18">Toy closed-loop rollout: initial x=3</text>',
             '<path d="M40 50V330H720" fill="none" stroke="#999"/>']
    for index, (name, weights, color) in enumerate([("expert", None, "#4b5563"), ("bc", initial, "#dc2626"), ("feedback", current, "#2563eb")]):
        rows, _, _ = rollout(weights, 3)
        points = " ".join(f'{40 + r["step"] * 32:.2f},{190 - r["state"] * 17:.2f}' for r in rows)
        lines.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2"/>')
        lines.append(f'<text x="{60 + index * 160}" y="365" fill="{color}" font-family="sans-serif">{name}</text>')
    lines.append('</svg>')
    (args.output_dir / "rollout.svg").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"output_dir": str(args.output_dir), "metrics": result["closed_loop"],
                      "iid_mse": result["iid_action_mse"], "shifted_mse": result["shifted_action_mse"]}))


if __name__ == "__main__":
    main()
