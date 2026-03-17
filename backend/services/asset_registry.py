from __future__ import annotations

from typing import Dict, List
import uuid


class AssetRegistry:
    """
    In-memory registry to track asset versions.
    """

    def __init__(self) -> None:
        self._store: Dict[str, List[Dict[str, object]]] = {}

    def create_asset(self, asset_data: Dict[str, object]) -> str:
        asset_id = str(uuid.uuid4())
        self._store[asset_id] = [dict(asset_data)]
        return asset_id

    def add_version(self, asset_id: str, asset_data: Dict[str, object]) -> None:
        if asset_id not in self._store:
            self._store[asset_id] = []
        self._store[asset_id].append(dict(asset_data))

    def get_asset(self, asset_id: str) -> List[Dict[str, object]]:
        return list(self._store.get(asset_id, []))
