"""
Code to create a copy of the fully documented example config file for the user
to edit.
"""

import inspect
import os
import shutil

from TTiP import resources
from TTiP.util.logger import setup_logger

LOGGER = setup_logger()


def gen_conf():
    """
    Create a copy of the config file, in the working directory.
    This will create a new file called new_conf.ini.
    If this exists it will try new_conf1.ini, new_conf2.ini, ... until a free
    name is found.
    """
    # Select name.
    name = 'new_conf{}.ini'
    count_str = ''
    count = 0

    while os.path.exists(name.format(count_str)):
        count += 1
        count_str = str(count)

    name = name.format(count_str)

    # Find default config
    conf_dir = os.path.dirname(inspect.getfile(resources))
    conf_file = os.path.join(conf_dir, 'default_config.ini')

    # Copy
    shutil.copyfile(conf_file, name)
    LOGGER.info('New config file created: %s', name)
