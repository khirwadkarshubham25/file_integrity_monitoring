from abc import ABC, abstractmethod

from file_integrity_monitoring.services.base_service import BaseService


class MonitoringServiceHelper(BaseService, ABC):
    def __init__(self):
        super().__init__()

    def set_status_code(self, *args, **kwargs):
        self.status_code = kwargs.get('status_code')
