Supporting information for n-Bridges
==================================================

.. contents::
  :local:
  :depth: 3

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
.. _Mapping:

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

And **P**, **Q**, **R**, **S** are unique residue position numbers. A mathematical description of
the mapping algorithm can be found in the Algorithm_ section.

Mapping algorithm
--------------------------------------------------
.. _Algorithm:

The mapping algorithm assumes a cluster consisting of *CE*, *SD* and *CG* coordinates,
alongside three satellite points *S1*, *S2*, and *S3*. Here, the three satellite points
are the Cartesian coordinates describing the aromatic centroid in any of phenylalanine,
tyrosine or tryptophan. The algorithm starts by mapping the *CE*, *SD*, and *CG* subcluster
to a frame *F*, where *SD* is considered the origin:

.. raw:: html

    <p align="center">
        <img src="https://latex.codecogs.com/svg.latex?\begin{bmatrix}^{F}\textrm{CG}\\^{F}\textrm{SD}\\^{F}\textrm{CE}\end{bmatrix}=\begin{bmatrix}\textrm{CG}\\\textrm{SD}\\\textrm{CE}\end{bmatrix}-\textrm{SD}">
    </p>

The algorithm computes the direction cosine between the mapped *CE* coordinates and the *x* axis,

.. raw:: html

    <p align="center">
        <img src="https://latex.codecogs.com/svg.latex?\alpha=\cos^{-1}\frac{_{}^{F}{CE}\cdot\begin{bmatrix}1&0&0\end{bmatrix}}{\left\|_{}^{F}{CE}\right\|}">
    </p>

The algorithm also computes an axis of rotation (the Euler axis),

.. raw:: html

    <p align="center">
        <img src="https://latex.codecogs.com/svg.latex?\vec{u_1}={_{}^{F}{CE}}\times\begin{bmatrix}1&0&0\end{bmatrix}">
    </p>

All members of *F* are rotated into a new frame *G* using a quaternion operation **p**. For simplicity, **p** is defined here as:

.. raw:: html

    <p align="center">
        <img src="https://latex.codecogs.com/svg.latex?\textbf{p}(\vec{u_1},-\alpha)">
    </p>

And *G* is defined as:

.. raw:: html

    <p align="center">
        <img src="https://latex.codecogs.com/svg.latex?\begin{bmatrix}^{G}\textrm{CG}\\^{G}\textrm{SD}\\^{G}\textrm{CE}\end{bmatrix}=\begin{bmatrix}\textbf{p}^{F}\textrm{CG}\textbf{p}^{-1}\\\textbf{p}^{F}\textrm{SD}\textbf{p}^{-1}\\\textbf{p}^{F}\textrm{CE}\textbf{p}^{-1}\end{bmatrix}">
    </p>

This operation renders the *SD-CE* bond axis colinear with the *x* axis. The *CG* coordinates remain non-coplanar with the *xy* plane. The
angle between the *xy* and *CG-SD-CE* planes is obtained:

.. raw:: html

    <p align="center">
        <img src="https://latex.codecogs.com/svg.latex?\theta=\textrm{atan}^2(\textrm{CG}.z,\textrm{CG}.y)">
    </p>

A new Euler axis is defined as:

.. raw:: html

    <p align="center">
        <img src="https://latex.codecogs.com/svg.latex?\vec{u_2}=\begin{bmatrix}1&0&0\end{bmatrix}">
    </p>

And a new quaternion **q** is now defined:

.. raw:: html

    <p align="center">
        <img src="https://latex.codecogs.com/svg.latex?\textbf{q}(\vec{u_2},-\theta)">
    </p>

The rotation into the final frame *H* follows,

.. raw:: html

    <p align="center">
        <img src="https://latex.codecogs.com/svg.latex?\begin{bmatrix}^{H}\textrm{CG}\\^{H}\textrm{SD}\\^{H}\textrm{CE}\end{bmatrix}=\begin{bmatrix}\textbf{q}^{G}\textrm{CG}\textbf{q}^{-1}\\\textbf{q}^{G}\textrm{SD}\textbf{q}^{-1}\\\textbf{q}^{G}\textrm{CE}\textbf{q}^{-1}\end{bmatrix}">
    </p>

The *CG*, *SD*, and *CE* coordinate frame *H* will now be positioned according to the criteria set out in the Mapping_ section. The satellite
points *S1*, *S2*, and *S3* can be transformed into frame *H* by first mapping into frame *F*:

.. raw:: html

    <p align="center">
        <img src="https://latex.codecogs.com/svg.latex?\begin{bmatrix}^{F}\textrm{S}_1\\^{F}\textrm{S}_2\\^{F}\textrm{S}_3\end{bmatrix}=\begin{bmatrix}\textrm{S}_1\\\textrm{S}_2\\\textrm{S}_3\end{bmatrix}-\textrm{SD}">
    </p>

Then defining a new quaternion composition **r**:

.. raw:: html

    <p align="center">
        <img src="https://latex.codecogs.com/svg.latex?\textbf{r}=\textbf{q}\textbf{p}">
    </p>


Generating the bridge distributions
--------------------------------------------------
To generate the bar chart describing the distribution of the 3-bridges, run:

.. code-block::

    make dist

This ``make`` target will generate the ``./*/plots/distribution.png`` plot.

Generating convex hulls for all 10 3-bridge permutations
--------------------------------------------------
To generate the 10 convex hulls for all possible 3-bridge permutations, run:

.. code-block::

    make convex-groupby

This ``make`` target will generate the ``./*/plots/(phe|tyr|trp)(phe|tyr|trp)(phe|tyr|trp)_bridges_3d.png`` plots. There
exist 10 combinations owing to the following:

.. raw:: html

    <p align="center">
        <img src="https://latex.codecogs.com/svg.latex?\frac{(r&plus;n-1)!}{(n-1)r!}">
    </p>

Where *n* = 3, given that Nature can choose from one of PHE, TYR or TRP and *r* = 3 corresponding
to a 3-bridge.

Generating the convex hulls
--------------------------------------------------
To generate three convex hulls depicting the spatial distribution of one of PHE, TYR, or TRP, run:

.. code-block::

    make convex

This ``make`` target will generate the ``./*/plots/(phe|tyr|trp)_bridges_3d.png`` plots.
