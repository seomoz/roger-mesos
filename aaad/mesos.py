import os
import json
import requests
import re

def get_metrics_snapshot(master_url):
    url = '{}/metrics/snapshot'.format(master_url)
    resp = requests.get('{}'.format(url))
    return resp.json()

def get_tasks_counts(master_url):
    data = get_metrics_snapshot(master_url)
    counts = {}
    for t in ['error', 'failed', 'finished', 'killed', 'killing', 'lost', 'running', 'staging', 'starting']:
        counts.update({ t: data['master/tasks_{}'.format(t)] })
    return counts

def get_tasks(master_url):
    print("In get tasks")
    tasks = {}
    limit = int(sum(get_tasks_counts(master_url).values()))
    url = '{}/tasks?limit={}'.format(master_url, limit)
    print("Url:{}".format(url))
    resp = requests.get('{}'.format(url))
    print("Resp:{}".format(resp))
    data = resp.json()
    for task in data['tasks']:
        if task['state'] in ['TASK_RUNNING', 'TASK_STAGING', 'TASK_STARTING']:
            tasks[task['name']] = { 'cpus': task['resources']['cpus'], 'mem': task['resources']['mem'], 'disk': task['resources']['disk'] }
    return tasks

def get_resources(master_url):
    data = get_metrics_snapshot(master_url)
    resources = {}
    for res in ['cpus', 'mem', 'disk']:
        resources['allocated_' + res] = data['master/{}_used'.format(res)]
        resources['total_' + res] = data['master/{}_total'.format(res)]
    return resources
