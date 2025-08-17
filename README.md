# GIAIC Quarter 3 Assignment 3 - Inventory Agent via OpenAI Agents SDK

This project consists of an inventory agent equipped with tools to manage an
inventory database.

## Agent Details

* **Name**: Inventory Management Agent
* **Instructions**: Use the given tools for adding, listing, updating, or
  deleting an item. When calling addItem, the input must not have id, and must
  have name and quantity. When calling updateItem or deleteItem, the input must
  have id. When calling updateItem, the input must also have either name or "
  quantity or both. When calling listItems, take no inputs.
* **Tools**:
    * `addItem`: Adds a new item to the inventory.
    * `updateItem`: Updates an existing item in the inventory.
    * `deleteItem`: Deletes an existing item in the inventory.
    * `listItems`: Lists all items in the inventory.
* **Tool Use Behavior**: It will stop at first tool call, in order to save LLM
   usage. We can do this because the inputs and the outputs of the tools are
   well-defined enough to always tell the user the same results for the operations.
* **Input Guardrail**: The guardrail protects the agent from responding to any
  query that is not relevant to its operations, which are addition, updation,
  deletion, and listing.
### Tool Details

* `addItem`: If an item already exists of the same name, then the tool reports
that the item already exists. Otherwise, the tool generates a random id, adds 
the item, and then informs that the item has been added with the id.

> Note: As Gemini truncated ids greater than or equal to 1e19, I have for now
>         reduced the max id(and amount of items) to a much smaller value i.e. 
>         1e9.

* `updateItem`: If no item exists with the given id, then the tool reports that 
no item exists with the given id. Otherwise, the tool updates the given
parameters for the item in the database, and reports about the updates.
* `deleteItem`: If no item exists with the given id, then the tool reports about
this. Otherwise, the tool deletes the item and reports about this.
* `listItem`: The tool simply reports all available rows in its database.

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
4. **List**: The user will tell the agent to list all items. The operation never
fails. All items are listed, each item consisting of its id, name, and quantity.

## Future Operations
* **Search**: The user will tell the agent to search for an item, by its id or
by its name. The operation fails if no item exists that satisfies the search
criterion. Otherwise, the agent produces the item, consisting of its id, name,
and quantity. It is possible that the user may not directly tell to search, but
may simply inquire about the status of the item.