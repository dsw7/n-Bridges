Supporting information for n-Bridges
==================================================
Code for the following publication:

- *TBD*

Basic sequence of events
--------------------------------------------------

Step 1 - Finding 3-bridges
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The first step of this project involved finding 3-bridges using the following dataset consisting of
low redundancy PDB entries:

.. code-block:: bash

   data/low_redundancy_delimiter_list.csv

The 3-bridges were found using the `MetAromatic <https://github.com/dsw7/MetAromatic>`_ project. First, the project's ``runner.ini`` was modified as follows:

.. code-block:: ini

    [root-configs]

    # Cutoff for the distance condition
    cutoff-distance=6.0

    # Cutoff for the angular condition
    cutoff-angle=360.00

    # Which chain to target in a PDB entry
    chain=A

    # Which cross product interpolation model to use
    # Valid models are cp (Cross Product) or rm (Rodrigues Method)
    model=cp

For details regarding these constraints, please see the `MetAromatic <https://github.com/dsw7/MetAromatic>`_ project README, specifically the sections describing the distance
and angular conditions. Next, a batch job was run as follows:

.. code-block:: bash

    $ /path/to/MetAromatic/runner.py batch --threads 5 \
    --database <mongodb-database-name> \
    --collection <mongodb-collection-name> \
    /path/to/data/low_redundancy_delimiter_list.csv
