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

"""Implement RESTful API endpoints using resources."""

import json

from flask import request
from flask_restplus import Resource

from warehouse_to_model.app import api, app
from warehouse_to_model.decorators import forward_jwt
from warehouse_to_model.models import get_sample_changes


@api.route('/experiments')
class Experiments(Resource):
    """Experiment API resource."""

    @forward_jwt
    def get(self, session):
        """Retrieve accessible experiments from the data warehouse."""
        response = session.get(f"{app.config['WAREHOUSE_API']}/experiments").json()
        return response.json(), response.status_code


@api.route('/experiments/<int:experiment_id>/samples')
class ExperimentSamples(Resource):
    """Experiment Samples API resource."""

    @forward_jwt
    def get(self, experiment_id, session):
        """Retrieve accessible experiments from the data warehouse."""
        response = session.get(f"{app.config['WAREHOUSE_API']}/experiments/{experiment_id}/samples")
        return response.json(), response.status_code


@api.route('/organisms')
class Organisms(Resource):
    """Organism API resource."""

    @forward_jwt
    def get(self, session):
        """Retrieve accessible organisms from the data warehouse."""
        response = session.get(f"{app.config['WAREHOUSE_API']}/organisms").json()
        return response.json(), response.status_code


@api.route('/sample/<int:sample_id>/info')
class SampleInfo(Resource):
    """Sample info API resource."""

    @forward_jwt
    def get(self, sample_id, session):
        """Information about measurements, medium and genotype changes for the given list of samples."""
        # Get the sample in question
        response = session.get(f"{app.config['WAREHOUSE_API']}/samples/{sample_id}")
        response.raise_for_status()
        sample = response.json()

        return get_sample_changes(session, sample)


@api.route('/sample/<int:sample_id>/simulate/fluxes')
class SampleSimulate(Resource):
    """API resource for simulating fluxes for the given sample."""

    @forward_jwt
    def post(self, sample_id, session):
        """Apply the changes from the given sample to the given model and return the modified model with fluxes."""
        try:
            model_id = request.json['model_id']
        except KeyError:
            return {'error': "Key 'model_id' missing from JSON body"}, 400

        # Get the sample in question
        response = session.get(f"{app.config['WAREHOUSE_API']}/samples/{sample_id}")
        response.raise_for_status()
        sample = response.json()

        message = get_sample_changes(session, sample)

        if 'objective' in request.json:
            message['objective'] = request.json['objective']

        payload = {'message': message}
        response = session.post(f"{app.config['MODEL_API']}/models/{model_id}", data=json.dumps(payload))
        return response.json(), response.status_code
