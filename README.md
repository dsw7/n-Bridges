# Supporting information for n-Bridges
Code for the following publications:

* Curtis A. Gibbs; David S. Weber; and Jeffrey J. Warren. Clustering of Aromatic Amino Acid Residues around
  Methionine in Proteins. *Biomolecules*. **2022**, *12* (1), 6.

## Table of Contents
- [Finding 3-bridges](#finding-3-bridges)
  - [Preparing dependencies](#preparing-dependencies)
  - [Getting bridging interactions](#getting-bridging-interactions)
  - [Mapping the interactions](#mapping-the-interactions)
  - [Data storage](#data-storage)
- [Mapping algorithm](#mapping-algorithm)
- [Generating the bridge distributions](#generating-the-bridge-distributions)
- [Generating convex hulls for all 10 3-bridge permutations](#generating-convex-hulls-for-all-10-3-bridge-permutations)
- [Generating the convex hulls](#generating-the-convex-hulls)

## Finding 3-bridges
### Preparing dependencies
The [MetAromatic](https://github.com/dsw7/MetAromatic) package was leveraged in order to make this research
possible. First, the project was cloned:

```bash
git clone https://github.com/dsw7/MetAromatic.git
```

Next, the project was built from source:

```bash
cd MetAromatic && make install
```

This exposed some of the MetAromatic project's utilities for use in the
`get_n_3_bridge_transformations_json.py` script.

### Getting bridging interactions
A short script, `get_n_3_bridge_transformations_json.py`, located under the `data` directory, was written
to mine bridging interactions using a `.csv` of low redundancy PDB entries:

```bash
data/low_redundancy_delimiter_list.csv
```

This script isolated the following coordinates for any members participating in a 3-bridging interaction:

* Methionine: $x$, $y$, $z$ coordinates for $CE$, $SD$ and $CG$ coordinates
* Aromatics: $x$, $y$, $z$ coordinates for the aromatic centroids in any of **PHE**, **TYR**, or **TRP**

### Mapping the interactions
The isolated 3-bridge data was then subjected to the following transformations:

* The methionine $SD$ coordinate was mapped to the $x$, $y$, $z$ coordinates $(0, 0, 0)$
* The methionine $SD-CE$ bond axis was transformed collinear with the vector $<1, 0, 0>$
* The methionine $CG-SD-CE$ plane was transformed coplanar with the $xy$ plane

A more rigorous mathematical description of the mapping algorithm can be found in the [Mapping
algorithm](#mapping-algorithm) section.

### Data storage
The mapped coordinates were loaded into a MongoDB collection. An example MongoDB document for `8I1B` can be
seen below:

```javascript
{
    "MET95" : [
        [
            0,                       // The SD coordinates mapped to (0, 0, 0)
            0,
            0
        ],
        [
            1.7932899932805066,      // The SD-CE bond axis: Collinear with <1, 0, 0>
            -1.0617213491997201e-16,
            3.245657730897657e-17
        ],
        [
            2.0502975055774364,      // The SD-CG bond axis: Coplanar with the xy-plane
            1.8305685287972522,
            -8.881784197001252e-16
        ]
    ],
    "TYR68" : [
        4.3213069436828375,          // The centroid coordinates of the first satellite
        4.585365158685238,
        -1.7532318471879298
    ],
    "PHE99" : [
        1.3596593463055182,          // The centroid coordinates of the second satellite
        4.299250047200179,
        3.4900506792385304
    ],
    "TYR90" : [
        5.783357705034454,           // The centroid coordinates of the third satellite
        0.6692003627477932,
        2.5985457048350815
    ],
    "code" : "8I1B"
}
```
A JSON file was generated from the collection via `mongoexport`:

```bash
data/n_3_bridge_transformations.json
```

This file was used for all downstream visualizations.

## Mapping algorithm
The mapping algorithm assumes a cluster consisting of $CE$, $SD$ and $CG$ coordinates, alongside three
satellite points $S1$, $S2$, and $S3$. Here, the three satellite points are the Cartesian coordinates
describing the aromatic centroid in any of phenylalanine, tyrosine or tryptophan. The algorithm starts by
mapping the $CE$, $SD$, and $CG$ subcluster to a frame $F$, where $SD$ is considered the origin:

$$
\begin{bmatrix}
    ^{F}\textrm{CG}\\
    ^{F}\textrm{SD}\\
    ^{F}\textrm{CE}
\end{bmatrix} = \begin{bmatrix}
    \textrm{CG}\\
    \textrm{SD}\\
    \textrm{CE}
\end{bmatrix} - \textrm{SD}
$$

The algorithm computes the direction cosine between the mapped $CE$ coordinates and the $x$ axis,

$$
\alpha = \cos^{-1} \frac
{
    \_{}^{F} {\textrm{CE}} \cdot \begin{bmatrix}1 & 0 & 0\end{bmatrix}
}
{
    \lVert \_{}^{F}{\textrm{CE}} \rVert
}
$$

The algorithm also computes an axis of rotation (the Euler axis),

$$
\vec{u\_1} = {\_{}^{F}{\textrm{CE}}} \times \begin{bmatrix}1 & 0 & 0\end{bmatrix}
$$

All members of $F$ are rotated into a new frame $G$ using a quaternion operation **p**. For simplicity, **p**
is defined here as:

$$
\textbf{p}(\vec{u\_1}, -\alpha)
$$

And $G$ is defined as:

$$
\begin{bmatrix}
    ^{G}\textrm{CG}\\
    ^{G}\textrm{SD}\\
    ^{G}\textrm{CE}
\end{bmatrix} = \begin{bmatrix}
    \textbf{p}^{F}\textrm{CG}\textbf{p}^{-1}\\
    \textbf{p}^{F}\textrm{SD}\textbf{p}^{-1}\\
    \textbf{p}^{F}\textrm{CE}\textbf{p}^{-1}
\end{bmatrix}
$$

This operation renders the $SD-CE$ bond axis colinear with the $x$ axis. The $CG$ coordinates remain
non-coplanar with the $xy$ plane. The angle between the $xy$ and $CG-SD-CE$ planes is obtained:

$$
\theta = \textrm{atan}2(\textrm{CG}.z, \textrm{CG}.y)
$$

A new Euler axis is defined as:

$$
\vec{u\_2} = \begin{bmatrix}1 & 0 & 0\end{bmatrix}
$$

And a new quaternion **q** is now defined:

$$
\textbf{q}(\vec{u\_2}, -\theta)
$$

The rotation into the final frame $H$ follows,

$$
\begin{bmatrix}
    ^{H}\textrm{CG}\\
    ^{H}\textrm{SD}\\
    ^{H}\textrm{CE}
\end{bmatrix} = \begin{bmatrix}
    \textbf{q}^{G}\textrm{CG}\textbf{q}^{-1}\\
    \textbf{q}^{G}\textrm{SD}\textbf{q}^{-1}\\
    \textbf{q}^{G}\textrm{CE}\textbf{q}^{-1}
\end{bmatrix}
$$

The $CG$, $SD$, and $CE$ coordinate frame $H$ will now be positioned according to the criteria set out in the
Mapping_ section. The satellite points $S1$, $S2$, and $S3$ can be transformed into frame $H$ by first mapping
into frame $F$:

$$
\begin{bmatrix}
    ^{F}\textrm{S}_1\\
    ^{F}\textrm{S}_2\\
    ^{F}\textrm{S}_3
\end{bmatrix} = \begin{bmatrix}
    \textrm{S}_1\\
    \textrm{S}_2\\
    \textrm{S}_3
\end{bmatrix} - \textrm{SD}
$$

Then defining a new quaternion composition **r**:

$$
\textbf{r} = \textbf{q}\textbf{p}
$$

The satellites can be mapped to $H$ by applying the quaternion operation,

$$
\begin{bmatrix}
    ^{H}\textrm{S}_1\\
    ^{H}\textrm{S}_2\\
    ^{H}\textrm{S}_3
\end{bmatrix} = \begin{bmatrix}
    \textbf{r}^{F}\textrm{S}_1\textbf{r}^{-1}\\
    \textbf{r}^{F}\textrm{S}_2\textbf{r}^{-1}\\
    \textbf{r}^{F}\textrm{S}_3\textbf{r}^{-1}
\end{bmatrix}
$$

Which summarizes the procedure for all six coordinates in a 3-bridge cluster.

## Generating the bridge distributions
To generate the bar chart describing the distribution of the 3-bridges, run:

```
make dist
```

This `make` target will generate the `./*/plots/distribution.png` plot.

## Generating convex hulls for all 10 3-bridge permutations
To generate the 10 convex hulls for all possible 3-bridge permutations, run:

```
make convex-groupby
```

This `make` target will generate the `./*/plots/(phe|tyr|trp)(phe|tyr|trp)(phe|tyr|trp)_bridges_3d.png`
plots. There exist 10 combinations owing to the following:

\frac{(r&plus;n-1)!}{(n-1)r!}

Where $n$ = 3, given that Nature can choose from one of PHE, TYR or TRP and $r$ = 3 corresponding
to a 3-bridge.

## Generating the convex hulls
To generate three convex hulls depicting the spatial distribution of one of PHE, TYR, or TRP, run:

```
make convex
```

This `make` target will generate the `./*/plots/(phe|tyr|trp)_bridges_3d.png` plots.
