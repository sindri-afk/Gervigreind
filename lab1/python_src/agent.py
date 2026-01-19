import random

#############

"""Agent acting in some environment"""
class Agent(object):

  def __init__(self):
    return

  # this method is called on the start of the new environment
  # override it to initialise the agent
  def start(self):
    print("start called")
    return

  # this method is called on each time step of the environment
  # it needs to return the action the agent wants to execute as as string
  def next_action(self, percepts):
    print("next_action called")
    return "NOOP"

  # this method is called when the environment has reached a terminal state
  # override it to reset the agent
  def cleanup(self, percepts):
    print("cleanup called")
    return

#############

"""A random Agent for the VacuumCleaner world

 RandomAgent sends actions uniformly at random. In particular, it does not check
 whether an action is actually useful or legal in the current state.
 """
class RandomAgent(Agent):

  def next_action(self, percepts):
    print("perceiving: " + str(percepts))
    actions = ["TURN_ON", "TURN_OFF", "TURN_RIGHT", "TURN_LEFT", "GO", "SUCK"]
    action = random.choice(actions)
    print("selected action: " + action)
    return action

#############

# class KingAgent(Agent):
#   """
#   Strategy for KingAgent: 
#   - TURN_ON: 
#   - GO -> until we find a bump
#   - When we find a bump we TURN_LEFT until we find another bump
#   - When we find another bump we TURN_RIGHT x2, and go until we hit a bump
#   - When we hit a bump there we TURN_RIGHT, GO, TURN_LEFT, GO
#   - then when we hit a bump TURN_LEFT, GO, TURN_RIGHT, GO etc..
#   - and always check for bumps
#   actions: [START, GO, SUCK, TURN_RIGHT, TURN_LEFT]
#   """
#   directions = ["N", "S", "W", "E"]

#   def start(self):
#     self.phase = "INIT"
#     self.directions = "N"

#     self.x = 0 # the starting pos is always 0,0
#     self.y = 0

#     self.last_action = None

#   def cleanup(self, percepts):
#     self.start()

#   def next_action(self, percepts):
#     dirt = "DIRT" in percepts
#     bump = "BUMP" in percepts
  
class SimpleSweepAgent(Agent):
  DIRS = ["N", "E", "S", "W"]

  def start(self):
    self.phase = "INIT"
    self.dir = "N"
    self.x = 0
    self.y = 0
    self.sweep_dir = "E"
    self.last_action = None
    print("SimpleSweepAgent start")

  def cleanup(self, percepts):
    self.start()

  def next_action(self, percepts):
    dirt = "DIRT" in percepts
    bump = "BUMP" in percepts

    # --- update internal model ---
    if self.last_action == "TURN_RIGHT":
      self.dir = self.DIRS[(self.DIRS.index(self.dir) + 1) % 4]
    elif self.last_action == "TURN_LEFT":
      self.dir = self.DIRS[(self.DIRS.index(self.dir) - 1) % 4]
    elif self.last_action == "GO" and not bump:
      if self.dir == "N": self.y += 1
      elif self.dir == "S": self.y -= 1
      elif self.dir == "E": self.x += 1
      elif self.dir == "W": self.x -= 1

    # --- always clean ---
    if dirt:
      self.last_action = "SUCK"
      return "SUCK"

    # --- INIT ---
    if self.phase == "INIT":
      self.phase = "FIND_NORTH"
      self.last_action = "TURN_ON"
      return "TURN_ON"

    # --- find north wall ---
    if self.phase == "FIND_NORTH":
      if self.dir != "N":
        self.last_action = "TURN_RIGHT"
        return "TURN_RIGHT"
      if bump and self.last_action == "GO":
        self.phase = "FIND_WEST"
        self.last_action = "TURN_LEFT"  # start turning toward W
        return "TURN_LEFT"
      self.last_action = "GO"
      return "GO"

    # --- find west wall (corner) ---
    if self.phase == "FIND_WEST":
      if self.dir != "W":
        self.last_action = "TURN_LEFT"
        return "TURN_LEFT"
      if bump and self.last_action == "GO":
        self.phase = "SWEEP"
        self.sweep_dir = "E"
      self.last_action = "GO"
      return "GO"

    # --- sweep row ---
    if self.phase == "SWEEP":
      # face sweep_dir
      if self.dir != self.sweep_dir:
        self.last_action = "TURN_RIGHT"
        return "TURN_RIGHT"

      # if bumped at row end -> shift south
      if bump and self.last_action == "GO":
        self.phase = "SHIFT_SOUTH"
        self.last_action = "TURN_RIGHT"  # start turning to S
        return "TURN_RIGHT"

      self.last_action = "GO"
      return "GO"

    # --- shift south one cell ---
    if self.phase == "SHIFT_SOUTH":
      if self.dir != "S":
        self.last_action = "TURN_RIGHT"
        return "TURN_RIGHT"

      # if we tried to go south and bumped -> finished sweep
      if bump and self.last_action == "GO":
        self.phase = "RETURN"
        # fall through to RETURN next call by turning now:
        self.last_action = "TURN_RIGHT"
        return "TURN_RIGHT"

      # otherwise go south one cell, then flip direction and continue sweeping
      self.last_action = "GO"
      # after this GO succeeds (no bump), position updates next call
      self.sweep_dir = "W" if self.sweep_dir == "E" else "E"
      self.phase = "SWEEP"
      return "GO"

    # --- return to (0,0) ---
    if self.phase == "RETURN":
      if self.x != 0:
        target = "W" if self.x > 0 else "E"
        if self.dir != target:
          self.last_action = "TURN_RIGHT"
          return "TURN_RIGHT"
        self.last_action = "GO"
        return "GO"

      if self.y != 0:
        target = "S" if self.y > 0 else "N"
        if self.dir != target:
          self.last_action = "TURN_RIGHT"
          return "TURN_RIGHT"
        self.last_action = "GO"
        return "GO"

      # At home (0,0)
      self.phase = "OFF"
      self.last_action = "TURN_OFF"
      return "TURN_OFF"

    # --- OFF fallback ---
    self.last_action = "TURN_OFF"
    return "TURN_OFF"
