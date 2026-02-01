import java.util.Collection;
import java.util.List;
import java.util.Random;

public class RandomAgent implements Agent
{
	private Random random = new Random();

	// the model of the environment 
	private Environment env;
	
	public RandomAgent() { }

    public void init(Collection<String> percepts) {
    	env = new Environment(percepts);
    }

    /**
     * returns a random legal move and updates the current state of the environment appropriately
     */
    public String nextAction(Collection<String> percepts) {
    	List<Action> moves = env.legalMoves(env.getCurrentState());
    	Action randomAction = moves.get(random.nextInt(moves.size()));
    	env.doAction(randomAction);
		System.out.println("executing " + randomAction);
		return randomAction.name();
	}
}
