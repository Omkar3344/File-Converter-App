from kivy.utils import platform
from functools import partial

# Check if we're on Android
if platform == 'android':
    from android.permissions import request_permissions, Permission, check_permission

def check_and_request_permissions():
    """Check and request required permissions for Android."""
    if platform != 'android':
        return True  # No permissions needed on other platforms
    
    # Define the permissions we need
    permissions = [
        Permission.READ_EXTERNAL_STORAGE,
        Permission.WRITE_EXTERNAL_STORAGE
    ]
    
    # Check if we have all permissions
    for permission in permissions:
        if not check_permission(permission):
            # Request permissions
            request_permissions(permissions)
            return False
    
    return True  # All permissions granted