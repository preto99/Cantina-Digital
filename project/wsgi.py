import sys
import logging
from app import app as application

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "C:\project\project")

# No need to run the app here as Apache will handle it.
