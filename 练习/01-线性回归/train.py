"""Fit an original synthetic straight-line dataset using only Python's stdlib."""
import argparse
import csv
import json
import math
import random
from pathlib import Path


def loss(rows, w, b):
    return sum((w * x + b - y) ** 2 for _, x, y in rows) / len(rows)


def gradient(rows, w, b):
    dw = sum(2 * (w * x + b - y) * x for _, x, y in rows) / len(rows)
    db = sum(2 * (w * x + b - y) for _, x, y in rows) / len(rows)
    return dw, db


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=7)
    parser.add_argument('--steps', type=int, default=500)
    parser.add_argument('--learning-rate', type=float, default=0.05)
    parser.add_argument('--output-dir', type=Path, default=Path('outputs/linear-regression'))
    args = parser.parse_args()
    if args.steps < 1 or not math.isfinite(args.learning_rate) or args.learning_rate <= 0:
        parser.error('steps必须为正整数，learning-rate必须为有限正数')
    rng = random.Random(args.seed)
    data = []
    for index in range(100):
        x = rng.uniform(-2, 2)
        data.append((index, x, 2 * x - 1 + rng.gauss(0, 0.1)))
    # IID synthetic examples; no adjacent frames or episodes are mixed here.
    splits = {'train': data[:60], 'validation': data[60:80], 'test': data[80:]}
    train = splits['train']
    epsilon, check_w, check_b = 1e-5, 0.3, -0.2
    analytical = gradient(train, check_w, check_b)
    numerical = ((loss(train, check_w + epsilon, check_b) - loss(train, check_w - epsilon, check_b)) / (2 * epsilon),
                 (loss(train, check_w, check_b + epsilon) - loss(train, check_w, check_b - epsilon)) / (2 * epsilon))
    errors = [abs(a - n) / max(1e-12, abs(a) + abs(n)) for a, n in zip(analytical, numerical)]
    w, b = 0.0, 0.0
    initial_loss = loss(train, w, b)
    history = [[0, w, b, initial_loss, loss(splits['validation'], w, b)]]
    for step in range(1, args.steps + 1):
        dw, db = gradient(train, w, b)
        w -= args.learning_rate * dw
        b -= args.learning_rate * db
        if not math.isfinite(w) or not math.isfinite(b):
            parser.error('参数出现非有限数，请降低学习率；这不是数据下载问题')
        if step % 10 == 0 or step == args.steps:
            history.append([step, w, b, loss(train, w, b), loss(splits['validation'], w, b)])
    result = {'seed': args.seed, 'steps': args.steps, 'learning_rate': args.learning_rate,
              'ground_truth': {'w': 2, 'b': -1, 'noise_std': 0.1}, 'learned': {'w': w, 'b': b},
              'split_sizes': {name: len(rows) for name, rows in splits.items()},
              'initial_train_mse': initial_loss,
              'final_mse': {name: loss(rows, w, b) for name, rows in splits.items()},
              'gradient_check': {'analytical': analytical, 'finite_difference': numerical,
                                 'relative_errors': errors, 'passed': max(errors) < 1e-6},
              'scope': 'IID synthetic linear regression; no neural-network or robot training.'}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / 'metrics.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    with (args.output_dir / 'history.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(['step', 'w', 'b', 'train_mse', 'validation_mse'])
        writer.writerows(history)
    with (args.output_dir / 'data.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(['split', 'sample_id', 'x', 'y', 'prediction'])
        for name, rows in splits.items():
            writer.writerows([name, index, x, y, w * x + b] for index, x, y in rows)
    print(f'初始训练误差：{initial_loss:.6f}')
    print(f'学到的参数：w={w:.6f}，b={b:.6f}；生成数据使用w=2、b=-1')
    print(f'训练/验证/测试误差：{result["final_mse"]}')
    print(f'梯度核对：{"通过" if result["gradient_check"]["passed"] else "失败"}')
    print(f'结果在：{args.output_dir}')
    return 0 if result['gradient_check']['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
