import os
import json
import requests
from ahab import Ahab

URI = os.environ('URI')
JOB_ID = os.environ('JOB_ID')
URL = URI + '/' + JOB_ID

def handler(event, data):
	if 'Config' in data and 'Hostname' in data['Config']:
		if event['status'] == 'start':
			update_status()
		elif event['status'] == 'die':
			clean_all()

def update_status():
	payload = {"status": "running"}
    r = requests.put(URL, data=json.dumps(payload))

def clean_all():
	payload = {"status": "done"}
    r = requests.put(URL, data=json.dumps(payload))
    d = requests.delete(URL)

listener = Ahab(handlers=[handler])
listener.listen()