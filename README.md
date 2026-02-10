# File Integrity Monitoring System (FIM)

A comprehensive Django-based File Integrity Monitoring solution that tracks file changes, detects unauthorized modifications, and provides real-time security alerts.

## 🎯 Overview

The File Integrity Monitoring System is a production-grade security application designed to detect, monitor, and report on file system changes in real-time. It creates baseline snapshots of critical files and directories, continuously monitors them for modifications, and generates alerts when changes are detected.

### Key Features

✅ **Baseline Management**
- Create and manage file baselines
- Support for multiple baseline configurations
- Exclude patterns and whitelist rules
- SHA256, SHA512, and BLAKE3 hash algorithms

✅ **File Change Detection**
- Real-time file monitoring
- Change type detection (added, modified, deleted, permission)
- Hash-based content verification
- Severity classification (critical, high, medium, low)

✅ **Alerting System**
- Automatic alert generation on file changes
- Alert management (read, archive)
- Severity-based notifications
- Audit trail for all events

✅ **Monitoring Sessions**
- Full, incremental, and quick scan modes
- Session tracking and history
- Statistics and performance metrics
- Change detection and reporting

✅ **Rule Management**
- Whitelist rules for expected changes
- Pattern-based exclusions
- Active/inactive rule management
- User-based rule creation and tracking

✅ **Security & Audit**
- User authentication and authorization
- Comprehensive audit logging
- Change acknowledgment tracking
- User action history

## 📋 Tech Stack

### Backend
- **Framework:** Django 4.2+
- **Language:** Python 3.8+
- **Database:** SQLite (dev)
- **API:** Django REST Framework (built-in views)
- **Authentication:** Django built-in + Token-based

### Frontend
- **HTML5** with Semantic HTML
- **CSS3** with Bootstrap 5.3
- **JavaScript** (Vanilla ES6+)
- **Icons:** FontAwesome 6.4

### Core Libraries
- `django-cors-headers` - CORS support
- `python-decouple` - Environment management

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip & virtualenv

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/khirwadkarshubham25/file_integrity_monitoring.git
cd file-integrity-monitoring
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Run development server**
```bash
python manage.py runserver
```

Visit `http://localhost:8000/accounts/login` to start using the system.

## 📚 API Documentation

### Authentication

All API endpoints require token-based authentication via `Authorization` header:

```javascript
fetch('/monitoring/api/baselines', {
    headers: {
        'Authorization': 'Bearer YOUR_TOKEN',
        'Content-Type': 'application/json'
    }
})
```

### Monitoring Endpoints

#### Baselines
- `GET /monitoring/api/baselines` - List all baselines
- `POST /monitoring/api/baselines` - Create baseline
- `GET /monitoring/api/baseline-details?baseline_id=1` - Get details
- `PUT /monitoring/api/baselines` - Update baseline
- `DELETE /monitoring/api/baselines` - Delete baseline

#### File Changes
- `GET /monitoring/api/file-changes/` - List file changes
- `GET /monitoring/api/file-change-details/?change_id=1` - Get change details
- `POST /monitoring/api/file-change-acknowledge/` - Acknowledge change

#### Alerts
- `GET /monitoring/api/alerts` - List alerts
- `GET /monitoring/api/alert-details?alert_id=1` - Get alert details
- `POST /monitoring/api/alert-read` - Mark alert as read
- `POST /monitoring/api/alert-archive` - Archive alert

#### Monitoring Sessions
- `GET /monitoring/api/monitoring-sessions` - List sessions
- `GET /monitoring/api/monitoring-session-details?session_id=1` - Get session details
- `POST /monitoring/api/monitoring-session-start` - Start new session

#### Whitelist Rules
- `GET /monitoring/api/whitelist-rules` - List rules
- `POST /monitoring/api/whitelist-rules` - Create rule
- `GET /monitoring/api/whitelist-rule-details?rule_id=1` - Get rule details
- `PUT /monitoring/api/whitelist-rules` - Update rule
- `DELETE /monitoring/api/whitelist-rules` - Delete rule

### Query Parameters

Most list endpoints support filtering and pagination:

```bash
GET /monitoring/api/baselines?page=1&page_size=10&status=ready&sort_by=created_at&sort_order=desc
```

**Common Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Records per page (default: 10)
- `sort_by` - Sort field
- `sort_order` - 'asc' or 'desc'
- `status` - Filter by status
- `severity` - Filter by severity

## 🔧 Configuration

### settings.py

Key settings to configure:

```python
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'fim_db',
        'USER': 'fim_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Security
APPEND_SLASH = False
SECRET_KEY = 'your-secret-key'
DEBUG = False  # Set to False in production
ALLOWED_HOSTS = ['yourdomain.com']

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://yourdomain.com",
]

# File Monitoring
FILE_HASH_ALGORITHM = 'sha256'  # sha256, sha512, blake3
BASELINE_SYNC_THRESHOLD = 5000  # Files count threshold for async processing
```

### Environment Variables (.env)

```
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
APPEND_SLASH=False
```

## 📊 Database Models

### Core Models

