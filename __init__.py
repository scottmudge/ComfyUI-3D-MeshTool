# Use ltdrdata’s batch import https://github.com/ltdrdata/comfy ui impact pack
import glob # Import the glob module for pattern matching of file paths
import importlib.util #I mport the importlib.util module for dynamically importing modules
import sys # Import the sys module for accessing variables and functions closely related to the Python interpreter
import os
extension_folder = os.path.dirname(os.path.realpath(__file__)) # Get the folder path where the current file is located
#sys.path.append(extension_folder)
NODE_CLASS_MAPPINGS = {} # Initialize two empty dictionaries to store node class mapping and node display name mapping
NODE_DISPLAY_NAME_MAPPINGS = {}

pyPath = os.path.join(extension_folder,'nodes') # Add 'nodes' to the module search path

def loadCustomNodes(): # Define the loadCustomNodes function for loading custom nodes and API files
    # Use glob.glob to search for all files ending in .py in the pyPath directory, including files in subdirectories.
    find_files = glob.glob(os.path.join(pyPath, "*.py"), recursive=True)

    # Use glob.glob to search for the api.py file in the pyPath directory
    #api_files = glob.glob(os.path.join(pyPath, "api.py"), recursive=True)
    # Merge the found node files and API file lists
    #find_files = files + api_files

    for file in find_files: # Traverse the file list
        file_relative_path = file[len(extension_folder):] # Calculate the path of the file relative to extension_folder
        module_name = file_relative_path.replace(os.sep, '.') # Replace the directory separator in the file path with a period to build the module name
        module_name = os.path.splitext(module_name)[0] # Remove the file extension from the module name and get the module name
        module = importlib.import_module(module_name, __name__) # Use importlib.import_module to dynamically import modules
        # If there is NODE_CLASS_MAPPINGS attribute in the module and it is not empty, update the global mapping
        if hasattr(module, "NODE_CLASS_MAPPINGS") and getattr(module, "NODE_CLASS_MAPPINGS") is not None:
            NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)
            
            # If there is NODE_DISPLAY_NAME_MAPPINGS attribute in the module and it is not empty, update the display name mapping
            if hasattr(module, "NODE_DISPLAY_NAME_MAPPINGS") and getattr(module, "NODE_DISPLAY_NAME_MAPPINGS") is not None:
                NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)
        if hasattr(module, "init"): # If there is an init function in the module, call it for initialization
            getattr(module, "init")()
            
    print(f"Successfully Loaded ComfyUI-3D-MeshTool, with {len(NODE_CLASS_MAPPINGS)} nodes!")

loadCustomNodes() # Call the loadCustomNodes function to perform the loading operation

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS'] # Define the __all__ variable to list the variables or functions in the module that can be accessed externally