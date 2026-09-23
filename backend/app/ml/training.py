import torch
import torch.nn as nn
import torch.optim as optim

from app.ml.graphsage import GraphSAGE, RiskClassifier


def create_training_data():
    """Create deterministic synthetic normal/suspicious graph data."""

    normal_features = torch.tensor(
        [
            [2.0, 500.0, 250.0, 2.0, 0.0, 2.0],
            [3.0, 600.0, 200.0, 3.0, 0.0, 3.0],
            [2.0, 450.0, 225.0, 2.0, 0.0, 2.0],
            [4.0, 800.0, 200.0, 4.0, 0.0, 4.0],
        ],
        dtype=torch.float32,
    )

    suspicious_features = torch.tensor(
        [
            [30.0, 9000.0, 300.0, 25.0, 5.0, 20.0],
            [40.0, 12000.0, 300.0, 30.0, 10.0, 25.0],
            [50.0, 15000.0, 300.0, 35.0, 15.0, 30.0],
            [60.0, 18000.0, 300.0, 40.0, 20.0, 35.0],
        ],
        dtype=torch.float32,
    )

    features = torch.cat(
        [normal_features, suspicious_features],
        dim=0,
    )

    labels = torch.tensor(
        [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0],
        dtype=torch.float32,
    )

    edge_index = torch.tensor(
        [
            [0, 1, 2, 3, 4, 5, 6, 7],
            [1, 0, 3, 2, 5, 4, 7, 6],
        ],
        dtype=torch.long,
    )

    return features, edge_index, labels


def normalize_features(features):
    """Normalize each feature to a comparable numerical scale."""

    feature_min = features.min(dim=0).values
    feature_max = features.max(dim=0).values

    feature_range = feature_max - feature_min
    feature_range = torch.where(
        feature_range == 0,
        torch.ones_like(feature_range),
        feature_range,
    )

    return (features - feature_min) / feature_range, feature_min, feature_max


def train():
    """Train the GUARDIAN-X demonstration detection model."""

    torch.manual_seed(42)

    features, edge_index, labels = create_training_data()

    features, feature_min, feature_max = normalize_features(features)

    model = GraphSAGE(
        input_dim=6,
        hidden_dim=16,
        output_dim=8,
    )

    classifier = RiskClassifier(
        input_dim=8,
    )

    optimizer = optim.Adam(
        list(model.parameters()) + list(classifier.parameters()),
        lr=0.01,
    )

    loss_function = nn.BCELoss()

    model.train()
    classifier.train()

    for epoch in range(500):
        optimizer.zero_grad()

        embeddings = model(
            features,
            edge_index,
        )

        risks = classifier(embeddings)

        loss = loss_function(
            risks,
            labels,
        )

        loss.backward()
        optimizer.step()

        if (epoch + 1) % 100 == 0:
            print(
                f"Epoch {epoch + 1}/500 - "
                f"Loss: {loss.item():.4f}"
            )

    torch.save(
        {
            "graphsage": model.state_dict(),
            "classifier": classifier.state_dict(),
            "feature_min": feature_min,
            "feature_max": feature_max,
        },
        "app/ml/guardian_model.pt",
    )

    model.eval()
    classifier.eval()

    with torch.no_grad():
        embeddings = model(
            features,
            edge_index,
        )

        risks = classifier(embeddings)

    print("\nTraining complete.")
    print("Risk scores:")

    for index, risk in enumerate(risks.tolist()):
        label = "SUSPICIOUS" if risk >= 0.5 else "NORMAL"

        print(
            f"Sample {index + 1}: "
            f"{risk:.4f} -> {label}"
        )

    print("\nModel saved to: app/ml/guardian_model.pt")


if __name__ == "__main__":
    train()