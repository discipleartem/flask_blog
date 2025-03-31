import warnings

# Ignore deprecation warnings from dependencies during tests
warnings.filterwarnings('ignore', category=DeprecationWarning, module='werkzeug.routing')
warnings.filterwarnings('ignore', category=DeprecationWarning, module='ast')
warnings.filterwarnings('ignore', category=DeprecationWarning, module='distutils')
warnings.filterwarnings('ignore', category=DeprecationWarning, module='flask.sessions')

# Enable test discovery
import pytest

# Make fixtures available to all test modules
__all__ = ['client', 'init_database', 'login_user']