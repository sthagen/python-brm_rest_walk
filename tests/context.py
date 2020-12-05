"""Setting up the context for test."""
import os
BRM_FS_ROOT = "."
BRM_SERVER = "https://example.com"
BRM_API_ROOT = "api"
BRM_USER = "none"
BRM_TOKEN = "0xcafedafe"


def init():
    """Set some environment variables."""
    os.environ["BRM_FS_ROOT"] = BRM_FS_ROOT
    os.environ["BRM_SERVER"] = BRM_SERVER
    os.environ["BRM_API_ROOT"] = BRM_API_ROOT
    os.environ["BRM_USER"] = BRM_USER
    os.environ["BRM_TOKEN"] = BRM_TOKEN


init()
reset = init
