import numpy as np
from plyfile import PlyData , PlyElement
from ..module.ply import *
import os



CATEGORY_str1 = "3D_MeshTool/" 

#---------------Basics---------------
CATEGORY_str2 = "Basics"

class ply_save:# To be developed
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {
                        "path":("STRING",{"default":""}),
                    }
                }
    CATEGORY = CATEGORY_str1+CATEGORY_str2
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("path",)
    FUNCTION = "save"
    def save(self,path):
        pass

class ply_load:
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {
                        "path":("STRING",{"default":""}),
                    }
                }
    CATEGORY = CATEGORY_str1+CATEGORY_str2
    RETURN_TYPES = ("GS_PLY",)
    RETURN_NAMES = ("gs_ply",)
    FUNCTION = "load"
    def load(self,path):
        h = os.path.splitext(path)[1]
        if path == "" or not os.path.isfile(path) or h != ".ply":
            print("Error(node-ply_load): The input path is incorrect, returning empty ply data")
            return (ply1().plydata,)
        else:
            print("Loading PLY file: ",path)
            return (PlyData.read(path),)

class ply_save:
    """
    说明:
    1 若不输入路径则保存在插件缓存文件夹内
    2 缓存文件夹内仅保留一个ply文件,若存在则覆盖
    explain:
    1 Description: If no path is entered, it will be saved in the plugin cache folder.
    2 Only one ply file is retained in the cache folder. If it exists, it will be overwritten.
    """
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {
                        "gs_ply":("GS_PLY",),
                        "save_path":("STRING",{"default":""}),
                    }
                }
    CATEGORY = CATEGORY_str1+CATEGORY_str2
    RETURN_TYPES = ("GS_PLY","STRING",)
    RETURN_NAMES = ("gs_ply","save_path",)
    FUNCTION = "save"
    def save(self,gs_ply,save_path):
        if save_path == "" : save_path=None
        a=ply1()
        a.plydata=gs_ply
        a.save(gs_ply,save_path)
        return (gs_ply,save_path,)

#---------------Edit---------------
CATEGORY_str2 = "Edit"

class options_data:# Create ply options suitable for comfyui, which are not used yet
    type_mapping_cf = {
            'e': 'FLOAT16',
            'f4': 'FLOAT',
            'f': 'FLOAT32',
            'f8': 'FLOAT64',
            'd': 'FLOAT64',
            'i1': 'INT8',
            'i2': 'INT16',
            'i4': 'INT',
            'i': 'INT',
            'i8': 'INT64',
            'l': 'INT64',
            'u1': 'UINT8',
            'uchar': 'UINT8',
            'u2': 'UINT16',
            'u4': 'UINT',
            'u8': 'UINT64',
            'b': 'BOOLEAN',
            's': 'STRING',
            }
    def __init__(self,rename=True):
        s=ply_options()
        self.value=list(s.options.values())
        self.key=list(s.options.keys())
        self.typename=list()
        self.keyname=None
        self.ui=dict()

        for i in range(len(self.key)):
            k=self.key[i]
            v=self.value[i]
            typename=self.type_mapping_cf[s.dtype[i][1]]
            self.ui[k]=(typename,{"default":v})
            self.typename.append(typename)
        
        if rename : self.ui_name()
    
    def ui_name(self,data=None,key_mapping={"f_dc_0":"red","f_dc_1":"green","f_dc_2":"blue",
                                            'scale_0':'x_scale', 'scale_1':'y_scale', 'scale_2':'z_scale',
                                            'rot_0':'i_rot', 'rot_1':'j_rot', 'rot_2':'k_rot', 'rot_3':'w_rot',}):
        if data is None : data = self.ui
        if type(key_mapping) == dict and type(data) == dict:
            self.ui={key_mapping.get(key,key): value for key, value in data.items()}
            self.keyname = list(self.ui.keys())
        else:
            print("Warning(node-ply_ui_name): Input or output data is not a dictionary, renaming failed")
   
class ply_data_set:# To be developed
    user_options=options_data()
    options_name=user_options.keyname
    @classmethod
    def INPUT_TYPES(s):
        ins=s()
        return {"required": ins.user_options.ui}
    #def INPUT_TYPES(s):
    #    return {"required":
    #                {
    #                    "nx":("FLOAT",{"default":0.0}),
    #                    "ny":("FLOAT",{"default":0.0}),
    #                    "nz":("FLOAT",{"default":1.0}),
    #                    "f_dc_0":("FLOAT",{"default":0.0}),
    #                    "f_dc_1":("FLOAT",{"default":0.0}),
    #                    "f_dc_2":("FLOAT",{"default":0.0}),
    #                    "opacity":("FLOAT",{"default":1.0}),
    #                    "scale_0":("FLOAT",{"default":1.0}),
    #                    "scale_1":("FLOAT",{"default":1.0}),
    #                    "scale_2":("FLOAT",{"default":1.0}),
    #                    "rot_0":("FLOAT",{"default":0.0}),
    #                    "rot_1":("FLOAT",{"default":0.0}),
    #                    "rot_2":("FLOAT",{"default":0.0}),
    #                    "rot_3":("FLOAT",{"default":1.0})
    #                }
    #            }
    CATEGORY = CATEGORY_str1+CATEGORY_str2
    RETURN_TYPES = ("GS_PLY",)
    RETURN_NAMES = ("gs_ply",)
    FUNCTION = "ply_set"

    def ply_set(self,*uoptions_name):
        pass
  
