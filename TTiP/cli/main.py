"""
This is the main entrypoint for TTiP, and can be used as a script or
entrypoint.
"""
import argparse
import sys
import time

from TTiP.cli.gen_conf import gen_conf
from TTiP.core.problem import create_problem_class
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
                        help='Path to problem definition config file.',
                        nargs='?')
    parser.add_argument('-g', '--gen_conf',
                        action='store_true',
                        help='Generate a clean config file with documented'
                             ' options.')

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
    params = config.get_parameters()
    constant_ionisation = 'ionisation' in params

    logger.debug('Setting timescales..')
    # Set up timescale
    steps, dt, max_t = config.get_time()
    time_dep = (steps is not None or dt is not None or max_t is not None)

    limit_conductivity, limit_flux = config.get_physics_settings()

    ProblemClass = create_problem_class(
        time_dep=time_dep,
        sh_conductivity=True,
        constant_ionisation=constant_ionisation,
        limit_flux=limit_flux,
        limit_conductivity=limit_conductivity)

    problem = ProblemClass(mesh, V)

    if time_dep:
        problem.set_timescale(steps=steps, dt=dt, max_t=max_t)

    # Set up parameters
    ignored = []
    for name, value in params.items():
        try:
            problem.set_function(name, value)
        except AttributeError:
            ignored.append(name)

    if ignored:
        logger.info('Ignoring unnecesary parameters: %s', ', '.join(ignored))

    logger.debug('Building sources..')
    # Set up source
    source = config.get_sources()
    problem.set_function('S', source)

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

    if args.gen_conf:
        gen_conf()
        return

    run(config_file=args.config, debug=args.debug)


if __name__ == '__main__':
    main()
