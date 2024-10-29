import numpy as np
import torch
from kiui.mesh_utils import clean_mesh, decimate_mesh
import pymeshlab as pml
from ..moduel.MeshTool import meshclean


def clean_mesh_custom(
    verts,
    faces,
    v_pct=1,
    min_f=0,
    min_d=0,
    repair=False,
    remesh=False,
    remesh_size=0.01,
    remesh_iters=3,
    close_holes=False,
    max_hole_size=1000,
    refine_holes=False,
    verbose=True,
):
    """ perform mesh cleaning, including floater removal, non manifold repair, and remeshing.

    Args:
        verts (np.ndarray): mesh vertices, float [N, 3]
        faces (np.ndarray): mesh faces, int [M, 3]
        v_pct (int, optional): percentage threshold to merge close vertices. Defaults to 1.
        min_f (int, optional): maximal number of faces for isolated component to remove. Defaults to 0.
        min_d (int, optional): maximal diameter percentage of isolated component to remove. Defaults to 0.
        repair (bool, optional): whether to repair non-manifold faces (cannot gurantee). Defaults to True.
        remesh (bool, optional): whether to perform a remeshing after all cleaning. Defaults to True.
        remesh_size (float, optional): the targeted edge length for remeshing. Defaults to 0.01.
        remesh_iters (int, optional): the iterations of remeshing. Defaults to 3.
        verbose (bool, optional): whether to print the cleaning process. Defaults to True.

    Returns:
        Tuple[np.ndarray]: vertices and faces after decimation.
    """
    # verts: [N, 3]
    # faces: [N, 3]

    _ori_vert_shape = verts.shape
    _ori_face_shape = faces.shape

    m = pml.Mesh(verts, faces)
    ms = pml.MeshSet()
    ms.add_mesh(m, "mesh")  # will copy!

    # filters
    ms.meshing_remove_unreferenced_vertices()  # verts not refed by any faces

    if v_pct > 0:
        ms.meshing_merge_close_vertices(
            threshold=pml.PercentageValue(v_pct)
        )  # 1/10000 of bounding box diagonal

    ms.meshing_remove_duplicate_faces()  # faces defined by the same verts
    ms.meshing_remove_null_faces()  # faces with area == 0

    if min_d > 0:
        ms.meshing_remove_connected_component_by_diameter(
            mincomponentdiag=pml.PercentageValue(min_d)
        )

    if min_f > 0:
        ms.meshing_remove_connected_component_by_face_number(mincomponentsize=min_f)

    # be careful: may lead to strangely missing triangles...
    if repair:
        # ms.meshing_remove_t_vertices(method=0, threshold=40, repeat=True)
        ms.meshing_repair_non_manifold_edges(method=0)
        ms.meshing_repair_non_manifold_vertices(vertdispratio=0)
    
    if close_holes:
        ms.meshing_close_holes(maxholesize = max_hole_size, refinehole = refine_holes)

    if remesh:
        # ms.apply_coord_taubin_smoothing()
        ms.meshing_isotropic_explicit_remeshing(
            iterations=remesh_iters, targetlen=pml.PureValue(remesh_size)
        )

    # extract mesh
    m = ms.current_mesh()
    m.compact()
    verts = m.vertex_matrix()
    faces = m.face_matrix()

    if verbose:
        print(f"[INFO] mesh cleaning: {_ori_vert_shape} --> {verts.shape}, {_ori_face_shape} --> {faces.shape}")

    return verts, faces


def close_mesh_holes(verts, faces, cleanup_first=True, max_hole_size=1000, refine_holes=False, verbose=True):
    # verts: [N, 3]
    # faces: [N, 3]
    
    _ori_vert_shape = verts.shape
    _ori_face_shape = faces.shape

    m = pml.Mesh(verts, faces)
    ms = pml.MeshSet()
    ms.add_mesh(m, "mesh")  # will copy!

    # filters
    if cleanup_first:
        ms.meshing_remove_unreferenced_vertices()  # verts not refed by any faces
        ms.meshing_remove_duplicate_faces()  # faces defined by the same verts
        ms.meshing_remove_null_faces()  # faces with area == 0

    ms.meshing_close_holes(maxholesize = max_hole_size, refinehole = refine_holes)

    # extract mesh
    m = ms.current_mesh()
    m.compact()
    verts = m.vertex_matrix()
    faces = m.face_matrix()

    if verbose:
        print(f"[INFO] mesh cleaning: {_ori_vert_shape} --> {verts.shape}, {_ori_face_shape} --> {faces.shape}")

    return verts, faces


