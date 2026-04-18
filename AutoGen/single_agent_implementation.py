from autogen_ext.models.ollama import OllamaChatCompletionClient
import os
import git
import requests
from autogen_ext.agents.file_surfer import FileSurfer
from autogen_agentchat.ui import Console
import sys
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core import EVENT_LOGGER_NAME
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(EVENT_LOGGER_NAME)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

LOCAL_DIR = "./git_repos/"
task_id = 1

import asyncio

async def execute_multi_agent_system():
    # Get task information
    response = requests.get(f"http://localhost:8081/task/index/{task_id}")
    path = checkout_repository(response.json())  # Ensure the function returns the path
    llama_client = OllamaChatCompletionClient(model="llama3.2")
    # Initialize the FileSurfer agent
    file_surfer = FileSurfer(
        name="GitRepositorySurfer",
        model_client=llama_client,
        base_path=path,
        description="A file surfer agent that can read and write files in a git repository.",
    )
    # Run the FileSurfer agent with the task
    result = await file_surfer.run(task="Read the tox.ini")
    
    # Iterate through messages to print each one clearly
    print("FileSurfer Messages:")
    for msg in result.messages:
        print(f"Source: {msg.source}\nContent:\n{msg.content}\n{'-'*40}")

def prepare_prompt():
    None

def checkout_repository(repository_information):
    # Check out repository 
    path = LOCAL_DIR + str(repository_information["instance_id"])
    repo_url = repository_information["git_clone"]
    repo_url_base = repo_url.split("https://", 1)[-1].split(".git")[0]
    repo_url_base = "https://" + repo_url_base + ".git"
    if not os.path.exists(path):  # Minor style improvement
        repo = git.Repo.clone_from(repo_url_base, path)
        repo.git.checkout(repository_information["Base_commit"])  # Ensure the repository is checked out
    return path  # Return the path for further use

def main():
    asyncio.run(execute_multi_agent_system())

if __name__ == "__main__":
    main()