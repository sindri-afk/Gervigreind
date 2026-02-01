import collections
import heapq
import time

######################

class Heuristics:

	env = None

	# inform the heuristics about the environment, needs to be called before the first call to eval()
	def init(self, env):
		self.env = env

	# return an estimate of the remaining cost of reaching a goal state from state s
	def eval(self, s):
		raise NotImplementedError()

######################

class SimpleHeuristics(Heuristics):

	def eval(self, s):
		h = 0
		# if there is dirt: max of { manhattan distance to dirt + manhattan distance from dirt to home }
		# else manhattan distance to home
		if len(s.dirts) == 0:
			h = self.nb_steps(s.position, self.env.home)
		else:
			for d in s.dirts:
				steps = self.nb_steps(s.position, d) + self.nb_steps(d, self.env.home)
				if (steps > h):
					h = steps
			h += len(s.dirts) # sucking up all the dirt
		if s.turned_on:
			h += 1 # to turn off
		return h

	 # estimates the number of steps between locations a and b by Manhattan distance
	def nb_steps(self, a, b):
		return abs(a[0] - b[0]) + abs(a[1] - b[1])

######################

class SearchAlgorithm:
	heuristics = None

	def __init__(self, heuristics):
		self.heuristics = heuristics

	# searches for a goal state in the given environment, starting in the current state of the environment,
	# stores the resulting plan and keeps track of nb. of node expansions, max. size of the frontier and cost of best solution found 
	def do_search(self, env):
		raise NotImplementedError()

	# returns the plan found, the last time do_search() was executed
	def get_plan(self):
		raise NotImplementedError()

	# returns the number of node expansions of the last search that was executed
	def get_nb_node_expansions(self):
		raise NotImplementedError()

	# returns the maximal size of the frontier of the last search that was executed
	def get_max_frontier_size(self):
		raise NotImplementedError()

	# returns the cost of the plan that was found
	def get_plan_cost(self):
		raise NotImplementedError()

######################

# A Node is a tuple of these four items:
#  - value: the evaluation of this node
#  - parent: the parent of the node, or None in case of the root node
#  - state: the state belonging to this node
#  - action: the action that was executed to get to this node (or None in case of the root node)

Node = collections.namedtuple('Node',['value', 'parent', 'state', 'action'])

######################

class AStarSearch(SearchAlgorithm):
	nb_node_expansions = 0
	max_frontier_size = 0
	goal_node = None

	def __init__(self, heuristic):
		super().__init__(heuristic)

	def do_search(self, env):
		self.heuristics.init(env)
		self.nb_node_expansions = 0
		self.max_frontier_size = 0
		self.goal_node = None

		start_time = time.time()

		# --- 1. Initial state ---
		start_state = env.get_current_state()
		start_cost = 0

		# Node.value stores PATH COST g (important for get_plan_cost)
		start_node = Node(start_cost, None, start_state, None)

		# Frontier: priority queue ordered by f = g + h
		frontier = []
		tie = 0
		start_f = start_cost + self.heuristics.eval(start_state)
		heapq.heappush(frontier, (start_f, tie, start_node))

		# Best cost found so far for each state
		best_cost = {start_state: 0}

		self.max_frontier_size = 1

		# --- 2. Main A* loop ---
		while frontier:
			self.max_frontier_size = max(self.max_frontier_size, len(frontier))

			f, _, node = heapq.heappop(frontier)

			# REQUIRED by assignment: count every pop
			self.nb_node_expansions += 1

			state = node.state
			cost = node.value

			# Ignore outdated nodes
			if cost > best_cost.get(state, float("inf")):
				continue

			# --- 3. Goal test ---
			if env.is_goal_state(state):
				self.goal_node = node
				break

			# --- 4. Expand successors ---
			for action in env.get_legal_actions(state):
				next_state = env.get_next_state(state, action)
				step_cost = env.get_cost(state, action)
				new_cost = cost + step_cost

				if new_cost < best_cost.get(next_state, float("inf")):
					best_cost[next_state] = new_cost
					child = Node(new_cost, node, next_state, action)

					tie += 1
					f_value = new_cost + self.heuristics.eval(next_state)
					heapq.heappush(frontier, (f_value, tie, child))

					self.max_frontier_size = max(self.max_frontier_size, len(frontier))

		self.runtime_seconds = time.time() - start_time
		return


	def get_plan(self):
		if not self.goal_node:
			return None

		plan = []
		n = self.goal_node
		while n.parent:
			plan.append(n.action)
			n = n.parent

		return plan[::-1]

	def get_nb_node_expansions(self):
		return self.nb_node_expansions

	def get_max_frontier_size(self):
		return self.max_frontier_size

	def get_plan_cost(self):
		if self.goal_node:
			return self.goal_node.value
		else:
			return 0
