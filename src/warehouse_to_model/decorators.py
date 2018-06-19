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

from functools import wraps

from flask import request
import requests


def forward_jwt(f):
    """
    Add a requests session with the Authorization header forwarded.

    Use on functions that make requests to third party API services. This will
    call the function yield an extra keyword argument `session`, which is a
    requests session that has the Authorization header set with the same value
    as provided by the original client.

    Use this session only with internal HTTP services.
    """

    @wraps(f)
    def wrap(*args, **kwargs):
        session = requests.Session()
        if 'Authorization' in request.headers:
            session.headers.update({
                'Authorization': request.headers['Authorization']})
        return f(*args, **kwargs, session=session)
    return wrap
