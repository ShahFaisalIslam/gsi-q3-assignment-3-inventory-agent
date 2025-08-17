# GIAIC Quarter 3 Assignment 3 - Inventory Agent via OpenAI Agents SDK

This project consists of an inventory agent equipped with tools to manage an
inventory database.

## Agent Details

* **Name**: Inventory Management Agent
* **Instructions**: You are an inventory manager which uses the given tools for
adding, updating, or deleting an item.
* **Tools**:
    * `addItem`: Adds a new item to the inventory.
    * `updateItem`: Updates an existing item in the inventory.
    * `deleteItem`: Deletes an existing item in the inventory.
* **Tool Use Behavior**: It will stop at first tool call, in order to save LLM
usage. We can do this because the inputs and the outputs of the tools are
well-defined enough to always tell the user the same results for the operations.
### Tool Details

* `addItem`: If an item already exists of the same name, then the tool reports
that the item already exists, and reports its id. Otherwise, the tool generates
a random id, adds the item, and then informs that the item has been added with
the id.
* `updateItem`: If no item exists with the given id, then the tool reports that 
no item exists with the given id. Otherwise, the tool updates the given
parameters for the item in the database, and reports about the updates.
* `deleteItem`: If no item exists with the given id, then the tool reports about
this. Otherwise, the tool deletes the item and reports about this.

## Database Schema

Each item in a database consists of the following:
1. `id`: Unique identifier of the item, generated when a new item is added.
2. `name`: Name of the item. No two items must match the same name.
3. `quantity`: Quantity of the item.

## Operations

1. **Add**: The user will tell the agent the item's name and quantity. The operation
must fail if there already exists an item with the same name. Otherwise, the
operation leads to adding an item with the name and the quantity, with a
randomly generated id for the item.
2. **Update**: The user will tell the agent to update an item with the given id, as
well as the new name or the new quantity or both. The operation must fail if no
item exists with the given id. Otherwise, the given fields are updated.
3. **Delete**: The user will tell the agent to delete an item with the given id. The
operation must fail if item exists with the given id. Otherwise, the item is
deleted.

## Future Operations
* **Display**: The user will tell the agent to display items, additionally
telling whether to display all items, display an item with a particular name,
or an item with a particular id. As for displaying all items, the agent should
do so. As for the particular cases, the operation must fail if no item satisfies
the particular requirements. Otherwise, the item with the particular id or name
should be displayed. The agent should not entertain any other case for display.
