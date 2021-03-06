"""
Tests for the read_config.py file.
"""
import os
import tempfile
from unittest import TestCase
from unittest.mock import patch

from firedrake import Constant, Function
from firedrake.mesh import MeshGeometry
from ufl import FunctionSpace
from ufl.algebra import Sum

from TTiP.core import read_config


class TestInit(TestCase):
    """
    Tests for the init method.
    """

    def setUp(self):
        """
        Create a temp_file for storing the config in.
        """
        self.conf_file = tempfile.NamedTemporaryFile()

    def tearDown(self):
        """
        Remove the temp_file
        """
        self.conf_file.close()

    def test_blank_config(self):
        """
        Test some required values for a blank config file.
        """
        c = read_config.Config(self.conf_file.name)

        self.assertIn('SOLVER', c.conf_parser)
        self.assertIn('file_path', c.conf_parser['SOLVER'])
        self.assertIn('method', c.conf_parser['SOLVER'])
        self.assertIn('MESH', c.conf_parser)
        self.assertIn('type', c.conf_parser['MESH'])
        self.assertIn('params', c.conf_parser['MESH'])
        self.assertIn('PARAMETERS', c.conf_parser)
        self.assertIn('SOURCES', c.conf_parser)
        self.assertIn('BOUNDARIES', c.conf_parser)
        self.assertIn('TIME', c.conf_parser)
        self.assertIn('INITIALVALUE', c.conf_parser)

    def test_not_blank_config(self):
        """
        Test a variety of values for a non empty config file.
        """
        with open(self.conf_file.name, 'w') as f:
            f.write('[SOLVER]\n'
                    'file_path: correct_file_path\n'
                    'method: new_method\n'
                    '[PARAMETERS]\n'
                    'part1: 8\n')
        c = read_config.Config(self.conf_file.name)

        self.assertEqual(c.conf_parser['SOLVER']['file_path'],
                         'correct_file_path')
        self.assertEqual(c.conf_parser['SOLVER']['method'], 'new_method')
        self.assertEqual(c.conf_parser['PARAMETERS']['part1'], '8')

    def test_non_existent_config(self):
        """
        Test that exception is raised for non-existant config file.
        """
        with self.assertRaises(ValueError):
            _ = read_config.Config('fake_name.not_a_file')


class TestGetBoundaryConds(TestCase):
    """
    Tests for the get_boundary_conds method.
    """

    def setUp(self):
        """
        Define the config file and the Config object.
        """
        problems_dir = os.path.join(
            os.path.dirname(__file__), os.pardir, os.pardir, 'mock_problems')
        self.config_file = os.path.join(problems_dir,
                                        'be_box_nosource_steady.ini')
        self.conf = read_config.Config(self.config_file)

    def test_correct_boundary_conds(self):
        """
        Test that the boundary section is correctly passed through.
        """
        def new_func(s, x):
            s.bcs = x is self.conf.conf_parser['BOUNDARIES']

        with patch.object(read_config.BoundaryCondsParser, 'parse', new_func):
            self.assertTrue(self.conf.get_boundary_conds())

    def test_correct_type(self):
        """
        Test that the boundary conds returns a list.
        """
        bcs = self.conf.get_boundary_conds()
        self.assertIsInstance(bcs, (list))


class TestGetSources(TestCase):
    """
    Tests for the get_sources method.
    """

    def setUp(self):
        """
        Define the config file and the Config object.
        """
        problems_dir = os.path.join(
            os.path.dirname(__file__), os.pardir, os.pardir, 'mock_problems')
        self.config_file = os.path.join(problems_dir,
                                        'be_box_nosource_steady.ini')
        self.conf = read_config.Config(self.config_file)

    def test_correct_sources(self):
        """
        Test that the sources section is correctly passed through.
        """
        def new_func(s, x):
            s.source = x is self.conf.conf_parser['SOURCES']

        with patch.object(read_config.SourcesParser, 'parse', new_func):
            self.assertTrue(self.conf.get_sources())

    def test_correct_type(self):
        """
        Test that the sources returns a Function.
        """
        s = self.conf.get_sources()
        self.assertIsInstance(s, (Function, Constant, Sum))


class TestGetTime(TestCase):
    """
    Tests for the get_time method.
    """

    def setUp(self):
        """
        Define the config file and the Config object.
        """
        problems_dir = os.path.join(
            os.path.dirname(__file__), os.pardir, os.pardir, 'mock_problems')
        self.config_file = os.path.join(problems_dir,
                                        'be_box_nosource_steady.ini')
        self.conf = read_config.Config(self.config_file)

    def test_correct_time(self):
        """
        Test that the time section is correctly passed through.
        """
        def new_func(s, x):
            s.steps = x is self.conf.conf_parser['TIME']

        with patch.object(read_config.TimeParser, 'parse', new_func):
            self.assertTrue(self.conf.get_time()[0])

    def test_correct_type(self):
        """
        Test that the time returns an int and 2 floats.
        """
        s, dt, mt = self.conf.get_time()
        if s is not None:
            self.assertIsInstance(s, int)
        if dt is not None:
            self.assertIsInstance(dt, (int, float))
        if mt is not None:
            self.assertIsInstance(mt, (int, float))


