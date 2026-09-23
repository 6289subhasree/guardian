"""Reproducible synthetic checkpoint for software demos only.

This is a simulation, not botnet ground truth. See train_dataset.py for a
session-split path using separately labeled captures.
"""
import json
import random
from pathlib import Path

import torch
import torch.nn as nn

from app.ml.graphsage import GraphSAGE, RiskClassifier
from app.ml.train_dataset import metrics

OUTPUT = Path(__file__).with_name('guardian_model.pt')


def generate_graphs(seed=42, total=100):
    rng = random.Random(seed)
    graphs = []
    for _ in range(total):
        features, labels = [], []
        malicious_node = rng.randrange(3) if rng.random() < 0.75 else -1
        for node in range(3):
            suspicious = node == malicious_node
            packets = rng.randint(28, 65) if suspicious else rng.randint(2, 10)
            avg_size = rng.randint(230, 400) if suspicious else rng.randint(140, 350)
            tcp = rng.randint(int(packets * .65), packets)
            udp = packets - tcp
            connections = rng.randint(17, min(40, packets)) if suspicious else rng.randint(1, min(7, packets))
            features.append([packets, packets * avg_size, avg_size, tcp, udp, connections])
            labels.append(int(suspicious))
        # Most boards contact one common broker, so neighbors often have
        # DIFFERENT labels. The model must not mark the whole graph infected.
        edges = torch.tensor([[0, 1, 1, 2, 2, 0], [1, 0, 2, 1, 0, 2]], dtype=torch.long)
        graphs.append((torch.tensor(features, dtype=torch.float32), edges,
                       torch.tensor(labels, dtype=torch.float32)))
    return graphs


def train(epochs=35):
    torch.manual_seed(42)
    graphs = generate_graphs()
    train_set, test_set = graphs[:80], graphs[80:]
    all_x = torch.cat([x for x, _, _ in train_set])
    low, high = all_x.min(0).values, all_x.max(0).values
    scale = torch.where(high == low, torch.ones_like(high), high - low)
    model = GraphSAGE(input_dim=6, hidden_dim=16, output_dim=8)
    classifier = RiskClassifier(input_dim=8)
    optimizer = torch.optim.Adam(list(model.parameters()) + list(classifier.parameters()), lr=0.01)
    loss_fn = nn.BCELoss()
    for _ in range(epochs):
        for x, edges, labels in train_set:
            optimizer.zero_grad()
            score = classifier(model((x - low) / scale, edges))
            loss = loss_fn(score, labels)
            loss.backward()
            optimizer.step()
    predicted, actual = [], []
    model.eval(); classifier.eval()
    with torch.no_grad():
        for x, edges, labels in test_set:
            predicted.extend(int(p >= 0.5) for p in classifier(model((x - low) / scale, edges)).tolist())
            actual.extend(int(label) for label in labels.tolist())
    report = {'type': 'synthetic only', 'train_graphs': len(train_set),
              'held_out_graphs': len(test_set), 'metrics': metrics(predicted, actual)}
    torch.save({'graphsage': model.state_dict(), 'classifier': classifier.state_dict(),
                'feature_min': low, 'feature_max': high}, OUTPUT)
    OUTPUT.with_suffix('.synthetic_evaluation.json').write_text(json.dumps(report, indent=2))
    return report


if __name__ == '__main__':
    print(json.dumps(train(), indent=2))
