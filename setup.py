from setuptools import find_packages, setup

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
install_requires = ['scipy',
                    'numpy']

kwargs['entry_points'] = entry_points
kwargs['packages'] = packages
kwargs['package_data'] = package_data
kwargs['install_requires'] = install_requires

setup(**kwargs)
