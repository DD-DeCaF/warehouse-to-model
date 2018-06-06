# Copyright (c) 2018, Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Configure the gunicorn server."""

import os

_config = os.environ["ENVIRONMENT"]

bind = "0.0.0.0:8000"
worker_class = "gevent"
timeout = 20
accesslog = "-"


if _config == "production":
    workers = os.cpu_count() * 2 + 1
    preload_app = True
    loglevel = "INFO"
    access_log_format = '''"%(r)s" %(s)s %(b)s %(L)s "%(f)s"'''
else:
    # FIXME: The number of workers is up for debate. At least for testing more
    # than one worker could make sense.
    workers = 1
    reload = True
    loglevel = "DEBUG"
    access_log_format = '''%(t)s "%(r)s" %(s)s %(b)s %(L)s "%(f)s"'''
