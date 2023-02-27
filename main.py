import math

class Object:
  visual = """
    NULL
  """
  x = 0
  y = 0
  width = 6

class Building(Object):
  visual = """
    ##########   
   ############# 
  ###############
    ####  #  #   
    ##########   
    ####  #  #   
    ##########   
    ##########   
  """
  width = 17


class Fence(Object):
  visual = """
   ⌂   ⌂   ⌂   ⌂  
  =|===|===|===|==
  =|===|===|===|==
  """
  width = 18


class Growable:
  visuals = ["""
    NULL
  """]
  visualState = 0
  x = 0
  y = 0
  width = 6

class Sunflower(Growable):
  visuals = ["""
  \o/
  """, """
  \o/
   | 
  """, """
  \❃/
  \|/
   | 
  """]
  width = 5

class Clover(Growable):
  visuals = ["""
   {} 
  \|/ 
  """, """
   {} 
  ~Y~ 
  \|/ 
   |  
  """, """
  {{}}
  ~Y~ 
  \|/ 
  \|/ 
  """]
  width = 6

def render(_objects, with_ids = False) -> None:
  # viewport is max 64x16 chars, we treat it like a 2D array by using the logic of:
  # x = (index % width),
  # y = math.floor(index / height)
  # index = x % width + y % width * width
  width = 64
  height = 16
  viewport = [" "] * width * height

  # TOOD: Implement z-index
  for id in _objects:
    object = _objects[id]
    vis = None
    if issubclass(type(object), Growable):
      vis = object.visuals[object.visualState].replace("\n", "")
    else:
      vis = object.visual.replace("\n", "")

    for i in range(0, len(vis)):
      # Map out to viewport cordinates
      object_px_x = (i % object.width) + object.x # (x offset from object x + object x) -> (real x)
      object_px_y = math.floor(i / object.width) + object.y # (y offset from object y + object y) -> (real y)
      object_px_index = object_px_x % width + object_px_y % width * width
      if object_px_index < len(viewport):
        viewport[object_px_index] = vis[i]

    if with_ids == True:
      id_index = object.x % width + object.y % width * width
      if id_index < len(viewport):
        # In case the object id is 2 or more digits, roll over to next columns to not
        # end up shifting over everything
        for i in range(0, len(str(id))):
          viewport[id_index + i] = str(id)[i]

  # The viewport also needs to be restricted to the width, so at the end, at every [width]
  # chars, we insert a newline 
  for i in range(0, height):
    viewport[i * width] = "\n"

  # We render completely in memory so that we only have to make a single print call
  print("".join(viewport))

def make_input(prompt: str, *args) -> str:
  template = prompt + "\n"
  # Allows us to unbox variable length args but packed into one array at runtime, basically reverse C# params
  for i in range(0, len(args)):
    if args[i] == None or args[i] == "":
      continue
    template += "[" + ((args[i])[0]).upper() + "]" + (args[i])[1:] + ("  " if i % 2 == 0 else " \n")
  return input(template)

# Safe integer input that protects us against exceptions, and will loop if invalid answer is given
def int_input(prompt):
  while True:
      try:
        response = int(input(prompt))
        break
      except ValueError:
        pass
  return response

garden_name = ""
object_map = {
  "building": Building,
  "fence": Fence,
  "sunflower": Sunflower,
  "clover": Clover
}
objects = { }

while True:
  print("""
    __  __ _ _____  _  ____   ____  _____  _  __ __  __  __ 
    \ \/ /| || () )| || _) \ / () \ | () )| ||  |  ||  \/  |
     \__/ |_||_|\_\|_||____//__/\__\|_|\_\|_| \___/ |_|\/|_|
  
  A garden designing game - by Zekiah-A ⚘
  """)
  
  match make_input("Use your keyboard to choose an option", "start game", "exit").lower():
    case "s" | "start game":
      print("[Warning] Console dimensions are recommended to be of at least 64x16 characters.")
      print("If you can't see the title above properly, you need to make your window wider.\n")
      garden_name = input("Enter the name of your garden\n")
      break
    case "e" | "exit":
      exit()

while True:
  response = None
  if len(objects) == 0:
    response = make_input("Create garden '" + garden_name + "' - options:", "place object", "view garden", "exit").lower()
  else:
     response = make_input("Edit garden '" + garden_name + "' - options:", "place object", "delete object", "move object ", "grow object", "view garden ", "exit").lower()

  match response:
    case "p" | "place object":
      # Dynamically instantiate the class from object name using a dictionary, we will ask the user
      # until they give us a response that will not give null when performing a lookup, fuzzy matching
      # with the dictionary is also implemented using next
      object_class = None
      while object_class == None:
        place_input = make_input("What object would you like to place?", *list(object_map.keys()))
        object_class = object_map.get(place_input)
        if object_class == None:
          object_class = next(value for key, value in object_map.items() if key.startswith(place_input.lower()))

      object = object_class()
      print(object.visuals[object.visualState] if issubclass(type(object), Growable) else object.visual)
      object.x = int_input("How far across would you like to place the object <->?\n")
      object.y = int_input("How far from the top will you like to place your object ↑↓?\n")
      # We have to make sure id is unique, if lots of deleteions and additions are done
      # length may not be enough to ensure they do not overlap
      id = len(objects) + 1
      while objects.get(id):
        id = len(objects) + 1
      objects[id] = object
      render(objects)
    case "d" | "delete object":
      render(objects, True)
      id = -1
      while objects.get(id) == None:
        id = int_input("Enter the ID of the object you want to delete\n")
      objects.pop(id) 
      render(objects)
      continue
    case "v" | "view garden":
      print("Viewing '" + garden_name + "'")
      render(objects)
    case "m" | "move object":
      render(objects, True)
      id = -1
      while objects.get(id) == None:
        id = int_input("Enter the ID of the object you want to move\n")
      
      objects[id].x = int_input("How far across would you like to move the object <--->?\n")
      objects[id].y = int_input("How far from the top will you like to move your object ^v?\n")
      render(objects)
      continue
    case "g" | "grow object":
        # Only let player select a growable object (plant)
        growable_objects = dict(filter(lambda pair: issubclass(type(pair[1]), Growable), objects.items()))
        if (len(growable_objects) == 0):
          print("You haven't placed down any growable objects yet, cannot grow any!\n")
          continue
        print("[ONLY SHOWING] Growable objects:")
        render(growable_objects, True)
        id = -1
        while growable_objects.get(id) == None:
          id = int_input("Enter the ID of the growable object you want to grow\n")

        if objects[id].visualState < len(objects[id].visuals) - 1:
          objects[id].visualState += 1
        else:
          print("Cannot grow more, object is already fully grown!")
        render(objects)
        continue
    case "e" | "exit":
      exit()
    case _:
      continue