import subprocess
import unittest


class TestPreCommitNormalization(unittest.TestCase):
    def test_normalization(self):
        """ We test if the code was properly formatted with pre-commit. """
        pre_commit_command = ["pre-commit", "run", "--all-files"]
        try:
            subprocess.check_call(pre_commit_command)
        except subprocess.CalledProcessError:
            msg = (
                "You did not apply pre-commit hook to your code, or you did not fix all the problems. "
                "We launched pre-commit during tests but there might still be some warnings or errors"
                "to silence with pragma."
            )
            self.fail(msg)
        self.assertTrue(True)
