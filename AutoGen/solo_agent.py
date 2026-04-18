from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.ollama import OllamaChatCompletionClient
import asyncio
import os
from ..multi_agent_system_helper.autogen_tools import test_changes_tool, read_dir_structure, read_file_tool, write_file_tool
from ..multi_agent_system_helper.helper_functions import set_working_directory, fetch_problem_statement, create_team_prompt, clone_repository

ollama_client = OllamaChatCompletionClient(model="llama3.2")
chatgpt_client = OpenAIChatCompletionClient(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY", ""))

planning_agent = AssistantAgent(
    name="planning_agent",
    model_client=chatgpt_client,
    system_message="You're part of a team of agents working on a GitHub repository that contains bugs. You, in particular, are responsible for coordinating the other agents to fix the bugs described in the task. To do so, you will read the problem statement and the repository structure, and then assign tasks to the coding agent. Use the tools provided to accomplish the task.",
    reflect_on_tool_use=True,
    tools=[read_file_tool, read_dir_structure]
)

read_file_agent = AssistantAgent(
    name="read_file_agent",
    model_client=chatgpt_client,
    system_message="You're a file reading agent. You will read the issued files and return their content. Use the tools provided to accomplish the task.",
    tools=[read_file_tool],
    reflect_on_tool_use=False
)

# Define returning value for the read file/coding and implementation agent

coding_agent = AssistantAgent(
    name="coding_agent",
    model_client=chatgpt_client,
    #reflect_on_tool_use=True,
    system_message="You're a coding agent. You will only fix the code and return this fixed code. Use the tools provided to accomplish the task."
)

implementation_agent = AssistantAgent(
    name="implementation_agent",
    model_client=chatgpt_client,
    system_message="You're an implementation agent. You will apply the changes made by the coding agent to the codebase. Use the tools provided to accomplish the task.",
    tools=[write_file_tool],
    reflect_on_tool_use=False
)

verify_agent = AssistantAgent(
    name="verify_agent",
    model_client=chatgpt_client,
    system_message="You're a verification agent. You will verify the changes made by the prior agents and rate them whether they are acceptable (then you write 'APPROVE') or not. When not, summarize your findings and propose them.",
    tools=[read_file_tool],
    reflect_on_tool_use=True
)

test_agent = AssistantAgent(
    name="test_agent",
    model_client=chatgpt_client,
    system_message="You're a testing agent. You will test the changes written to the codebase by the others. To do so, you can use the provided tools. Afterwards, propose the results.",
    tools=[test_changes_tool],
    reflect_on_tool_use=True
)

team = RoundRobinGroupChat([planning_agent, read_file_agent, coding_agent, implementation_agent, test_agent, verify_agent], termination_condition=TextMentionTermination("APPROVE"))

async def main():
    repository_data = fetch_problem_statement(1)
    if not repository_data:
        print("No repository data found.")
        return
    repository_path = clone_repository(repository_data['git_clone'])
    prompt = create_team_prompt(repository_data, repository_path)
    set_working_directory(repository_path)
    print(f"Working directory set to: {os.getcwd()}")
    await team.reset()
    await Console(team.run_stream(task=prompt))

if __name__ == "__main__":
    asyncio.run(main())


# TODO: Brauch es den root-path? Wir setzen diesen ja - ergo: Rel. Path genügt