class mesh_Optimization:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "mesh":("MESH",),
                "Optimization_to":("FLOAT",{"default":0.65,"min":0,"max":1.0,"step":0.05}),#优化面到此百分比
                "algorithm":("BOOLEAN",{"default":"True","label_on": "pymeshlab", "label_off": "pyfqmr"}),#选优化算法
                "remesh":("BOOLEAN",{"default":False}),#是否刷新网格
                "optimalplacement":("BOOLEAN",{"default":True}),#是否平滑
                },
            }
    CATEGORY = "3D_MeshTool/optimization"
    RETURN_TYPES = ("MESH","INT","INT",)
    RETURN_NAMES = ("Mesh_Out","Face_Before","Face_After",)
    FUNCTION = "mesh_edit_Optimization"
    def mesh_edit_Optimization(self,mesh,Optimization_to,algorithm,remesh,optimalplacement):
        #new_v,new_f = None,None
        v = mesh.v.detach().cpu().numpy()
        f = mesh.f.detach().int().cpu().numpy()
        nv=v.shape[0];nf=f.shape[0]
        f1=int(nf*Optimization_to)
        print("Mesh has %d vertices and %d faces." % (nv, nf))
        print("Optimization to %d faces." % (f1))
        if algorithm:algorithm="pymeshlab"
        else:algorithm="pyfqmr"
        if Optimization_to > 0.0 and Optimization_to <= 1.0:
            new_v,new_f=decimate_mesh(v,f,f1,algorithm,remesh,optimalplacement)
            mesh.v = torch.from_numpy(new_v).contiguous().float().to(mesh.device)
            mesh.f = torch.from_numpy(new_f).contiguous().float().to(mesh.device)
            meshclean.revf3(mesh)
        return (mesh,nf,f1)
    
class mesh_CloseHoles:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "mesh":("MESH",),
                "Cleanup_first":("BOOLEAN",{"default":True}),
                "Close_holes":("BOOLEAN",{"default":True}),
                "Max_hole_size":("INT",{"default":1000,"min":1,"max":5000,"step":1}),
                "Refine_holes":("BOOLEAN",{"default":False}),
                },
            }
    CATEGORY = "3D_MeshTool/optimization"
    RETURN_TYPES = ("MESH","INT","INT",)
    RETURN_NAMES = ("Mesh_Out")
    FUNCTION = "mesh_edit_CloseHoles"
    def mesh_edit_CloseHoles(self,
                          mesh,
                          Cleanup_first,
                          Close_holes,
                          Max_hole_size,
                          Refine_holes
                          ):
        v = mesh.v.detach().cpu().numpy()
        f = mesh.f.detach().int().cpu().numpy()
        new_v,new_f=close_mesh_holes(v,
                                f,
                                cleanup_first = Cleanup_first,
                                max_hole_size = Max_hole_size,
                                refine_holes = Refine_holes
                                )
        mesh.v = torch.from_numpy(new_v).contiguous().float().to(mesh.device)
        mesh.f = torch.from_numpy(new_f).contiguous().float().to(mesh.device)
        meshclean.revf3(mesh)
        return (mesh,)

