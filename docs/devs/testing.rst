

Testing
=======

All tests for TTiP are done using pytest and are automated through github
actions. Coverage is monitored using codecov.

Tests
^^^^^
Currently, the only testing in TTiP is unit testing.
Most functions in the code are supported by multiple tests to cover every input
permutation. Some functions are declaritive and are not tested as this would
likely lead to code being duplicated in the tests.

Linting
^^^^^^^
All source code is ran through both pylint and flake8 to enfore coding
standards. This is done as a github action before pull requests are merged.

Coverage
^^^^^^^^
The coverage is calculated once the tests suite completes. When new code is
added, coverage should be considered and tests added.
