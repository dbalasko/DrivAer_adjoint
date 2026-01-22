#!/usr/bin/env python3
"""
Script to convert XYZ format FFD control points to OpenFOAM dictionary format.
Supports Plot3D-style XYZ format with separate x, y, z coordinate arrays.
"""

import numpy as np
import sys
from pathlib import Path


def parse_xyz_file(filename):
    """
    Parse XYZ format FFD file.
    
    Expected format:
    Line 1: version/type (usually 1)
    Line 2: nx ny nz (dimensions)
    Line 3: all x-coordinates
    Line 4: all y-coordinates  
    Line 5: all z-coordinates
    
    Args:
        filename: Path to the XYZ file
        
    Returns:
        tuple: (points_array, dimensions)
            - points_array: numpy array of shape (n_points, 3)
            - dimensions: tuple (nx, ny, nz)
    """
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Parse version/type (line 1)
    version = int(lines[0].strip())
    print(f"File version/type: {version}")
    
    # Parse dimensions (line 2)
    dims = [int(x) for x in lines[1].strip().split()]
    if len(dims) != 3:
        raise ValueError(f"Expected 3 dimensions, got {len(dims)}")
    
    nx, ny, nz = dims
    n_points = nx * ny * nz
    print(f"Grid dimensions: {nx} x {ny} x {nz} = {n_points} points")
    
    # Parse coordinates (lines 3, 4, 5)
    x_coords = [float(x) for x in lines[2].strip().split()]
    y_coords = [float(x) for x in lines[3].strip().split()]
    z_coords = [float(x) for x in lines[4].strip().split()]
    
    # Verify we have the correct number of coordinates
    if len(x_coords) != n_points:
        raise ValueError(f"Expected {n_points} x-coordinates, got {len(x_coords)}")
    if len(y_coords) != n_points:
        raise ValueError(f"Expected {n_points} y-coordinates, got {len(y_coords)}")
    if len(z_coords) != n_points:
        raise ValueError(f"Expected {n_points} z-coordinates, got {len(z_coords)}")
    
    # Combine into points array
    points = np.zeros((n_points, 3))
    points[:, 0] = x_coords
    points[:, 1] = y_coords
    points[:, 2] = z_coords
    
    print(f"Successfully parsed {n_points} control points")
    print(f"X range: [{np.min(x_coords):.6f}, {np.max(x_coords):.6f}]")
    print(f"Y range: [{np.min(y_coords):.6f}, {np.max(y_coords):.6f}]")
    print(f"Z range: [{np.min(z_coords):.6f}, {np.max(z_coords):.6f}]")
    
    return points, (nx, ny, nz)


def write_openfoam_format(points, output_file, box_name="boxcpsBsplines0"):
    """
    Write FFD points to OpenFOAM dictionary format.
    
    Args:
        points: numpy array of shape (n_points, 3)
        output_file: output filename
        box_name: name for the FFD box (used in object field)
    """
    n_points = len(points)
    
    with open(output_file, 'w') as f:
        # Write FoamFile header
        f.write("/*--------------------------------*- C++ -*----------------------------------*\\\n")
        f.write("| =========                 |                                                 |\n")
        f.write("| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |\n")
        f.write("|  \\\\    /   O peration     | Version:  v2406                                 |\n")
        f.write("|   \\\\  /    A nd           | Website:  www.openfoam.com                      |\n")
        f.write("|    \\\\/     M anipulation  |                                                 |\n")
        f.write("\\*---------------------------------------------------------------------------*/\n")
        f.write("FoamFile\n")
        f.write("{\n")
        f.write("    version     2.0;\n")
        f.write("    format      ascii;\n")
        f.write("    class       dictionary;\n")
        f.write("    location    \"../constant/controlPoints\";\n")
        f.write(f"    object      {box_name};\n")
        f.write("}\n")
        f.write("// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n")
        f.write("\n")
        
        # Write control points
        f.write(f"controlPoints   {n_points} ( ")
        
        # Write points in a reasonably formatted way (not all on one line)
        points_per_line = 1  # One point per line for better readability
        for i, point in enumerate(points):
            if i > 0 and i % points_per_line == 0:
                f.write("\n")
            f.write(f"( {point[0]:.8g} {point[1]:.8g} {point[2]:.8g} ) ")
        
        f.write(");\n")
        f.write("\n")
        f.write("\n")
        f.write("// ************************************************************************* //\n")
    
    print(f"\nWrote OpenFOAM format file: {output_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python xyz_to_openfoam.py <xyz_file> [output_file] [box_name]")
        print("\nExamples:")
        print("  python xyz_to_openfoam.py teslaFFD.xyz")
        print("  python xyz_to_openfoam.py teslaFFD.xyz boxcpsBsplines0")
        print("  python xyz_to_openfoam.py teslaFFD.xyz boxcpsBsplines0 myFFDBox")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Determine output filename
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        output_file = Path(input_file).stem  # Remove .xyz extension
    
    # Determine box name
    if len(sys.argv) >= 4:
        box_name = sys.argv[3]
    else:
        box_name = Path(output_file).stem
    
    # Parse the XYZ file
    print(f"Reading XYZ file: {input_file}")
    points, dimensions = parse_xyz_file(input_file)
    
    # Write OpenFOAM format
    write_openfoam_format(points, output_file, box_name)
    
    print("\nConversion complete!")
    print(f"Grid dimensions: {dimensions[0]} x {dimensions[1]} x {dimensions[2]}")
    print(f"Total points: {len(points)}")
    print("\nYou can now use this file with DAFoam's FFD setup.")


if __name__ == "__main__":
    main()
