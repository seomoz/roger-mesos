import os
import json
import requests
import re
import logging

logger = logging.getLogger(os.getenv('LOGGER_NAME', __name__))

def get_metrics_snapshot(master_url):
    url = '{}/metrics/snapshot'.format(master_url.rstrip('/'))
    resp = requests.get('{}'.format(url))
    if not resp.status_code // 100 == 2:
        logger.error('Got response {} from {}'.format(resp.status_code, url))
        raise ValueError('Got a non-2xx response ({}) from {}.'.format(resp.status_code, url))
    return resp.json()

def get_tasks_counts(master_url):
    data = get_metrics_snapshot(master_url.rstrip('/'))
    counts = {}
    for t in ['error', 'failed', 'finished', 'killed', 'killing', 'lost', 'running', 'staging', 'starting']:
        counts.update({ t: data['master/tasks_{}'.format(t)] })
    return counts

def get_tasks(master_url):
    tasks = {}
    tasks_count = get_tasks_counts(master_url.rstrip('/'))
    limit = int(sum(tasks_count.values()))
    url = '{}/tasks?limit={}'.format(master_url.rstrip('/'), limit)
    resp = requests.get('{}'.format(url))
    if not resp.status_code // 100 == 2:
        logger.error('Got response {} from {}'.format(resp.status_code, url))
        raise ValueError('Got a non-2xx response ({}) from {}.'.format(resp.status_code), url)
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
