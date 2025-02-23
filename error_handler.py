from typing import Dict, Optional
import logging
from telegram import Update
from telegram.ext import CallbackContext

class ErrorHandler:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    