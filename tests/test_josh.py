# _*_ coding: utf-8 _*_

"""This module tests everything about scheduler a job"""

import unittest
from josh.generate_uid import GenerateUID

class JoshSchedulerTests(unittest.TestCase):
    """Job Scheduler Test class"""

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.uid = GenerateUID

    def test_uid_job_scheduler(self):
        """Generate random ID with uuid"""
        first_id = self.uid.get_uuid()
        second_id = self.uid.get_uuid()
        self.assertNotEqual(first_id, second_id)

if __name__ == '__main__':
    unittest.main()
