# Defining the tools used in the AutoGen project

import os
from .helper_functions import send_test, resolve_file_path

# Tool AutoGen
def read_file_tool(path:str):
    """
    Reads a file from the given path and returns its content.
    """
    try:
        resolved_path = resolve_file_path(path)
        with open(resolved_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        raise Exception(f"File not found: {path}")
    except Exception as e:
        raise Exception(f"An error occurred while reading the file: {e}")

# Tool AutoGen
def read_dir_structure(directory_path:str="."):
    """
    Reads the directory structure relative from the given directory path.
    Returns:
        dict: A dictionary representing the directory structure.
    """
    dir_structure = {}
    try:
        for root, dirs, files in os.walk(directory_path):
            relative_path = os.path.relpath(root, directory_path)
            dir_structure[relative_path] = {
                "directories": dirs,
                "files": files
            }
        return dir_structure
    except Exception as e:
        raise Exception(f"An error occurred while reading the directory structure: {e}")

# Tool AutoGen
def write_file_tool(path:str, content:str):
    """
    Writes the passed content to a file at the specified path.
    This will overwrite the entire content of the file.
    """
    try:
        resolved_path = resolve_file_path(path)
        # Create directory if it doesn't exist
        directory = os.path.dirname(resolved_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(resolved_path, "w") as file:
            file.write(content)
        return f"Successfully wrote to {resolved_path}"
    except Exception as e:
        raise Exception(f"An error occurred while writing to the file: {e}")

# Tool AutoGen
def test_changes_tool(instance_id:str, FAIL_TO_PASS:list[str], PASS_TO_PASS:list[str], repoDir:str):
    """
    Tests the changes made in the repository using an external testing service.
    """
    request_data = {
        "instance_id": instance_id,
        "repoDir": "/repos/" + repoDir,
        "FAIL_TO_PASS": FAIL_TO_PASS,
        "PASS_TO_PASS": PASS_TO_PASS,
    }
    return send_test(request_data)