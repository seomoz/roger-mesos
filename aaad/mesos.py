import os
import json
import requests
import re
import logging
import expiringdict

logger = logging.getLogger(os.getenv('LOGGER_NAME', __name__))

from expiringdict import ExpiringDict
cache = ExpiringDict(max_len=os.getenv('MESOS_CACHE_MAX_LEN', 20), max_age_seconds=os.getenv('MESOS_CACHE_EXPIRY_SECONDS', 10))

def get_metrics_snapshot(master_url):
    url = '{}/metrics/snapshot'.format(master_url.rstrip('/'))
    cache_key = 'get_metrics_snapshot' + master_url
    resp_json = cache.get(cache_key)
    if resp_json:
        return resp_json
    resp = requests.get('{}'.format(url))
    if resp.status_code // 100 != 2:
        logger.error('Got response {} from {}'.format(resp.status_code, url))
        Response.raise_for_status()
    resp_json = resp.json()
    cache[cache_key] = resp_json
    return resp_json

def get_tasks_counts(master_url):
    data = get_metrics_snapshot(master_url.rstrip('/'))
    counts = {}
    for t in ['error', 'failed', 'finished', 'killed', 'killing', 'lost', 'running', 'staging', 'starting']:
        counts.update({ t: data.get('master/tasks_{}'.format(t), 0.0) })
    return counts

def get_tasks(master_url):
    tasks_count = get_tasks_counts(master_url.rstrip('/'))
    limit = int(sum(tasks_count.values()))
    url = '{}/tasks?limit={}'.format(master_url.rstrip('/'), limit)
    cache_key = 'get_tasks' + master_url
    tasks = cache.get(cache_key)
    if tasks:
        return tasks
    tasks = {}
    resp = requests.get('{}'.format(url))
    if resp.status_code // 100 != 2:
        logger.error('Got response {} from {}'.format(resp.status_code, url))
        Response.raise_for_status()
    data = resp.json()
    for task in data['tasks']:
        if task['state'] in ['TASK_RUNNING', 'TASK_STAGING', 'TASK_STARTING']:
            tasks[task['name']] = { 'cpus': task['resources']['cpus'], 'mem': task['resources']['mem'], 'disk': task['resources']['disk'] }
    cache[cache_key] = tasks
    return tasks

def get_task_ids_and_resources(master_url):
    tasks_count = get_tasks_counts(master_url.rstrip('/'))
    limit = int(sum(tasks_count.values()))
    url = '{}/tasks?limit={}'.format(master_url.rstrip('/'), limit)
    cache_key = 'get_task_ids_and_resources' + master_url
    tasks = cache.get(cache_key)
    if tasks:
        return tasks
    tasks = {}
    resp = requests.get('{}'.format(url))
    if resp.status_code // 100 != 2:
        logger.error('Got response {} from {}'.format(resp.status_code, url))
        Response.raise_for_status()
    data = resp.json()
    for task in data['tasks']:
        if task['state'] in ['TASK_RUNNING', 'TASK_STAGING', 'TASK_STARTING']:
            tasks[task['id']] = { 'cpus': task['resources']['cpus'], 'mem': task['resources']['mem'], 'disk': task['resources']['disk'] }
    cache[cache_key] = tasks
    return tasks

def get_resources(master_url):
    data = get_metrics_snapshot(master_url)
    resources = {}
    for res in ['cpus', 'mem', 'disk']:
        resources['allocated_' + res] = data['master/{}_used'.format(res)]
        resources['total_' + res] = data['master/{}_total'.format(res)]
    return resources
