#!/bin/env python3

from tkinter import (
  Tk,
  Canvas, Frame, Menu,
  N, E, S, W, ### The Constants related to the positioning
  Event as TkEvent
)
from typing import Union, Callable
from PIL import ImageTk, Image

class NetApp(Tk):
  def __init__(self, name: str, base_size: Union[int, int], title: str = ""):
    """Create a Specific App for the Networks and Telecommunications
    using tkinter.

    Args:
        name (str): The displayed name of the app
        base_size (Union[int, int]): The default size of the window
        title (str, optional): The title of the window. Defaults to `name`.

    """
    super().__init__(name, name)

    self.name = name
    self.x_size = base_size[0]
    self.y_size = base_size[1]
    self.app_title = title

    if self.app_title == "":
      self.app_title = self.name

    self.equipments = {}
    self.equipment_nbr = 0
    self.reverse_equipments = {}

    self.mainframe = Frame(self, height=self.x_size, width=self.y_size)
    self.playground = Canvas(self.mainframe, bg="white", width=self.x_size, height=self.y_size)
    self.focused_tag = 0

    ### Let's define the menus
    self.master_menu = None
    self.rightclick_menu = None
    self.menus = {}
    self.__setMenuAndActions()
    self.__setRightClickMenuAndActions()

    ### Let's set the display
    self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    self.playground.grid(column=1, row=1, rowspan=self.y_size, columnspan=self.x_size)

  def __setRightClickMenuAndActions(self):
    self.rightclick_menu = Menu(self, tearoff=0)
    self.rightclick_menu.add_command(label="Change Name", command= lambda: print("Name Changed!"))
    self.rightclick_menu.add_command(label="Change Icon", command= lambda: print("Icon Changed!"))

  def __createNewMenu(self, title: str, return_title: bool = True) -> Union[Union[str, Menu], Menu]:
    """A private method to create a new menu and configure it internally.

    Args:
        title (str): The name to display, it should be pretty explicit.
        return_title (bool, optional): Specifies if you want to return the title. Defaults to True.

    Returns:
        Union[Union[str, Menu], Menu]: Returns either (title, Menu_Object) or Menu_Object
    """
    new_menu = Menu(self.master_menu, tearoff=0)

    self.menus[title] = {
      "name": title,
      "object": new_menu,
      "commands": {},
      "menus": {}
    }

    self.master_menu.add_cascade(label=title, menu=new_menu)

    if not return_title:
      return new_menu
    else:
      return (title, new_menu)
    
  def __createNewCommand(self, parent_menu: Union[str, Menu], title: str, command: Callable, return_title: bool = False) -> Union[None, str]:
    """A private method to create a New Command inside a parent menu and configure it internally.

    Args:
        parent_menu (Union[str, Menu]): The parent menu of the command (i.e. where you want the command to appear).
        title (str): The name of the command.
        command (Callable): The callable function
        return_title (bool, optional): `True` if you want this method to return the title. Defaults to False.

    Returns:
        Union[None, str]: Either return nothing or the title of the command.
    """
    parent_menu_label: str = parent_menu[0]
    parent_menu_object: Menu = parent_menu[1]

    parent_menu_object.add_command(label=title, command=command)

    ### Let's update the menus dictionary
    self.menus[parent_menu_label]["commands"].update({
      title: command
    })

    if not return_title:
      return None
    else:
      return title


  def __setMenuAndActions(self):
    """A private method to set the different menus and Actions of the Tkinter Window.
    """
    self.master_menu = Menu(self)
    self.config(menu=self.master_menu)

    ### File Menu
    file_menu = self.__createNewMenu("File")
    self.__createNewCommand(file_menu, "Export into PNG", self.export_png)

    ### Edit Menu
    edit_menu = self.__createNewMenu("Edit")
    self.__createNewCommand(edit_menu, "Insert Switch", lambda: self.add_equipment("switch"))
    self.__createNewCommand(edit_menu, "Insert Router", lambda: self.add_equipment("router"))
    self.__createNewCommand(edit_menu, "Insert Laptop", lambda: self.add_equipment("pc"))
    self.__createNewCommand(edit_menu, "Insert Mobile", lambda: self.add_equipment("mobile"))

  def __configureEquipment(self, equipment_tag: int) -> None:
    """A private method to configure the equipment with the given tag.

    Args:
        equipment_tag (int): The canvas `tagOrId` of the equipment
    """

    self.equipments[self.equipment_nbr]["bindings"].update({
      "left-click": {
        "id": self.playground.tag_bind(equipment_tag, "<Button-1>", lambda event: self.startDragFocus(event)),
        "command": self.startDragFocus
      },
      "left-click-motion": {
        "id": self.playground.tag_bind(equipment_tag, "<B1-Motion>", lambda event: self.endDragFocus(event)),
        "command": self.endDragFocus
      },
      "double-left-click": {
        "id": self.playground.tag_bind(equipment_tag, "<Double-Button-1>", lambda event: self.deleteItem(event)),
        "command": self.deleteItem
      },
      "right-click": {
        "id": self.playground.tag_bind(equipment_tag, "<Button-3>", lambda event: self.popRightClickMenu(event)),
        "command": self.popRightClickMenu
      }
    })

    ### Always set the last element on top
    self.playground.tag_raise(equipment_tag)

  def __prepareDeletionOfEquipment(self, equipment_tag: int) -> None:
    """A private method to unconfigure the equipment with the given tag.

    Args:
        equipment_tag (int): The canvas `tagOrId` of the equipment
    """

    self.equipments[self.reverse_equipments[equipment_tag]] = None

    ### Always set the last element on top
    self.playground.tag_lower(equipment_tag)

  def run(self):
    self.title(self.app_title)
    self.geometry(f"{self.x_size}x{self.y_size}")
    self.mainloop()

  def add_equipment(self, type) -> None:
    """Add the given equipment to the playground

    Args:
        type (str): Either `switch`, `router`, `pc`, `mobile`. (All entries are going to be lowercased)

    Raises:
        ValueError: You gave an unsupported type.
    """
    self.equipment_nbr += 1

    default_coords = (self.x_size // 2, self.y_size // 2) ### We're getting the center of the current window

    new_equipment = NetworkEquipment(type)
    canvas_tag = self.playground.create_image(default_coords, image=new_equipment.icon)

    self.equipments.update({
      self.equipment_nbr: {
        "item": new_equipment,
        "canvas_id": canvas_tag,
        "bindings": {}
      }
    })

    self.reverse_equipments.update({
      canvas_tag: self.equipment_nbr
    })

    self.__configureEquipment(canvas_tag)

    print(self.equipments)

  ### Drag & Drop
  def startDragFocus(self, event: TkEvent):
    x, y = event.x, event.y
    print(f"coords=({x}/{y})")

    self.focused_tag = self.playground.find_closest(x, y)[0]

  def endDragFocus(self, event: TkEvent):
    widget: Canvas = event.widget
    x = event.x if widget.winfo_x() + event.x <= self.x_size else self.x_size
    y = event.y if widget.winfo_y() + event.y <= self.y_size else self.y_size

    ### We're dividing by 2 the icon size to find the difference
    ### between the mouse position and the center of the icon.
    difference_mouse_icon = NetworkEquipment.icon_size[0] // 2

    self.playground.moveto(self.focused_tag, x-difference_mouse_icon, y-difference_mouse_icon)

  ### Double clicks
  def deleteItem(self, event: TkEvent):
    x, y = event.x, event.y

    selected_tag = self.playground.find_closest(x, y)[0]
    self.__prepareDeletionOfEquipment(selected_tag)
    self.playground.delete(selected_tag)

  ### Right Clicks
  def popRightClickMenu(self, event: TkEvent):
    x, y = event.x_root, event.y_root

    if self.rightclick_menu is not None:
      self.rightclick_menu.tk_popup(x, y)

  ### Export area
  def export_png(self):
    print("Current playground exported into PNG!")



class NetworkEquipment:

  supported_equipments = [
    "switch", "router",
    "pc", "mobile"
  ]
  icon_size = (64, 64)

  def __init__(self, type: str):
    """A simple class holding all the utils required to work
    with specific simulated network equipment inside a Tkinter Canvas.

    Args:
        type (str): Either `switch`, `router`, `pc`, `mobile`. (All entries are going to be lowercased)

    Raises:
        ValueError: You gave an unsupported type.
    """

    if type.lower() in NetworkEquipment.supported_equipments:
      self.equipment = type
      self.icon_path = f"./src/icons/{self.equipment}.png"
      self.icon = ImageTk.PhotoImage(Image.open(self.icon_path, "r").resize(NetworkEquipment.icon_size))

    else:
      raise ValueError("Unsupported Network Equipment")

t = NetApp("test-app", (800, 800))
t.run()