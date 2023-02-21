import mesa

from dataclasses import dataclass

@dataclass
class Location:
    x: int
    y: int


class Passenger(mesa.Agent):
    """An agent with starting location and target destination"""

    def __init__(self, unique_id, model, grid_width, grid_height, x, y):
        super().__init__(unique_id, model)
        self.src = Location(x, y)
        self.dest = Location(self.random.randrange(grid_width),self.random.randrange(grid_height))
        self.num_people = 1
        print(self.src, self.dest)


class Car(mesa.Agent):
    """An agent with starting location and target destination"""

    def __init__(self, unique_id, model, x, y, max_passengers=4):
        super().__init__(unique_id, model)
        self.current =  Location(x, y)
        self.destinations = self.get_destinations()
        self.next_dest =  self.destinations[0]
        self.passengers = []
        self.max_passengers = max_passengers
        self.model = model

        # print(self.current, self.next_dest)


    def get_destinations(self):
        destinations = []
        for client in self.model.clients:
            destinations.append(client.src)
            destinations.append(client.dest)

        return destinations
    
    def update_destinations(self, passenger):
        self.destinations.append(passenger.src)
        self.destinations.append(passenger.dest)
        if len(self.destinations)==2:
            self.next_dest = passenger.src


    def move(self):
        if self.current.x < self.next_dest.x:
            self.current = Location(self.current.x+1, self.current.y)
        elif self.current.x > self.next_dest.x:
            self.current = Location(self.current.x-1, self.current.y)
        elif self.current.y < self.next_dest.y:
            self.current = Location(self.current.x, self.current.y+1)
        else:
            self.current = Location(self.current.x, self.current.y-1)

        self.model.grid.move_agent(self, (self.current.x, self.current.y))

        
    def step(self):
        # if at destination point
        if self.current.x == self.next_dest.x and self.current.y == self.next_dest.y:            
            print("Destination Reached", self.current.x, self.current.y, self.destinations)
            if self.destinations:
                self.destinations.pop(0)
            if self.destinations:
                self.next_dest = self.destinations[0]
            else:
                print("Waiting for new client", self.destinations)
        if self.destinations:
            self.move()

        # NEXT TO DO: extend to include new passengers in next timestep
        # If Passengers waiting at current cell, take them onbboard
        # Passengers currently chosen in a queue-based order
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        potential_passengers = [obj for obj in this_cell if isinstance(obj, Passenger)]
        if len(potential_passengers) > 0:
            passenger = potential_passengers[0]
            self.model.grid.remove_agent(passenger)
            # self.passengers.append(passenger)

