import mesa

from Agents import Passenger, Car, StepType

def compute_manhattan(model):
    total_dist = 0
    for agent in model.schedule.agents:
        if type(agent) == "Car":
            total_dist += abs(agent.current.x - agent.next_dest.x) + abs(agent.current.y - agent.next_dest.y)
    return total_dist

class TransportModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, num_passengers, num_cars, width, height):
        super().__init__()

        self.num_passengers = num_passengers
        self.num_cars = num_cars
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivation(self)
        self.running = True
        self.clients = []
        self.cars = []

        # Create passenger agents
        for i in range(self.num_passengers):
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            a = Passenger(self.next_id(), self, self.grid.width, self.grid.height, x, y, self.schedule.steps)
            self.schedule.add(a)

            self.clients.append(a)
            self.grid.place_agent(a, (x, y))

        # Create car agents
        # 1 for now
        for i in range(self.num_cars):
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            a = Car(self.next_id(), self, x, y, step_type=StepType.QUEUE)
            self.schedule.add(a)
            self.cars.append(a)
            self.grid.place_agent(a, (x, y))

        self.datacollector = mesa.DataCollector(
            model_reporters={"Manhattan": compute_manhattan}, agent_reporters={}
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        # TO DO: only create new agent is current number of clients waiting < 5 
        if (self.schedule.steps % 15 == 0):
            # Create new passenger agent
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            a = Passenger(self.next_id(), self, self.grid.width, self.grid.height, x, y, self.schedule.steps)
            self.schedule.add(a)
            self.clients.append(a)
            self.grid.place_agent(a, (x, y))



        
