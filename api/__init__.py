import logging
from puyuan.settings import LOGGING
# setup logger using LOGGING_CONFIG in settings.py

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)
