import os
import sys

# 1. Ensure the host_runtime directory is prioritized in sys.path
# (Protects against Android environments where __file__ might be undefined)
app_dir = (
    os.path.dirname(os.path.abspath(__file__))
    if '__file__' in globals()
    else (sys.path[0] if sys.path else os.getcwd())
)
if app_dir and app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from engine import start_daemon

# 2. Resolve dynamic port passed by Dart via environment variable (or fallback to 9765)
port = int(os.environ.get("PORT", 9765))

# 3. Boot the Flask host daemon
start_daemon(port=port)