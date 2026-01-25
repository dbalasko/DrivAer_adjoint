## Only used to visualise FFD points in paraview, importing as .xyz or plot3d wasn't working\
# Written by claude, don't necessarily trust

import numpy as np
from pyevtk.hl import gridToVTK

def readPlot3D(filename):
    """Read Plot3D format FFD file"""
    with open(filename, 'r') as f:
        # Read number of blocks
        nBlocks = int(f.readline().strip())
        
        # Read dimensions
        dims = f.readline().strip().split()
        nx, ny, nz = int(dims[0]), int(dims[1]), int(dims[2])
        
        # Read X coordinates
        x = []
        for line in f:
            if line.strip():
                x.extend([float(v) for v in line.strip().split()])
                if len(x) >= nx*ny*nz:
                    break
        x = np.array(x[:nx*ny*nz]).reshape((nz, ny, nx))
        
        # Read Y coordinates
        y = []
        for line in f:
            if line.strip():
                y.extend([float(v) for v in line.strip().split()])
                if len(y) >= nx*ny*nz:
                    break
        y = np.array(y[:nx*ny*nz]).reshape((nz, ny, nx))
        
        # Read Z coordinates
        z = []
        for line in f:
            if line.strip():
                z.extend([float(v) for v in line.strip().split()])
                if len(z) >= nx*ny*nz:
                    break
        z = np.array(z[:nx*ny*nz]).reshape((nz, ny, nx))
        
    return x, y, z

# Convert
x, y, z = readPlot3D('boxcpsBsplines0.xyz')

# Write VTK
gridToVTK(
    './boxcpsBsplines0',
    x, y, z
)

print("Converted to FFD_grid.vts - open this in ParaView!")
