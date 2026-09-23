import torch
import torch.nn as nn


class GraphSAGELayer(nn.Module):
    """Lightweight GraphSAGE neighborhood aggregation layer."""

    def __init__(self, input_dim: int, output_dim: int):
        super().__init__()

        self.linear = nn.Linear(input_dim * 2, output_dim)

    def forward(
        self,
        node_features: torch.Tensor,
        edge_index: torch.Tensor,
    ) -> torch.Tensor:
        """Aggregate neighbor features and update node representations."""

        num_nodes = node_features.size(0)

        neighbor_sum = torch.zeros_like(node_features)

        neighbor_count = torch.zeros(
            num_nodes,
            1,
            device=node_features.device,
        )

        if edge_index.numel() > 0:
            source = edge_index[0]
            destination = edge_index[1]

            neighbor_sum.index_add_(
                0,
                destination,
                node_features[source],
            )

            neighbor_count.index_add_(
                0,
                destination,
                torch.ones(
                    destination.size(0),
                    1,
                    device=node_features.device,
                ),
            )

        neighbor_mean = neighbor_sum / neighbor_count.clamp(min=1.0)

        combined = torch.cat(
            [node_features, neighbor_mean],
            dim=1,
        )

        return torch.relu(self.linear(combined))


class GraphSAGE(nn.Module):
    """Small two-layer GraphSAGE network for GUARDIAN-X."""

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 16,
        output_dim: int = 8,
    ):
        super().__init__()

        self.layer1 = GraphSAGELayer(input_dim, hidden_dim)
        self.layer2 = GraphSAGELayer(hidden_dim, output_dim)

    def forward(
        self,
        node_features: torch.Tensor,
        edge_index: torch.Tensor,
    ) -> torch.Tensor:

        x = self.layer1(node_features, edge_index)
        x = self.layer2(x, edge_index)

        return x


class RiskClassifier(nn.Module):
    """Convert GraphSAGE node embeddings into a risk score."""

    def __init__(self, input_dim: int = 8):
        super().__init__()

        self.classifier = nn.Sequential(
            nn.Linear(input_dim, 1),
            nn.Sigmoid(),
        )

    def forward(self, embeddings: torch.Tensor) -> torch.Tensor:
        return self.classifier(embeddings).squeeze(-1)