#!/usr/bin/env python3
"""
Convert binary STL to ASCII STL format
"""
import struct
import sys
from pathlib import Path

def read_binary_stl(filename):
    """Read binary STL file and return triangles"""
    with open(filename, 'rb') as f:
        # Skip 80-byte header
        header = f.read(80)
        
        # Read number of triangles
        num_triangles = struct.unpack('I', f.read(4))[0]
        
        triangles = []
        for _ in range(num_triangles):
            # Normal vector (3 floats)
            normal = struct.unpack('fff', f.read(12))
            
            # 3 vertices, each with 3 coordinates
            v1 = struct.unpack('fff', f.read(12))
            v2 = struct.unpack('fff', f.read(12))
            v3 = struct.unpack('fff', f.read(12))
            
            # Skip attribute byte count
            f.read(2)
            
            triangles.append({
                'normal': normal,
                'vertices': [v1, v2, v3]
            })
    
    return triangles

def write_ascii_stl(filename, triangles, solid_name='object'):
    """Write triangles to ASCII STL file"""
    with open(filename, 'w') as f:
        f.write(f'solid {solid_name}\n')
        
        for tri in triangles:
            normal = tri['normal']
            vertices = tri['vertices']
            
            f.write(f'  facet normal {normal[0]:.6e} {normal[1]:.6e} {normal[2]:.6e}\n')
            f.write('    outer loop\n')
            for vertex in vertices:
                f.write(f'      vertex {vertex[0]:.6e} {vertex[1]:.6e} {vertex[2]:.6e}\n')
            f.write('    endloop\n')
            f.write('  endfacet\n')
        
        f.write(f'endsolid {solid_name}\n')

def convert_stl(input_file, output_file=None):
    """Convert binary STL to ASCII STL"""
    input_path = Path(input_file)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Generate output filename if not provided
    if output_file is None:
        output_file = input_path.with_suffix('.ascii.stl')
    
    print(f"Reading binary STL: {input_file}")
    triangles = read_binary_stl(input_file)
    print(f"Found {len(triangles)} triangles")
    
    print(f"Writing ASCII STL: {output_file}")
    write_ascii_stl(output_file, triangles, solid_name=input_path.stem)
    
    print("Conversion complete!")
    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python stl_convert.py <input.stl> [output.stl]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    convert_stl(input_file, output_file)
