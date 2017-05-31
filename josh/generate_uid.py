# _*_ coding: utf-8 _*_

"""This module Generates unique uuid"""

import uuid

class GenerateUID:

    def get_uuid():
        """Create unique uuid and return it"""
        return str(uuid.uuid1())