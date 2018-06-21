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

"""Define data model behaviour."""

import json

from flask import request

from warehouse_to_model.app import app


def get_sample_changes(session, sample):
    """
    Return the changes (measurements, medium and genotype changes) for the given sample.

    :param session: A requests session with authentication details prepared
    :param sample: A dict structure of a warehouse sample
    :return:
    """
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
