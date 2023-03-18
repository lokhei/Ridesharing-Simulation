import mesa
import random

from Agents import Passenger, Car, StepType

def compute_manhattan(model):
    total_dist = 0
    for agent in model.schedule.agents:
        if type(agent) == "Car":
            print(total_dist)
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
        self.seed5 = random.Random(5)
        self.seed6 = random.Random(6)


        # Create passenger agents
        seed1 = random.Random(1)
        seed2 = random.Random(2)
        for i in range(self.num_passengers):
            # Add the agent to a random grid cell
            x = seed1.randrange(self.grid.width)
            y = seed2.randrange(self.grid.height)
            a = Passenger(self.next_id(), self, self.grid.width, self.grid.height, x, y, self.schedule.steps)
            self.schedule.add(a)

            self.clients.append(a)
            self.grid.place_agent(a, (x, y))

        # Create car agents
        # 1 for now
        seed3 = random.Random(3)
        seed4 = random.Random(4)
        for i in range(self.num_cars):
            # Add the agent to a random grid cell
            x = seed3.randrange(self.grid.width)
            y = seed4.randrange(self.grid.height)
            a = Car(self.next_id(), self, x, y, step_type=StepType.CLOSEST)
            self.schedule.add(a)
            self.cars.append(a)
            self.grid.place_agent(a, (x, y))

       

        self.datacollector = mesa.DataCollector(
            model_reporters={"Manhattan": compute_manhattan},
            agent_reporters={
            "Steps": lambda a: a.steps_taken if a.type == "Car" else None,
            "WaitingTime": lambda b: b.actual_waiting_time if b.type == "Passenger" else None
            }
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        # TO DO: only create new agent is current number of clients waiting < 5 
        if (self.schedule.steps % 10 == 0):
            # Create new passenger agent
            x = self.seed5.randrange(self.grid.width)
            y = self.seed6.randrange(self.grid.height)
            a = Passenger(self.next_id(), self, self.grid.width, self.grid.height, x, y, self.schedule.steps)
            self.schedule.add(a)
            self.clients.append(a)
            self.grid.place_agent(a, (x, y))



        
