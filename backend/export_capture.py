"""Export a labeled five-minute graph snapshot as one JSONL training session."""
import argparse
import json
from pathlib import Path

from app.services.graph_service import device_graph_service

parser = argparse.ArgumentParser()
parser.add_argument('--label', choices=['normal', 'suspicious'], required=True)
parser.add_argument('--suspicious-device', help='Required for a suspicious session; other nodes remain labeled normal')
parser.add_argument('--session', required=True, help='Unique ID for this capture session')
parser.add_argument('--output', type=Path, default=Path('captures.jsonl'))
args = parser.parse_args()
graph = device_graph_service.build_graph()
if not graph.nodes:
    parser.error('No registered devices with recent observations; capture traffic first')
if args.label == 'suspicious' and args.suspicious_device not in {n.device_id for n in graph.nodes}:
    parser.error('--suspicious-device must name an observed registered device')
record = {
    'session': args.session,
    'nodes': [{'device_id': node.device_id, 'features': node.features,
               'label': int(args.label == 'suspicious' and node.device_id == args.suspicious_device)}
              for node in graph.nodes],
    'edges': [[edge.source_device_id, edge.destination_device_id] for edge in graph.edges],
}
with args.output.open('a', encoding='utf-8') as output:
    output.write(json.dumps(record) + '\n')
print(f'Appended {len(graph.nodes)} labeled nodes for {args.session} to {args.output}')
