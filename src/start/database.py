"""This module contains class that accesses and manipulates the database.

The database is a JSON."""

from random import randint
from typing import Final
from typing_extensions import TypedDict
import json
from io import SEEK_SET

class Item(TypedDict):
    """Represents an item, and equivalent to a row in database"""
    id: int
    name: str
    quantity: int

class Singleton(type):
    """Meta-class that ensures any class derived from it has exactly one instance."""
    _instances : dict = {}
    def __call__(self, *args, **kwds):
        if self.__name__ not in self.__class__._instances:
            self.__class__._instances[self.__name__] = super().__call__(*args, **kwds)
        return self.__class__._instances[self.__name__]

class Database(metaclass=Singleton):
    """A singleton class for accessing and manipulating a JSON-based database."""

    DB_PATH : Final[str] = "database.json"
    MAX_ITEMS : Final[int] = 1000000000  # Discovered the hard way that gemini
                              # misbehaves with numbers greater than or equal to
                              # 1e19. So let's be nice and let the number be 
                              # much smaller.

    def __init__(self):
        with open(self.DB_PATH,"+a") as file:
            try:
                file.seek(0,SEEK_SET)  # To ensure data is read from the start
                self.__db : list[dict] = json.load(file)
            except: self.__db = []
    @classmethod
    def generate_id(cls) -> int:
        """Generates an item id.
        
        Assigns a random number as an id for a new item. Re-run this function if the
        generated id already exists in the database to avoid collisions.

        Returns:
            Id for a new item.
        """
        return randint(0,cls.MAX_ITEMS)

    def __save(self):
        """Saves database in the file."""
        with open(self.DB_PATH,"w") as file:
            json.dump(self.__db,file)

    def __get_row(self,id : int | None=None,name : str | None=None) -> dict | None:
        """Get row from the database with the given id or name, either of which
        gets matched.
        
        Args:
            id: Item's id, if given. It is given precedence over name if name
            is also provided.
            name: Item's name, if given.
        
        Returns:
            Row, if found. Otherwise, None.
        """
        if id is not None:
            for row in self.__db:
                if row["id"] == id:
                    return row

        if name is not None:
            for row in self.__db:
                if row["name"] == name:
                    return row

        return None

    def add(self,name : str, quantity: int) -> int | None:
        """Adds an item with the given name and quantity to the database.
        
        For now, it does not check whether the database is already full. Later,
        it will.

        Args:
            name: Item's name.
            quantity: Item's quantity.
        
        Returns:
            non-negative id if successful, None otherwise
        """
        id : int = -1

        # Stop if another item already exists with the same name.
        if self.__get_row(name=name):
            return None

        # We should use something that lets us feed already existing ids into
        # the id generator, instead of this loop which is good initially but
        # a really bad idea when this database really starts getting filled.
        # However, reaching that limit is not a problem for the demo this 
        # one suffices for.
        while True:
            id = self.generate_id()
            if not self.__get_row(id=id):
                break

        item : Item = Item(id=id,name=name,quantity=quantity)
        self.__db.append(item)
        self.__save()
        return id

    def update(self,id : int,name : str | None = None,
               quantity : str | None = None) -> bool:
        """Updates the fields of an item of the given id with the given values.

        Args:
            id: Item's id.
            name: Item's new name, if given.
            quantity: Item's new quantity, if given.
        
        
        Returns:
            True, if the update was successful. False, otherwise.
        """


        # Get the row, or die trying.
        row : dict = self.__get_row(id=id)
        if not row:
            return False

        # Change the row's parameters if provided
        if name:
            row["name"] = name
        if quantity:
            row["quantity"] = quantity

        # Fit it back into where it came from
        index : int = 0
        for _row in self.__db:
            if _row["id"] == id:
                break
            index += 1
        self.__db[index] = row
        self.__save()
        return True

    def delete(self,id : int):
        """Deletes an item of the given id.

        Args:
            id: Item's id.
        
        Returns:
            True, if the delete was successful. False, otherwise.
        """

        # Get index, or die trying
        index : int = 0
        for row in self.__db:
            if row["id"] == id:
                break
            index += 1
        if index == len(self.__db):
            return False
        
        # Pop it off
        self.__db.pop(index)
        self.__save()
        return True

    def __repr__(self) -> str:
        """Displays all rows in the database"""
        output : str = ""
        index : int = 1
        for row in self.__db:
            output += f"{index}. id:{row["id"]} name:{row["name"]} quantity:{row["quantity"]}\n"
            index += 1
        return output

    def list(self) -> str:
        """Lists all items with their ids in the database"""
        output : str = ""
        for row in self.__db:
            output += f"Name: {row["name"]}, id: {row["id"]}\n"
        return output

if __name__ == "__main__":
    db : Database = Database()
    
    print(f"Database:\n{db}")

    print("Database items:")
    print(db.list())

    choice : int = int(input("Enter 1 for adding, 2 for updating, and 3 for deleting: "))
    if choice == 1:
        print("Adding item")
        name : str = input("Name: ").lower()
        quantity: int = int(input("Quantity: "))
        print(f"Adding {name} with quantity {quantity}")
        if id:= db.add(name,quantity):
            print(f"Successfully added {quantity} {name}. Id: {id}")
        else:
            print(f"Failed to add {name}: Already exists. Perhaps you want to update it.")
    elif choice == 2:
        print("Updating item")
        id : int = int(input("ID: "))
        name : str = input("Name (if changing): ")
        quantity : int = int(input("Quantity(if changing, set to zero if not): "))
        if name == "":
            name = None
        if quantity == 0:
            quantity = None
        if db.update(id,name=name,quantity=quantity):
            if name:
                print(f"Successfully updated name of item #{id} to {name}.")
            if quantity:
                print(f"Successfully updated quantity of item #{id} to {quantity}.")
        else:
            print(f"Failed to update item #{id}: Does not exist. Perhaps you want to add it.")
    elif choice == 3:
        print("Deleting item")
        id : int = int(input("ID: "))
        if db.delete(id):
            print(f"Successfully deleted item #{id}.")
        else:
            print(f"Failed to delete item #{id}: Does not exist. Perhaps you already deleted it.")