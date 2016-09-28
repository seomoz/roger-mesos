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
            names_to_buckets = self.quota_data['names']
            for key, bucket in names_to_buckets.iteritems():
                prog = re.compile("^{}$".format(name))
                if prog.match(key):
                    return bucket
            return None

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
                allowed_names = set()
                for name, bucket in self.quota_data['names'].iteritems():
                    if bucket == bucket_name:
                        allowed_names.add(name)

            tasks = None
            try:
                tasks = mesos.get_tasks(master_url)
            except (Exception) as e:
                logger.exception("Exception while trying to get tasks using master url: {}".format(master_url))
                raise

            total_allocated_cpu, total_allocated_mem, total_allocated_disk = (0.0,)*3
            for task in tasks.keys():
                for allowed_name in allowed_names:
                    pattern = re.compile(".*\.{}.*".format(allowed_name))
                    if pattern.match(task):
                        total_allocated_cpu += float(tasks[task]['cpus'])
                        total_allocated_mem += float(tasks[task]['mem'])
                        total_allocated_disk += float(tasks[task]['disk'])
                        break

            allocation['resources']['cpus'] = total_allocated_cpu
            allocation['resources']['mem'] = total_allocated_mem
            allocation['resources']['disk'] = total_allocated_disk

            return allocation

        def get_buckets_for_names(self, names):
            ''' Returns the list of buckets that the names have access to '''
            quota_name_buckets = self.quota_data['names']
            intersection = set(quota_name_buckets).intersection(names)
            buckets = set()
            for name_keys in intersection:
                buckets.add(quota_name_buckets[name_keys])
            return list(buckets)

    instance = None
    def __init__(self):
        if not Quotas.instance:
            Quotas.instance = Quotas.__Quotas(quota_file)