class mesh_Cleanup:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "mesh":("MESH",),
                "Cleanup_block_nf":("FLOAT",{"default":0.05,"min":0,"max":1.0,"step":0.05}),#清理掉面小于此百分比(相对于总面数)的块
                "Cleanup_block_sc":("INT",{"default":20,"min":0,"max":100,"step":1}),#清理掉小于此直径的块
                "Merge_vertex_threshold":("INT",{"default":1,"min":1,"max":1000,"step":1}),#合并顶点阈值
                "repair_face":("BOOLEAN",{"default":True}),#是否修复非流形面
                "Close_holes":("BOOLEAN",{"default":True}),
                "Max_hole_size":("INT",{"default":1000,"min":1,"max":5000,"step":1}),
                "Refine_holes":("BOOLEAN",{"default":False}),
                #"re_mesh":("BOOLEAN",{"default":True}),#是否重新执行网格划分
                #"remesh_size":("FLOAT",{"default":0.01,"min":0.001,"max":1.0,"step":0.01}),#重新执行网格划分的大小
                #"remesh_iters":("INT",{"default":10,"min":1,"max":100,"step":1}),#重新执行网格划分的迭代次数
                },
            }
    CATEGORY = "3D_MeshTool/optimization"
    RETURN_TYPES = ("MESH","INT","INT",)
    RETURN_NAMES = ("Mesh_Out","Face_Before","Face_After",)
    FUNCTION = "mesh_edit_Cleanup"
    def mesh_edit_Cleanup(self,
                          mesh,
                          Cleanup_block_nf,
                          Cleanup_block_sc,
                          Merge_vertex_threshold,
                          repair_face,
                          Close_holes,
                          Max_hole_size,
                          Refine_holes
                          ):
        v = mesh.v.detach().cpu().numpy()
        f = mesh.f.detach().int().cpu().numpy()
        nf=len(f)
        f1=int(nf*Cleanup_block_nf)
        if Cleanup_block_nf > 0.0 and Cleanup_block_nf <= 1.0:
            new_v,new_f=clean_mesh_custom(v,
                                   f,
                                   v_pct = Merge_vertex_threshold,
                                   min_f = f1,
                                   min_d = Cleanup_block_sc,
                                   repair = repair_face,
                                   remesh = False,
                                   close_holes = Close_holes,
                                   max_hole_size = Max_hole_size,
                                   refine_holes = Refine_holes
                                   )
            mesh.v = torch.from_numpy(new_v).contiguous().float().to(mesh.device)
            mesh.f = torch.from_numpy(new_f).contiguous().float().to(mesh.device)
            meshclean.revf3(mesh)
        return (mesh,nf,f1)

class mesh_subdivide:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "mesh":("MESH",),
                "repair_face":("BOOLEAN",{"default":True}),#是否修复非流形面
                "re_mesh":("BOOLEAN",{"default":True}),#是否重新执行网格划分
                "remesh_size":("FLOAT",{"default":0.01,"min":0.001,"max":1.0,"step":0.01}),#重新执行网格划分的大小
                "remesh_iters":("INT",{"default":10,"min":1,"max":100,"step":1}),#重新执行网格划分的迭代次数
                "Merge_vertex_threshold":("INT",{"default":1,"min":1,"max":1000,"step":1}),#合并顶点阈值
                },
            }
    CATEGORY = "3D_MeshTool/optimization"
    RETURN_TYPES = ("MESH",)
    RETURN_NAMES = ("mesh_subdivide",)
    FUNCTION = "mesh_subdivide"
    def mesh_subdivide(self,mesh,repair_face,re_mesh,remesh_size,remesh_iters,Merge_vertex_threshold):
        v = mesh.v.detach().cpu().numpy()
        f = mesh.f.detach().int().cpu().numpy()
        new_v,new_f=clean_mesh(v,
                               f,
                               v_pct = Merge_vertex_threshold,
                               min_f = 32,
                               min_d = 5,
                               repair = repair_face,
                               remesh = re_mesh,
                               remesh_size = remesh_size,
                               remesh_iters = remesh_iters,
                               )
        mesh.v = torch.from_numpy(new_v).contiguous().float().to(mesh.device)
        mesh.f = torch.from_numpy(new_f).contiguous().float().to(mesh.device)
        meshclean.revf3(mesh)
        return (mesh,)

NODE_CLASS_MAPPINGS={
    "Mesh_Optimization":mesh_Optimization,
    "Mesh_Cleanup":mesh_Cleanup,
    "Mesh_Subdivide":mesh_subdivide,
    }
NODE_DISPLAY_NAMES_MAPPINGS={
    "Mesh_Optimization":"Mesh Optimization",
    "Mesh_Cleanup":"Mesh Cleanup",
    "Mesh_Subdivide":"Mesh Subdivide",
    }