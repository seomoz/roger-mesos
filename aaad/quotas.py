import os
import yaml
import logging
import mesos
import re

logger = logging.getLogger(os.getenv('LOGGER_NAME', __name__))

quota_file = os.getenv('QUOTA_FILE', '')
master_url = os.getenv('MESOS_MASTER_URL', 'http://localhost:5050')

class Quotas:
    class __Quotas:
        def __init__(self, filename):
            self.filename = filename
            self.quota_data = None
            if filename:
                with open(filename, 'r') as data_file:
                    self.quota_data = yaml.load(data_file)

        def is_quota_enabled(self):
            if self.quota_data:
                return True
            return False

        def get_buckets(self):
            ''' Returns all bucket details as a list of buckets '''
            if not self.quota_data:
                return None
            return self.quota_data['buckets']

        def get_bucket_for_task_name(self, name):
            ''' Returns the bucket for the task name '''
            bucket = None
            names = self.quota_data['names']
            for item in names:
                item_name = item.keys()[0]
                prog = re.compile("^{}$".format(item_name))
                if prog.match(name):
                    bucket = item[item_name]
                    return bucket
            return bucket

        def get_quota_for_bucket(self, bucket_name):
            ''' Returns bucket details for the given bucket_name '''
            if not self.quota_data:
                return None
            return self.quota_data['buckets'].get(bucket_name)

        def get_task_allocation(self, bucket_name):
            ''' Computes and returns total allocation across all tasks using the bucket '''
            if not self.quota_data['buckets'].get(bucket_name):
                return None
            allocation = { 'resources': {'cpus': 0.0, 'mem': 0.0, 'disk': 0.0 } }
            if bucket_name:
                allowed_names = []
                for item in self.quota_data['names']:
                    if item.values()[0] == bucket_name:
                        allowed_names.append(item.keys()[0])

            try:
                tasks = mesos.get_tasks(master_url)
            except (Exception) as e:
                logger.exception("Exception while trying to get tasks using master url: {}".format(master_url))

            total_allocated_cpu, total_allocated_mem, total_allocated_disk = (0.0,)*3
            for task in tasks.keys():
                for allowed_name in allowed_names:
                    pattern = re.compile(".*\.{}.*".format(allowed_name))
                    if pattern.match(task):
                        total_allocated_cpu += float(tasks[task]['cpus'])
                        total_allocated_mem += float(tasks[task]['mem'])
                        total_allocated_disk += float(tasks[task]['disk'])

            allocation['resources']['cpus'] = total_allocated_cpu
            allocation['resources']['mem'] = total_allocated_mem
            allocation['resources']['disk'] = total_allocated_disk

            return allocation

    instance = None
    def __init__(self):
        if not Quotas.instance:
            Quotas.instance = Quotas.__Quotas(quota_file)
