import collections
from enum import IntEnum
import re

##############

class Orientation(IntEnum):
  NORTH = 0
  EAST = 1
  SOUTH = 2
  WEST = 3

  # this allows things like: Orientation.NORTH + 1 == Orientation.EAST
  def __add__(self, i):
    orientations = list(Orientation)
    return orientations[(int(self) + i) % 4]

  def __sub__(self, i):
    orientations = list(Orientation)
    return orientations[(int(self) - i) % 4]

##############

State = collections.namedtuple('State',['position','orientation','turned_on','dirts'])

##############

class Environment:
  width = 0
  height = 0
  home = (0,0)
  dirts = ()
  obstacles = set() # set of positions of obstacles
  current_state = None

  # randomly initialize an environment of the given size
  def __init__(self, percepts):
    self.init_from_percepts(percepts)
    return

  def init_from_percepts(self, percepts):
    # Possible percepts are:
    # - "(SIZE x y)" denoting the size of the environment, where x,y are integers
    # - "(HOME x y)" with x,y >= 1 denoting the initial position of the robot
    # - "(ORIENTATION o)" with o in {"NORTH", "SOUTH", "EAST", "WEST"} denoting the initial orientation of the robot
    # - "(AT o x y)" with o being "DIRT" or "OBSTACLE" denoting the position of a dirt or an obstacle
    # Moving north increases the y coordinate and moving east increases the x coordinate of the robots position.
    # The robot is turned off initially, so don't forget to turn it on.
    
    dirts = []
    self.obstacles = set()
    percept_name_pattern = re.compile(r'\(\s*([^\s]+).*')
    for percept in percepts:
      match = percept_name_pattern.match(percept)
      if match:
        percept_name = match.group(1)
        if percept_name == "HOME":
          match = re.match(r'\(\s*HOME\s+([0-9]+)\s+([0-9]+)\s*\)', percept)
          if match:
            self.home = (int(match.group(1)), int(match.group(2)))
            print("robot is at " + str(self.home))
        elif percept_name == "SIZE":
          match = re.match(r'\(\s*SIZE\s+([0-9]+)\s+([0-9]+)\s*\)', percept)
          if match:
            self.width = int(match.group(1))
            self.height =int(match.group(2))
            print("environment is of size %d x %d" % (self.width, self.height))
        elif percept_name == "AT":
          match = re.match(r'\(\s*AT\s+([^\s]+)\s+([0-9]+)\s+([0-9]+)\s*\)', percept)
          if match:
            thing = match.group(1)
            position = (int(match.group(2)), int(match.group(3)))
            print(thing + " is at " + str(position))
            if thing == "DIRT":
              dirts.append(position)
            elif thing == "OBSTACLE":
              self.obstacles.add(position)
            else:
              print("unrecognized object " + thing + " in " + percept)
        elif percept_name == "ORIENTATION":
          match = re.match(r'\(\s*ORIENTATION\s+([^\s]+)\s*\)', percept)
          if match:
            orientation = Orientation[match.group(1)]
          print("orientation is " + str(orientation))
        else:
          print("unrecognized percept: " + percept)

      else:
        print("strange percept that does not match pattern: " + percept)
    self.dirts = tuple(dirts)
    self.current_state = State(self.home, orientation, False, self.dirts)

  def get_current_state(self):
    return self.current_state

  def get_legal_actions(self, state):
    actions = []
    if not state.turned_on:
      actions.append("TURN_ON")
    else:
      if state.position == self.home and len(state.dirts) == 0:
        actions.append("TURN_OFF")
      if state.position in state.dirts:
        actions.append("SUCK")
      nextposition = self.facingposition(state)
      if nextposition[0] > 0 and nextposition[0] <= self.width \
          and nextposition[1] > 0 and nextposition[1] <= self.height \
          and nextposition not in self.obstacles:
        actions.append("GO")
      actions.append("TURN_LEFT")
      actions.append("TURN_RIGHT")
    return actions

  def facingposition(self, state):
    if state.orientation == Orientation.NORTH:
      return (state.position[0], state.position[1]+1)
    elif state.orientation == Orientation.EAST:
      return (state.position[0]+1, state.position[1])
    elif state.orientation == Orientation.SOUTH:
      return (state.position[0], state.position[1]-1)
    elif state.orientation == Orientation.WEST:
      return (state.position[0]-1, state.position[1])

  def get_next_state(self, state, action):
    if action == "GO":
      return State(self.facingposition(state), state.orientation, state.turned_on, state.dirts)
    elif action == "TURN_ON":
      return State(state.position, state.orientation, True, state.dirts)
    elif action == "TURN_OFF":
      return State(state.position, state.orientation, False, state.dirts)
    elif action == "TURN_RIGHT":
      return State(state.position, state.orientation + 1, state.turned_on, state.dirts)
    elif action == "TURN_LEFT":
      return State(state.position, state.orientation - 1, state.turned_on, state.dirts)
    elif action == "SUCK":
      nextdirts = tuple(filter(lambda x: x != state.position, state.dirts))
      return State(state.position, state.orientation, state.turned_on, nextdirts)
    else:
      raise Exception("Unknown action %s" % (str(action)))

  def get_cost(self, state, action):
    if action == "TURN_OFF":
      return 1 + 50 * len(state.dirts)
    else:
      return 1

  def is_goal_state(self, state):
    return len(state.dirts)==0 and not state.turned_on

##############
