#!/usr/bin/env python3
"""
Convert B-spline control point CSV files to VTK temporal format for ParaView.
Automatically processes all CSV files matching the pattern and creates a PVD collection.

Usage:
    python csv_to_vtk_converter.py

Configuration:
    Modify the INPUT_DIR, OUTPUT_DIR, and FILE_PATTERN variables below.
"""

import numpy as np
import os
from pathlib import Path
import zipfile

# ============================================================================
# CONFIGURATION - Modify these for your use case
# ============================================================================

INPUT_DIR = '.'  # Directory containing CSV files (current directory by default)
OUTPUT_DIR = './vtk_output'  # Directory for output files
FILE_PATTERN = 'boxcpsBsplines*.csv'  # Pattern to match CSV files
OUTPUT_NAME = 'control_points'  # Base name for output files
CREATE_ZIP = True  # Set to True to create a zip archive with all files

# ============================================================================


def read_control_points(csv_file):
    """Read control points from CSV file."""
    # Read CSV, skipping the header
    data = np.genfromtxt(csv_file, delimiter=',', skip_header=1)
    
    # Extract coordinates
    points = data[:, 0:3]  # x, y, z
    indices = data[:, 3:6].astype(int)  # i, j, k
    active = data[:, 6:9]  # active flags
    
    return points, indices, active


def write_vtp_polydata(filename, points, indices, active, timestep):
    """Write control points to XML VTK PolyData format (.vtp)."""
    n_points = len(points)
    
    with open(filename, 'w') as f:
        # XML VTP Header
        f.write('<?xml version="1.0"?>\n')
        f.write('<VTKFile type="PolyData" version="1.0" byte_order="LittleEndian" header_type="UInt64">\n')
        f.write('  <PolyData>\n')
        f.write(f'    <Piece NumberOfPoints="{n_points}" NumberOfVerts="{n_points}" NumberOfLines="0" NumberOfStrips="0" NumberOfPolys="0">\n')
        
        # Points
        f.write('      <Points>\n')
        f.write('        <DataArray type="Float32" Name="Points" NumberOfComponents="3" format="ascii">\n')
        for point in points:
            f.write(f'          {point[0]:.6f} {point[1]:.6f} {point[2]:.6f}\n')
        f.write('        </DataArray>\n')
        f.write('      </Points>\n')
        
        # Vertices (connectivity)
        f.write('      <Verts>\n')
        f.write('        <DataArray type="Int32" Name="connectivity" format="ascii">\n')
        f.write('          ')
        for i in range(n_points):
            f.write(f'{i} ')
        f.write('\n        </DataArray>\n')
        f.write('        <DataArray type="Int32" Name="offsets" format="ascii">\n')
        f.write('          ')
        for i in range(1, n_points + 1):
            f.write(f'{i} ')
        f.write('\n        </DataArray>\n')
        f.write('      </Verts>\n')
        
        # Point Data
        f.write('      <PointData>\n')
        
        # i_index
        f.write('        <DataArray type="Int32" Name="i_index" format="ascii">\n')
        f.write('          ')
        for idx in indices:
            f.write(f'{idx[0]} ')
        f.write('\n        </DataArray>\n')
        
        # j_index
        f.write('        <DataArray type="Int32" Name="j_index" format="ascii">\n')
        f.write('          ')
        for idx in indices:
            f.write(f'{idx[1]} ')
        f.write('\n        </DataArray>\n')
        
        # k_index
        f.write('        <DataArray type="Int32" Name="k_index" format="ascii">\n')
        f.write('          ')
        for idx in indices:
            f.write(f'{idx[2]} ')
        f.write('\n        </DataArray>\n')
        
        # point_id
        f.write('        <DataArray type="Int32" Name="point_id" format="ascii">\n')
        f.write('          ')
        for i in range(n_points):
            f.write(f'{i} ')
        f.write('\n        </DataArray>\n')
        
        # Active flags as vector
        f.write('        <DataArray type="Float32" Name="active" NumberOfComponents="3" format="ascii">\n')
        for act in active:
            f.write(f'          {act[0]:.1f} {act[1]:.1f} {act[2]:.1f}\n')
        f.write('        </DataArray>\n')
        
        f.write('      </PointData>\n')
        
        f.write('    </Piece>\n')
        f.write('  </PolyData>\n')
        f.write('</VTKFile>\n')


