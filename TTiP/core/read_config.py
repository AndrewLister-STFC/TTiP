"""
Uses the files in process_inputs to parse relevent sections of the config file.
"""

import configparser
import os
from inspect import getfile

from TTiP import resources
from TTiP.process_inputs.boundary_conds import BoundaryCondsParser
from TTiP.process_inputs.parameters import ParametersParser
from TTiP.process_inputs.parsers.mesh import MeshParser
from TTiP.process_inputs.parsers.time import TimeParser
from TTiP.process_inputs.sources import SourcesParser


class Config:
    def __init__(self, filename):
        resources_dir = os.path.dirname(getfile(resources))
        self.conf_parser = configparser.ConfigParser()

        default_file = os.path.join(resources_dir, 'default_config.ini')
        self.conf_parser.read(default_file)

        self.conf_parser.read(filename)

    def get_boundary_conds(self):
        parser = BoundaryCondsParser()
        parser.parse(self.conf_parser['BOUNDARIES'])
        return 

    def get_sources(self):
        parser = SourcesParser()
        parser.parse(self.conf_parser['SOURCES'])
        return parser.source

    def get_time(self):
        parser = TimeParser()
        parser.parse(self.conf_parser['TIME'])
        return (parser.steps, parser.dt, parser.max_t)

    def get_mesh(self):
        parser = MeshParser()
        parser.parse(self.conf_parser['MESH'])
        return parser.mesh

    def get_parameters(self):
        parser = ParametersParser()
        parser.parse(self.conf_parser['PARAMETERS'])
        return parser.density
