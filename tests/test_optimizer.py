import unittest
from repartition.optimizer import calculate_load_variance, detect_imbalance, rebalance
from storage.node_simulation import StorageNode


class TestOptimizer(unittest.TestCase):
    def setUp(self):
        """Create nodes with known utilizations for testing."""
        self.nodes = [StorageNode(f"N{i}") for i in range(3)]
        # Set up: N0=5 blocks, N1=2 blocks, N2=5 blocks
        for _ in range(5):
            self.nodes[0].store_block(f"h{_}", f"f{_}")
            self.nodes[2].store_block(f"h{_+10}", f"g{_}")
        for _ in range(2):
            self.nodes[1].store_block(f"h{_+20}", f"k{_}")

    def test_calculate_load_variance(self):
        """Test variance calculation."""
        var = calculate_load_variance(self.nodes)
        # Utilizations: [5, 2, 5]; mean = 4; variance = ((5-4)^2 + (2-4)^2 + (5-4)^2) / 3 = 6/3 = 2.0
        self.assertAlmostEqual(var, 2.0, places=5)

    def test_variance_balanced(self):
        """Test variance for balanced nodes."""
        balanced = [StorageNode(f"B{i}") for i in range(3)]
        for node in balanced:
            for j in range(4):
                node.store_block(f"h{j}", f"f{j}")
        var = calculate_load_variance(balanced)
        self.assertEqual(var, 0.0)

    def test_detect_imbalance_true(self):
        """Test imbalance detection when variance exceeds threshold."""
        is_imbalanced = detect_imbalance(self.nodes, threshold=1.0)
        self.assertTrue(is_imbalanced)

    def test_detect_imbalance_false(self):
        """Test imbalance detection when variance is below threshold."""
        is_imbalanced = detect_imbalance(self.nodes, threshold=3.0)
        self.assertFalse(is_imbalanced)

    def test_rebalance_moves_block(self):
        """Test that rebalance moves a block from most to least loaded."""
        before_var = calculate_load_variance(self.nodes)
        moved = rebalance(self.nodes)
        after_var = calculate_load_variance(self.nodes)
        self.assertTrue(moved)
        self.assertLess(after_var, before_var)

    def test_rebalance_no_move_when_balanced(self):
        """Test that rebalance is no-op when already balanced."""
        balanced = [StorageNode(f"B{i}") for i in range(3)]
        for node in balanced:
            for j in range(4):
                node.store_block(f"h{j}", f"f{j}")
        moved = rebalance(balanced)
        self.assertFalse(moved)

    def test_rebalance_empty_nodes(self):
        """Test rebalance with empty node list."""
        empty = []
        moved = rebalance(empty)
        self.assertFalse(moved)


if __name__ == "__main__":
    unittest.main()
