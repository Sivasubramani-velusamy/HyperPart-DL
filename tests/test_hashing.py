import unittest
from deduplication.hashing import generate_hash


class TestGenerateHash(unittest.TestCase):
    def test_sha256_hash(self):
        """Test SHA256 hashing."""
        data = b"hello world"
        h = generate_hash(data, algorithm="sha256")
        # Known SHA256 hash for "hello world"
        self.assertEqual(h, "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9")

    def test_sha1_hash(self):
        """Test SHA1 hashing."""
        data = b"hello world"
        h = generate_hash(data, algorithm="sha1")
        # Known SHA1 hash for "hello world"
        self.assertEqual(h, "2aae6c35c94fcfb415dbe95f408b9ce91ee846ed")

    def test_sha256_default(self):
        """Test that SHA256 is default when algorithm not specified."""
        data = b"test"
        h1 = generate_hash(data)
        h2 = generate_hash(data, algorithm="sha256")
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)  # SHA256 hex is 64 chars

    def test_different_inputs_different_hashes(self):
        """Test that different inputs produce different hashes."""
        h1 = generate_hash(b"Alice")
        h2 = generate_hash(b"Bob")
        self.assertNotEqual(h1, h2)

    def test_identical_inputs_same_hash(self):
        """Test that identical inputs produce identical hashes (deterministic)."""
        data = b"consistent data"
        h1 = generate_hash(data)
        h2 = generate_hash(data)
        self.assertEqual(h1, h2)


if __name__ == "__main__":
    unittest.main()
