from agents import ItemHelpers, Agent, Runner
import asyncio
from multi_agent_system_helper.helper_functions import clone_repository, delete_repository
from .openai_agents_sdk_tools import create_team_prompt, fetch_problem_statement
from multi_agent_system_helper.openai_agents_sdk_tools import test_fixes, read_file_tool, write_file_tool, set_working_directory, read_dir_structure, get_repository_structure
import os
from pydantic import BaseModel
from typing import List

# TODO: Rename this file



### AGENTS ###

CODER_NAME = "Coder"
TESTER_NAME = "Tester"
VALIDATOR_NAME = "Validator"
PLANNER_NAME = "Planner"

with open("prompts/coder", "r") as f:
    coder_instructions = f.read()
with open("prompts/tester", "r") as f:
    tester_instructions = f.read()
with open("prompts/validator", "r") as f:
    validator_instructions = f.read()
with open("prompts/validator", "r") as f:
    validator_instructions = f.read()
with open("prompts/planner", "r") as f:
    planner_instructions = f.read()

coding_agent = Agent(
    name=CODER_NAME,
    instructions=coder_instructions,
    tools=[read_file_tool, write_file_tool]
)

test_agent = Agent(
    name=TESTER_NAME,
    instructions=tester_instructions,
    tools=[
        test_fixes
    ]
)

validation_agent = Agent(
    name=VALIDATOR_NAME,
    instructions=validator_instructions,
    tools=[read_file_tool]
)

with open("prompts/planner", "r") as f:
    planner_instructions = f.read()

planning_agent = Agent(
    name=PLANNER_NAME,
    instructions=planner_instructions,
    tools=[
        coding_agent.as_tool(
            tool_name=CODER_NAME,
            tool_description="Fixes code in assigned files based on a task description."
        ),
        test_agent.as_tool(
            tool_name=TESTER_NAME,
            tool_description="Tests the code changes made by the coding agent."
        ),
                validation_agent.as_tool(
            tool_name="validation_agent_tool",
            tool_description="Validates the code changes made by the coding agent."
        )
    ]
)

async def main():
    repository_data = fetch_problem_statement(25)
    repository_path = clone_repository(repository_data['git_clone'])
    try:
        prompt = create_team_prompt(repository_data, repository_path)
        #set_working_directory(repository_path)
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
                    print(f"-- Tool was called by the agent: {event.item.agent.name}")
                    print(f"Tool: {event.item.raw_item}")
                elif event.item.type == "tool_call_output_item":
                    print(f"-- Tool output: {event.item.output}")
                elif event.item.type == "message_output_item":
                    print(f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}")
        delete_repository(repository_path)
    except Exception as e:
        delete_repository(repository_path)

if __name__ == "__main__":
    asyncio.run(main())