class TestGetMesh(TestCase):
    """
    Tests for the get_mesh method.
    """

    def setUp(self):
        """
        Define the config file and the Config object.
        """
        problems_dir = os.path.join(
            os.path.dirname(__file__), os.pardir, os.pardir, 'mock_problems')
        self.config_file = os.path.join(problems_dir,
                                        'be_box_nosource_steady.ini')
        self.conf = read_config.Config(self.config_file)

    def test_correct_mesh(self):
        """
        Test that the mesh section is correctly passed through.
        """
        def new_func(s, x):
            s.mesh = x is self.conf.conf_parser['MESH']
            s.func_space = None

        with patch.object(read_config.MeshParser, 'parse', new_func):
            self.assertTrue(self.conf.get_mesh()[0])

    def test_correct_type(self):
        """
        Test that the mesh is a Mesh and that V is a FunctionSpace.
        """
        m, V = self.conf.get_mesh()
        self.assertIsInstance(m, MeshGeometry)
        self.assertIsInstance(V, FunctionSpace)


class TestGetParameters(TestCase):
    """
    Tests for the get_parameters method.
    """

    def setUp(self):
        """
        Define the config file and the Config object.
        """
        problems_dir = os.path.join(
            os.path.dirname(__file__), os.pardir, os.pardir, 'mock_problems')
        self.config_file = os.path.join(problems_dir,
                                        'be_box_nosource_steady.ini')
        self.conf = read_config.Config(self.config_file)

    def test_correct_parameters(self):
        """
        Test that the parameters section is correctly passed through.
        """
        def new_func(s, x):
            s.parameters['foo'] = x is self.conf.conf_parser['PARAMETERS']

        with patch.object(read_config.ParametersParser, 'parse', new_func):
            p = self.conf.get_parameters()
            self.assertTrue(p['foo'])

    def test_density_correct_type(self):
        """
        Test that the density is a Function.
        """
        p = self.conf.get_parameters()
        self.assertIsInstance(p['electron_density'], (Function, Constant, Sum))

    def test_coulomb_ln_correct_type(self):
        """
        Test that the coulomb_ln is a Function.
        """
        p = self.conf.get_parameters()
        self.assertIsInstance(p['coulomb_ln'], (Function, Constant, Sum))

    def test_ionisation_correct_type(self):
        """
        Test that ionisation is a Function.
        """
        p = self.conf.get_parameters()
        self.assertIsInstance(p['ionisation'], (Function, Constant, Sum))


class TestGetInitialVal(TestCase):
    """
    Tests for the get_initial_val method.
    """

    def setUp(self):
        """
        Define the config file and the Config object.
        """
        problems_dir = os.path.join(
            os.path.dirname(__file__), os.pardir, os.pardir, 'mock_problems')
        self.config_file = os.path.join(problems_dir,
                                        'be_box_nosource_steady.ini')
        self.conf = read_config.Config(self.config_file)

    def test_correct_initial_val(self):
        """
        Test that the initial value section is correctly passed through.
        """
        def new_func(s, x):
            s.initial_val = x is self.conf.conf_parser['INITIALVALUE']

        with patch.object(read_config.InitialValParser, 'parse', new_func):
            self.assertTrue(self.conf.get_initial_val())

    def test_correct_type(self):
        """
        Test that the initial val is a Function.
        """
        iv = self.conf.get_initial_val()
        self.assertIsInstance(iv, (Function, Constant, Sum))


class TestGetSolverParams(TestCase):
    """
    Tests for the get_solver_params method.
    """

    def setUp(self):
        """
        Define the config file and the Config object.
        """
        problems_dir = os.path.join(
            os.path.dirname(__file__), os.pardir, os.pardir, 'mock_problems')
        self.config_file = os.path.join(problems_dir,
                                        'be_box_nosource_steady.ini')
        self.conf = read_config.Config(self.config_file)

    def test_correct_solver(self):
        """
        Test that the solver section is correctly passed through.
        """
        def new_func(s, x):
            s.file_path = x is self.conf.conf_parser['SOLVER']

        with patch.object(read_config.SolverParser, 'parse', new_func):
            self.assertTrue(self.conf.get_solver_params()[0])

    def test_correct_types(self):
        """
        Test that the outputs are the expected type.
        """
        fp, m, p = self.conf.get_solver_params()
        self.assertIsInstance(fp, str)
        self.assertIsInstance(m, str)
        self.assertIsInstance(p, dict)


class TestGetPhysicsSettings(TestCase):
    """
    Tests for the get_physics_settings method.
    """

    def setUp(self):
        """
        Define the config file and the Config object.
        """
        problems_dir = os.path.join(
            os.path.dirname(__file__), os.pardir, os.pardir, 'mock_problems')
        self.config_file = os.path.join(problems_dir,
                                        'be_box_nosource_steady.ini')
        self.conf = read_config.Config(self.config_file)

    def test_correct_physics(self):
        """
        Test that the physics section is correctly passed through.
        """
        def new_func(s, x):
            s.limit_conductivity = x is self.conf.conf_parser['PHYSICS']

        with patch.object(read_config.PhysicsParser, 'parse', new_func):
            self.assertTrue(self.conf.get_physics_settings()[0])

    def test_correct_types(self):
        """
        Test that the outputs are the expected type.
        """
        lim_con, lim_flux = self.conf.get_physics_settings()
        self.assertIsInstance(lim_con, bool)
        self.assertIsInstance(lim_flux, bool)
