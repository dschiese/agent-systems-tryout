from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import ExternalTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.ollama import OllamaChatCompletionClient
import requests
import subprocess
import asyncio
import os

# Static variables

LITE_URL:str = "http://localhost:8081/task/index/";
BASE_PATH:str = "repositories";

# primary_agent = AssistantAgent(
#     "primary",
#     model_client=OllamaChatCompletionClient(model="llama3.2"),
#     system_message="Your are a helpful assistant."
# )



# critic_agent = AssistantAgent(
#     "critic",
#     model_client=OllamaChatCompletionClient(model="llama3.2"),
#         system_message="Provide constructive feedback. Respond with 'DONE' to when your feedbacks are addressed."
# )

# text_termination = TextMentionTermination("APPROVE")
# team = RoundRobinGroupChat([primary_agent, critic_agent], termination_condition=text_termination)
# import asyncio

# async def main():
#     await team.reset()  # Reset the team for a new task.
#     async for message in team.run_stream(task="Write a short poem about the fall season."):  # type: ignore
#         if isinstance(message, TaskResult):
#             print("Stop Reason:", message.stop_reason)
#         else:
#             print(message)

# asyncio.run(main())




# Own implementation

# FUNCTIONS

def fetch_repository(index:int):
    response = requests.get(LITE_URL + str(index))
    if response.status_code == 200:
        if response.json() == "":
            return None
        else:
            return response.json()
    else:
        raise Exception(f"Failed to fetch repository with index {index}. Status code: {response.status_code}")
    
def clone_repository(git_clone_command:str):
    try:
        clone, dir, commit = separate_git_clone_command(git_clone_command)
        subprocess.run(clone, shell=True, check=False)
        subprocess.run(commit, cwd=dir, shell=True, check=False)
        # Get current working directory
        current_dir = subprocess.run("pwd", shell=True, capture_output=True, text=True).stdout.strip() + f"/{dir}"
        subprocess.run("cd ../..", shell=True, check=True)
        return current_dir; # TODO: Returns the correct path when clone has worked, otherwise the command failed and the dir is not changed.
    except:
        raise Exception(f"Failed to clone repository with command: {git_clone_command}")
    
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

def run_agent_system(prompt:str, repository_path:str):
    None;

def prepare_agent_system(repository_data:dict, path_to_repo:str):
    with open("./prompts/task_template", "r") as file:
        task_template = file.read()
    repository_data["path_to_repository"] = path_to_repo
    task:str = task_template.format(**repository_data)
    return task

def create_solo_prompt(repository_data:dict, path_to_repo:str):
    with open("./prompts/solotasktemplate", "r") as file:
        task_template = file.read()
    return task_template

def load_agent_promt(agent:str):
    with open(f"./prompts/{agent}", "r") as file:
        return file.read()
    
def read_file_tool(path:str):
    """
    Reads a file from the given path and returns its content.
    """
    try:
        with open(path, "r") as file:
            return file.read()
    except FileNotFoundError:
        raise Exception(f"File not found: {path}")
    except Exception as e:
        raise Exception(f"An error occurred while reading the file: {e}")

def write_file_tool(path:str, content:str):
    """
    Writes the passed content to a file at the specified path.
    This will overwrite the entire content of the file.
    """
    try:
        with open(path, "w") as file:
            file.write(content)
    except Exception as e:
        raise Exception(f"An error occurred while writing to the file: {e}")

def read_dir_structure(file_path:str):
    """
    Reads the directory structure starting from the given file path.
    Returns a dictionary representing the structure.
    """
    dir_structure = {}
    for root, dirs, files in os.walk(file_path):
        relative_path = os.path.relpath(root, file_path)
        dir_structure[relative_path] = {
            "directories": dirs,
            "files": files
        }
    return dir_structure

# AGENTS AND MDOELS

ollama_client = OllamaChatCompletionClient(model="llama3.2")
chatgpt_client = OpenAIChatCompletionClient(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY", ""))

coding_agent = AssistantAgent(
    name="coding_agent",
    model_client=chatgpt_client,
    system_message=load_agent_promt("coder"),
    tools=[read_file_tool, write_file_tool]
)

planning_agent = AssistantAgent(
    name="planning_agent",
    model_client=chatgpt_client,
    system_message=load_agent_promt("planner"),
    tools=[read_file_tool, write_file_tool, read_dir_structure]
)

test_agent = AssistantAgent(
    name="test_agent",
    model_client=chatgpt_client,
    system_message=load_agent_promt("tester"),
    tools=[read_file_tool, write_file_tool]
)

validate_agent = AssistantAgent(
    name="validate_agent",
    model_client=ollama_client,
    system_message=load_agent_promt("validator"),
    tools=[read_file_tool, write_file_tool]
)

text_termination = TextMentionTermination("APPROVE")
team = RoundRobinGroupChat([planning_agent, coding_agent], termination_condition=text_termination)

solo_agent = AssistantAgent(
    name="solo_agent",
    model_client=chatgpt_client,
    system_message="You're a helpful assistant. You will be given a task to complete. Use the tools provided to accomplish the task.",
    tools=[read_file_tool, write_file_tool]
)

# MAIN FUNCTION

# async def main():
#     index = 150
#     while index < 151: # TODO: Change to True when system is ready
#         repository_data = fetch_repository(index)
#         if not repository_data:
#             break
#         repository_path = clone_repository(repository_data['git_clone'])
#         prompt = prepare_agent_system(repository_data, repository_path)
#         await team.reset()
#         await Console(team.run_stream(task=prompt))
#         index += 1

async def main():
    repository_data = fetch_repository(1)
    if not repository_data:
        print("No repository data found.")
        return
    repository_path = clone_repository(repository_data['git_clone'])
    prompt = create_solo_prompt(repository_data, repository_path)
    await Console(solo_agent.run_stream(task=prompt, cancellation_token=CancellationToken()))


if __name__ == "__main__":
    asyncio.run(main())

