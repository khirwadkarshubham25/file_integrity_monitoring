import os

from django.utils import timezone
from rest_framework import status

from file_integrity_monitoring.commons.commons import Commons
from file_integrity_monitoring.commons.generic_constants import GenericConstants
from monitoring.models import MonitoringSession, Baseline, FileChange, BaselineFile
from monitoring.services.alert_create_service import AlertCreateService
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper


class MonitoringSessionCreateService(MonitoringServiceHelper):
    """Service to orchestrate monitoring session, scan files, compare hashes, and create alerts"""

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
            return {"message": GenericConstants.BASELINE_NAME_REQUIRED_MESSAGE}

        # Get baseline
        try:
            baseline = Baseline.objects.get(id=params.get("baseline_id"))
        except Baseline.DoesNotExist:
            self.error = True
            self.set_status_code(status_code=status.HTTP_404_NOT_FOUND)
            return {"message": GenericConstants.BASELINE_NOT_FOUND_MESSAGE}

        # Validate baseline has files scanned
        if baseline.baseline_files.count() == 0:
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.BASELINE_FILES_COUNT_ERROR_MESSAGE}

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
            session.files_monitored = scan_results['files_scanned']
            session.changes_detected = scan_results['changes_found']
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
                    "files_monitored": session.files_monitored,
                    "changes_detected": session.changes_detected,
                    "alerts_created": scan_results['alerts_created']
                }
            )

            self.set_status_code(status_code=status.HTTP_201_CREATED)
            return {
                "message": GenericConstants.MONITORING_SESSION_CREATE_SUCCESSFUL_MESSAGE,
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
        """
        Scan directory and compare files against baseline.

        Scan Types:
        - full: Scan all files, calculate hashes, detect all changes
        - incremental: Scan only recently modified files
        - quick: Compare file size and mtime only (no hashing)
        """
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
            baseline_files = {bf.file_path: bf for bf in baseline.baseline_files.all()}

            # Track which baseline files we found (for detecting deletions)
            found_baseline_files = set()

            # Walk directory and scan files based on type
            for root, dirs, files in os.walk(baseline.path):
                # Filter excluded directories
                dirs[:] = [d for d in dirs if not self.should_exclude(
                    os.path.join(root, d),
                    baseline.exclude_patterns
                )]

                # Process files
                for file in files:
                    file_path = os.path.join(root, file)

                    # Skip excluded files
                    if self.should_exclude(file_path, baseline.exclude_patterns):
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

                        sha512, sha256 = None, None
                        if baseline.algorithm_type == GenericConstants.ALGORITHM_SHA512:
                            is_success, sha512 = self.calculate_hash(file_path, baseline.algorithm_type)
                        else:
                            is_success, sha256 = self.calculate_hash(file_path, baseline.algorithm_type)
                        baseline_file = BaselineFile.objects.create(
                            baseline=baseline,
                            file_path=file_path,
                            file_name=os.path.basename(file_path),
                            sha256=sha256,
                            sha512=sha512,
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
                        change = self._create_file_change(
                            file_path=file_path,
                            baseline=baseline,
                            baseline_file=baseline_file,
                            change_type='added',
                            current_hash=self.calculate_hash(file_path, baseline.algorithm_type)[1],
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
                        baseline_file=baseline_file,
                        change_type='deleted',
                        current_hash=None,
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
                        baseline_file=baseline_file,
                        change_type='modified',
                        current_hash=None,  # Not calculated in quick scan
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
                is_success, current_hash = self.calculate_hash(file_path, baseline.algorithm_type)

                if current_hash and current_hash != baseline_file.sha256:
                    change = self._create_file_change(
                        file_path=file_path,
                        baseline=baseline,
                        baseline_file=baseline_file,
                        change_type='modified',
                        current_hash=current_hash,
                        severity='critical',
                        user_id=user_id
                    )
                    return change

            # FULL SCAN: Always calculate hash and compare
            else:  # monitor_type == 'full'
                is_success, current_hash = self.calculate_hash(file_path, baseline.algorithm_type)

                # Check for hash change
                if current_hash and current_hash != baseline_file.sha256:
                    change = self._create_file_change(
                        file_path=file_path,
                        baseline=baseline,
                        baseline_file=baseline_file,
                        change_type='modified',
                        current_hash=current_hash,
                        severity='critical',
                        user_id=user_id
                    )
                    return change

                # Check for permission changes
                if current_permissions != baseline_file.permissions:
                    change = self._create_file_change(
                        file_path=file_path,
                        baseline=baseline,
                        baseline_file=baseline_file,
                        change_type='permission',
                        current_hash=current_hash,
                        severity='medium',
                        user_id=user_id
                    )
                    return change

        except Exception as e:
            print(f"Error comparing file {file_path}: {str(e)}")

        return None

    def _create_file_change(self, file_path, baseline, baseline_file, change_type, current_hash, severity, user_id):
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
                # Update existing change
                existing_change.current_hash = current_hash or existing_change.current_hash
                existing_change.severity = severity
                existing_change.save()
                file_change = existing_change
            else:
                # Create new FileChange
                file_change = FileChange.objects.create(
                    baseline=baseline,
                    baseline_file=baseline_file,
                    file_path=file_path,
                    change_type=change_type,
                    current_hash=current_hash,
                    severity=severity,
                    acknowledged=False,
                    user_id=user_id
                )

            # Create alert for this change
            alert_service = AlertCreateService()
            status_code, response = alert_service.execute_service(
                data={'change_id': file_change.id, 'user_id': user_id}
            )

            return file_change

        except Exception as e:
            print(f"Error creating file change for {file_path}: {str(e)}")
            return None