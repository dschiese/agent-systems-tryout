from agents import ItemHelpers, AsyncOpenAI, Agent, Runner, LocalShellTool, LocalShellExecutor, OpenAIResponsesModel
import asyncio
from ..multi_agent_system_helper.helper_functions import set_working_directory, separate_git_clone_command, clone_repository, create_team_prompt, fetch_problem_statement
from ..multi_agent_system_helper.openai_agents_sdk_tools import read_file_tool, write_file_tool
import os
# TODO: Rename this file
### AGENTS ###

coding_agent = Agent(
    name="coding_agent",
    instructions="You're a coding agent. Your task is to read the files assigned to you, think of a solution , and then write the fixed code to the files.",
    handoffs=[],
    tools=[read_file_tool, write_file_tool]
)

planning_agent = Agent(
    name="planning_agent",
    instructions="You're part of a team of agents working on a GitHub repository that contains bugs. You, in particular, are responsible for coordinating the other agents to fix the bugs described in the task. To do so, you will read the problem statement and the repository structure, and then assign tasks to the coding agent with the errornous files mentioned. Use the tools provided to accomplish the task.",
    handoffs=[coding_agent]
)





async def main():
    repository_data = fetch_problem_statement(1)
    if not repository_data:
        print("No repository data found.")
        return
    repository_path = clone_repository(repository_data['git_clone'])
    prompt = create_team_prompt(repository_data, repository_path)
    set_working_directory(repository_path)
    print(f"Working directory set to: {os.getcwd()}")
    result = Runner.run_streamed(
        planning_agent,
        context={"repos_data": repository_data},
        input=prompt
    )
    async for event in result.stream_events():
        # We'll ignore the raw responses event deltas
        if event.type == "raw_response_event":
            continue
        # When the agent updates, print that
        elif event.type == "agent_updated_stream_event":
            print(f"Agent updated: {event.new_agent.name}")
            continue
        # When items are generated, print them
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                print("-- Tool was called")
            elif event.item.type == "tool_call_output_item":
                print(f"-- Tool output: {event.item.output}")
            elif event.item.type == "message_output_item":
                print(f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}")
            else:
                pass  # Ignore other event types

if __name__ == "__main__":
    asyncio.run(main())