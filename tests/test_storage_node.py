import unittest
from storage.node_simulation import StorageNode


class TestStorageNode(unittest.TestCase):
    def setUp(self):
        """Set up a fresh storage node for each test."""
        self.node = StorageNode("test_node")

    def test_initialization(self):
        """Test that a new node starts empty."""
        self.assertEqual(self.node.node_id, "test_node")
        self.assertEqual(self.node.get_utilization(), 0)
        self.assertEqual(self.node.get_labels(), [])

    def test_store_block(self):
        """Test storing blocks."""
        self.node.store_block("hash123", "file1.txt")
        self.assertEqual(self.node.get_utilization(), 1)
        self.assertIn("file1.txt", self.node.get_labels())

    def test_store_multiple_blocks(self):
        """Test storing multiple blocks."""
        self.node.store_block("hash1", "file1.txt")
        self.node.store_block("hash2", "file2.txt")
        self.node.store_block("hash3", "file3.txt")
        self.assertEqual(self.node.get_utilization(), 3)
        labels = self.node.get_labels()
        self.assertEqual(len(labels), 3)
        self.assertIn("file1.txt", labels)
        self.assertIn("file2.txt", labels)
        self.assertIn("file3.txt", labels)

    def test_remove_block(self):
        """Test removing blocks (LIFO)."""
        self.node.store_block("hash1", "file1.txt")
        self.node.store_block("hash2", "file2.txt")
        removed = self.node.remove_block()
        self.assertEqual(removed, ("hash2", "file2.txt"))
        self.assertEqual(self.node.get_utilization(), 1)

    def test_remove_block_empty(self):
        """Test removing from empty node returns None."""
        removed = self.node.remove_block()
        self.assertIsNone(removed)
        self.assertEqual(self.node.get_utilization(), 0)

    def test_get_labels_duplicates(self):
        """Test that get_labels includes duplicates if same file stored multiple times."""
        self.node.store_block("hash1", "file.txt")
        self.node.store_block("hash1", "file.txt")
        labels = self.node.get_labels()
        self.assertEqual(labels, ["file.txt", "file.txt"])


if __name__ == "__main__":
    unittest.main()
