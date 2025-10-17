# magmaOpt


### Installation instructions

This code relies on

```
pip install meshio[all]
conda install -c conda-forge meshio
```

(`[all]` pulls in all optional dependencies. By default, meshio only uses numpy.)
You can then use the command-line tool

<!--pytest-codeblocks:skip-->

```sh
meshio convert    input.msh output.vtk   # convert between two formats

meshio info       input.xdmf             # show some info about the mesh

meshio compress   input.vtu              # compress the mesh file
meshio decompress input.vtu              # decompress the mesh file

meshio binary     input.msh              # convert to binary format
meshio ascii      input.msh              # convert to ASCII format
```

with any of the supported formats.

In Python, simply do

<!--pytest-codeblocks:skip-->

```python
import meshio

mesh = meshio.read(
    filename,  # string, os.PathLike, or a buffer/open file
    # file_format="stl",  # optional if filename is a path; inferred from extension
    # see meshio-convert -h for all possible formats
)
# mesh.points, mesh.cells, mesh.cells_dict, ...

# mesh.vtk.read() is also possible
```

to read a mesh. To write, do

```python
import meshio

# two triangles and one quad
points = [
    [0.0, 0.0],
    [1.0, 0.0],
    [0.0, 1.0],
    [1.0, 1.0],
    [2.0, 0.0],
    [2.0, 1.0],
]
cells = [
    ("triangle", [[0, 1, 2], [1, 3, 2]]),
    ("quad", [[1, 4, 5, 3]]),
]

mesh = meshio.Mesh(
    points,
    cells,
    # Optionally provide extra data on points, cells, etc.
    point_data={"T": [0.3, -1.2, 0.5, 0.7, 0.0, -3.0]},
    # Each item in cell data must match the cells array
    cell_data={"a": [[0.1, 0.2], [0.4]]},
)
mesh.write(
    "foo.vtk",  # str, os.PathLike, or buffer/open file
    # file_format="vtk",  # optional if first argument is a path; inferred from extension
)

# Alternative with the same options
meshio.write_points_cells("foo.vtk", points, cells)
```

For both input and output, you can optionally specify the exact `file_format`
(in case you would like to enforce ASCII over binary VTK, for example).

#### Time series

The [XDMF format](https://xdmf.org/index.php/XDMF_Model_and_Format) supports
time series with a shared mesh. You can write times series data using meshio
with

<!--pytest-codeblocks:skip-->

```python
with meshio.xdmf.TimeSeriesWriter(filename) as writer:
    writer.write_points_cells(points, cells)
    for t in [0.0, 0.1, 0.21]:
        writer.write_data(t, point_data={"phi": data})
```

and read it with

<!--pytest-codeblocks:skip-->

```python
with meshio.xdmf.TimeSeriesReader(filename) as reader:
    points, cells = reader.read_points_cells()
    for k in range(reader.num_steps):
        t, point_data, cell_data = reader.read_data(k)
```

### ParaView plugin

<img alt="gmsh paraview" src="https://nschloe.github.io/meshio/gmsh-paraview.png" width="60%">
*A Gmsh file opened with ParaView.*

If you have downloaded a binary version of ParaView, you may proceed as follows.

- Install meshio for the Python major version that ParaView uses (check `pvpython --version`)
- Open ParaView
- Find the file `paraview-meshio-plugin.py` of your meshio installation (on Linux:
  `~/.local/share/paraview-5.9/plugins/`) and load it under _Tools / Manage Plugins / Load New_
- _Optional:_ Activate _Auto Load_

You can now open all meshio-supported files in ParaView.

### Performance comparison

The comparisons here are for a triangular mesh with about 900k points and 1.8M
triangles. The red lines mark the size of the mesh in memory.

#### File sizes

<img alt="file size" src="https://nschloe.github.io/meshio/filesizes.svg" width="60%">

#### I/O speed

<img alt="performance" src="https://nschloe.github.io/meshio/performance.svg" width="90%">

#### Maximum memory usage

<img alt="memory usage" src="https://nschloe.github.io/meshio/memory.svg" width="90%">

### Installation

meshio is [available from the Python Package Index](https://pypi.org/project/meshio/),
so simply run

```
pip install meshio
```

to install.

Additional dependencies (`netcdf4`, `h5py`) are required for some of the output formats
and can be pulled in by

```
pip install meshio[all]
```

You can also install meshio from [Anaconda](https://anaconda.org/conda-forge/meshio):

```
conda install -c conda-forge meshio
```

### Testing

To run the meshio unit tests, check out this repository and type

```
tox
```

### License

meshio is published under the [MIT license](https://en.wikipedia.org/wiki/MIT_License).