def write_pvd_file(pvd_filename, vtp_files, timesteps):
    """Write PVD (ParaView Data) file that links all timesteps."""
    with open(pvd_filename, 'w') as f:
        f.write('<?xml version="1.0"?>\n')
        f.write('<VTKFile type="Collection" version="0.1" byte_order="LittleEndian">\n')
        f.write('  <Collection>\n')
        
        for vtp_file, timestep in zip(vtp_files, timesteps):
            # Use relative path (just basename)
            vtp_basename = os.path.basename(vtp_file)
            f.write(f'    <DataSet timestep="{timestep}" group="" part="0" file="{vtp_basename}"/>\n')
        
        f.write('  </Collection>\n')
        f.write('</VTKFile>\n')


def create_zip_archive(output_dir, output_name, pvd_file, vtp_files):
    """Create a zip archive containing all VTK files."""
    zip_filename = os.path.join(output_dir, f'{output_name}_temporal.zip')
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add PVD file
        zipf.write(pvd_file, os.path.basename(pvd_file))
        
        # Add all VTP files
        for vtp_file in vtp_files:
            zipf.write(vtp_file, os.path.basename(vtp_file))
    
    return zip_filename


def main():
    print("="*70)
    print("CSV to VTK Temporal Converter for ParaView")
    print("="*70)
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Find all CSV files matching the pattern
    csv_files = sorted(Path(INPUT_DIR).glob(FILE_PATTERN))
    
    if not csv_files:
        print(f"\nERROR: No CSV files found matching pattern '{FILE_PATTERN}' in '{INPUT_DIR}'")
        print("Please check INPUT_DIR and FILE_PATTERN in the script.")
        return
    
    print(f"\nFound {len(csv_files)} CSV files:")
    for f in csv_files:
        print(f"  {f.name}")
    
    # Process each CSV file
    vtp_files = []
    timesteps = []
    
    print("\nProcessing files...")
    print("-"*70)
    
    for csv_file in csv_files:
        # Extract timestep number from filename
        basename = csv_file.stem
        timestep_str = basename.replace('boxcpsBsplines', '')
        
        try:
            timestep = int(timestep_str)
        except ValueError:
            print(f"Warning: Could not extract timestep from {csv_file.name}, skipping")
            continue
        
        # Read control points
        points, indices, active = read_control_points(csv_file)
        
        # Write VTP file (XML VTK PolyData)
        vtp_filename = os.path.join(OUTPUT_DIR, f'{OUTPUT_NAME}_t{timestep:04d}.vtp')
        write_vtp_polydata(vtp_filename, points, indices, active, timestep)
        
        print(f"Timestep {timestep:3d}: {len(points):4d} points -> {os.path.basename(vtp_filename)}")
        
        vtp_files.append(vtp_filename)
        timesteps.append(timestep)
    
    # Write PVD collection file
    pvd_filename = os.path.join(OUTPUT_DIR, f'{OUTPUT_NAME}_temporal.pvd')
    write_pvd_file(pvd_filename, vtp_files, timesteps)
    
    print("-"*70)
    print(f"\n✓ Created {len(vtp_files)} VTP files")
    print(f"✓ Created PVD collection: {os.path.basename(pvd_filename)}")
    
    # Create zip archive if requested
    if CREATE_ZIP:
        zip_filename = create_zip_archive(OUTPUT_DIR, OUTPUT_NAME, pvd_filename, vtp_files)
        print(f"✓ Created zip archive: {os.path.basename(zip_filename)}")
    
    print("\n" + "="*70)
    print("HOW TO USE IN PARAVIEW:")
    print("="*70)
    if CREATE_ZIP:
        print(f"1. Extract '{OUTPUT_NAME}_temporal.zip' to a folder")
        print(f"2. Open '{OUTPUT_NAME}_temporal.pvd' in ParaView")
    else:
        print(f"1. Copy all files from '{OUTPUT_DIR}' to the same folder")
        print(f"2. Open '{OUTPUT_NAME}_temporal.pvd' in ParaView")
    print("3. Use VCR controls (play/pause buttons) to animate through timesteps")
    print("4. Apply 'Glyph' filter (sphere glyphs) to visualize points")
    print("5. Color by 'i_index', 'j_index', or 'k_index'")
    print("="*70)


if __name__ == '__main__':
    main()
