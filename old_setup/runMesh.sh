#!/bin/bash
cd "${0%/*}" || exit 1    # Run from this directory

echo "=========================================="
echo "Step 1: Running blockMesh"
echo "=========================================="
blockMesh | tee log.blockMesh

if [ ! -d "constant/polyMesh" ]; then
    echo "ERROR: blockMesh failed!"
    exit 1
fi

echo ""
echo "=========================================="
echo "Step 2: Converting blockMesh to STL"
echo "=========================================="
mkdir -p constant/triSurface

# Convert the mesh boundaries to STL format (temporary file)
foamToSurface constant/triSurface/windtunnel.stl | tee log.foamToSurface
cd constant/triSurface
cat Mirrors.stl body.stl fastback.stl fastback_optSurface.stl windows.stl > drivaer_combined.stl
cd ..
cd ..

surfaceFeatureExtract | tee log.surfaceFeatureExtract

echo ""
echo "=========================================="
echo "Step 3: Combining geometries"
echo "=========================================="
if [ ! -f "constant/triSurface/drivaer_combined.stl" ]; then
    echo "WARNING: drivaer_combined.stl not found in constant/triSurface/"
    echo "Please ensure your car geometry is placed there"
    echo "Proceeding with wind tunnel geometry only..."
    mv constant/triSurface/windtunnel.stl constant/triSurface/combined.stl
else
    # Combine the STL files
    surfaceAdd constant/triSurface/windtunnel.stl constant/triSurface/drivaer_combined.stl constant/triSurface/combined.stl | tee log.surfaceAdd
    
    # Remove temporary windtunnel.stl
    rm -f constant/triSurface/windtunnel.stl
    echo "Cleaned up temporary windtunnel.stl"
fi

echo ""
echo "=========================================="
echo "Step 4: Checking surface quality"
echo "=========================================="
surfaceCheck constant/triSurface/combined.stl | tee log.surfaceCheck

echo ""
echo "=========================================="
echo "Step 5: Running cartesianMesh"
echo "=========================================="
# Remove old polyMesh before running cartesianMesh
rm -rf constant/polyMesh


# Create .fms file

surfaceFeatureEdges constant/triSurface/combined.stl constant/triSurface/combined.fms

# Run cartesianMesh
cartesianMesh | tee log.cartesianMesh

if [ ! -d "constant/polyMesh" ]; then
    echo "ERROR: cartesianMesh failed!"
    exit 1
fi

echo ""
echo "=========================================="
echo "Step 6: Checking mesh quality"
echo "=========================================="
checkMesh -allGeometry -allTopology | tee log.checkMesh

echo ""
echo "=========================================="
echo "Meshing complete!"
echo "=========================================="
echo "Final geometry: constant/triSurface/combined.stl"
echo "Mesh files are in: constant/polyMesh"
echo "=========================================="

cp -r 0.orig 0
