import hashlib
import os
import traceback

from django.utils import timezone
from rest_framework import status

from file_integrity_monitoring.commons.commons import Commons
from monitoring.models import MonitoringSession, Baseline, FileChange, BaselineFile
from monitoring.services.create_alert_service import CreateAlertService
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper


class MonitoringSessionService(MonitoringServiceHelper):
    """Service to orchestrate monitoring session, scan files, compare hashes, and create alerts"""

    # Hash calculation settings
    CHUNK_SIZE = 8192

    # Scan type definitions
    SCAN_TYPES = {
        'full': 'full',  # Scan all files
        'incremental': 'incremental',  # Scan only modified files
        'quick': 'quick'  # Scan only size/timestamp changes
    }

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        """Extract monitoring session parameters"""
        data = kwargs.get("data")
        return {
            "baseline_id": data.get("baseline_id"),
            "monitor_type": data.get("monitor_type", "full"),  # full, incremental, quick
            "description": data.get("description", ""),
            "user_id": data.get("user_id")
        }

    def get_data(self, *args, **kwargs):
        """Execute monitoring session: scan files, compare hashes, create file changes and alerts"""
        params = self.get_request_params(*args, **kwargs)

        # Validate baseline_id
        if not params.get("baseline_id"):
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": "Baseline ID is required"}

        # Get baseline
        try:
            baseline = Baseline.objects.get(id=params.get("baseline_id"))
        except Baseline.DoesNotExist:
            self.error = True
            self.set_status_code(status_code=status.HTTP_404_NOT_FOUND)
            return {"message": "Baseline not found"}

        # Validate baseline has files scanned
        if baseline.baseline_files.count() == 0:
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": "Baseline has no files. Please rescan baseline."}

        # Create monitoring session
        session = MonitoringSession(
            baseline=baseline,
            monitor_type=params.get("monitor_type"),
            description=params.get("description"),
            status='running',
            user_id=params.get("user_id")
        )
        session.save()

        try:
            # Scan directory and compare hashes
            scan_results = self._scan_and_compare(
                baseline,
                params.get("monitor_type"),
                params.get("user_id")
            )

            # Update session statistics
            session.files_scanned = scan_results['files_scanned']
            session.files_changed = scan_results['changes_found']
            session.files_added = scan_results['files_added']
            session.files_deleted = scan_results['files_deleted']
            session.files_modified = scan_results['files_modified']
            session.status = 'completed'
            session.end_time = timezone.now()
            session.save()

            # Create audit log
            Commons.create_audit_log(
                user_id=params.get("user_id"),
                action="create",
                resource_type="MonitoringSession",
                resource_id=session.id,
                new_values={
                    "baseline_id": baseline.id,
                    "monitor_type": params.get("monitor_type"),
                    "files_scanned": session.files_scanned,
                    "files_changed": session.files_changed,
                    "alerts_created": scan_results['alerts_created']
                }
            )

            self.set_status_code(status_code=status.HTTP_201_CREATED)
            return {
                "message": "Monitoring session completed successfully",
                "session_id": session.id,
                "baseline_id": baseline.id,
                "baseline_name": baseline.name,
                "monitor_type": params.get("monitor_type"),
                "status": session.status,
                "files_scanned": session.files_scanned,
                "files_changed": session.files_changed,
                "files_added": session.files_added,
                "files_deleted": session.files_deleted,
                "files_modified": session.files_modified,
                "alerts_created": scan_results['alerts_created'],
                "duration_seconds": int((session.end_time - session.start_time).total_seconds()),
                "errors": scan_results['errors']
            }

        except Exception as e:
            # Handle errors
            session.status = 'failed'
            session.error_message = str(e)
            session.end_time = timezone.now()
            session.save()

            self.error = True
            self.set_status_code(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return {
                "message": f"Monitoring session failed: {str(e)}",
                "session_id": session.id,
                "status": "failed"
            }

    def _scan_and_compare(self, baseline, monitor_type, user_id):
        results = {
            'files_scanned': 0,
            'changes_found': 0,
            'files_added': 0,
            'files_deleted': 0,
            'files_modified': 0,
            'alerts_created': 0,
            'errors': 0
        }

        try:
            # Get baseline files for comparison
            baseline_files = BaselineFile.objects.filter(baseline=baseline)
            baseline_files = {bf.file_path: bf for bf in baseline_files}
            found_baseline_files = set()

            for root, dirs, files in os.walk(baseline.path):
                dirs[:] = [d for d in dirs if not self._should_exclude(
                    os.path.join(root, d),
                    baseline.exclude_patterns
                )]

                # Process files
                for file in files:
                    file_path = os.path.join(root, file)

                    if self._should_exclude(file_path, baseline.exclude_patterns):
                        continue

                    results['files_scanned'] += 1

                    if file_path in baseline_files:
                        # File exists in baseline - check for modifications
                        found_baseline_files.add(file_path)
                        baseline_file = baseline_files[file_path]

                        change = self._compare_file(
                            file_path,
                            baseline_file,
                            baseline,
                            monitor_type,
                            user_id
                        )

                        if change:
                            results['changes_found'] += 1
                            results['files_modified'] += 1
                            results['alerts_created'] += 1
                    else:
                        # File NOT in baseline - it was added
                        change = self._create_file_change(
                            file_path=file_path,
                            baseline=baseline,
                            change_type='added',
                            severity='medium',
                            user_id=user_id
                        )

                        if change:
                            results['changes_found'] += 1
                            results['files_added'] += 1
                            results['alerts_created'] += 1

            # Detect deleted files (in baseline but not found during scan)
            for file_path, baseline_file in baseline_files.items():
                if file_path not in found_baseline_files:
                    # File exists in baseline but NOT on disk - it was deleted
                    change = self._create_file_change(
                        file_path=file_path,
                        baseline=baseline,
                        change_type='deleted',
                        severity='high',
                        user_id=user_id
                    )

                    if change:
                        results['changes_found'] += 1
                        results['files_deleted'] += 1
                        results['alerts_created'] += 1

        except Exception as e:
            print(f"Error during scan and compare: {str(e)}")
            results['errors'] += 1

        return results

    def _compare_file(self, file_path, baseline_file, baseline, monitor_type, user_id):
        """
        Compare current file against baseline file.

        monitor_type determines what we check:
        - full: Complete hash comparison
        - incremental: Hash + mtime check
        - quick: Only size and mtime (no hashing)
        """
        try:
            stat_info = os.stat(file_path)
            current_size = stat_info.st_size
            current_mtime = stat_info.st_mtime
            current_permissions = stat_info.st_mode
            current_uid = stat_info.st_uid
            current_gid = stat_info.st_gid
            current_inode = stat_info.st_ino

            # QUICK SCAN: Only check size and mtime
            if monitor_type == 'quick':
                size_changed = current_size != baseline_file.file_size
                mtime_changed = current_mtime != baseline_file.mtime

                if size_changed or mtime_changed:
                    # File appears modified (but we don't hash it)
                    severity = 'high' if size_changed else 'medium'
                    change = self._create_file_change(
                        file_path=file_path,
                        baseline=baseline,
                        change_type='modified',
                        severity=severity,
                        user_id=user_id
                    )
                    return change

            # INCREMENTAL SCAN: Check mtime first, hash if changed
            elif monitor_type == 'incremental':
                # First check timestamp - skip if unchanged
                if current_mtime == baseline_file.mtime and current_size == baseline_file.file_size:
                    # File hasn't been modified, skip hashing
                    return None

                # File modified - calculate hash and compare
                current_hash = self._calculate_hash(file_path, baseline.algorithm_type)

                if current_hash and current_hash != baseline_file.sha256:
                    change = self._create_file_change(
                        file_path=file_path,
                        baseline=baseline,
                        change_type='modified',
                        severity='critical',
                        user_id=user_id
                    )
                    return change

            else:  # monitor_type == 'full'
                if current_permissions != baseline_file.permissions:
                    change = self._create_file_change(
                        file_path=file_path,
                        baseline=baseline,
                        change_type='permission',
                        severity='medium',
                        user_id=user_id
                    )
                    return change


                current_hash = self._calculate_hash(file_path, baseline.algorithm_type)

                # Check for hash change
                if current_hash and current_hash != baseline_file.sha256:
                    change = self._create_file_change(
                        file_path=file_path,
                        baseline=baseline,
                        change_type='modified',
                        severity='critical',
                        user_id=user_id
                    )
                    return change

        except Exception as e:
            print(f"Error comparing file {file_path}: {str(e)}")

        return None

    def _create_file_change(self, file_path, baseline, change_type, severity, user_id):
        """Create FileChange record and associated alert"""
        try:
            # Check if FileChange already exists for this file
            existing_change = FileChange.objects.filter(
                baseline=baseline,
                file_path=file_path,
                change_type=change_type,
                acknowledged=False
            ).first()

            if existing_change:
                existing_change.severity = severity
                existing_change.save()
                file_change = existing_change
            else:
                # Create new FileChange
                file_change = FileChange.objects.create(
                    baseline=baseline,
                    file_path=file_path,
                    change_type=change_type,
                    severity=severity,
                    acknowledged=False,
                    user_id=user_id
                )

            # Create alert for this change
            alert_service = CreateAlertService()
            response = alert_service.execute_service(
                data={'change_id': file_change.id, 'user_id': user_id}
            )

            return file_change

        except Exception as e:
            traceback.print_exc()
            print(f"Error creating file change for {file_path}: {str(e)}")
            return None

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

            # Read file in chunks
            with open(file_path, 'rb') as f:
                while chunk := f.read(self.CHUNK_SIZE):
                    hash_obj.update(chunk)

            return hash_obj.hexdigest()

        except Exception as e:
            print(f"Error calculating hash for {file_path}: {str(e)}")
            return None