import java.util.Collection;

public interface Agent
{
    public String nextAction(Collection<String> percepts);
}
