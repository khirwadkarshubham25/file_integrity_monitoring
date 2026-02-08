from django.db import models
from django.db.models import JSONField
from django.utils import timezone

from accounts.models import Users


class Baseline(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('paused', 'Paused'),
    ]

    HASH_ALGORITHM_CHOICES = [
        ('sha256', 'SHA256'),
        ('sha512', 'SHA512'),
        ('blake3', 'BLAKE3'),
    ]

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    path = models.CharField(max_length=1024)

    version = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    user = models.ForeignKey(Users, on_delete=models.PROTECT, related_name='baselines')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    monitoring_enabled = models.BooleanField(default=True)

    exclude_patterns = JSONField(default=list, blank=True)
    algorithm_type = models.CharField(max_length=20, choices=HASH_ALGORITHM_CHOICES, default='sha256')

    metadata = JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name

    def file_count(self):
        """Get total files in this baseline"""
        return self.baseline_files.count()

    def recent_changes_count(self):
        """Get count of recent file changes"""
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=7)
        return self.file_changes.filter(detected_at__gte=cutoff).count()


class BaselineFile(models.Model):
    id = models.BigAutoField(primary_key=True)
    baseline = models.ForeignKey(Baseline, on_delete=models.CASCADE, related_name='baseline_files')

    file_path = models.CharField(max_length=1024)
    file_name = models.CharField(max_length=255, db_index=True)

    # Hashes
    sha256 = models.CharField(max_length=64, db_index=True)
    sha512 = models.CharField(max_length=128, blank=True, null=True)
    blake3 = models.CharField(max_length=64, blank=True, null=True)

    # File metadata
    file_size = models.BigIntegerField()
    permissions = models.IntegerField()  # Unix file permissions
    uid = models.IntegerField()
    gid = models.IntegerField()
    inode = models.BigIntegerField()
    hard_links = models.IntegerField()

    # Timestamps
    mtime = models.FloatField()
    atime = models.FloatField()
    ctime = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    metadata = JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ['baseline', 'file_path']
        ordering = ['file_path']
        indexes = [
            models.Index(fields=['baseline', 'file_path']),
            models.Index(fields=['sha256']),
            models.Index(fields=['file_name']),
        ]

    def __str__(self):
        return f"{self.file_path} ({self.baseline.name})"


class FileChange(models.Model):
    CHANGE_TYPE_CHOICES = [
        ('created', 'File Created'),
        ('modified', 'File Modified'),
        ('deleted', 'File Deleted'),
        ('moved', 'File Moved'),
        ('permission_changed', 'Permission Changed'),
        ('ownership_changed', 'Ownership Changed'),
    ]

    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ('info', 'Info'),
    ]

    id = models.BigAutoField(primary_key=True)
    baseline = models.ForeignKey(Baseline, on_delete=models.CASCADE, related_name='file_changes')
    baseline_file = models.ForeignKey(BaselineFile, on_delete=models.SET_NULL, null=True, blank=True)

    file_path = models.CharField(max_length=1024, db_index=True)
    change_type = models.CharField(max_length=50, choices=CHANGE_TYPE_CHOICES)

    change_details = JSONField(default=dict)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, db_index=True)

    expected = models.BooleanField(default=False)
    detected_at = models.DateTimeField(auto_now_add=True, db_index=True)

    acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_reason = models.TextField(blank=True)

    metadata = JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['baseline', 'detected_at']),
            models.Index(fields=['file_path']),
            models.Index(fields=['severity']),
        ]

    def __str__(self):
        return f"{self.change_type} - {self.file_path}"

    def acknowledge(self, user, reason=''):
        """Mark change as acknowledged"""
        self.acknowledged = True
        self.acknowledged_by = user
        self.acknowledged_at = timezone.now()
        self.acknowledged_reason = reason
        self.save()


class Alert(models.Model):
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ('info', 'Info'),
    ]

    id = models.BigAutoField(primary_key=True)
    file_change = models.ForeignKey(FileChange, on_delete=models.CASCADE, related_name='alerts')

    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, db_index=True)
    title = models.CharField(max_length=255)
    message = models.TextField()

    file_path = models.CharField(max_length=1024, db_index=True)
    change_type = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    read = models.BooleanField(default=False)
    read_by = models.ManyToManyField(Users, related_name='read_alerts', blank=True)

    alert_channels = JSONField(default=list)  # ['email', 'slack', 'in_app']
    is_archived = models.BooleanField(default=False)

    metadata = JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['severity', 'created_at']),
            models.Index(fields=['read']),
        ]

    def __str__(self):
        return f"[{self.severity.upper()}] {self.title}"

    def mark_as_read(self, user):
        """Mark alert as read by user"""
        self.read = True
        self.read_by.add(user)
        self.save()


class MonitoringSession(models.Model):
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.BigAutoField(primary_key=True)
    baseline = models.ForeignKey(Baseline, on_delete=models.CASCADE, related_name='monitoring_sessions')

    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    files_scanned = models.PositiveIntegerField(default=0)
    files_changed = models.PositiveIntegerField(default=0)
    files_critical = models.PositiveIntegerField(default=0)
    files_added = models.PositiveIntegerField(default=0)
    files_deleted = models.PositiveIntegerField(default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    error_message = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True)
    metadata = JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['baseline', 'start_time']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.baseline.name} - {self.start_time}"

    def duration_seconds(self):
        """Get session duration in seconds"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (timezone.now() - self.start_time).total_seconds()


class WhitelistRule(models.Model):
    CHANGE_TYPE_CHOICES = [
        ('content_changed', 'Content Changed'),
        ('permission_changed', 'Permission Changed'),
        ('ownership_changed', 'Ownership Changed'),
        ('all', 'All Changes'),
    ]

    id = models.BigAutoField(primary_key=True)
    baseline = models.ForeignKey(Baseline, on_delete=models.CASCADE, related_name='whitelist_rules')

    file_pattern = models.CharField(max_length=1024, help_text='Glob pattern or regex')
    change_types = JSONField(default=list, help_text='List of allowed change types')

    reason = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    created_by = models.ForeignKey(Users, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['baseline', 'active']),
        ]

    def __str__(self):
        return f"{self.file_pattern} - {self.baseline.name}"

    def is_expired(self):
        """Check if rule has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False