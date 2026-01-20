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
class SimpleSweepAgent(Agent):
  DIRS = ["N", "E", "S", "W"]

  def start(self):
    self.phase = "INIT"
    self.dir = "N"

    # Arbitrary start/origin in our *relative* coordinate system.
    # Could be (25,25) etc. Only consistency matters.
    self.start_x = 0
    self.start_y = 0
    self.x = self.start_x
    self.y = self.start_y

    # current sweep direction along a row: "E" or "W"
    self.sweep_dir = "E"

    # remembers what we did last turn
    self.last_action = None

    # used only in SHIFT_SOUTH: did we already attempt the south GO?
    self.shift_tried_go = False

    print("SimpleSweepAgent start")

  def cleanup(self, percepts):
    self.start()

  def _turn_toward(self, target_dir):
    """Return TURN_LEFT or TURN_RIGHT to rotate one step toward target_dir."""
    cur = self.DIRS.index(self.dir)
    tgt = self.DIRS.index(target_dir)
    right_steps = (tgt - cur) % 4
    left_steps = (cur - tgt) % 4
    return "TURN_RIGHT" if right_steps <= left_steps else "TURN_LEFT"

  def next_action(self, percepts):
    dirt = "DIRT" in percepts
    bump = "BUMP" in percepts

    # -------- update internal model based on last action + current bump ----------
    if self.last_action == "TURN_RIGHT":
      self.dir = self.DIRS[(self.DIRS.index(self.dir) + 1) % 4

      ]
    elif self.last_action == "TURN_LEFT":
      self.dir = self.DIRS[(self.DIRS.index(self.dir) - 1) % 4]
    elif self.last_action == "GO":
      # only move if GO succeeded (no bump)
      if not bump:
        if self.dir == "N":
          self.y += 1
        elif self.dir == "S":
          self.y -= 1
        elif self.dir == "E":
          self.x += 1
        elif self.dir == "W":
          self.x -= 1

    print(
      f"Phase: {self.phase}, Dir: {self.dir}, "
      f"Pos: ({self.x},{self.y}), Start: ({self.start_x},{self.start_y}), "
      f"Last: {self.last_action}, Bump: {bump}, Dirt: {dirt}"
    )

    # ---------------- always clean ----------------
    if dirt:
      self.last_action = "SUCK"
      return "SUCK"

    # ---------------- INIT ----------------
    if self.phase == "INIT":
      # Define the origin at the moment we actually begin the episode.
      # (No matter what absolute square the world calls "home", this is our start.)
      self.x = self.start_x
      self.y = self.start_y

      self.phase = "FIND_NORTH"
      self.last_action = "TURN_ON"
      return "TURN_ON"

    # ---------------- find north wall ----------------
    if self.phase == "FIND_NORTH":
      if self.dir != "N":
        act = self._turn_toward("N")
        self.last_action = act
        return act

      if bump and self.last_action == "GO":
        self.phase = "FIND_WEST"
        act = self._turn_toward("W")
        self.last_action = act
        return act

      self.last_action = "GO"
      return "GO"

    # ---------------- find west wall (north-west corner) ----------------
    if self.phase == "FIND_WEST":
      if self.dir != "W":
        act = self._turn_toward("W")
        self.last_action = act
        return act

      if bump and self.last_action == "GO":
        self.phase = "SWEEP"
        self.sweep_dir = "E"
        act = self._turn_toward("E")  # turn away from wall to avoid GO-bump spam
        self.last_action = act
        return act

      self.last_action = "GO"
      return "GO"

    # ---------------- sweep row ----------------
    if self.phase == "SWEEP":
      if self.dir != self.sweep_dir:
        act = self._turn_toward(self.sweep_dir)
        self.last_action = act
        return act

      if bump and self.last_action == "GO":
        self.phase = "SHIFT_SOUTH"
        self.shift_tried_go = False
        act = self._turn_toward("S")
        self.last_action = act
        return act

      self.last_action = "GO"
      return "GO"

    # ---------------- shift south exactly one cell ----------------
    if self.phase == "SHIFT_SOUTH":
      if self.dir != "S":
        act = self._turn_toward("S")
        self.last_action = act
        return act

      # If we already tried going south, interpret the result now
      if self.shift_tried_go and self.last_action == "GO":
        if bump:
          # can't go south => finished sweeping, go return to start
          self.phase = "RETURN"
          # start turning toward a sensible direction for return
          if self.x != self.start_x:
            need = "W" if self.x > self.start_x else "E"
          else:
            need = "S" if self.y > self.start_y else "N"
          act = self._turn_toward(need)
          self.last_action = act
          return act
        else:
          # moved south 1 cell => flip sweep direction and continue
          self.sweep_dir = "W" if self.sweep_dir == "E" else "E"
          self.phase = "SWEEP"
          act = self._turn_toward(self.sweep_dir)
          self.last_action = act
          return act

      # Otherwise: attempt to go south ONE time
      self.shift_tried_go = True
      self.last_action = "GO"
      return "GO"

    # ---------------- return to starting position (start_x,start_y) ----------------
    if self.phase == "RETURN":
      # If we bump while returning, don't spam GO.
      # Turn once to change approach and avoid infinite bump loops.
      if bump and self.last_action == "GO":
        self.last_action = "TURN_RIGHT"
        return "TURN_RIGHT"

      dx = self.start_x - self.x
      dy = self.start_y - self.y

      # fix x first
      if dx != 0:
        target_dir = "E" if dx > 0 else "W"
        if self.dir != target_dir:
          act = self._turn_toward(target_dir)
          self.last_action = act
          return act
        self.last_action = "GO"
        return "GO"

      # then fix y
      if dy != 0:
        target_dir = "N" if dy > 0 else "S"
        if self.dir != target_dir:
          act = self._turn_toward(target_dir)
          self.last_action = act
          return act
        self.last_action = "GO"
        return "GO"

      # at start (our chosen origin)
      self.phase = "OFF"
      self.last_action = "TURN_OFF"
      return "TURN_OFF"

    # ---------------- off ----------------
    if self.phase == "OFF":
      self.last_action = "TURN_OFF"
      return "TURN_OFF"

    # fallback
    self.last_action = "TURN_OFF"
    return "TURN_OFF"
