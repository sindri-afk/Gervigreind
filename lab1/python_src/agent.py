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

    # position relative to starting square (home)
    self.x = 0
    self.y = 0

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
    # distances if we go right vs left
    right_steps = (tgt - cur) % 4
    left_steps = (cur - tgt) % 4
    return "TURN_RIGHT" if right_steps <= left_steps else "TURN_LEFT"

  def next_action(self, percepts):
    dirt = "DIRT" in percepts
    bump = "BUMP" in percepts

    # -------- update internal model based on last action + current bump ----------
    if self.last_action == "TURN_RIGHT":
      self.dir = self.DIRS[(self.DIRS.index(self.dir) + 1) % 4]

    elif self.last_action == "TURN_LEFT":
      self.dir = self.DIRS[(self.DIRS.index(self.dir) - 1) % 4]

    elif self.last_action == "GO":
      # only move if GO succeeded (no bump)
      if not bump:
        if self.dir == "N": self.y += 1
        elif self.dir == "S": self.y -= 1
        elif self.dir == "E": self.x += 1
        elif self.dir == "W": self.x -= 1

    print(f"Phase: {self.phase}, Dir: {self.dir}, Pos: ({self.x},{self.y}), Last: {self.last_action}, Bump: {bump}, Dirt: {dirt}")

    # ---------------- always clean ----------------
    if dirt:
      self.last_action = "SUCK"
      return "SUCK"

    # ---------------- INIT ----------------
    if self.phase == "INIT":
      self.phase = "FIND_NORTH"
      self.last_action = "TURN_ON"
      return "TURN_ON"

    # ---------------- find north wall ----------------
    if self.phase == "FIND_NORTH":
      if self.dir != "N":
        act = self._turn_toward("N")
        self.last_action = act
        return act

      # if we just tried to go north and bumped => at north wall
      if bump and self.last_action == "GO":
        self.phase = "FIND_WEST"
        # start turning toward west
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

      # if we just tried to go west and bumped => at west wall corner
      if bump and self.last_action == "GO":
        self.phase = "SWEEP"
        self.sweep_dir = "E"
        # let SWEEP handle orientation; do a turn away from wall to avoid GO-bump spam
        act = self._turn_toward("E")
        self.last_action = act
        return act

      self.last_action = "GO"
      return "GO"

    # ---------------- sweep row ----------------
    if self.phase == "SWEEP":
      # face along the row
      if self.dir != self.sweep_dir:
        act = self._turn_toward(self.sweep_dir)
        self.last_action = act
        return act

      # if we just tried to go along the row and bumped => end of row
      if bump and self.last_action == "GO":
        self.phase = "SHIFT_SOUTH"
        self.shift_tried_go = False
        # begin turning toward south
        act = self._turn_toward("S")
        self.last_action = act
        return act

      self.last_action = "GO"
      return "GO"

    # ---------------- shift south exactly one cell ----------------
    if self.phase == "SHIFT_SOUTH":
      # first face south
      if self.dir != "S":
        act = self._turn_toward("S")
        self.last_action = act
        return act

      # if we already attempted the south GO, interpret the result now
      if self.shift_tried_go and self.last_action == "GO":
        if bump:
          # can't go south => finished mowing
          self.phase = "RETURN"
          # start turning toward something sensible for return
          act = self._turn_toward("W" if self.x > 0 else "E" if self.x < 0 else ("S" if self.y > 0 else "N"))
          self.last_action = act
          return act
        else:
          # successfully moved south 1 cell => flip sweep direction and continue
          self.sweep_dir = "W" if self.sweep_dir == "E" else "E"
          self.phase = "SWEEP"
          # start turning toward new sweep dir (legal action, no NOOP)
          act = self._turn_toward(self.sweep_dir)
          self.last_action = act
          return act

      # otherwise: attempt to go south ONE time
      self.shift_tried_go = True
      self.last_action = "GO"
      return "GO"

    # ---------------- return to home (0,0) ----------------
    if self.phase == "RETURN":
      # If we bumped on a GO in return mode, our model might be wrong.
      # Fix by snapping the coordinate we were trying to reduce to 0.
      if bump and self.last_action == "GO":
        if self.dir == "S" and self.y > 0: self.y = 0
        if self.dir == "N" and self.y < 0: self.y = 0
        if self.dir == "W" and self.x > 0: self.x = 0
        if self.dir == "E" and self.x < 0: self.x = 0

      # move x toward 0 first
      if self.x != 0:
        target = "W" if self.x > 0 else "E"
        if self.dir != target:
          act = self._turn_toward(target)
          self.last_action = act
          return act
        self.last_action = "GO"
        return "GO"

      # then move y toward 0
      if self.y != 0:
        target = "S" if self.y > 0 else "N"
        if self.dir != target:
          act = self._turn_toward(target)
          self.last_action = act
          return act
        self.last_action = "GO"
        return "GO"

      # at home
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
