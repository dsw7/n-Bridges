Supporting information for n-Bridges
==================================================
Code for the following publication:

- *TBD*

Basic sequence of events
--------------------------------------------------

Step 1 - Finding low redundancy methionine-aromatic interactions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The first step of this project involved finding methionine-aromatic interactions using the following dataset consisting of
low redundancy PDB entries:

.. code-block:: bash

    data/low_redundancy_delimiter_list.csv

The methionine-aromatic interactions were found using the `MetAromatic <https://github.com/dsw7/MetAromatic>`_ project. First, the project's ``runner.ini`` was modified as follows:

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

Here, the data was dumped into a MongoDB database.

Step 2 - Finding 3-Bridges
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Methionine-aromatic interactons banked in Step 1 were then processed using a modified `NetworkX <https://networkx.org/>`_ script for finding bridging interactions in
the `MetAromatic <https://github.com/dsw7/MetAromatic>`_ project. The following file was obtained:

.. code-block:: bash

    data/3bridges_codes.csv

This file consists of low redundancy PDB stuctures containing one or more 3-bridges.

Step 3 - Isolating 3-Bridges and other relevant data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Next, the data in Step 2 was further processed to only include the following:

- Methionine: *x, y, z* coordinates for **CE**, **SD** and **CG** coordinates
- Aromatics: *x, y, z* coordinates for the aromatic centroids in any of **PHE**, **TYR**, or **TRP**

Step 4 - Mapping
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In the last step, the data in Step 3 was mapped following:

- The methionine **SD** coordinate was mapped to the *x, y, z* coordinates (0, 0, 0)
- The methionine **SD-CE** bond axis was render co-linear with the vector (1, 0, 0)
- The methionine **CG-SD-CE** plane was rendered coplanar with the *xy* plane

All mappings were loaded into the following JSON file:

.. code-block:: bash

    data/n_3_bridge_transformations.json

An example entry in the JSON is of form:

.. code-block::

    {
            "MET95" : [
                    [
                            0,
                            0,
                            0
                    ],
                    [
                            1.7932899932805066,
                            -1.0617213491997201e-16,
                            3.245657730897657e-17
                    ],
                    [
                            2.0502975055774364,
                            1.8305685287972522,
                            -8.881784197001252e-16
                    ]
            ],
            "TYR68" : [
                    4.3213069436828375,
                    4.585365158685238,
                    -1.7532318471879298
            ],
            "PHE99" : [
                    1.3596593463055182,
                    4.299250047200179,
                    3.4900506792385304
            ],
            "TYR90" : [
                    5.783357705034454,
                    0.6692003627477932,
                    2.5985457048350815
            ],
            "code" : "8I1B"
    }

Where the individual fields match:

.. code-block::

    {
        MET<P>: [
            SD_coordinates: [x, y, z],
            CE_coordinates: [x, y, z],
            CG_coordinates: [x, y, z]
        ],
        <PHE|TYR|TRP><Q>: [x, y, z],
        <PHE|TYR|TRP><R>: [x, y, z],
        <PHE|TYR|TRP><S>: [x, y, z]
        code: [pdb-code]
    }

And **P**, **Q**, **R**, **S** are unique residue position numbers.

Generating the bridge distributions
--------------------------------------------------
To generate the bar chart describing the distribution of the 3-bridges, run:

.. code-block::

    make dist

Which will yield the ``distribution.png`` file:

.. raw:: html

    <p align="center">
        <img src="distributions/distribution.png" width="600" height="500">
    </p>

Generating the convex hulls
--------------------------------------------------
To generate the three convex hulls in this project, run:

.. code-block::

    make convex

Which field yield the convex hulls for the phenylalanine satellites:

.. raw:: html

    <p align="center">
        <img src="convex_hulls/phe_bridges_3d.png">
    </p>

And the tyrosine satellites:

.. raw:: html

    <p align="center">
        <img src="convex_hulls/tyr_bridges_3d.png">
    </p>

And last the tryptophan satellites:

.. raw:: html

    <p align="center">
        <img src="convex_hulls/trp_bridges_3d.png">
    </p>
