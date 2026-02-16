import io
import os
import sys
import unittest

from main import main as run_main


class MainIntegrationTest(unittest.TestCase):
    def test_main_runs_and_outputs_expected(self):
        buf = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = buf
            run_main()
        finally:
            sys.stdout = old_stdout

        out = buf.getvalue()
        # Basic expected output strings
        self.assertIn("Deduplication ratio", out)
        self.assertIn("Hypergraph nodes:", out)
        # Check that the plot file was written
        self.assertTrue(os.path.exists("utilization.png"))


if __name__ == "__main__":
    unittest.main()