class ply_point_Edit:# To be developed
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {
                        "gs_ply":("GS_PLY",),
                        "point_opacity":("FLOAT",{"default":1.0}),
                        "point_size":("FLOAT",{"default":1.0,"min":-32.0,"max":32.0,"step":0.2}),
                        "point_color_R":("INT",{"default":None,"min":0,"max":255,"step":5}),
                        "point_color_G":("INT",{"default":None,"min":0,"max":255,"step":5}),
                        "point_color_B":("INT",{"default":None,"min":0,"max":255,"step":5}),
                    }
                }
    CATEGORY = CATEGORY_str1+CATEGORY_str2
    RETURN_TYPES = ("GS_PLY",)
    RETURN_NAMES = ("gs_ply",)
    FUNCTION = "point_edit"
    def point_edit(self,gs_ply,point_opacity,point_size,point_color_R,point_color_G,point_color_B):
        a=ply1()# 
        k=set(gs_ply["vertex"].data.dtype.names)
        if "opacity" in k:
            opacity=getvalue(gs_ply,["opacity"])
            data=addkey(point_opacity,"opacity")
            gs_ply=ply1.setvalue(data,gs_ply)
        if "size" in k:
            data=addkey(point_size,"size")
            a.setvalue(data)
        return (a.plydata,)

class ply_normalize:# Quick test, processing the coordinates and colors of industrial ply's 'vertex'
    """
    处理工业ply的'vertex'的坐标和颜色,使其能够导入到comfyui中
    Process the coordinates and colors of 'vertex' in industrial ply to enable it to be imported into comfyui
    """
    @classmethod
    def INPUT_TYPES(s):
        RGB=["f_dc_0", "f_dc_1", "f_dc_2"]
        return {"required": 
                    {
                        "gs_ply": ("GS_PLY",),
                        "xyz_normalize":("BOOLEAN",{"default":True}),
                        "RGB_normalize":("BOOLEAN",{"default":True}),
                        "opacity_transfer":("BOOLEAN",{"default":False}),
                        "auto_PointSize":("BOOLEAN",{"default":False}),
                        "PointSize_scale":("FLOAT",{"default":3.00,"min":0.00,"max":4.00,"step":0.10,"display": "slider"}),
                        "R": (RGB,{"default":"f_dc_0"}),
                        "G": (RGB,{"default":"f_dc_1"}),
                        "B": (RGB,{"default":"f_dc_2"}),
                     },
                }
    CATEGORY = CATEGORY_str1+CATEGORY_str2
    RETURN_TYPES = (
        "GS_PLY",
    )
    RETURN_NAMES = (
        "gs_ply",
    )
    FUNCTION = "normalize"
    def normalize(self,gs_ply,xyz_normalize,RGB_normalize,opacity_transfer,auto_PointSize,PointSize_scale,R,G,B):
        a=ply1() # Create a new standard ply class
        k=set(gs_ply["vertex"].data.dtype.names)

        if xyz_normalize: # Process original ply coordinates
            xyz_k=["x","y","z"]
            if set(xyz_k).issubset(k):
                xyz_d=getvalue(gs_ply,xyz_k) # Get xyz of original ply
                xyz1=xyz(xyz_d) # Create xyz class
                xyz1.normalize() # Normalize
                data=addkey(xyz1.xyz_data,xyz_k)# Add key-value pair
                a.setvalue(data) # Update ply data
            else:
                print("Warning(node-ply_normalize): 'x','y','z' not in 'gs_ply' vertex data, xyz normalization failed")

        if RGB_normalize: # Process original ply color
            rgb_k=["red","green","blue"]
            if set(rgb_k).issubset(k):
                rgb_d=getvalue(gs_ply,rgb_k) # Get the rgb of the original ply
                rgb1=xyz(rgb_d) # Create xyz class
                rgb1.lin_mapping() # Color mapping
                rgb_k=[R,G,B] # Color name mapping--red: f_dc_1, green: f_dc_2, blue: f_dc_0
                data=addkey(rgb1.xyz_data,rgb_k)# Add key-value pair
                a.setvalue(data) # Update ply data
            else:
                print("Warning(node-ply_normalize):'red','green','blue' not in 'gs_ply' vertex data, RGB normalization failed")

        if opacity_transfer: #Transfer original transparency
            opacity_k=["scalar_Intensity"]
            if set(opacity_k).issubset(k):
                opacity_d=getvalue(gs_ply,opacity_k) # Get the opacity of the original ply
                opacity_k=["opacity"]
                data=addkey(opacity_d,opacity_k) #Add key-value pair
                a.setvalue(data) # Update ply data
            else:
                print("Warning(node-ply_normalize):'scalar_Intensity' not in 'gs_ply' vertex data, opacity transfer failed")

       # Set the size of each point, standard ply scaling factor -9 (min) ~ -5 (max), input range 0-4
        scale_v=a.plydata["vertex"]["scale_0"][0]
        if auto_PointSize: # Automatically set the size of each point according to the overall size of the point cloud
            scale_v = np.clip(1 / xyz1.o_xyz_size * (PointSize_scale - 9.0) , -9.0, -5.0)
        else:
            scale_v = np.clip(PointSize_scale - 9 , -9.0, -5.0)
        a.plydata["vertex"]["scale_0"] = scale_v
        a.plydata["vertex"]["scale_1"] = scale_v
        a.plydata["vertex"]["scale_2"] = scale_v

        return (a.plydata,)

    def getvalue(self,keys,keys_data): # Detect whether multiple batches of key values ​​exist in the ply data and return the existing keys (used to automatically detect possible keys) #---------To be developed
        pass

NODE_CLASS_MAPPINGS={
    "ply_load":ply_load,
    "ply_normalize":ply_normalize,
    "ply_save":ply_save,
    }

NODE_DISPLAY_NAME_MAPPINGS={
    "ply_load":"ply load",
    "ply_normalize":"ply normalize",
    "ply_save":"ply save",
}