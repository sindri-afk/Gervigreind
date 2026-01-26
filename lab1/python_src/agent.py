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
class VacuumAgent(Agent):
    DIRS = ["N", "E", "S", "W"]

    def start(self):
        self.phase = "INIT"
        self.dir = "N"

        # relative coordinates
        self.start_x = 0
        self.start_y = 0
        self.x = 0
        self.y = 0

        self.sweep_dir = "E"
        self.last_action = None
        self.shift_tried_go = False

        self.row_completed = False

        print("Vacuuming initiated::")

    def cleanup(self, percepts):
        self.start()

    def _turn_toward(self, target_dir):
        cur = self.DIRS.index(self.dir)
        tgt = self.DIRS.index(target_dir)
        right = (tgt - cur) % 4
        left = (cur - tgt) % 4
        return "TURN_RIGHT" if right <= left else "TURN_LEFT"

    def next_action(self, percepts):
        dirt = "DIRT" in percepts
        bump = "BUMP" in percepts

        if self.last_action == "TURN_RIGHT":
            self.dir = self.DIRS[(self.DIRS.index(self.dir) + 1) % 4]
        elif self.last_action == "TURN_LEFT":
            self.dir = self.DIRS[(self.DIRS.index(self.dir) - 1) % 4]
        elif self.last_action == "GO" and not bump:
            if self.dir == "N":
                self.y += 1
            elif self.dir == "S":
                self.y -= 1
            elif self.dir == "E":
                self.x += 1
            elif self.dir == "W":
                self.x -= 1

        if dirt:
            self.last_action = "SUCK"
            return "SUCK"

        if self.phase == "INIT":
            self.phase = "FIND_NORTH"
            self.last_action = "TURN_ON"
            return "TURN_ON"

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

        if self.phase == "FIND_WEST":
            if self.dir != "W":
                act = self._turn_toward("W")
                self.last_action = act
                return act

            if bump and self.last_action == "GO":
                self.phase = "SWEEP"
                self.sweep_dir = "E"
                self.row_completed = False
                act = self._turn_toward("E")
                self.last_action = act
                return act

            self.last_action = "GO"
            return "GO"

        if self.phase == "SWEEP":
            if self.dir != self.sweep_dir:
                act = self._turn_toward(self.sweep_dir)
                self.last_action = act
                return act

            if bump and self.last_action == "GO":
                self.row_completed = True
                self.phase = "SHIFT_SOUTH"
                self.shift_tried_go = False
                act = self._turn_toward("S")
                self.last_action = act
                return act

            self.last_action = "GO"
            return "GO"

        if self.phase == "SHIFT_SOUTH":
            if self.dir != "S":
                act = self._turn_toward("S")
                self.last_action = act
                return act

            if self.shift_tried_go and self.last_action == "GO":
                if bump:
                    if self.row_completed:
                        self.phase = "RETURN"
                    else:
                        self.phase = "SWEEP"
                        act = self._turn_toward(self.sweep_dir)
                        self.last_action = act
                        return act
                else:
                    self.sweep_dir = "W" if self.sweep_dir == "E" else "E"
                    self.row_completed = False
                    self.phase = "SWEEP"
                    act = self._turn_toward(self.sweep_dir)
                    self.last_action = act
                    return act

            self.shift_tried_go = True
            self.last_action = "GO"
            return "GO"

        if self.phase == "RETURN":
            dx = self.start_x - self.x
            dy = self.start_y - self.y

            if dx != 0:
                target = "E" if dx > 0 else "W"
                if self.dir != target:
                    act = self._turn_toward(target)
                    self.last_action = act
                    return act
                self.last_action = "GO"
                return "GO"

            if dy != 0:
                target = "N" if dy > 0 else "S"
                if self.dir != target:
                    act = self._turn_toward(target)
                    self.last_action = act
                    return act
                self.last_action = "GO"
                return "GO"

            self.phase = "OFF"
            self.last_action = "TURN_OFF"
            return "TURN_OFF"

        self.last_action = "TURN_OFF"
        return "TURN_OFF"
