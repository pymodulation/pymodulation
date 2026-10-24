************
Installation
************

.. note::

    Python 3.12 is used to run the library tests in continuous integration. Compatibility with earlier Python versions has not been validated!

Installing from PyPI
====================

Install the published package from PyPI [1]_:

.. code-block:: bash

    python -m pip install pymodulation

Installing from Source
======================

Clone the Git repository [2]_ and install the library from its root directory:

.. code-block:: bash

    git clone https://github.com/pymodulation/pymodulation.git
    cd pymodulation
    python -m pip install .

Development Installation
========================

From the repository root, install in editable mode with dependencies for tests,
examples and documentation:

.. code-block:: bash

    python -m pip install -e ".[test,examples,docs]"

Editable mode makes local source changes available without reinstalling. Optional dependency groups can also be installed individually, for example
``python -m pip install -e ".[examples]"``.

Building the Documentation
==========================

To install only the library and its documentation dependencies, run the following
command from the repository root:

.. code-block:: bash

    python -m pip install ".[docs]"

Build the HTML documentation with Sphinx:

.. code-block:: bash

    python -m sphinx -W --keep-going -b html docs /tmp/pymodulation-docs

Open ``/tmp/pymodulation-docs/index.html`` to view the result.

References
==========

.. [1] https://pypi.org/project/pymodulation/
.. [2] https://github.com/pymodulation/pymodulation
