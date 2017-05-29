# _*_ coding: utf-8 _*_

"""This module provide a pythonic interface for Amazon's DynamoDB"""

import json
from datetime import datetime
import boto3
from .generate_uid import GenerateUID
from .response import HttpResponse
from pynamodb.connection import Connection
from pynamodb.models import Model
from pynamodb.attributes import ( UnicodeAttribute, NumberAttribute, UnicodeSetAttribute, UTCDateTimeAttribute, JSONAttribute )
from pynamodb.exceptions import PutError
from botocore.exceptions import ClientError

client = boto3.client('dynamodb')

class SchedulerModel(Model):
    """
    A Dynamodb scheduler
    """

    class Meta:
        table_name = "scheduler"
        region = "us-west-2"

    job_id = UnicodeAttribute(hash_key=True)
    created_at = UTCDateTimeAttribute(null=None)
    name = UnicodeAttribute()
    docker_image = UnicodeAttribute()
    instance_type = UnicodeAttribute()
    spot_price = UnicodeAttribute()
    status = UnicodeAttribute()
    env_vars = UnicodeAttribute()
    start_time = UnicodeAttribute()
    docker_command = UnicodeAttribute()
    callback_uri = UnicodeAttribute()
    s3_url = UnicodeAttribute()


class DynamoDB(object):
    def __init__(self, payload=None):
        self.payload = payload

    def create_item(self):
        job_id = GenerateUID.get_uuid()
        job_item = SchedulerModel(
            job_id,
            name=self.payload['name'],
            docker_image=self.payload['docker_image'],
            instance_type=self.payload['instance_type'],
            spot_price=self.payload['spot_price'],
            status="scheduled",
            env_vars=str(self.payload['env_vars']),
            start_time=self.payload['start_time'],
            created_at=datetime.now(),
            docker_command=self.payload['docker_command'],
            callback_uri=self.payload['callback_uri'],
            s3_url=self.payload['s3_url']
        )
        try:
            job_item.save()
            return {"statusCode": 200, "job_id": job_id}
        except PutError as err:
            resp = HttpResponse(400, err.msg)
            response = resp.response()
            return response        

    def get_name(self, job_id):
        item = SchedulerModel.get(job_id)
        return item.name

    def get_items(self):
        try:
            items = client.scan(TableName='scheduler')
            resp = HttpResponse(200, json.dumps(items['Items']))
            response = resp.response()
            return response
        except ClientError as err:
            resp = HttpResponse(err.response['ResponseMetadata'] \
            ['HTTPStatusCode'], err.response['Error']['Message'])
            response = resp.response()
            return response
    
    def get_item(self, job_id):
        try:
            item = client.get_item(Key={'job_id': {'S': job_id}}, TableName='scheduler')
            if 'Item' in item:
                resp = HttpResponse(200, json.dumps(item['Item']))
                response = resp.response()
                return response
            else:
                resp = HttpResponse(404, 'Job ID not found')
                response = resp.response()
                return response
        except ClientError as err:
            resp = HttpResponse(err.response['ResponseMetadata'] \
            ['HTTPStatusCode'], err.response['Error']['Message'])
            response = resp.response()
            return response
    
    def update_status(self, job_id, status):
        try:
            update = client.update_item(ExpressionAttributeNames={'#ST': 'status'}, ExpressionAttributeValues={':s': {'S': status}}, \
            Key={'job_id': {'S': job_id}}, ReturnValues='ALL_NEW', TableName='scheduler', UpdateExpression='SET #ST = :s')
            resp = HttpResponse(204, json.dumps('update status successfully'))
            response = resp.response()
            return response
        except ClientError as err:
            resp = HttpResponse(err.response['ResponseMetadata'] \
            ['HTTPStatusCode'], err.response['Error']['Message'])
            response = resp.response()
            return response
