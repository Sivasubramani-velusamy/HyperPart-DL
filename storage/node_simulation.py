from typing import List, Tuple, Optional


class StorageNode:
    """Represents a storage node in a distributed system.
    
    Stores file blocks identified by hash and label, supporting replication
    and load balancing operations.
    
    Attributes:
        node_id: Unique identifier for the node.
        data_blocks: List of (hash, label) tuples representing stored files.
    """

    def __init__(self, node_id: str, capacity: Optional[int] = None) -> None:
        """Initialize a storage node.
        
        Args:
            node_id: Unique identifier for this node.
        """
        self.node_id: str = node_id
        self.data_blocks: List[Tuple[str, str]] = []  # list of (hash, label)
        # capacity: max number of blocks this node can store. None => unlimited
        self.capacity: Optional[int] = capacity

    def store_block(self, block_hash: str, label: str) -> bool:
        """Store a file block on this node.
        
        Args:
            block_hash: SHA256 hash of the file content.
            label: Human-readable name/label of the file.
        """
        if self.capacity is not None and len(self.data_blocks) >= self.capacity:
            return False
        self.data_blocks.append((block_hash, label))
        return True

    def remove_block(self) -> Tuple[str, str] | None:
        """Remove and return the last block from storage.
        
        Returns:
            The removed (hash, label) tuple or None if storage is empty.
        """
        if not self.data_blocks:
            return None
        return self.data_blocks.pop()

    def get_utilization(self) -> int:
        """Get the number of blocks stored on this node.
        
        Returns:
            Count of blocks currently stored.
        """
        return len(self.data_blocks)

    def get_capacity(self) -> Optional[int]:
        """Return configured capacity (None means unlimited)."""
        return self.capacity

    def remaining_capacity(self) -> Optional[int]:
        """Return remaining slots (None means unlimited)."""
        if self.capacity is None:
            return None
        return max(0, self.capacity - len(self.data_blocks))

    def get_utilization_ratio(self) -> float:
        """Return utilization as fraction of capacity (0..1). If unlimited, use absolute count."""
        if self.capacity is None or self.capacity == 0:
            # represent as absolute count to preserve ordering
            return float(len(self.data_blocks))
        return len(self.data_blocks) / float(self.capacity)

    def get_labels(self) -> List[str]:
        """Get all file labels stored on this node.
        
        Returns:
            List of file labels (names) currently stored.
        """
        return [label for (_h, label) in self.data_blocks]

    def display_blocks(self) -> None:
        """Print a summary of all blocks stored on this node."""
        print(f"Node {self.node_id} blocks ({len(self.data_blocks)}):")
        for h, label in self.data_blocks:
            print(f"  - {label} ({h[:8]})")

