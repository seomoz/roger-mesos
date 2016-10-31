
import os
import yaml
import logging
import re

import mesos
import utils

logger = logging.getLogger(os.getenv('LOGGER_NAME', __name__))

quota_files = os.getenv('QUOTA_FILES', '')
master_url = os.getenv('MESOS_MASTER_URL', 'http://localhost:5050')

class Quotas:
    class __Quotas:
        '''Takes a commas separated list of yaml file paths in the QUOTA_FILES environment variable.
        '''
        def __init__(self, filenames_spec):
            self.quota_data = None
            self.REGEX_PATTERN = "^{}$"
            self.quota_data = self._parse_quota_files(filenames_spec)

        def _parse_quota_files(self, filenames_spec):
            self.quota_data = {}
            filenames = filenames_spec.split(',')
            for item in filenames:
                filename = item.strip()
                if filename:
                    with open(filename, 'r') as data_file:
                        self.quota_data = utils.merge_dicts(self.quota_data, yaml.load(data_file))
            return self.quota_data

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
                prog = re.compile(self.REGEX_PATTERN.format(key))
                if prog.match(name):
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
                        allowed_names.add(name.replace("/","_"))

            tasks = None
            try:
                tasks = mesos.get_task_ids_and_resources(master_url)
            except (Exception) as e:
                logger.exception("Exception while trying to get tasks using master url: {}".format(master_url))
                raise

            total_allocated_cpu, total_allocated_mem, total_allocated_disk = (0.0,)*3
            for task in tasks.keys():
                for allowed_name in allowed_names:
                    pattern = re.compile(self.REGEX_PATTERN.format(allowed_name))
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
            Quotas.instance = Quotas.__Quotas(quota_files)
