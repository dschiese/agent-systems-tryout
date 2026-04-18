import os
import requests
import subprocess

ROOT_REPOSITORY_DIRECTORY = "/home/dennisschiese/Projekte/Master/2. Semester/Automated Software Engineering/Projekt/repositories"
LITE_ENDPOINT = "http://localhost:8081/tasks/index/"

def fetch_problem_statement(index:int):
    """
    Fetches the problem statement from the Lite server for a given index.
    Args:
        index (int): The index of the problem statement to fetch.
    Returns:
        dict: The problem statement as a JSON object.
    Raises:
        Exception: If the request fails or the status code is not in the 200-299 range.
    """
    response = requests.get(LITE_ENDPOINT + str(index))
    if 200 <= response.status_code < 300:
        return response.json()
    else:
        raise Exception(f"Failed to fetch problem statement")
    raise Exception(f"Failed to fetch repository with index {index}. Status code: {response.status_code}")

def clone_repository(git_clone_command:str):
    """
    Clones a repository using the provided git clone command.
    Args:
        git_clone_command (str): The git clone command to execute.
    Returns:
        None
    Raises:
        Exception: If the git clone command fails.
    """
    try:
        os.chdir(os.path.join(os.getcwd(), "repositories"))  # Ensure we are in the correct directory
        clone, dir, commit = separate_git_clone_command(git_clone_command)
        subprocess.run(clone, shell=True, check=True)
        subprocess.run(commit, cwd=dir, shell=True, check=True)
        current_dir = subprocess.run("pwd", shell=True, check=True, capture_output=True, text=True).stdout.strip()
        return dir  # Returns the correct path when clone has worked, otherwise the command failed and the dir is not changed.
    except:
        pass
        # raise Exception(f"Failed to clone repository with command")

def separate_git_clone_command(git_clone_command:str):
    """
    Separates the git clone command into its components: clone command, directory, and commit.
    """
    parts = git_clone_command.split("&&")
    if len(parts) < 3:
        raise ValueError("Git clone command must contain at least three parts: clone command, directory, and commit.")
    
    clone_command = " ".join(parts[:-2])  # Everything except the last two parts
    directory = parts[-2].replace("cd", "").strip();  # Second to last part
    commit = parts[-1]  # Last part
    
    return clone_command, directory, commit

def resolve_file_path(file:str):
    """
    Resolves the relative path of a file
    Args:
        file (str): The file path to resolve.
    Returns:
        str: The relative path of the file.
    """
    # Current dir and the requested file
    print(f"Requested file: {file}")
    path = subprocess.run(f"find . -path '*/{file}'", shell=True, check=True, capture_output=True, text=True).stdout.strip()
    if not path:
        if "/" not in file:
            raise FileExistsError(f"File not found by provided name: {file}. Try exploring the directory: " + str(get_repository_structure(os.getcwd())))
        rindex = file.rindex("/")
        file_name = file[rindex + 1:]
        print(f"Fallback to file name: {file_name}")
        path = resolve_file_path(file_name)
#    if not path:
#        dir_path = os.path.dirname(file)
#        alternatives_list = subprocess.run(f"ls {dir_path}", shell=True, check=True, capture_output=True, text=True).stdout.strip().split('\n')
#        alternatives = "\n".join([os.path.join(dir_path, alt) for alt in alternatives_list if alt])
#        return "Didn't found the file, do you mean of of these?\n" + alternatives;
    return path

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
    
def create_team_prompt(repository_data:dict, path_to_repo:str):
    with open("../prompts/solotasktemplate", "r") as file: # TODO: Rename file
        task_template = file.read()
    repository_data["root_path"] = os.getcwd()
    repository_data["path_to_repository"] = path_to_repo
    return task_template.format(**repository_data)

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

def send_test(request_data:dict):
    try:
        response = requests.post(
            url="http://localhost:8082/test",
            json=request_data
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to test changes. Status code: {response.status_code}")
    except requests.RequestException as e:
        raise Exception(f"An error occurred while testing changes: {e}")
    
def delete_repository(repository_path:str):
    """
    Deletes the repository directory.
    Args:
        repository_path (str): The path to the repository directory to delete.
    Returns:
        None
    Raises:
        Exception: If the directory does not exist or cannot be deleted.
    """
    try:
        if os.path.exists(repository_path):
            subprocess.run(f"rm -rf {repository_path}", shell=True, check=True)
            print(f"Repository at {repository_path} deleted successfully.")
        else:
            raise Exception(f"Repository path does not exist: {repository_path}")
    except Exception as e:
        raise Exception(f"An error occurred while deleting the repository: {e}")