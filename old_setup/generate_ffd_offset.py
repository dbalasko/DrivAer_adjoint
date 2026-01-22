#!/usr/bin/env python3
"""
Generate FFD box from STL file with specified offset.
Creates a box around the geometry with user-defined margins.
"""

import sys
import struct
import numpy as np
import argparse


def is_ascii_stl(filepath):
    """Check if STL file is ASCII format."""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(80)
            if header.startswith(b'solid'):
                f.seek(0)
                try:
                    first_line = f.readline().decode('ascii').strip()
                    if first_line.startswith('solid'):
                        return True
                except:
                    return False
            return False
    except:
        return False


def get_stl_bounds(stl_file):
    """
    Get bounding box of STL file.
    
    Returns:
        min_point, max_point: (x,y,z) tuples of bounds
    """
    min_x = min_y = min_z = float('inf')
    max_x = max_y = max_z = float('-inf')
    
    if is_ascii_stl(stl_file):
        print("Reading ASCII STL file...")
        with open(stl_file, 'r') as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith('vertex'):
                    parts = stripped.split()
                    if len(parts) == 4:
                        x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                        min_x, max_x = min(min_x, x), max(max_x, x)
                        min_y, max_y = min(min_y, y), max(max_y, y)
                        min_z, max_z = min(min_z, z), max(max_z, z)
    else:
        print("Reading binary STL file...")
        with open(stl_file, 'rb') as f:
            f.read(80)  # header
            num_triangles = struct.unpack('I', f.read(4))[0]
            
            for i in range(num_triangles):
                f.read(12)  # normal
                for j in range(3):  # 3 vertices
                    x, y, z = struct.unpack('fff', f.read(12))
                    min_x, max_x = min(min_x, x), max(max_x, x)
                    min_y, max_y = min(min_y, y), max(max_y, y)
                    min_z, max_z = min(min_z, z), max(max_z, z)
                f.read(2)  # attribute
    
    return (min_x, min_y, min_z), (max_x, max_y, max_z)


def generate_ffd_box(stl_file, output_file, 
                     nx=11, ny=2, nz=2,
                     offset_x=0.1, offset_y=0.1, offset_z=0.05,
                     x_start=None, x_end=None):
    """
    Generate FFD box around STL geometry.
    
    Args:
        stl_file: Input STL file
        output_file: Output FFD.xyz file
        nx, ny, nz: Number of FFD points in each direction
        offset_x, offset_y, offset_z: Offset margins (in same units as STL)
        x_start, x_end: Optional override for X bounds (useful for rear-end only)
    """
    # Get geometry bounds
    min_point, max_point = get_stl_bounds(stl_file)
    
    print(f"\nGeometry bounds:")
    print(f"  X: [{min_point[0]:.3f}, {max_point[0]:.3f}]")
    print(f"  Y: [{min_point[1]:.3f}, {max_point[1]:.3f}]")
    print(f"  Z: [{min_point[2]:.3f}, {max_point[2]:.3f}]")
    
    # Override X bounds if specified (for rear-end only optimization)
    if x_start is not None:
        min_point = (x_start, min_point[1], min_point[2])
        print(f"\nOverriding X start: {x_start:.3f}")
    if x_end is not None:
        max_point = (x_end, max_point[1], max_point[2])
        print(f"Overriding X end: {x_end:.3f}")
    
    # Create FFD box with offsets
    x_min = min_point[0] - offset_x
    x_max = max_point[0] + offset_x
    y_min = min_point[1] - offset_y
    y_max = max_point[1] + offset_y
    z_min = min_point[2] - offset_z
    z_max = max_point[2] + offset_z
    
    print(f"\nFFD box bounds (with offsets):")
    print(f"  X: [{x_min:.3f}, {x_max:.3f}] (offset: {offset_x:.3f})")
    print(f"  Y: [{y_min:.3f}, {y_max:.3f}] (offset: {offset_y:.3f})")
    print(f"  Z: [{z_min:.3f}, {z_max:.3f}] (offset: {offset_z:.3f})")
    
    # Generate FFD points
    x_coords = np.linspace(x_min, x_max, nx)
    y_coords = np.linspace(y_min, y_max, ny)
    z_coords = np.linspace(z_min, z_max, nz)
    
    print(f"\nFFD dimensions: {nx} × {ny} × {nz} = {nx*ny*nz} points")
    
    # Write FFD file in Plot3D format
    with open(output_file, 'w') as f:
        # Header: 1 block
        f.write("1\n")
        
        # Dimensions: nx, ny, nz
        f.write(f"{nx} {ny} {nz}\n")
        
        # X coordinates (all points)
        x_list = []
        for k in range(nz):
            for j in range(ny):
                for i in range(nx):
                    x_list.append(f"{x_coords[i]:.6f}")
        f.write(" ".join(x_list) + "\n")
        
        # Y coordinates (all points)
        y_list = []
        for k in range(nz):
            for j in range(ny):
                for i in range(nx):
                    y_list.append(f"{y_coords[j]:.6f}")
        f.write(" ".join(y_list) + "\n")
        
        # Z coordinates (all points)
        z_list = []
        for k in range(nz):
            for j in range(ny):
                for i in range(nx):
                    z_list.append(f"{z_coords[k]:.6f}")
        f.write(" ".join(z_list) + "\n")
    
    print(f"\nFFD file created: {output_file}")
    print(f"\nTo visualize in ParaView:")
    print(f"  1. Open ParaView")
    print(f"  2. File > Open > {output_file}")
    print(f"  3. Apply")
    print(f"  4. Change representation to 'Surface With Edges' or 'Wireframe'")


