import numpy as np
import sys

def writeFFDFile(fileName,nBlocks,nx,ny,nz,points):
    '''
    Take in a set of points and write the plot 3dFile
    '''
    f = open(fileName,'w')
    f.write('%d\n'%nBlocks)
    for i in range(nBlocks):
        f.write('%d %d %d '%(nx[i],ny[i],nz[i]))
    f.write('\n')
    for block in range(nBlocks):
        for k in range(nz[block]):
            for j in range(ny[block]):
                for i in range(nx[block]):
                    f.write('%f '%points[block][i,j,k,0])
        f.write('\n')
        for k in range(nz[block]):
            for j in range(ny[block]):
                for i in range(nx[block]):
                    f.write('%f '%points[block][i,j,k,1])
        f.write('\n')
        for k in range(nz[block]):
            for j in range(ny[block]):
                for i in range(nx[block]):
                    f.write('%f '%points[block][i,j,k,2])
    f.close()
    return

def returnBlockPoints(corners,nx,ny,nz):
    '''
    corners needs to be 8 x 3
    Corner ordering:
    0: xMin, yMin, zMin
    1: xMax, yMin, zMin
    2: xMax, yMin, zMax
    3: xMin, yMin, zMax
    4: xMin, yMax, zMin
    5: xMax, yMax, zMin
    6: xMax, yMax, zMax
    7: xMin, yMax, zMax
    '''
    points = np.zeros([nx,ny,nz,3])
    
    for idim in range(3):
        # Create edges in Z direction (at the 4 corners of bottom/top faces)
        edge_yMin_xMin = np.linspace(corners[0][idim], corners[3][idim], nz)  # Bottom-left edge
        edge_yMin_xMax = np.linspace(corners[1][idim], corners[2][idim], nz)  # Bottom-right edge
        edge_yMax_xMin = np.linspace(corners[4][idim], corners[7][idim], nz)  # Top-left edge
        edge_yMax_xMax = np.linspace(corners[5][idim], corners[6][idim], nz)  # Top-right edge
        
        for k in range(nz):
            # For this Z position, interpolate in X direction at yMin and yMax
            edge_yMin = np.linspace(edge_yMin_xMin[k], edge_yMin_xMax[k], nx)
            edge_yMax = np.linspace(edge_yMax_xMin[k], edge_yMax_xMax[k], nx)
            
            for i in range(nx):
                # For this X,Z position, interpolate in Y direction
                edge_y = np.linspace(edge_yMin[i], edge_yMax[i], ny)
                points[i,:,k,idim] = edge_y
    
    return points

################ FFD ##############
nBlocks = 1
nx = [10]
ny = [6]
nz = [6]
corners = np.zeros([nBlocks,8,3])
xMin, yMin, zMin = 1.53, 0.5, 0.0
xMax, yMax, zMax = 4.2, 1.2, 1.0
dx = xMax - xMin
dy = yMax - yMin
dz = zMax - zMin
margin = 0.05

corners[0,0,:] = [xMin - margin*dx, yMin - margin*dy, zMin - margin*dz]  # 0
corners[0,1,:] = [xMax + margin*dx, yMin - margin*dy, zMin - margin*dz]  # 1
corners[0,2,:] = [xMax + margin*dx, yMin - margin*dy, zMax + margin*dz]  # 2
corners[0,3,:] = [xMin - margin*dx, yMin - margin*dy, zMax + margin*dz]  # 3
corners[0,4,:] = [xMin - margin*dx, yMax + margin*dy, zMin - margin*dz]  # 4
corners[0,5,:] = [xMax + margin*dx, yMax + margin*dy, zMin - margin*dz]  # 5
corners[0,6,:] = [xMax + margin*dx, yMax + margin*dy, zMax + margin*dz]  # 6
corners[0,7,:] = [xMin - margin*dx, yMax + margin*dy, zMax + margin*dz]  # 7

points = []
for block in range(nBlocks):
    points.append(returnBlockPoints(corners[block],nx[block],ny[block],nz[block]))

fileName = 'boxcpsBsplines0.xyz'
writeFFDFile(fileName,nBlocks,nx,ny,nz,points)

print(f"FFD file written: {fileName}")
print(f"Total points: {nx[0]} x {ny[0]} x {nz[0]} = {nx[0]*ny[0]*nz[0]}")
