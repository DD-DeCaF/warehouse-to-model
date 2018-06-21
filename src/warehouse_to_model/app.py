# Copyright (c) 2018, Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Expose the main Flask-RESTPlus application."""

import logging
import logging.config

from flask import Flask
from flask_cors import CORS
from flask_restplus import Api
from raven.contrib.flask import Sentry


app = Flask(__name__)
api = Api(
    title="Warehouse to Model",
    version="0.1.0",
    description="Abstraction layer for the DD-DeCaF warehouse",
)


def init_app(application, interface):
    """Initialize the main app with config information and routes."""
    from .settings import current_config
    application.config.from_object(current_config())

    # Configure logging
    logging.config.dictConfig(application.config['LOGGING'])

    # Configure Sentry
    if application.config['SENTRY_DSN']:
        sentry = Sentry(dsn=application.config['SENTRY_DSN'], logging=True,
                        level=logging.ERROR)
        sentry.init_app(application)

    # Initialize the API
    interface.init_app(application)

    # Add CORS information for all resources.
    CORS(application)
