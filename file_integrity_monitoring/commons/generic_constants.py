class GenericConstants:
    INTERNAL_SERVER_ERROR_MESSAGE = "Internal server error"

    EMAIL_ALREADY_EXISTS_MESSAGE = "Email already exists"
    INVALID_ROLE_MESSAGE = "Invalid role"
    REGISTER_USER_SUCCESSFUL_MESSAGE = "User registered successfully"

    INVALID_EMAIL_OR_PASSWORD_MESSAGE = "Invalid email or password"
    USER_INACTIVE_MESSAGE = "User is inactive"
    LOGIN_SUCCESSFUL_MESSAGE = "Login successful"

    ROLE_ALREADY_EXISTS_MESSAGE = "Role already exists"
    ROLE_CREATED_SUCCESSFUL_MESSAGE = "Role successfully created"
    ROLE_NOT_FOUND_MESSAGE = "Role not found"
    ROLE_UPDATE_SUCCESSFUL_MESSAGE = "Role updated successfully"
    ROLE_DELETE_SUCCESSFUL_MESSAGE = "Role deleted successfully"

    USER_ID_REQUIRED_MESSAGE = "User id is required"
    USER_NOT_FOUND_MESSAGE = "User not found"
    USER_CREATED_SUCCESSFUL_MESSAGE = "User created successfully"
    USER_UPDATED_SUCCESSFUL_MESSAGE = "User updated successfully"
    USER_DELETED_SUCCESSFUL_MESSAGE = "User deleted successfully"

    AUDIT_LOG_NOT_FOUND_MESSAGE = "Audit log not found"
    AUDIT_LOG_CREATE_SUCCESSFUL_MESSAGE = "Audit log created successfully"

    BASELINE_NAME_REQUIRED_MESSAGE = "Baseline name is required"
    BASELINE_PATH_REQUIRED_MESSAGE = "Baseline path is required"
    BASELINE_PATH_DOES_NOT_EXIST = f"Path does not exist: {0}"
    BASELINE_NAME_ALREADY_EXISTS_MESSAGE = "Baseline with this name already exists"
    BASELINE_ID_REQUIRED_MESSAGE = "Baseline id is required"
    BASELINE_NOT_FOUND_MESSAGE = "Baseline not found"
    BASELINE_FILES_COUNT_ERROR_MESSAGE = "Baseline Files count could not be computed"
    BASELINE_FILE_HASH_ERROR_MESSAGE = "Baseline File hash could not be computed"
    BASELINE_FILE_NOT_FOUND_ERROR_MESSAGE = "Baseline File not found error"
    BASELINE_CREATE_SUCCESSFUL_MESSAGE = "Baseline created successfully"
    BASELINE_UPDATE_SUCCESSFUL_MESSAGE = "Baseline updated successfully"
    BASELINE_DELETE_SUCCESSFUL_MESSAGE = "Baseline deleted successfully"

    FILE_CHANGE_NOT_FOUND_MESSAGE = "File change not found"
    FILE_CHANGE_ID_REQUIRED_MESSAGE = "File change id is required"
    FILE_ACKNOWLEDGE_SUCCESSFUL_MESSAGE = "File acknowledged successfully"

    ALERT_ID_REQUIRED_MESSAGE = "Alert id is required"
    ALERT_NOT_FOUND_MESSAGE = "Alert not found"
    ALERT_MARK_READ_SUCCESSFUL_MESSAGE = "Alert read successfully"
    ALERT_ALREADY_ARCHIVED_MESSAGE = "Alert already archived"
    ALERT_ARCHIVED_SUCCESSFUL_MESSAGE = "Alert archived successfully"
    ALERT_ALREADY_EXISTS = "Alert already exists for this file change"
    ALERT_CREATE_SUCCESSFUL_MESSAGE = "Alert created successfully"

    SESSION_ID_REQUIRED_MESSAGE = "Session ID is required"
    MONITORING_SESSION_NOT_FOUND_MESSAGE = "Monitoring session not found"
    MONITORING_SESSION_CREATE_SUCCESSFUL_MESSAGE = "Monitoring session completed successfully"
    MONITORING_SESSION_CREATE_ERROR_MESSAGE = "Monitoring session create could not be completed"

    FILE_PATTERN_REQUIRED_MESSAGE = "File pattern is required"

    WHITELIST_RULE_ID_REQUIRED_MESSAGE = "Whitelist Rule id is required"
    WHITELIST_RULE_NOT_FOUND_MESSAGE = "Whitelist rule not found"
    WHITELIST_RULE_CREATE_SUCCESSFUL_MESSAGE = "Whitelist rule created successfully"
    WHITELIST_RULE_UPDATE_SUCCESSFUL_MESSAGE = "Whitelist rule updated successfully"
    WHITELIST_RULE_DELETE_SUCCESSFUL_MESSAGE = "Whitelist rule deleted successfully"

    SYNC_FILE_THRESHOLD = 5000
    CHUNK_SIZE = 8192

    STATUS_SCANNING = "scanning"
    STATUS_READY = "ready"
    STATUS_ERROR = "error"
    STATUS_ACTIVE = "active"

    ACTION_CREATE = "create"

    RESOURCE_TYPE_BASELINE = "Baseline"
    RESOURCE_TYPE_BASELINE_FILES = "Baseline Files"

    ALGORITHM_SHA256 = "sha256"
    ALGORITHM_SHA512 = "sha512"