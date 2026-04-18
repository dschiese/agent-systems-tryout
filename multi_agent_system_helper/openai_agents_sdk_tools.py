from agents import function_tool
import requests
import os
from .helper_functions import resolve_file_path
import subprocess

@function_tool
def read_dir_structure():
    """
    Reads the directory structure of the current working directory and returns only .py files and their directories as a string.
    Returns:
        str: The filtered directory structure.
    """
    try:
        result = subprocess.run(
            "tree -P \"*.py\" -fi .",
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise Exception(f"An error occurred while reading the directory structure: {e}")

@function_tool
def write_file_tool(path:str, content:str):
    """
    Writes the passed content to a file at the specified path.
    This will overwrite the entire content of the file.
    """
    try:
        print(f"Writing to file: {path}")
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

@function_tool
def get_repository_structure(repository:str):
    """
    Fetches the structure of the repository from the given directory
    Args:
        repository (str): The directory name of the repository.
    Returns:
        str: The structure of the repository.
    """
    return subprocess.run(
        f"tree -P \"*.py\" -fi {repository}",
        shell=True,
        check=True,
        capture_output=True,
        text=True
    ).stdout.strip()

@function_tool
def read_file_tool(path:str):
    """
    Reads a file from the given path and returns its content.
    """
    try:
        resolved_path = resolve_file_path(path)
        with open(resolved_path, "r") as file:
            return file.read()
    except FileExistsError:
        return e
    except FileNotFoundError:
        raise Exception(f"File not found: {resolved_path}")
    except Exception as e:
        raise Exception(f"An error occurred while reading the file: {e}")
    
@function_tool
def test_fixes(repository_name:str, instance_id:str, FAIL_TO_PASS:list, PASS_TO_PASS:list):
    print(f"Starting Testing-Agent... with args: Repository: {repository_name}, Instance ID: {instance_id}, FAIL_TO_PASS: {FAIL_TO_PASS}, PASS_TO_PASS: {PASS_TO_PASS} ")
    """
    Tests the fixes made in the repository. It expects the values from the repository data that are passed as arguments to this function.
    Args:
        repository_name (str): The name of the repository.
        instance_id (str): The instance ID for tracking.
        FAIL_TO_PASS (list): List of test cases that failed before the fix.
        PASS_TO_PASS (list): List of test cases that passed before the fix.
    Returns:
        str: A message indicating the result of the tests.
    """
    url = f"http://localhost:8082/test"
    data = {
        "instance_id": instance_id,
        "repoDir": repository_name,
        "FAIL_TO_PASS": FAIL_TO_PASS,
        "PASS_TO_PASS": PASS_TO_PASS
    }
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        print("Testing-Agent finished.")
        return response.json().get("message", "No message returned from server.")
    else:
        raise Exception(f"Failed to test fixes: {response.text}")


@function_tool
def test_changes_tool():
    """
    Placeholder for a tool that tests changes made to the codebase.
    This function should be implemented with actual testing logic.
    """
    raise NotImplementedError("This tool is not yet implemented.")

def set_working_directory(directory_path:str):
    """
    Changes the current working directory to the specified path.
    Args:
        directory_path (str): The directory path to change to.
    Returns:
        str: The new working directory path.
    """
    try:
        os.chdir(directory_path)
        return f"Working directory changed to: {os.getcwd()}"
    except FileNotFoundError:
        raise Exception(f"Directory not found: {directory_path}")
    except Exception as e:
        raise Exception(f"An error occurred while changing the working directory: {e}")