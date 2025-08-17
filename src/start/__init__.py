"""This module contains the submission of the project.

The module contains an inventory management agent that manipulates an inventory
database such that it can add, update, and delete items from the database.

This agent can also list all items. This is because it bugs me why one would
keep memory of the ids for the items. Okay, we can ensure that the update and
deletion processes require id from the user, but why should the user have to
remember ids for the items? Why not let the user be able to actually check what
id is for what item?
"""
from .database import Database

from agents import (
    Agent,Runner,OpenAIChatCompletionsModel,set_tracing_disabled,function_tool,
    input_guardrail,GuardrailFunctionOutput,RunResult,enable_verbose_stdout_logging
)
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel

import asyncio
import os

#enable_verbose_stdout_logging()

# Disable tracing till a third-party provider is available
set_tracing_disabled(True)

# Constants
load_dotenv()
API_KEY : str = os.environ["GEMINI_API_KEY"] #  Either provide your key
                                                    #  in .env file or replace
                                                    #  the os.environ expression
                                                    #  with your own key.
BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai"
MODEL : str = "gemini-2.5-flash" #  Can be replaced with other available models
                                 #  in google.

# Model
agent_model : OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model=MODEL,
    openai_client=AsyncOpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )
)

# Item model
class Item(BaseModel):
    id : int | None = None
    name : str | None = None
    quantity: int | None = None

# Tools

## Add an item
@function_tool
def addItem(item : Item) -> str:
    """Adds the given item in the database unless it already exists.
    
    Args:
        item(Item) : Item details, id is ignored.

    Returns:
        str : Message about what has taken place.
    """
    db : Database = Database()
    if id:= db.add(item.name,item.quantity):
        return f"Item '{item.name}'({item.quantity}) successfully added with id {id}."
    else:
        return f"Addition failed: Item '{item.name}' already exists."

## Update an item
@function_tool
def updateItem(item : Item) -> None:
    """Adds the given item in the database unless it already exists.
    
    Args:
        item(Item) : Item details, including the new name and/or quantity.

    Returns:
        str : Message about what has taken place.
    """
    if not item.id:
        return f"Update failed: No id provided!"

    db : Database = Database()
    if db.update(item.id,item.name,item.quantity):
        output : str = f"Successfully updated item with id {item.id}."
        if item.name:
            output += f" New name: {item.name}."
        if item.quantity:
            output += f" New quantity: {item.quantity}."
        return output
    else:
        return f"Update failed: Item '{item.name}' does not exist."


## Delete an item
@function_tool
def deleteItem(item : Item) -> str:
    """Deletes an item with the id matching the given item's id.
    
    Args:
        item(Item): Item details. Only id required.

    Returns:
        str: Message about what has taken place.
    """
    db: Database = Database()
    if db.delete(item.id):
        return f"Item with id {item.id} successfully deleted."
    else:
        return f"Deletion failed: No item exists with id {item.id}."

## List items
@function_tool
def listItems() -> str:
    """List all items along with their ids.
    
    In future, this tool will have options to narrow down the list, to avoid
    having to transfer huge amounts of information.

    Returns:
        str : A list of items and their ids.
    """
    
    return f"List: \n{Database()}"

## TODO: Add a function to search for an item by name or id, to for example
## let the user know what item is represented by an id, or what the id is for
## an item.

# Input Guardrail

## Output Type
class PromptValidation(BaseModel):
    is_valid : bool
    reasoning: str

## Agent
ig_agent : Agent = Agent(
    name="Add-List-Update-Delete Prompt Validator",
    instructions=("You check if the prompt is about adding, updating, deleting"
                  ", or listing items."),
    output_type=PromptValidation,
    model=agent_model
)

## Function
@input_guardrail
async def validate_prompt(ctx,agent,prompt : str) -> GuardrailFunctionOutput:
    """Validates the given prompt that it is about either addition, listing,
    updation or deletion.
    
    Args:
        ctx : Context
        agent: Agent calling the guardrail
        prompt: Prompt being validated
    
    Returns:
        GuardrailFunctionOutput: Output telling the data of the validation
        process and whether the tripwire triggered.
    """
    results : RunResult = await Runner.run(
        ig_agent,
        prompt
    )

    output : PromptValidation = results.final_output_as(PromptValidation)
    return GuardrailFunctionOutput(
        output_info=output,
        tripwire_triggered=not output.is_valid
    )

# Agent
agent : Agent = Agent(
    name="Inventory Manager",
    instructions=("Use the given tools for adding, listing, updating, or "
                  "deleting an item. When calling addItem, the input must not "
                  "have id, and must have name and quantity. When calling "
                  "updateItem or deleteItem, the input must have id. When "
                  "calling updateItem, the input must also have either name or "
                  "quantity or both. When calling listItems, take no inputs"),
    input_guardrails=[validate_prompt],
    tools=[addItem,updateItem,deleteItem,listItems],
    tool_use_behavior="stop_on_first_tool",
    model=agent_model
)

# Funny class to have workflow and print_dots synchronize
class DotSignal:
    stop : bool = False

async def workflow(prompt : str) -> None:
    """Invokes the agent for the given prompt.
    
    Args:
        prompt: User's prompt for the agent.
    """

    result : RunResult = await Runner.run(
        agent,
        prompt
    )

    # To gracefully stop the dots
    DotSignal.stop = True
    while DotSignal.stop:
        await asyncio.sleep(1)

    print(result.final_output)


async def print_dots() -> None:
    """Keep printing dots to make the user feel something is going on."""
    print("Processing",end="",flush=True)
    while not DotSignal.stop:
        print(".",end="",flush=True)
        await asyncio.sleep(1)
    print(flush=True)
    DotSignal.stop = False

async def dotted_workflow(prompt : str) -> None:
    """Workflow, plus the printing of dots"""
    tasks = [
        asyncio.create_task(workflow(prompt)),
        asyncio.create_task(print_dots()),        
    ]

    await asyncio.gather(*tasks)

def main() -> None:
    """Continuously takes inputs from the user till the user stops the program."""
    # Welcome the user
    print("The inventory agent welcomes you! Please tell it to add,"
            " update, or delete an item! Or press Ctrl+C to exit!")
    print("(You can also ask it to list the items, to lookup their id)") 
    while True:
        try:
            # Ask for prompt
            prompt : str = input(">>> ")
            if not prompt:
                print("No prompt, exiting")
                break
            # Run the agent
            asyncio.run(dotted_workflow(prompt))
            print(f"Your prompt was: {prompt}")
        except KeyboardInterrupt:
            print("Exit signal received, exiting")
            break
        except Exception as e:
            print(f"Exiting due to the following: {e}")
            break