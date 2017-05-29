# Josh
[![Build Status](https://travis-ci.org/andrleite/josh.svg?branch=master)](https://travis-ci.org/andrleite/josh)
[![Coverage Status](https://coveralls.io/repos/github/andrleite/josh/badge.svg?branch=master)](https://coveralls.io/github/andrleite/josh?branch=master)

### Ad-hoc Jobs Scheduler
Josh is a software which schedule container based jobs to run in AWS spot instances.
---
* Base Infrastructure:
    * API GATEWAY
    * AWS LAMBDA
    * LAUNCH CONFIGURATION/AUTO SCALING GROUP
    * DYNAMODB
    * COREOS
    * TERRAFORM
    * SPOT INSTANCE
    
**To run**:

install terraform:
https://www.terraform.io/downloads.html

```bash
export AWS_ACCESS_KEY_ID="ACCESS_KEY_ID"
export AWS_SECRET_ACCESS="SECRET_ACCESS_KEY"
export AWS_DEFAULT_REGION="us-west-2"
```

**Run terraform**:
Need aws account id
```bash
terraform plan -var accountId=xxxxxx -var bucket_name=mybucket
terraform apply -var accountId=xxxxxx
```
terraform will output **api_url**

api_url: endpoint to create job scheduler. 
e.g: https://flm7nplru8.execute-api.us-west-2.amazonaws.com/prod/schedulers

#### create new JOB (POST, 201)

**start_time** (ISO-8601/UTC)
s3_url: Object url to download callback script in job isntance. Format: https://s3-region.amazonaws.com/bucket_name/docker_listen.py
eg: https://s3-us-west-2.amazonaws.com/s3-josh-bucket1/docker_listen.py

e.g: 
```bash
curl -H "Content-Type: application/json" -X POST -d \
'{"name": "JOBNAME", "docker_image": "alpine", "instance_type": "m3.medium", \
"spot_price": "0.5", "env_vars": {"DB_HOST": "10.0.0.0", "JOB_TIMEOT": "10"}, \
"start_time": "2017-05-30T19:50:00Z", "docker_command": "sleep 300", "callback_url": \ "https://flm7nplru8.execute-api.us-west-2.amazonaws.com/prod/schedulers", \
"s3_url": "https://s3-us-west-2.amazonaws.com/s3-josh-bucket1/docker_listen.py"}'
https://flm7nplru8.execute-api.us-west-2.amazonaws.com/prod/schedulers
```
#### List Jobs (GET, 200)
```bash
curl -H "Content-Type: application/json" -X GET https://flm7nplru8.execute-api.us-west-2.amazonaws.com/prod/schedulers
```

#### List JOB (GET, 200)
```bash
curl -H "Content-Type: application/json" -X GET https://flm7nplru8.execute-api.us-west-2.amazonaws.com/prod/schedulers/99eda6ba-441f-11e7-a73a-b8e85638171c
```
#### Update start_time (PUT, 204)
```bash
curl -H "Content-Type: application/json"-X PUT -d '{"start_time": "2017-05-30T20:50:00Z"}' https://flm7nplru8.execute-api.us-west-2.amazonaws.com/prod/schedulers/99eda6ba-441f-11e7-a73a-b8e85638171c
```
#### Update status (PUT, 204)
```bash
curl -H "Content-Type: application/json"-X PUT -d '{"status": "done"}' https://flm7nplru8.execute-api.us-west-2.amazonaws.com/prod/schedulers/99eda6ba-441f-11e7-a73a-b8e85638171c
```
#### Delete job (DELETE, 204)
```bash
curl -H "Content-Type: application/json"-X DELETE https://flm7nplru8.execute-api.us-west-2.amazonaws.com/prod/schedulers/99eda6ba-441f-11e7-a73a-b8e85638171c
```
