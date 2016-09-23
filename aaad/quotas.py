import os
import yaml
import logging

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
            # TODO - Implementation pending
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
            allocation = { 'resources': {'cpus': 0, 'mem': 0 } }
            # TODO - Implementation pending
            return allocation

    instance = None
    def __init__(self):
        if not Quotas.instance:
            Quotas.instance = Quotas.__Quotas(quota_file)
