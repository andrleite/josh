# _*_ coding: utf-8 _*_

"""This module contains the scheduler class to create scheduled jobs."""

#  pylint: disable=too-few-public-methods

import os
import sys
import re
from model import DynamoDB
from response import HttpResponse
from infrastructure import InfraStructure

print('Loading function')

IMAGE_ID = os.environ['AMI_ID']

pattern1 = re.compile("/schedulers.+")
pattern2 = re.compile("/schedulers/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")

def lambda_handler(event, context):
    DATABASE = DynamoDB(event['body'])

    if event['path'] == '/schedulers' or bool(pattern2.match(event['path'])) == True:
        pass
    else:
        resp = HttpResponse(404, "Not Found resource: %s" % event['path'])
        response = resp.response()
        return response
        sys.exit(1)

    if event['httpMethod'] == 'POST':
        item = DATABASE.create_item()
        INFRA = InfraStructure(event['body'], image_id=IMAGE_ID, job_id=item['job_id'])
        launch_configuration = INFRA.create_launch_configuration()
        auto_scaling = INFRA.create_auto_scaling_group()
        scheduler = INFRA.put_scheduled()

        if launch_configuration and auto_scaling and scheduler and item['statusCode'] == 200:
            resp = HttpResponse(201, "created Job successfully")
            response = resp.response()
            return response
        elif launch_configuration != 200:
            return launch_configuration
        elif auto_scaling != 200:
            return auto_scaling
        elif scheduler != 200:
            return scheduler
        else:
            return item

    elif event['httpMethod'] == 'GET' and event['path'] == '/schedulers':
        return DATABASE.get_items()

    elif event['httpMethod'] == 'GET' and bool(pattern2.match(event['path'])) == True:
        return DATABASE.get_item(event['path'].split("/")[2])


    elif event['httpMethod'] == 'PUT' and bool(pattern2.match(event['path'])) == True:
        if 'status' in event['body']:
            return DATABASE.update_status(event['path'].split("/")[2], event['body']['status'])

        elif 'start_time' in event['body']:
            job_name = DATABASE.get_name(event['path'].split("/")[2])
            start_time = event['body']['start_time']
            payload = {"name": job_name, "start_time": start_time}
            update_scheduler = InfraStructure(payload)
            return update_scheduler.put_scheduled()

        else:
            resp = HttpResponse(400, "Nothing to update. Pass status or start_time on body.")
            response = resp.response()
            return response
            sys.exit(1)

    elif event['httpMethod'] == 'DELETE' and bool(pattern2.match(event['path'])) == True:
        job_name = DATABASE.get_name(event['path'].split("/")[2])
        payload = {"name": job_name}
        delete_job = InfraStructure(payload)
        try:
            delete_job.delete_auto_scaling_group()
        except Exception as err:
            return err
        else:
            try:
                delete_job.delete_launch_configuration()
                resp = HttpResponse(204, "Deleted Successfuly Job {0}".format(job_name))
                response = resp.response()
                return response
            except Exception as err:
                return err

    else:
        resp = HttpResponse(400, "Not Implemented any method for path {0} and method {1}.".format(event['path'], event['httpMethod']))
        response = resp.response()
        return response 
        sys.exit(1)