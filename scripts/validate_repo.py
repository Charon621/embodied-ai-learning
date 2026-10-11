"""Check curriculum structure and independently audit CPU-lab artifacts.

No external dependencies or network. Exit nonzero on a failed check.
Optional lab runs write only to outputs/validation; --report saves a small summary.
"""
import argparse
import csv
import datetime
import hashlib
import json
import math
import os
import platform
import re
import statistics
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {".build", ".git", ".venv", "outputs", "my-progress", "__pycache__"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def close(actual, expected, label):
    require(math.isclose(actual, expected, rel_tol=1e-8, abs_tol=1e-9),
            f"{label}: CSV={actual}, JSON={expected}")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def csv_rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    require(bool(rows), f"Empty CSV: {path}")
    return rows


def finite_tree(value, label):
    if isinstance(value, float):
        require(math.isfinite(value), f"Non-finite number in {label}")
    elif isinstance(value, dict):
        for child in value.values():
            finite_tree(child, label)
    elif isinstance(value, list):
        for child in value:
            finite_tree(child, label)


def public_files(suffix):
    return [p for p in ROOT.rglob("*" + suffix)
            if not EXCLUDED.intersection(p.relative_to(ROOT).parts)]


def check_structure():
    course = read_json(ROOT / "curriculum.json")
    sources = read_json(ROOT / "docs/sources.json")
    modules = course["modules"]
    ids = [m["id"] for m in modules]
    require(len(ids) == len(set(ids)), "Duplicate module ID")
    completed = set()
    weeks = []
    home = (ROOT / "README.md").read_text(encoding="utf-8")
    for reader_number, m in enumerate(modules, 1):
        require(set(m["prerequisites"]) <= completed,
                f"Missing prerequisite or non-topological order: {m['id']}")
        require((ROOT / m["path"]).is_file(), f"Missing module: {m['path']}")
        require(m["reader_number"] == reader_number, f"Reader chapter order: {m['id']}")
        chapter = (ROOT / m["path"]).read_text(encoding="utf-8")
        require(chapter.startswith(f"# 第{reader_number}章："), f"Readable chapter title: {m['path']}")
        require("](" + m["path"] + ")" in home, f"Chapter missing from homepage: {m['path']}")
        require("## 这一章怎么学" in chapter, f"Missing chapter learning steps: {m['path']}")
        if reader_number < len(modules):
            next_file = Path(modules[reader_number]["path"]).name
            require("[下一章](" + next_file + ")" in chapter, f"Missing next chapter: {m['path']}")
        begin, end = m["weeks"]
        require(begin <= end and m["estimated_hours"] > 0, f"Invalid duration: {m['id']}")
        require((end - begin + 1) * course["weekly_hours"] == m["estimated_hours"],
                f"Week/hour mismatch: {m['id']}")
        weeks.extend(range(begin, end + 1))
        completed.add(m["id"])
    require(weeks == list(range(1, course["planned_weeks"] + 1)), "Overlapping or missing weeks")
    require(sum(m["estimated_hours"] for m in modules) == course["total_estimated_hours"],
            "Total hours mismatch")
    source_ids = [s["id"] for s in sources]
    require(len(source_ids) == len(set(source_ids)), "Duplicate source ID")
    for s in sources:
        for key in ("title", "type", "level", "why", "verified_note", "checked_on"):
            require(bool(s.get(key)), f"Missing {key}: {s['id']}")
        require(bool(s["modules"]) and set(s["modules"]) <= set(ids), f"Source modules: {s['id']}")
        require(isinstance(s["required"], bool), f"Source required must be bool: {s['id']}")
        require(s["estimated_hours"] > 0, f"Source hours: {s['id']}")
        url = urlsplit(s["url"])
        require(url.scheme == "https" and bool(url.netloc), f"Source HTTPS URL: {s['id']}")
        datetime.date.fromisoformat(s["checked_on"])
    links = 0
    for path in public_files(".md"):
        content = path.read_text(encoding="utf-8")
        # File targets are checked. Remote URLs and heading anchors require manual review.
        for raw in re.findall(r"!?\[[^\]\n]*\]\(([^\s)]+)(?:\s+[^)]*)?\)", content):
            raw = raw.strip("<>")
            if raw.startswith("#") or urlsplit(raw).scheme:
                continue
            target = unquote(raw.split("#", 1)[0])
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            require(resolved.exists(), f"Broken file link in {path.relative_to(ROOT)}: {raw}")
            links += 1
    scripts = public_files(".py")
    for path in scripts:
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    return {"modules": len(modules), "sources": len(sources),
            "required_sources": sum(s["required"] for s in sources),
            "hours": course["total_estimated_hours"], "weeks": course["planned_weeks"],
            "local_file_links": links, "python_files_compiled": len(scripts),
            "homepage_chapter_links": len(modules), "chapter_navigation": "checked"}


def run_basics(seeds):
    reports = []
    for seed in seeds:
        destination = ROOT / "outputs/validation" / f"seed-{seed}" / "linear"
        script = ROOT / "练习/01-线性回归/train.py"
        result = subprocess.run([sys.executable, str(script), "--seed", str(seed), "--output-dir", str(destination)],
                                cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=30,
                                env={**os.environ, "PYTHONUTF8": "1"})
        require(result.returncode == 0, f"Intro linear exercise failed: {result.stderr[-1000:]}")
        metrics = audit_outputs(destination, ["metrics.json", "history.csv", "data.csv"])
        grouped = defaultdict(list)
        rows = csv_rows(destination / "data.csv")
        require(len(rows) == 100 and len({r["sample_id"] for r in rows}) == 100, "Linear data coverage")
        for row in rows:
            grouped[row["split"]].append((float(row["prediction"]) - float(row["y"])) ** 2)
        for name, squared in grouped.items():
            close(statistics.mean(squared), metrics["final_mse"][name], "Linear independent MSE")
            require(len(squared) == metrics["split_sizes"][name], "Linear split count")
        require(abs(metrics["learned"]["w"] - 2) < 0.1 and abs(metrics["learned"]["b"] + 1) < 0.1,
                "Default linear fit differs from known synthetic coefficients")
        require(metrics["gradient_check"]["passed"] is True, "Finite-difference gradient check failed")
        reports.append(metrics)
        print(f"PASS linear seed={seed}: gradient, ground truth and independent CSV MSE", flush=True)
    destination = ROOT / "outputs/validation/attention"
    result = subprocess.run([sys.executable, str(ROOT / "练习/02-注意力/attention.py"), "--output-dir", str(destination)],
                            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=30,
                            env={**os.environ, "PYTHONUTF8": "1"})
    require(result.returncode == 0, f"Attention exercise failed: {result.stderr[-1000:]}")
    attention = read_json(destination / "result.json")
    reference = math.exp(1 / math.sqrt(2)) / (math.exp(1 / math.sqrt(2)) + 1)
    close(attention["two_keys"]["weights"][0], reference, "Attention weight reference")
    close(attention["two_keys"]["output"][0], 2 * reference, "Attention value reference")
    require(attention["second_key_masked"]["output"] == [2.0, 0.0], "Attention mask result")
    for index, row in enumerate(attention["causal_three_tokens"]):
        close(sum(row["weights"]), 1, "Attention normalized weights")
        require(all(v == 0 for v in row["weights"][index + 1:]), "Causal attention leaks future tokens")
    print("PASS attention: hand-calculation reference and causal visibility", flush=True)
    return {"linear": reports, "attention": attention}


def audit_outputs(directory, expected):
    for name in expected:
        require((directory / name).is_file(), f"Missing artifact: {directory / name}")
    for path in directory.glob("*.svg"):
        require(ET.parse(path).getroot().tag.endswith("svg"), f"Invalid SVG: {path}")
    data = read_json(directory / "metrics.json")
    finite_tree(data, str(directory))
    return data


def audit_bc(directory):
    data = audit_outputs(directory, ["metrics.json", "rollouts.csv", "rollout.svg"])
    groups = defaultdict(list)
    for row in csv_rows(directory / "rollouts.csv"):
        groups[(row["policy"], row["initial_state"])].append(row)
    expected = {(policy, str(start)) for policy in ("expert", "bc", "feedback")
                for start in (-3, -2, -1, -0.2, 0.2, 1, 2, 3)}
    require(set(groups) == expected, "BC policy/initial-state coverage mismatch")
    by_policy = defaultdict(list)
    for (policy, _), rows in groups.items():
        require([int(r["step"]) for r in rows] == list(range(len(rows))), "BC step sequence")
        last = rows[-1]
        x = float(last["state"])
        endpoint = x + 0.25 * x * x + float(last["action"])
        failed = abs(endpoint) > 8 or not math.isfinite(endpoint)
        require(len(rows) <= 20 and (failed or len(rows) == 20), "BC episode length")
        cost = sum(float(r["state"]) ** 2 for r in rows) + (1000 if failed else endpoint ** 2)
        by_policy[policy].append((cost, failed))
    for policy, results in by_policy.items():
        close(statistics.mean(r[0] for r in results),
              data["closed_loop"][policy]["mean_state_cost"], "BC closed-loop cost")
        require(sum(r[1] for r in results) == data["closed_loop"][policy]["failed_episodes"],
                "BC failure-count mismatch")
    require(data["closed_loop"]["feedback"]["mean_state_cost"] <
            data["closed_loop"]["bc"]["mean_state_cost"], "Toy feedback trend changed; investigate")
    return {"iid_action_mse": data["iid_action_mse"],
            "shifted_action_mse": data["shifted_action_mse"], "closed_loop": data["closed_loop"],
            "feedback_added_labels": sum(h["queried_labels"] for h in data["feedback_history"])}


def audit_flow(directory):
    data = audit_outputs(directory, ["metrics.json", "field.csv", "samples.csv", "flow.svg"])
    rows = csv_rows(directory / "samples.csv")
    require(len(rows) == data["config"]["samples"], "Flow sample count")
    require(len({r["sample_id"] for r in rows}) == len(rows), "Flow duplicate sample ID")
    values = [float(r["learned_final"]) for r in rows]
    largest = data["runs"][-1]
    close(statistics.mean(values), largest["learned"]["mean"], "Flow endpoint mean")
    close(statistics.pstdev(values), largest["learned"]["std"], "Flow endpoint std")
    require(data["checks_passed"] is True, "Flow numerical/quality checks failed")
    errors = [r["oracle_rmse_to_exact_endpoint"] for r in data["runs"]]
    require(all(b < a for a, b in zip(errors, errors[1:])), "Analytic Euler convergence changed")
    return {"held_out_velocity_rmse_to_analytic": data["held_out_velocity_rmse_to_analytic"],
            "runs": data["runs"], "checks_passed": data["checks_passed"]}


def audit_world(directory):
    data = audit_outputs(directory, ["metrics.json", "train.csv", "holdout.csv",
                        "prediction_errors.csv", "predictions.csv", "control_summary.csv",
                        "trajectories.csv", "prediction_errors.svg", "control_trajectories.svg"])
    errors = defaultdict(list)
    for row in csv_rows(directory / "predictions.csv"):
        ep = float(row["predicted_position"]) - float(row["actual_position"])
        ev = float(row["predicted_velocity"]) - float(row["actual_velocity"])
        errors[(row["split"], row["model"], int(row["horizon"]))].append((ep * ep + ev * ev) / 2)
    expected = {(split, model, horizon) for split in ("in_distribution", "out_of_distribution")
                for model in ("fitted", "biased")
                for horizon in range(1, data["config"]["free_rollout_horizon"] + 1)}
    require(set(errors) == expected, "World prediction group coverage")
    for (split, model, horizon), squared in errors.items():
        require(len(squared) == data["config"]["holdout_episodes_per_split"], "World prediction count")
        recorded = next(r for r in data["prediction"][split][model]["free_rollout"]
                        if r["horizon"] == horizon)
        close(math.sqrt(statistics.mean(squared)), recorded["state_rmse"], "World rollout RMSE")
    controls = defaultdict(list)
    for row in csv_rows(directory / "control_summary.csv"):
        controls[(row["scenario"], row["controller"])].append(float(row["cost"]))
    for (scenario, controller), costs in controls.items():
        require(len(costs) == data["config"]["control_trials_per_scenario"], "World control trial count")
        close(statistics.mean(costs), data["control"][scenario][controller]["mean_cost"],
              "World mean control cost")
    trajectory_costs = defaultdict(float)
    for row in csv_rows(directory / "trajectories.csv"):
        action = float(row["action"])
        require(-1 - 1e-12 <= action <= 1 + 1e-12, "Action exceeds constraint")
        terminal = int(row["step"]) == data["config"]["control_steps"] - 1
        q = 4 if terminal else 1
        stage_cost = q * (float(row["next_position"]) - float(row["goal"])) ** 2
        stage_cost += 0.10 * float(row["next_velocity"]) ** 2 + 0.03 * action ** 2
        close(stage_cost, float(row["stage_cost"]), "World independently recomputed stage cost")
        trajectory_costs[(row["scenario"], row["controller"], row["trial"])] += stage_cost
    for row in csv_rows(directory / "control_summary.csv"):
        close(trajectory_costs[(row["scenario"], row["controller"], row["trial"])],
              float(row["cost"]), "World summed trajectory cost")
    return {"prediction": data["prediction"], "control": data["control"]}


def run_labs(seeds):
    scripts = [("bc", "01_behavior_cloning.py", audit_bc),
               ("flow", "02_flow_matching.py", audit_flow),
               ("world", "03_world_model_planning.py", audit_world)]
    results = []
    for seed in seeds:
        row = {"seed": seed}
        for name, filename, audit in scripts:
            destination = ROOT / "outputs" / "validation" / f"seed-{seed}" / name
            command = [sys.executable, str(ROOT / "labs" / filename), "--seed", str(seed),
                       "--output-dir", str(destination)]
            completed = subprocess.run(command, cwd=ROOT, text=True, encoding="utf-8",
                                       capture_output=True, timeout=180,
                                       env={**os.environ, "PYTHONUTF8": "1"})
            require(completed.returncode == 0,
                    f"{filename} seed {seed} failed: {completed.stderr[-2000:]}")
            row[name] = audit(destination)
            print(f"PASS {name} seed={seed}: artifacts and independent CSV checks", flush=True)
        results.append(row)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-labs", action="store_true")
    parser.add_argument("--seeds", default="7,19,42")
    parser.add_argument("--report", type=Path, help="Optional JSON evidence summary")
    args = parser.parse_args()
    try:
        structure = check_structure()
        print("PASS structure:", json.dumps(structure), flush=True)
        results = []
        basics = {}
        if args.run_labs:
            seeds = list(dict.fromkeys(int(v) for v in args.seeds.split(",")))
            require(bool(seeds), "At least one seed required")
            basics = run_basics(seeds)
            results = run_labs(seeds)
        if args.report:
            hashes = {str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in public_files(".py")}
            report = {"checked_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      "python": platform.python_version(), "platform": platform.system(),
                      "structure": structure, "script_sha256": hashes, "runs": results, "intro_exercises": basics,
                      "scope": "CPU toy experiments only; no external-model, GPU or robot validation."}
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                                   encoding="utf-8", newline="\n")
        print("All requested checks passed.")
    except (ValueError, OSError, KeyError, IndexError, SyntaxError, ET.ParseError,
            subprocess.TimeoutExpired) as error:
        print("FAIL:", error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
