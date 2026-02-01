import java.util.List;

public class AStarSearch implements SearchAlgorithm {

	private int nbNodeExpansions;
	private int maxFrontierSize;

	private Heuristics heuristics;

	private Node goalNode;

	public AStarSearch(Heuristics h) {
		this.heuristics = h;
	}

	@Override
	public void doSearch(Environment env) {
		heuristics.init(env);
		nbNodeExpansions = 0;
		maxFrontierSize = 0;
		goalNode = null;

		// TODO implement the search here
		// Update nbNodeExpansions and maxFrontierSize while doing the search:
		// - nbNodeExpansions should be incremented by one for each node popped from the frontier
		// - maxFrontierSize should be the largest size of the frontier observed during the search measured in number of nodes
		// Once a goal node has been found, set the goalNode variable to it, this should take care of getPlan() and getPlanCost() below,
		// as long as the node contains the right information.

	}

	@Override
	public List<Action> getPlan() {
		if (goalNode == null) return null;
		else return goalNode.getPlan();
	}

	@Override
	public int getNbNodeExpansions() {
		return nbNodeExpansions;
	}

	@Override
	public int getMaxFrontierSize() {
		return maxFrontierSize;
	}

	@Override
	public int getPlanCost() {
		if (goalNode != null) return goalNode.evaluation;
		else return 0;
	}

}
