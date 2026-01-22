#!/usr/bin/env python3
"""
Scale STL file by factor of 0.001
"""
import numpy as np
from stl import mesh

# Input/Output files
input_file = "fastback_optSurface.stl"
output_file = "fastback_optscaled.stl"
scale_factor = 0.001

# Load STL
print(f"Loading {input_file}...")
your_mesh = mesh.Mesh.from_file(input_file)

# Get original bounds
print(f"Original bounds:")
print(f"  X: [{your_mesh.x.min():.3f}, {your_mesh.x.max():.3f}]")
print(f"  Y: [{your_mesh.y.min():.3f}, {your_mesh.y.max():.3f}]")
print(f"  Z: [{your_mesh.z.min():.3f}, {your_mesh.z.max():.3f}]")

# Scale all vertices
your_mesh.vectors *= scale_factor

# Get new bounds
print(f"\nScaled bounds (factor = {scale_factor}):")
print(f"  X: [{your_mesh.x.min():.6f}, {your_mesh.x.max():.6f}]")
print(f"  Y: [{your_mesh.y.min():.6f}, {your_mesh.y.max():.6f}]")
print(f"  Z: [{your_mesh.z.min():.6f}, {your_mesh.z.max():.6f}]")

# Save scaled STL
print(f"\nSaving to {output_file}...")
your_mesh.save(output_file)
print("Done!")
