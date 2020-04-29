"""
This is the main entrypoint for TTiP, and can be used as a script or
entrypoint.
"""
import argparse
import sys
import time

from scipy.constants import e

from TTiP.core.problem import SteadyStateProblem, TimeDependantProblem
from TTiP.core.read_config import Config
from TTiP.core.solver import Solver
from TTiP.util.logger import setup_logger


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
    logger = setup_logger(debug=debug)

    logger.info('Running TTiP on %s', config_file)
    config = Config(config_file)

    logger.info('Setting up the problem.')
    start_time = time.time()
    logger.debug('Building mesh..')
    # Setup mesh and function space
    mesh, V = config.get_mesh()

    # Get parameters
    density, coulomb_ln, Z = config.get_parameters()

    logger.debug('Setting timescales..')
    # Set up timescale
    steps, dt, t_max = config.get_time()
    if steps is None and dt is None and t_max is None:
        problem = SteadyStateProblem(mesh=mesh, V=V)
    else:
        problem = TimeDependantProblem(mesh=mesh, V=V)
        problem.set_timescale(steps=steps, dt=dt, t_max=t_max)

        # Set time dependant parameters
        problem.set_density(density)

        problem.enable_flux_limiting()

    # Set up other parameters
    problem.set_coulomb_ln(coulomb_ln)
    problem.set_Z(Z)

    logger.debug('Building sources..')
    # Set up source
    source = config.get_sources()
    problem.set_S(source)

    logger.debug('Building boundary conditions..')
    # Set up boundary conditions
    bcs = config.get_boundary_conds()
    for bc in bcs:
        problem.add_boundary(**bc)
    if not bcs:
        problem.set_no_boundary()

    logger.debug('Building initial value..')
    # Set up initial value
    initial_val = config.get_initial_val()
    problem.T.assign(initial_val)

    logger.info('Problem set up (%.1fs)', time.time() - start_time)
    logger.info('Running the solve.')
    start_time = time.time()

    # Solve
    file_path, method, params = config.get_solver_params()
    try:
        problem.set_method(method, **params)
    except AttributeError:
        pass

    solver = Solver(problem)
    solver.solve(file_path=file_path)
    logger.info('Success (%.1fs) - Results are stored in: %s',
                time.time() - start_time, file_path)


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
