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

from flask_restplus import Resource

from warehouse_to_model.app import api, app
from warehouse_to_model.decorators import forward_jwt


@api.route('/experiments')
class Experiments(Resource):
    """Experiment API resource."""

    @forward_jwt
    def get(self, session):
        """Retrieve accessible experiments from the data warehouse."""
        response = session.get(f"{app.config['WAREHOUSE_API']}/experiments").json()
        return response.json(), response.status_code


@api.route('/experiments/<int:id>/samples')
class ExperimentSamples(Resource):
    """Experiment Samples API resource."""

    @forward_jwt
    def get(self, id, session):
        """Retrieve accessible experiments from the data warehouse."""
        response = session.get(f"{app.config['WAREHOUSE_API']}/experiments/{id}/samples")
        return response.json(), response.status_code


@api.route('/organisms')
class Organisms(Resource):
    """Organism API resource."""

    @forward_jwt
    def get(self, session):
        """Retrieve accessible organisms from the data warehouse."""
        response = session.get(f"{app.config['WAREHOUSE_API']}/organisms").json()
        return response.json(), response.status_code


@api.route('/sample/<int:id>/info')
class SampleInfo(Resource):
    """Sample info API resource."""

    @forward_jwt
    def get(self, id, session):
        """Information about measurements, medium and genotype changes for the given list of samples."""
        # Get the sample in question
        response = session.get(f"{app.config['WAREHOUSE_API']}/samples/{id}")
        response.raise_for_status()
        sample = response.json()

        # Get genotype changes: Collect all genotype changes in the strain lineage
        def iterate_strain(genotype, strain_id):
            # FIXME: n+1 requests
            response = session.get(f"{app.config['WAREHOUSE_API']}/strains/{strain_id}")
            response.raise_for_status()
            strain = response.json()
            genotype = f"{genotype} {strain['genotype']}"
            if strain['parent_id'] is None:
                return genotype
            else:
                return iterate_strain(genotype, strain['parent_id'])
        genotype_changes = iterate_strain("", sample['strain_id'])

        # Get measurements
        response = session.get(f"{app.config['WAREHOUSE_API']}/samples/{sample['id']}/measurements")
        response.raise_for_status()
        measurements = response.json()

        # Get medium
        response = session.get(f"{app.config['WAREHOUSE_API']}/media/{sample['medium_id']}")
        response.raise_for_status()
        medium = response.json()

        return {
            'genotype-changes': genotype_changes,
            'measurements': measurements,
            'medium': medium['compounds'],
        }
