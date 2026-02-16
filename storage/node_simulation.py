from typing import List, Tuple


class StorageNode:
    def __init__(self, node_id: str) -> None:
        self.node_id: str = node_id
        self.data_blocks: List[Tuple[str, str]] = []  # list of (hash, label)

    def store_block(self, block_hash: str, label: str) -> None:
        self.data_blocks.append((block_hash, label))

    def remove_block(self) -> Tuple[str, str] | None:
        if not self.data_blocks:
            return None
        return self.data_blocks.pop()

    def get_utilization(self) -> int:
        return len(self.data_blocks)

    def get_labels(self) -> List[str]:
        return [label for (_h, label) in self.data_blocks]

    def display_blocks(self) -> None:
        print(f"Node {self.node_id} blocks ({len(self.data_blocks)}):")
        for h, label in self.data_blocks:
            print(f"  - {label} ({h[:8]})")

