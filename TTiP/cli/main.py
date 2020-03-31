"""
This is the main entrypoint for TTiP, and can be used as a script or
entrypoint.
"""
import argparse
import sys

from scipy.constants import e

from firedrake import FunctionSpace
from TTiP.core.problem import SteadyStateProblem, TimeDependantProblem
from TTiP.core.read_config import Config
from TTiP.core.solver import Solver


def get_argparser():
    """
    Get the argparser.

    Returns:
        ArgumentParser: The object that will handle command line arguments.
    """
    epilog = '''Usage Examples:
    $ ttip my_problem.ini
    $ ttip -d myproblem.ini
    '''

    parser = argparse.ArgumentParser(
        prog='TTiP', add_help=True, epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help='Run in debug mode')
    parser.add_argument('config',
                        nargs=1,
                        help='Path to problem definition config file.')

    return parser


def run(config_file, debug=False):
    """
    Run the solve on the given problem definition config file.

    Args:
        config_file (string): The path to the config file to run.
        debug (bool, optional): Print debug output. Defaults to False.
    """
    # pylint: disable=too-many-locals

    config = Config(config_file)

    # Setup mesh
    mesh = config.get_mesh()

    # Setup function space
    V = FunctionSpace(mesh, 'CG', 1)

    # Set up timescale
    steps, dt, t_max = config.get_time()
    if steps is None and dt is None and t_max is None:
        problem = SteadyStateProblem(mesh=mesh, V=V)
    else:
        problem = TimeDependantProblem(mesh=mesh, V=V)
        problem.set_timescale(steps=steps, dt=dt, t_max=t_max)

    # Set up parameters
    density = config.get_parameters()
    C = 1.5*e*density
    problem.set_C(C)

    # Set up source
    source = config.get_sources()
    problem.set_S(source)

    # Set up boundary conditions
    bcs = config.get_boundary_conds()
    for bc in bcs:
        problem.add_boundary(**bc)
    if not bcs:
        problem.set_no_boundary()

    # Set up initial value
    initial_val = config.get_inital_val()
    problem.T.assign(initial_val)

    # Solve
    file_path, method, params = config.get_solver_params()
    solver = Solver(problem)
    solver.solve(file_path=file_path, method=method, **params)


def main():
    """
    Parse command line arguments and call run.
    """
    parser = get_argparser()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args(sys.argv[1:])

    run(config_file=args.config, debug=args.debug)


if __name__ == '__main__':
    main()
