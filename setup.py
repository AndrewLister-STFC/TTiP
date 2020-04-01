from setuptools import setup, find_packages

kwargs = {'name': 'TTiP',
          'version': '0.0',
          'description': 'Thermal Transport in Plasma - A solver for heat flow'
                         ' problems developed for use within the field of '
                         'plasma physics.',
          'author': 'Andrew Lister',
          'url': 'http://github.com/AndrewLister-STFC/TTiP'
          }

entry_points = {'console_scripts': ['ttip = TTiP.cli.main:main']}
packages = find_packages(exclude=('*mock*', '*test*'))
package_data = {'TTiP': ['resources/default_config.ini']}

kwargs['entry_points'] = entry_points
kwargs['packages'] = packages
kwargs['package_data'] = package_data

setup(**kwargs)
