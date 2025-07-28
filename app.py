import logging
import os
import sys
import warnings

from flask import Flask, request, jsonify
from flask_compress import Compress

# Logging setup (following team pattern)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format='%(thread)d: %(message)s'
)
logger = logging.getLogger("metrics-api")

# Flask app setup
app = Flask(__name__)
Compress(app)
