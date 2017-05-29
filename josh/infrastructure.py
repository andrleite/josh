# _*_ coding: utf-8 _*_

"""This module provide a auto scaling group and launch configuration"""

import boto3
from botocore.exceptions import ClientError
from response import HttpResponse

# __ami_id__ = 'ami-a8b320c8'
__keypair__ = 'josh1'
__client__ = boto3.client('autoscaling')
__ec2__ = boto3.client('ec2')
__zones__ = __ec2__.describe_availability_zones()
__az_list__ = [zone['ZoneName'] for zone in __zones__['AvailabilityZones']]

class InfraStructure(object):
    def __init__(self, payload=None, image_id=None, job_id=None):
        self.payload = payload
        self.image_id = image_id
        self.job_id = job_id

    def generate_userdata(self):
        data = self.payload['env_vars']

        userdata = """#!/bin/bash
        echo JOB_NAME="{0}" >> /etc/environment
        echo JOB_ID="{1}" >> /etc/environment
        echo CALLBACK_URI={2} >> /etc/environment
        """.format(self.payload['name'], self.job_id, self.payload['callback_uri'])

        for key, value in data.items():
            userdata = userdata + \
                'echo {0}="{1}" >> /etc/environment\n'.format(key, value)

        userdata = userdata + \
            'docker run -d {0} {1}'.format(self.payload['docker_image'], self.payload['docker_command'])
        userdata = userdata + \
            'wget {0}'.format(self.payload['s3_url'])
        return userdata

    def create_launch_configuration(self):
        try:
            create_lc = __client__.create_launch_configuration(
                LaunchConfigurationName=self.payload['name'],
                ImageId=self.image_id,
                KeyName=__keypair__,
                InstanceType=self.payload['instance_type'],
                InstanceMonitoring={
                    'Enabled': True
                },
                UserData=self.generate_userdata(),
                SpotPrice=self.payload['spot_price']
            )
            return create_lc['ResponseMetadata']['HTTPStatusCode']
        except ClientError as err:
            resp = HttpResponse(err.response['ResponseMetadata'] \
            ['HTTPStatusCode'], err.response['Error']['Message'])
            response = resp.response()
            return response

    def create_auto_scaling_group(self):
        try:
            asg = __client__.create_auto_scaling_group(
                AutoScalingGroupName=self.payload['name'],
                LaunchConfigurationName=self.payload['name'],
                MinSize=0,
                MaxSize=0,
                DesiredCapacity=0,
                DefaultCooldown=300,
                AvailabilityZones=__az_list__,
                Tags=[{
                    'Key': 'Name',
                    'Value': self.payload['name'],
                    'PropagateAtLaunch': True
                }]
            )
            return asg['ResponseMetadata']['HTTPStatusCode']
        except ClientError as err:
            resp = HttpResponse(err.response['ResponseMetadata'] \
            ['HTTPStatusCode'], err.response['Error']['Message'])
            response = resp.response()
            return response

    def put_scheduled(self):
        schedule_name = self.payload['name'] + '-scheduler'
        try:
            asg_sch = __client__.put_scheduled_update_group_action(
                AutoScalingGroupName=self.payload['name'],
                DesiredCapacity=1,
                # StartTime=datetime(2017, 5, 23, 2, 35, 0, tzinfo=pytz.utc) \
                # .strftime('%Y-%m-%d %H:%M:%S %Z'),
                StartTime=self.payload['start_time'],
                MaxSize=1,
                MinSize=1,
                ScheduledActionName=schedule_name,
            )
            return HttpResponse(asg_sch['ResponseMetadata']['HTTPStatusCode'], \
            'Update Job Scheduler Successfuly').response()
        except ClientError as err:
            resp = HttpResponse(err.response['ResponseMetadata'] \
            ['HTTPStatusCode'], err.response['Error']['Message'])
            response = resp.response()
            return response
            #print(e.response['ResponseMetadata']['HTTPStatusCode'], e.response['Error']['Message'])

    def delete_auto_scaling_group(self):
        try:
            del_asg = __client__.delete_auto_scaling_group(
                AutoScalingGroupName=self.payload['name'],
                ForceDelete=True
            )
            return del_asg['ResponseMetadata']['HTTPStatusCode']
        except ClientError as err:
            resp = HttpResponse(err.response['ResponseMetadata'] \
            ['HTTPStatusCode'], err.response['Error']['Message'])
            response = resp.response()
            return response

    def delete_launch_configuration(self):
        try:
            del_lc = __client__.delete_launch_configuration(
                LaunchConfigurationName=self.payload['name'],
            )
            return del_lc['ResponseMetadata']['HTTPStatusCode']
        except ClientError as err:
            resp = HttpResponse(err.response['ResponseMetadata'] \
            ['HTTPStatusCode'], err.response['Error']['Message'])
            response = resp.response()
            return response

# asg = InfraStructure(name='test',image_id='ami-a8b320c8', instance_type='m3.medium',
#     spot_price='0.5', start_time='2017-05-28T17:25:00Z', env_vars='{"DB_HOST": "db.host"}',
#     docker_image='alpine', job_id='4444-4444-4444-4444')
# try:
#    # launch_configuration = asg.create_launch_configuration()
#    # auto_scaling = asg.create_auto_scaling_group()
#     scheduler = asg.put_scheduled()
#    # print(launch_configuration)
#    # print(auto_scaling)
#     print(scheduler)
# except Exception as err:
#     print(err.args)

# try:
#    del_asg = asg.delete_auto_scaling_group()
#    del_lc = asg.delete_launch_configuration()
#    print(del_asg)
#    print(del_lc)
# except Exception as e: print(e)
