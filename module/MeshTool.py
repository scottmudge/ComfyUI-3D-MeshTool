import torch

class setmeshdata: # To be developed
    def __init__(self):
        pass
    @classmethod
    def name(cls, mesh, name):
        mesh.name = name
    @classmethod
    def f(cls, mesh, f):
        mesh.f = f

class meshclean:
    def __init__(self):
        pass
    @classmethod
    def revf3(cls, mesh): # Used to clear mismatched normals/uvs/vertex colors after adding or deleting vertices/faces
        mesh.fn=None;mesh.fv=None;mesh.ft=None
        mesh.vn=None;mesh.vt=None;mesh.ft=None

class meshtexturing:
    def __init__(self):
        pass
    @classmethod
    def vctotexture(vertex_colors, uv_coords, texture_size=(256, 256)):# Vertex color to texture (to be tested)
        # Normalize UV ​​coordinates to the range [0, texture_size -1]
        uv_coords = uv_coords * torch.tensor([texture_size[0] - 1, texture_size[1] - 1], dtype=torch.float32)
        # Handle edge cases
        uv_coords = torch.clamp(uv_coords, 0, torch.tensor([texture_size[0] - 1, texture_size[1] - 1], dtype=torch.float32))
        # Initialize texture
        texture = torch.zeros((texture_size[1], texture_size[0], 3), dtype=torch.float32)
        # Bilinear interpolation to calculate texture color
        u_floor = torch.floor(uv_coords[:, 0]).long()
        v_floor = torch.floor(uv_coords[:, 1]).long()
        u_ceil = torch.ceil(uv_coords[:, 0]).long()
        v_ceil = torch.ceil(uv_coords[:, 1]).long()
        u_weight = uv_coords[:, 0] - u_floor
        v_weight = uv_coords[:, 1] - v_floor
        for i in range(len(uv_coords)):
            # Color of four adjacent points
            color00 = vertex_colors[i]
            color01 = vertex_colors[i] if v_ceil[i] < texture_size[1] else color00
            color10 = vertex_colors[i] if u_ceil[i] < texture_size[0] else color00
            color11 = vertex_colors[i] if (u_ceil[i] < texture_size[0] and v_ceil[i] < texture_size[1]) else color00
            # Bilinear interpolation
            texture[v_floor[i], u_floor[i]] += (1 - u_weight[i]) * (1 - v_weight[i]) * color00
            texture[v_floor[i], u_ceil[i]] += u_weight[i] * (1 - v_weight[i]) * color10
            texture[v_ceil[i], u_floor[i]] += (1 - u_weight[i]) * v_weight[i] * color01
            texture[v_ceil[i], u_ceil[i]] += u_weight[i] * v_weight[i] * color11
        return texture
    
    @classmethod
    def UVmapping(cls,mesh,vt1,vt2): # UV mapping (to be developed)
        pass