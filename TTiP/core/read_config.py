"""
Uses the files in process_inputs to parse relevent sections of the config file.
"""
import configparser
import os
from inspect import getfile

from firedrake import FunctionSpace
from TTiP import resources
from TTiP.parsers.boundary_conds_parser import BoundaryCondsParser
from TTiP.parsers.initial_vals_parser import InitialValParser
from TTiP.parsers.mesh_parser import MeshParser
from TTiP.parsers.parameters_parser import ParametersParser
from TTiP.parsers.solver_parser import SolverParser
from TTiP.parsers.sources_parser import SourcesParser
from TTiP.parsers.time_parser import TimeParser


class Config:
    """
    A class for combining processing of each section for the config.
    This is used to read in the file, set any defaults, and the pass the raw
    config to the specific parser (e.g. mesh or time).

    Attributes:
        conf_parser (ConfigParser):
            The dict-like object that is returned from configparser.
    """
    def __init__(self, filename):
        """
        Initialsiser for the Config class.
        This reads the file and sets defaults.

        Args:
            filename (string):
                The path to the file that contains the problem information.
        """
        if not os.path.exists(filename):
            raise ValueError('Config file does not exist.')

        resources_dir = os.path.dirname(getfile(resources))
        self.conf_parser = configparser.ConfigParser()

        default_file = os.path.join(resources_dir, 'default_config.ini')
        self.conf_parser.read(default_file)

        self.conf_parser.read(filename)

        self._mesh = None
        self._V = None

    def get_boundary_conds(self):
        """
        Get the boundary conditions as a list of dictionaries.

        Returns:
            list<dict>: All given boundary conditions.
        """
        if self._mesh is None:
            self.get_mesh()
        parser = BoundaryCondsParser(self._mesh, self._V)
        parser.parse(self.conf_parser['BOUNDARIES'])
        return parser.bcs

    def get_sources(self):
        """
        Get the source term.

        Returns:
            Function: The source term (a sum of all given functions)
        """
        if self._mesh is None:
            self.get_mesh()
        parser = SourcesParser(self._mesh, self._V)
        parser.parse(self.conf_parser['SOURCES'])
        return parser.source

    def get_time(self):
        """
        Get the time stepping data.
        (None, None, None) if steady state.

        Returns:
            tuple<int, float, float>:
                Number of steps, length of each step, max time to iterate to.
        """
        parser = TimeParser()
        parser.parse(self.conf_parser['TIME'])
        return (parser.steps, parser.dt, parser.max_t)

    def get_mesh(self):
        """
        Get the mesh for the problem.

        Returns:
            Mesh: The initialised mesh for the problem.
        """
        if self._mesh is None:
            parser = MeshParser()
            parser.parse(self.conf_parser['MESH'])
            self._mesh = parser.mesh
            self._V = FunctionSpace(self._mesh, 'CG', 1)

        return self._mesh, self._V

    def get_parameters(self):
        """
        Get the parameters for the problem.
        (Currently only density - more will be added)

        Returns:
            Function: The density of the plasma
        """
        if self._mesh is None:
            self.get_mesh()
        parser = ParametersParser(self._mesh, self._V)
        parser.parse(self.conf_parser['PARAMETERS'])
        return parser.density

    def get_initial_val(self):
        """
        Get the initial value term.

        Returns:
            Function: The initial value term (a sum of all given functions)
        """
        if self._mesh is None:
            self.get_mesh()
        parser = InitialValParser(self._mesh, self._V)
        parser.parse(self.conf_parser['INITIALVALUE'])
        return parser.initial_val

    def get_solver_params(self):
        """
        Get the solver arguments.

        Returns:
            string, string, dict: The file_path, the method, any params.
        """
        parser = SolverParser()
        parser.parse(self.conf_parser['SOLVER'])
        return parser.file_path, parser.method, parser.params
