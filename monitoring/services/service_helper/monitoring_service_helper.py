import fnmatch
import hashlib
import os
from abc import ABC

from file_integrity_monitoring.commons.generic_constants import GenericConstants
from file_integrity_monitoring.services.base_service import BaseService
from monitoring.models import BaselineFile


class MonitoringServiceHelper(BaseService, ABC):
    def __init__(self):
        super().__init__()

    def set_status_code(self, *args, **kwargs):
        self.status_code = kwargs.get('status_code')

    def count_files(self, path, exclude_patterns):
        """Count total files in directory"""
        try:
            count = 0
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if not self.should_exclude(os.path.join(root, d), exclude_patterns)]
                for file in files:
                    file_path = os.path.join(root, file)
                    if not self.should_exclude(file_path, exclude_patterns):
                        count += 1
            return count
        except Exception as e:
            print(f"Error counting files: {str(e)}")
            return 0

    def scan_baseline_files_sync(self, baseline, params):
        path = params.get("path")
        algorithm_type = params.get("algorithm_type")
        exclude_patterns = params.get("exclude_patterns", [])

        baseline_files = []

        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if not self.should_exclude(os.path.join(root, d), exclude_patterns)]

            for file in files:
                file_path = os.path.join(root, file)
                if self.should_exclude(file_path, exclude_patterns):
                    continue

                try:
                    stat_info = os.stat(file_path)
                    file_size = stat_info.st_size
                    permissions = stat_info.st_mode
                    uid = stat_info.st_uid
                    gid = stat_info.st_gid
                    inode = stat_info.st_ino
                    hard_links = stat_info.st_nlink
                    mtime = stat_info.st_mtime
                    atime = stat_info.st_atime
                    ctime = stat_info.st_ctime

                    sha256_hash = self.calculate_hash(file_path, "sha256")

                    sha512_hash = None
                    if algorithm_type == "sha512":
                        sha512_hash = self.calculate_hash(file_path, "sha512")

                    baseline_file = BaselineFile(
                        baseline=baseline,
                        file_path=file_path,
                        file_name=os.path.basename(file_path),
                        sha256=sha256_hash,
                        sha512=sha512_hash,
                        file_size=file_size,
                        permissions=permissions,
                        uid=uid,
                        gid=gid,
                        inode=inode,
                        hard_links=hard_links,
                        mtime=mtime,
                        atime=atime,
                        ctime=ctime,
                        metadata={}
                    )
                    baseline_files.append(baseline_file)

                except Exception as e:
                    print(f"Error processing file {file_path}: {str(e)}")
                    continue

        # Bulk insert all files
        if baseline_files:
            BaselineFile.objects.bulk_create(baseline_files, batch_size=1000)

    @staticmethod
    def should_exclude(file_path, exclude_patterns):
        if not exclude_patterns:
            return False

        file_name = os.path.basename(file_path)

        for pattern in exclude_patterns:

            if pattern.startswith("*"):
                if file_name.endswith(pattern[1:]):
                    return True

            elif pattern.endswith("*"):
                if file_name.startswith(pattern[:-1]):
                    return True

            elif pattern == file_name:
                return True

            elif "*" in pattern:
                if fnmatch.fnmatch(file_name, pattern):
                    return True

        return False

    @staticmethod
    def calculate_hash(file_path, algorithm="sha256"):
        print(file_path)
        try:
            if algorithm == "sha512":
                hash_obj = hashlib.sha512()
            else:
                hash_obj = hashlib.sha256()

            with open(file_path, 'rb') as f:
                while chunk := f.read(GenericConstants.CHUNK_SIZE):
                    hash_obj.update(chunk)

            return hash_obj.hexdigest()

        except Exception as e:
            print(f"Error calculating hash for {file_path}: {str(e)}")
            return None