#!/bin/bash

if [ -z "$WM_PROJECT" ]; then
  echo "OpenFOAM environment not found, forgot to source the OpenFOAM bashrc?"
  exit
fi

# pre-processing

# generate mesh
echo "Generating block mesh.."
blockMesh #>> log.meshGeneration
echo "Extracting surface geometry"
surfaceFeatureExtract #>> log.meshGeneration

# Import tesla geometry & mesh in parallel
decomposePar #>> log.meshGeneration
## foamJob -parallel -screen snappyHexMesh #>> log.meshGeneration
mpirun -np 32 snappyHexMesh -parallel 
reconstructParMesh -latestTime #>> log.meshGeneration
echo "Reconstructed parallel mesh"

# Copy mesh
rm -rf constant/polyMesh
cp -r 3/polyMesh constant/

# Tidy up directory
rm -rf processor* 1 2 3

renumberMesh -overwrite #>> log.meshGeneration
echo "Generating mesh.. Done!"

# copy initial and boundary condition files
cp -r 0.orig 0
