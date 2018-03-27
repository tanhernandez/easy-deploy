# settings.py
from os.path import join, dirname, realpath
from dotenv import load_dotenv
import os

dotenv_path = dirname(realpath(__file__)) + '\\.env'
# OR, the same with increased verbosity:
load_dotenv(dotenv_path)

# Map the values the needs to be public
DEV_BRANCH = os.environ.get("DEV_BRANCH")
PROD_BRANCH = os.environ.get("PROD_BRANCH")
DEV_IP = os.environ.get("DEV_IP")
PROD_IP = os.environ.get("PROD_IP")
PUBLIC_SSH_KEY = os.environ.get("PUBLIC_SSH_KEY")

