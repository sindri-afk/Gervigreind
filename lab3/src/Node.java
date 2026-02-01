import java.util.LinkedList;
import java.util.List;

public class Node implements Comparable<Node> {
	public State state;
	public Node parent;
	public Action action;
	public int depth;
	public int evaluation;

	/**
	 * create the root node of the search tree
	 * @param state the state belonging to this node
	 * @param val the evaluation of this node
	 */
	public Node(State state, int val) {
		this.parent = null;
		this.state = state;
		this.action = null;
		this.depth = 0;
		this.evaluation = val;
	}
	/**
	 * create a new node
	 * @param parent the parent of the node
	 * @param state the state belonging to this node
	 * @param action the action that was executed to get to this node
	 * @param val the evaluation of this node
	 */
	public Node(Node parent, State state, Action action, int val) {
		this.parent = parent;
		this.state = state;
		this.action = action;
		this.depth = parent.depth + 1;
		this.evaluation = val;
	}
	
	public List<Action> getPlan() {
		List<Action> plan = null;
		plan = new LinkedList<Action>();
		// go from the current node to the root by following the parent pointers
		// and collect the actions on the way
		Node n = this;
		while (n.parent != null) {
			plan.add(0, n.action);
			n = n.parent;
		}
		return plan;
	}

	public String toString() {
		return "Node{depth: " + depth + ", value: " + evaluation + ", state: " + state + ", path: " + getPlan() + "}";
	}

	public int compareTo(Node o) {
		return this.evaluation - o.evaluation;
	}
}