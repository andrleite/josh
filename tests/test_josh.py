# _*_ coding: utf-8 _*_

"""This module tests everything about scheduler a job"""

import unittest
from model import DynamoDB

class JoshSchedulerTests(unittest.TestCase):
    """Job Scheduler Test class"""

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.scheduler = DynamoDB

    def test_uid_job_scheduler(self):
        """Generate random ID with uuid"""
        first_id = self.scheduler.get_uuid()
        second_id = self.scheduler.get_uuid()
        self.assertNotEqual(first_id, second_id)

if __name__ == '__main__':
    unittest.main()
