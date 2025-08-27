import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from rich.console import Console
from rich.tree import Tree

class RecordingGenerator:
    def __init__(self, config):
        self.config = config
        self.output_dir = Path(config.OUTPUT_DIR)
        self.console = Console()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_recording(self, devices: List[Dict], device_type: str, resource_type: str) -> str:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        base = self.output_dir / f'{device_type}_{resource_type}_{ts}'
        self._create_structure(base, devices, resource_type)
        (base / 'metadata.json').write_text(json.dumps(self._metadata(devices, device_type, resource_type), indent=2))
        (base / 'index.json').write_text(json.dumps(self._index(devices, resource_type), indent=2))
        self.console.print(f'[green]✓[/green] Recording generated: {base}')
        self._show_tree(base)
        return str(base)

    def _create_structure(self, base: Path, devices: List[Dict], resource_type: str):
        rf = base / 'redfish' / 'v1'
        rf.mkdir(parents=True, exist_ok=True)

        if resource_type == 'StorageController':
            col = rf / 'Storage' / '1' / 'Controllers'
        elif resource_type == 'Drive':
            col = rf / 'Storage' / '1' / 'Drives'
        elif resource_type == 'Volume':
            col = rf / 'Storage' / '1' / 'Volumes'
        elif resource_type == 'Chassis':
            col = rf / 'Chassis'
        elif resource_type == 'StoragePool':
            # Store StoragePools under the Storage service for consistency with other resources
            col = rf / 'Storage' / '1' / 'StoragePools'
        else:
            col = rf / resource_type
        col.mkdir(parents=True, exist_ok=True)

        collection = {
            '@odata.type': f'#{resource_type}Collection.{resource_type}Collection',
            '@odata.id': f'/redfish/v1/{col.relative_to(rf)}',
            'Name': f'{resource_type} Collection',
            'Members@odata.count': len(devices),
            'Members': []
        }

        for i, d in enumerate(devices, 1):
            dp = col / str(i)
            dp.mkdir(exist_ok=True)
            d['@odata.id'] = f'/redfish/v1/{dp.relative_to(rf)}'
            (dp / 'index.json').write_text(json.dumps(d, indent=2))
            collection['Members'].append({'@odata.id': d['@odata.id']})

        (col / 'index.json').write_text(json.dumps(collection, indent=2))

    def _metadata(self, devices: List[Dict], device_type: str, resource_type: str) -> Dict:
        return {
            'recording_info': {
                'timestamp': datetime.now().isoformat(),
                'device_type': device_type,
                'resource_type': resource_type,
                'device_count': len(devices),
                'generator_version': '1.0.0',
                'schema_version': '2023.2'
            },
            'statistics': {
                'total_devices': len(devices),
                'healthy_devices': sum(1 for d in devices if d.get('Status', {}).get('Health') == 'OK'),
                'enabled_devices': sum(1 for d in devices if d.get('Status', {}).get('State') == 'Enabled')
            }
        }

    def _index(self, devices: List[Dict], resource_type: str) -> Dict:
        return {
            'resource_type': resource_type,
            'devices': [
                {'id': d.get('Id'), 'name': d.get('Name'), 'odata_id': d.get('@odata.id'), 'status': d.get('Status')}
                for d in devices
            ]
        }

    def _show_tree(self, base: Path):
        tree = Tree(f'[bold cyan]{base.name}[/bold cyan]')
        def walk(node, p: Path, depth=0):
            if depth > 5: return
            for item in sorted(p.iterdir()):
                if item.is_dir():
                    b = node.add(f'[blue]{item.name}/[/blue]'); walk(b, item, depth+1)
                else:
                    node.add(f'[green]{item.name}[/green]')
        walk(tree, base); self.console.print(tree)
