"""Two-key and causal single-head attention, with no external dependencies."""
import argparse
import csv
import json
import math
from pathlib import Path


def attention(query, keys, values, visible=None):
    visible = len(keys) if visible is None else visible
    logits = [sum(a * b for a, b in zip(query, key)) / math.sqrt(len(query)) for key in keys]
    max_logit = max(logits[:visible])
    exps = [math.exp(logit - max_logit) if i < visible else 0.0 for i, logit in enumerate(logits)]
    weights = [value / sum(exps) for value in exps]
    output = [sum(weight * value[d] for weight, value in zip(weights, values)) for d in range(len(values[0]))]
    return {'logits_before_mask': logits, 'weights': weights, 'output': output}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=Path('outputs/attention'))
    args = parser.parse_args()
    keys = [[1, 0], [0, 1]]
    values = [[2, 0], [0, 2]]
    two_keys = attention([1, 0], keys, values)
    masked = attention([1, 0], keys, values, visible=1)
    sequence = [[1, 0], [0, 1], [1, 1]]
    causal = [attention(q, sequence, [[2, 0], [0, 2], [1, 1]], visible=i + 1)
              for i, q in enumerate(sequence)]
    result = {'two_keys': two_keys, 'second_key_masked': masked, 'causal_three_tokens': causal,
              'scope': 'Single-head arithmetic demonstration; no trained transformer.'}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    with (args.output_dir / 'token-budget.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(['frames', 'height', 'width', 'patch', 'tokens', 'full_attention_entries', 'factorized_entries'])
        for frames, height, width in [(1, 224, 224), (1, 512, 512), (16, 224, 224)]:
            spatial = (height // 16) * (width // 16)
            total = spatial * frames
            writer.writerow([frames, height, width, 16, total, total ** 2, frames * spatial ** 2 + spatial * frames ** 2])
    print('两个key的权重：', two_keys['weights'])
    print('加权结果：', two_keys['output'])
    print('屏蔽第二个key：', masked['output'])
    print('三个token的因果mask权重：', [row['weights'] for row in causal])
    print('结果在：', args.output_dir)


if __name__ == '__main__':
    main()
