import os
import importlib
import types


__all__ = ["import_module_from_path", "import_function_from_script"]


# Import a python module from it's filesystem path
def import_module_from_path(main_py_path: str) -> types.ModuleType:
    """Import a python module from it's FileSystem path

    Arguments:
        - main_py_path: path to the python script to import

    Returns:
        - module object
    """
    if not os.path.exists(main_py_path):
        raise FileExistsError("Looks like file not exists")
    if not os.path.isfile(main_py_path):
        raise TypeError("Looks like path supplied is not a file")
    module_name = main_py_path.replace("\\", "/").split("/")[-1].split(".")[0]
    return importlib.import_module(module_name, main_py_path)


def import_function_from_script(script_path: str, function_name: str):
    """Function to extract the a python function from a module

    Arguments:
        - script_path: path to the python script
        - function_name: name of the function to import

    Returns:
        - Returns the object named by function_name
    """
    module = import_module_from_path(script_path)
    return getattr(module, function_name)