**Baseline**
- id, name, path, status (scanning/ready/failed)
- algorithm_type (sha256/sha512)
- exclude_patterns (JSON)
- created_by, created_at, updated_at

**BaselineFile**
- baseline (FK)
- file_path, file_name, file_size
- sha256, sha512
- permissions, uid, gid, inode
- mtime, atime, ctime, metadata

**FileChange**
- id, baseline (FK), file_path
- change_type (added/modified/deleted/permission)
- severity (critical/high/medium/low)
- acknowledged, acknowledged_at, acknowledged_by
- previous_hash, current_hash
- detected_at

**Alert**
- id, file_change (FK)
- severity, message
- read, read_at, archived, archived_at
- created_at

**MonitoringSession**
- id, baseline (FK)
- monitor_type (full/incremental/quick)
- status (running/completed/failed)
- files_monitored, changes_detected
- files_added, files_deleted, files_modified
- start_time, end_time

**WhitelistRule**
- id, baseline (FK)
- pattern, rule_type
- active, created_by, created_at

**AuditLog**
- user, action, model_name, object_id
- changes (JSON), timestamp

## 🔒 Security Features

- **User Authentication:** Django built-in authentication system
- **Password Security:** PBKDF2 hashing with SHA256
- **CSRF Protection:** Django CSRF tokens on all forms
- **SQL Injection Prevention:** Django ORM parameterized queries
- **XSS Protection:** Template auto-escaping enabled
- **Audit Logging:** All user actions logged
- **Change Acknowledgment:** Track who acknowledged what changes
- **Baseline Integrity:** Hash-based file verification

## 📈 Performance Considerations

### Baseline Creation
- **Small Baseline (< 5000 files):** Synchronous processing, ~6-7 seconds
- **Large Baseline (> 5000 files):** Asynchronous with background thread, ~2 minutes

### Monitoring Sessions
- **Full Scan:** All files, always hash calculation (~10 seconds for 2500 files)
- **Incremental Scan:** Only modified files, faster (~3 seconds)
- **Quick Scan:** Metadata only, no hashing (~1 second)

### Database Indexing
Ensure indexes on:
- `FileChange.baseline_id, change_type, severity`
- `Alert.file_change_id, read, archived`
- `MonitoringSession.baseline_id, status`
- `AuditLog.user_id, timestamp`

## 🐛 Troubleshooting

### Issue: 404 on API endpoints
**Solution:** Ensure `APPEND_SLASH = False` in settings.py

### Issue: Changes not appearing in table
**Solution:** Check API response key matches template expectation (e.g., `data.changes`)

### Issue: Baseline creation hanging
**Solution:** Check file system permissions and disk space availability

### Issue: Database connection error
**Solution:** Verify DATABASE_URL and PostgreSQL service is running

## 🚦 Status Codes

### HTTP Responses
- `200 OK` - Successful GET request
- `201 Created` - Successful POST (resource created)
- `202 Accepted` - Request accepted (async processing)
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Server Error` - Internal server error

## 📅 Future Enhancements

These features are planned for future releases:

- [ ] **Reports App** - Compliance reports, export history, scheduled emails
- [ ] **Integrations App** - Slack, Email, Jira, Splunk, webhooks
- [ ] **Tasks App** - Celery-based async jobs, background processing
- [ ] **Advanced Filtering** - Complex query builders
- [ ] **Bulk Operations** - Batch create, update, delete
- [ ] **API Documentation** - Swagger/OpenAPI integration
- [ ] **Mobile App** - iOS/Android native application
- [ ] **Multi-tenancy** - Support for multiple organizations


## 👨‍💻 Author

**Your Name**
- GitHub: [khirwadkarshubham25](https://github.com/khirwadkarshubham25/)
- Email: khirwadkar.shubham25@gmail.com

## 🙏 Acknowledgments

- Django framework and community
- Bootstrap for responsive design
- FontAwesome for icons


## 📌 MVP Project Notice

**⚠️ This is an MVP (Minimum Viable Product) implementation of the File Integrity Monitoring System.**

This project demonstrates core FIM functionality with the essential features needed for file integrity monitoring. It includes:
- ✅ Baseline creation and management
- ✅ File change detection
- ✅ Alert generation and management
- ✅ User authentication
- ✅ Basic monitoring sessions
- ✅ Whitelist rules

**For a full-featured production deployment** with additional capabilities such as:
- 🔄 Background task processing (Celery/Redis)
- 📊 Advanced reporting and analytics
- 🔗 Third-party integrations (Slack, Email, Jira, Splunk)
- 📱 Mobile applications
- 🔐 Advanced security features (2FA, LDAP, RBAC)
- 📈 High-availability setup
- 🌐 Multi-tenancy support
- 🚀 Enterprise deployment guidance

**Please contact the author for enterprise solutions and customization:**

**Author:** Shubham Khirwadkar  
**Email:** khirwadkar.shubham25@gmail.com  
**GitHub:** [khirwadkarshubham25](https://github.com/khirwadkarshubham25/)
---

**Last Updated:** February 2026
**Version:** 1.0.0
**Status:** Production Ready ✅