def main():
    parser = argparse.ArgumentParser(
        description='Generate FFD box from STL geometry.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate FFD box for entire geometry
  python generate_ffd.py tesla.stl FFD.xyz
  
  # Custom number of points (11 in X, 3 in Y, 2 in Z)
  python generate_ffd.py tesla.stl FFD.xyz --nx 11 --ny 3 --nz 2
  
  # Custom offsets
  python generate_ffd.py tesla.stl FFD.xyz --offset-x 0.2 --offset-y 0.15
  
  # Rear-end only (specify X range)
  python generate_ffd.py tesla.stl FFD.xyz --x-start 1.5 --x-end 4.5
  
  # Full example for rear optimization
  python generate_ffd.py tesla.stl FFD.xyz --nx 13 --ny 2 --nz 2 \
         --x-start 2.0 --x-end 4.5 --offset-x 0.1 --offset-y 0.1 --offset-z 0.05

Typical values:
  Full car:  nx=15-20, ny=3-5,  nz=2-3
  Rear-end:  nx=10-15, ny=2,    nz=2
  Offsets:   0.05-0.2 (5-20cm for car in meters)
        """
    )
    
    parser.add_argument('stl_file', help='Input STL file')
    parser.add_argument('output_file', help='Output FFD.xyz file')
    
    parser.add_argument('--nx', type=int, default=11,
                       help='Number of FFD points in X direction (default: 11)')
    parser.add_argument('--ny', type=int, default=2,
                       help='Number of FFD points in Y direction (default: 2)')
    parser.add_argument('--nz', type=int, default=2,
                       help='Number of FFD points in Z direction (default: 2)')
    
    parser.add_argument('--offset-x', type=float, default=0.1,
                       help='Offset in X direction (default: 0.1)')
    parser.add_argument('--offset-y', type=float, default=0.1,
                       help='Offset in Y direction (default: 0.1)')
    parser.add_argument('--offset-z', type=float, default=0.05,
                       help='Offset in Z direction (default: 0.05)')
    
    parser.add_argument('--x-start', type=float, default=None,
                       help='Override X min (for rear-end only)')
    parser.add_argument('--x-end', type=float, default=None,
                       help='Override X max (for rear-end only)')
    
    args = parser.parse_args()
    
    try:
        generate_ffd_box(args.stl_file, args.output_file,
                        nx=args.nx, ny=args.ny, nz=args.nz,
                        offset_x=args.offset_x, 
                        offset_y=args.offset_y, 
                        offset_z=args.offset_z,
                        x_start=args.x_start,
                        x_end=args.x_end)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
