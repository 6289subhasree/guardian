import torch
from pathlib import Path

from app.ml.graphsage import GraphSAGE, RiskClassifier
from app.models.network_features import NetworkFeatures


class DetectionResult:
    """Result produced by the GUARDIAN-X ML detection service."""

    def __init__(
        self,
        device_id: str,
        risk_score: float,
        status: str,
    ):
        self.device_id = device_id
        self.risk_score = risk_score
        self.status = status

    def __repr__(self):
        return (
            f"DetectionResult("
            f"device_id='{self.device_id}', "
            f"risk_score={self.risk_score:.4f}, "
            f"status='{self.status}'"
            f")"
        )


class DetectionService:
    """Run GUARDIAN-X ML inference on network features."""

    def __init__(
        self,
        model_path: str | Path | None = None,
    ):
        self.model_path = Path(model_path) if model_path else Path(__file__).with_name("guardian_model.pt")

        checkpoint = torch.load(
            self.model_path,
            map_location="cpu",
        )

        self.feature_min = checkpoint["feature_min"]
        self.feature_max = checkpoint["feature_max"]

        self.graphsage = GraphSAGE(
            input_dim=6,
            hidden_dim=16,
            output_dim=8,
        )

        self.classifier = RiskClassifier(
            input_dim=8,
        )

        self.graphsage.load_state_dict(
            checkpoint["graphsage"]
        )

        self.classifier.load_state_dict(
            checkpoint["classifier"]
        )

        self.graphsage.eval()
        self.classifier.eval()

    def _normalize_features(
        self,
        features: torch.Tensor,
    ) -> torch.Tensor:
        """Normalize features using the training values."""

        feature_range = self.feature_max - self.feature_min

        feature_range = torch.where(
            feature_range == 0,
            torch.ones_like(feature_range),
            feature_range,
        )

        return (
            features - self.feature_min
        ) / feature_range

    def _build_graph_features(
        self,
        network_features: NetworkFeatures,
    ) -> torch.Tensor:
        """Convert NetworkFeatures into the trained feature vector."""

        return torch.tensor(
            [
                network_features.packet_count,
                network_features.total_bytes,
                network_features.average_packet_size,
                network_features.tcp_count,
                network_features.udp_count,
                network_features.connection_count,
            ],
            dtype=torch.float32,
        ).unsqueeze(0)

    def detect(
        self,
        network_features: NetworkFeatures,
    ) -> DetectionResult:
        """Run GraphSAGE inference and return a risk result."""

        features = self._build_graph_features(
            network_features
        )

        features = self._normalize_features(
            features
        )

        edge_index = torch.empty(
            (2, 0),
            dtype=torch.long,
        )

        with torch.no_grad():
            embeddings = self.graphsage(
                features,
                edge_index,
            )

            risk_score = self.classifier(
                embeddings
            ).item()

        status = (
            "SUSPICIOUS"
            if risk_score >= 0.5
            else "NORMAL"
        )

        return DetectionResult(
            device_id=network_features.device_id,
            risk_score=risk_score,
            status=status,
        )

    def detect_graph(self, network_features: list[NetworkFeatures], edges: list[tuple[str, str]]) -> list[DetectionResult]:
        """Score nodes together, passing observed device-to-device edges to GraphSAGE."""
        if not network_features:
            return []
        indices = {feature.device_id: index for index, feature in enumerate(network_features)}
        features = self._normalize_features(torch.cat([
            self._build_graph_features(feature) for feature in network_features
        ]))
        links = [(indices[source], indices[target]) for source, target in edges
                 if source in indices and target in indices]
        # Neighbor aggregation sees both endpoints of an observed communication.
        links += [(target, source) for source, target in links]
        edge_index = (torch.tensor(links, dtype=torch.long).T.contiguous()
                      if links else torch.empty((2, 0), dtype=torch.long))
        with torch.no_grad():
            scores = self.classifier(self.graphsage(features, edge_index)).tolist()
        return [DetectionResult(feature.device_id, score,
                                "SUSPICIOUS" if score >= 0.5 else "NORMAL")
                for feature, score in zip(network_features, scores)]
