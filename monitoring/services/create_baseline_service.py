from rest_framework import status
import os
import hashlib
import threading
from pathlib import Path

from monitoring.models import Baseline, BaselineFile
from accounts.models import Users
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper
from file_integrity_monitoring.commons.generic_constants import GenericConstants
from file_integrity_monitoring.commons.commons import Commons


class CreateBaselineService(MonitoringServiceHelper):
    """Service to create a new baseline with file hashing (Approach 3: Hybrid)"""

    # Thresholds for hybrid approach
    SYNC_FILE_THRESHOLD = 5000  # Files < 5000: sync, >= 5000: async
    CHUNK_SIZE = 8192  # For reading files in chunks

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        """Extract and validate baseline creation parameters"""
        data = kwargs.get("data")
        return {
            "name": data.get("name"),
            "description": data.get("description", ""),
            "path": data.get("path"),
            "algorithm_type": data.get("algorithm_type", "sha256"),
            "exclude_patterns": data.get("exclude_patterns", []),
            "monitoring_enabled": data.get("monitoring_enabled", True),
            "user_id": data.get("user_id") or data.get("created_by")
        }

    def get_data(self, *args, **kwargs):
        """Create baseline and optionally scan files"""
        params = self.get_request_params(*args, **kwargs)

        # Validate required fields
        if not params.get("name"):
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": "Baseline name is required"}

        if not params.get("path"):
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": "Path is required"}

        # Check if baseline with same name already exists
        if Baseline.objects.filter(name=params.get("name")).exists():
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": "Baseline with this name already exists"}

        # Validate path exists
        if not os.path.isdir(params.get("path")):
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": f"Path does not exist: {params.get('path')}"}

        # Get user
        try:
            user = Users.objects.get(id=params.get("user_id"))
        except Users.DoesNotExist:
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": "User not found"}

        # Create baseline with "scanning" status
        baseline = Baseline.objects.create(
            name=params.get("name"),
            description=params.get("description"),
            path=params.get("path"),
            algorithm_type=params.get("algorithm_type"),
            exclude_patterns=params.get("exclude_patterns"),
            monitoring_enabled=params.get("monitoring_enabled"),
            user=user,
            status="scanning"
        )

        # Count files to determine approach
        file_count = self._count_files(params.get("path"), params.get("exclude_patterns"))

        # Approach 3: Hybrid
        if file_count < self.SYNC_FILE_THRESHOLD:
            # SYNCHRONOUS: Small directories (< 5000 files)
            try:
                self._scan_baseline_files_sync(baseline, params)
                baseline.status = "ready"
                baseline.save()

                self.set_status_code(status_code=status.HTTP_201_CREATED)
                return {
                    "message": "Baseline created and scanned successfully",
                    "baseline_id": baseline.id,
                    "name": baseline.name,
                    "path": baseline.path,
                    "status": "ready",
                    "file_count": baseline.baseline_files.count(),
                    "scanning": False
                }
            except Exception as e:
                baseline.status = "error"
                baseline.save()
                self.error = True
                self.set_status_code(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return {"message": f"Error scanning baseline: {str(e)}"}
        else:
            # ASYNCHRONOUS: Large directories (>= 5000 files)
            # Queue background task using threading (no Celery needed)
            thread = threading.Thread(
                target=self._scan_baseline_files_async,
                args=(baseline.id, params),
                daemon=True
            )
            thread.start()

            self.set_status_code(status_code=status.HTTP_202_ACCEPTED)
            return {
                "message": "Baseline created. File scanning in progress...",
                "baseline_id": baseline.id,
                "name": baseline.name,
                "path": baseline.path,
                "status": "scanning",
                "file_count": 0,
                "scanning": True,
                "estimated_files": file_count
            }

    def _count_files(self, path, exclude_patterns):
        """Count total files in directory"""
        try:
            count = 0
            for root, dirs, files in os.walk(path):
                print(root, dirs, files)
                # Filter excluded directories
                dirs[:] = [d for d in dirs if not self._should_exclude(os.path.join(root, d), exclude_patterns)]
                # Count non-excluded files
                for file in files:
                    file_path = os.path.join(root, file)
                    if not self._should_exclude(file_path, exclude_patterns):
                        count += 1
            return count
        except Exception as e:
            print(f"Error counting files: {str(e)}")
            return 0

    def _should_exclude(self, file_path, exclude_patterns):
        """Check if file should be excluded based on patterns"""
        if not exclude_patterns:
            return False

        file_name = os.path.basename(file_path)

        for pattern in exclude_patterns:
            # Simple wildcard matching
            if pattern.startswith("*"):
                # *.log matches anything ending with .log
                if file_name.endswith(pattern[1:]):
                    return True
            elif pattern.endswith("*"):
                # .git* matches anything starting with .git
                if file_name.startswith(pattern[:-1]):
                    return True
            elif pattern == file_name:
                # Exact match
                return True
            elif "*" in pattern:
                # Handle patterns like: file*.txt
                import fnmatch
                if fnmatch.fnmatch(file_name, pattern):
                    return True

        return False

    def _scan_baseline_files_sync(self, baseline, params):
        """Synchronously scan directory and store file hashes (< 5000 files)"""
        path = params.get("path")
        algorithm_type = params.get("algorithm_type")
        exclude_patterns = params.get("exclude_patterns", [])

        baseline_files = []

        for root, dirs, files in os.walk(path):
            # Filter excluded directories
            dirs[:] = [d for d in dirs if not self._should_exclude(os.path.join(root, d), exclude_patterns)]

            # Process files
            for file in files:
                file_path = os.path.join(root, file)
                # Skip excluded files
                if self._should_exclude(file_path, exclude_patterns):
                    continue

                try:
                    # Get file metadata
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

                    # Calculate SHA256 hash (always)
                    sha256_hash = self._calculate_hash(file_path, "sha256")

                    # Calculate SHA512 hash if specified
                    sha512_hash = None
                    if algorithm_type == "sha512":
                        sha512_hash = self._calculate_hash(file_path, "sha512")

                    # Create BaselineFile object
                    baseline_file = BaselineFile(
                        baseline=baseline,
                        file_path=file_path,
                        file_name=os.path.basename(file_path),
                        sha256=sha256_hash,
                        sha512=sha512_hash,
                        blake3=None,  # Can add BLAKE3 later if needed
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

    def _scan_baseline_files_async(self, baseline_id, params):
        """Asynchronously scan directory (>= 5000 files) - runs in background thread"""
        try:
            baseline = Baseline.objects.get(id=baseline_id)

            # Perform same scan as sync version
            self._scan_baseline_files_sync(baseline, params)

            # Update status to ready
            baseline.status = "ready"
            baseline.save()

            # Create audit log for completion
            Commons.create_audit_log(
                user_id=params.get("user_id"),
                action="scan_complete",
                resource_type="Baseline",
                resource_id=baseline_id,
                new_values={
                    "status": "ready",
                    "file_count": baseline.baseline_files.count()
                }
            )

        except Exception as e:
            print(f"Error in async scan for baseline {baseline_id}: {str(e)}")
            try:
                baseline = Baseline.objects.get(id=baseline_id)
                baseline.status = "error"
                baseline.save()
            except:
                pass

    def _calculate_hash(self, file_path, algorithm="sha256"):
        """Calculate hash of a file"""
        try:
            if algorithm == "sha256":
                hash_obj = hashlib.sha256()
            elif algorithm == "sha512":
                hash_obj = hashlib.sha512()
            elif algorithm == "md5":
                hash_obj = hashlib.md5()
            elif algorithm == "sha1":
                hash_obj = hashlib.sha1()
            else:
                hash_obj = hashlib.sha256()  # Default

            # Read file in chunks to handle large files
            with open(file_path, 'rb') as f:
                while chunk := f.read(self.CHUNK_SIZE):
                    hash_obj.update(chunk)

            return hash_obj.hexdigest()

        except Exception as e:
            print(f"Error calculating hash for {file_path}: {str(e)}")
            return None

    def _create_audit_log(self, user_id, action, baseline_id, baseline_name, file_count):
        """Create audit log for baseline operations"""
        Commons.create_audit_log(
            user_id=user_id,
            action=action,
            resource_type="Baseline",
            resource_id=baseline_id,
            new_values={
                "name": baseline_name,
                "file_count": file_count
            }
        )