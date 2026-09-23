"""Train and evaluate GraphSAGE on separately captured labeled sessions.

Never report this model as validated on botnets without real ground truth and
representative independent test sessions. Split by session to prevent leakage.
"""
import argparse
import json
import random
from collections import Counter
from pathlib import Path

import torch
import torch.nn as nn

from app.ml.graphsage import GraphSAGE, RiskClassifier


def load_sessions(path: Path):
    sessions = []
    seen = set()
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        name = item['session']
        if name in seen:
            raise ValueError(f'Duplicate session: {name}; each capture needs a unique ID')
        seen.add(name)
        nodes = item['nodes']
        if not nodes or any(len(node['features']) != 6 or node['label'] not in (0, 1) for node in nodes):
            raise ValueError(f'Invalid nodes in session {name}')
        sessions.append(item)
    session_labels = Counter(int(any(node['label'] for node in item['nodes'])) for item in sessions)
    if len(sessions) < 8 or min(session_labels.get(0, 0), session_labels.get(1, 0)) < 4:
        raise ValueError('Need at least eight sessions: four all-normal and four containing labeled suspicious devices')
    return sessions


def graph_tensors(session, low, high):
    nodes = session['nodes']
    x = torch.tensor([node['features'] for node in nodes], dtype=torch.float32)
    x = (x - low) / torch.where(high == low, torch.ones_like(high), high - low)
    labels = torch.tensor([node['label'] for node in nodes], dtype=torch.float32)
    lookup = {node['device_id']: i for i, node in enumerate(nodes)}
    edges = [(lookup[a], lookup[b]) for a, b in session['edges'] if a in lookup and b in lookup]
    edges += [(b, a) for a, b in edges]
    edge_index = torch.tensor(edges, dtype=torch.long).T.contiguous() if edges else torch.empty((2, 0), dtype=torch.long)
    return x, edge_index, labels


def metrics(predicted, actual):
    tp = sum(p == 1 and y == 1 for p, y in zip(predicted, actual))
    fp = sum(p == 1 and y == 0 for p, y in zip(predicted, actual))
    fn = sum(p == 0 and y == 1 for p, y in zip(predicted, actual))
    tn = sum(p == 0 and y == 0 for p, y in zip(predicted, actual))
    return {'TP': tp, 'FP': fp, 'FN': fn, 'TN': tn,
            'precision': round(tp / (tp + fp), 3) if tp + fp else 0,
            'recall': round(tp / (tp + fn), 3) if tp + fn else 0,
            'false_positive_rate': round(fp / (fp + tn), 3) if fp + tn else 0}


def train(dataset: Path, output: Path, epochs: int = 150):
    if epochs < 1:
        raise ValueError('epochs must be positive')
    torch.manual_seed(42)
    sessions = load_sessions(dataset)
    random.Random(42).shuffle(sessions)
    # Both classes must be represented in the held-out sessions.
    by_class = {label: [item for item in sessions if int(any(n['label'] for n in item['nodes'])) == label]
                for label in (0, 1)}
    if len(by_class[0]) < 2 or len(by_class[1]) < 2:
        raise ValueError('Need at least two sessions per class')
    test_names = {by_class[0][0]['session'], by_class[1][0]['session']}
    train_set = [item for item in sessions if item['session'] not in test_names]
    test_set = [item for item in sessions if item['session'] in test_names]
    train_x = torch.tensor([n['features'] for s in train_set for n in s['nodes']], dtype=torch.float32)
    low, high = train_x.min(dim=0).values, train_x.max(dim=0).values
    model = GraphSAGE(input_dim=6, hidden_dim=16, output_dim=8)
    classifier = RiskClassifier(input_dim=8)
    optimizer = torch.optim.Adam(list(model.parameters()) + list(classifier.parameters()), lr=0.01)
    loss_fn = nn.BCELoss()
    for _ in range(epochs):
        for session in train_set:
            x, edges, labels = graph_tensors(session, low, high)
            optimizer.zero_grad()
            loss = loss_fn(classifier(model(x, edges)), labels)
            loss.backward()
            optimizer.step()
    model.eval(); classifier.eval()
    predicted, actual = [], []
    with torch.no_grad():
        for session in test_set:
            x, edges, labels = graph_tensors(session, low, high)
            predicted += [int(score >= 0.5) for score in classifier(model(x, edges)).tolist()]
            actual += [int(label) for label in labels.tolist()]
    report = {'train_sessions': [s['session'] for s in train_set],
              'held_out_sessions': sorted(test_names), 'metrics': metrics(predicted, actual),
              'source': 'user-labeled capture sessions; interpret only within dataset scope'}
    output.parent.mkdir(parents=True, exist_ok=True)
    torch.save({'graphsage': model.state_dict(), 'classifier': classifier.state_dict(),
                'feature_min': low, 'feature_max': high}, output)
    output.with_suffix('.evaluation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset', type=Path)
    parser.add_argument('--output', type=Path, default=Path('app/ml/guardian_model.pt'))
    parser.add_argument('--epochs', type=int, default=150)
    args = parser.parse_args()
    print(json.dumps(train(args.dataset, args.output, args.epochs), indent=2))
