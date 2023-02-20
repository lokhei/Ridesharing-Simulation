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
        self.current = self.src
        self.dest = Location(self.random.randrange(grid_width),self.random.randrange(grid_height))
        print(self.src, self.dest)


class Car(mesa.Agent):
    """An agent with starting location and target destination"""

    def __init__(self, unique_id, model, grid_width, grid_height, x, y, max_passengers=4):
        super().__init__(unique_id, model)
        self.src = Location(x, y)
        self.current = self.src
        self.next_dest = model.passengers[0].current
        print(self.src, self.next_dest)
        self.passengers = []
        self.max_passengers = max_passengers
        self.model = model

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
        
        if self.current.x == self.next_dest.x and self.current.y == self.next_dest.y:            
            print("Destination Reached")
            self.next_dest = self.passengers[0].dest
        else:
            self.move()

        # If Passengers waiting at current cell, take them onbboard
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        potential_passengers = [obj for obj in this_cell if isinstance(obj, Passenger)]
        if len(potential_passengers) > 0 and len(self.passengers) < self.max_passengers:
            # TO DO: choose passenger according to some order
            # passenger = self.random.choice(potential_passengers) 
            passenger = potential_passengers[0]
            # potential_passengers.remove(passenger)
            self.model.grid.remove_agent(passenger)
            self.passengers.append(passenger)

