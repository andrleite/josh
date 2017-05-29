# _*_ coding: utf-8 _*_

"""This module provide a Http responses"""

import simplejson as json

class HttpResponse(object):
    def __init__(self, http_status_code=None, message=None):
        self.http_status_code = http_status_code
        self.message = message

    def response(self):
        resp = {"isBase64Encoded": False, "statusCode": self.http_status_code, "headers": {"Content-Type": "application/json"},}
        resp_body = json.dumps({"message": self.message})
        resp.update({"body": resp_body})
        return resp