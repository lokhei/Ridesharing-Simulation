import mesa

from dataclasses import dataclass
from enum import Enum

@dataclass
class Location:
    x: int
    y: int

@dataclass
class PassengerLoc:
    src: Location
    dest: Location

class StepType(Enum):
    QUEUE = 1
    CLOSEST = 2
    WAITING = 3


class DestVis(mesa.Agent):
    def __init__(self, unique_id, model, passenger_id):
        super().__init__(unique_id, model)
        self.type = "dest_vis"
        self.passenger_id = passenger_id



class Passenger(mesa.Agent):
    """An agent with starting location and target destination"""

    def __init__(self, unique_id, model, grid_width, grid_height, x, y, step, seed, secondary_id, num_people = 1):
        super().__init__(unique_id, model)
        self.type = "Passenger"
        self.src = Location(x, y)
        self.dest = Location(seed.randrange(grid_width),seed.randrange(grid_height))
        while self.src == self.dest:
            self.dest = Location(seed.randrange(grid_width),seed.randrange(grid_height))
        self.num_people = num_people
        print(f"Agent {unique_id}: {self.src} to {self.dest}")
        self.waiting_time =  self.random.randint(10,40)

        self.remove = False

        # for metrics
        self.request_time = step
        self.pickup_time = -1
        self.dropoff_time = -1
        self.latest_arrival_time = self.request_time + self.waiting_time
        self.secondary_id = secondary_id


    def step(self):
        # passenger leaves if past waiting time
        if self.waiting_time and self.pos and self.model.schedule.steps > self.request_time + self.waiting_time:
            self.model.schedule.remove(self)
            self.model.grid.remove_agent(self)
            print(f"Waited too long - passenger {self.unique_id} has left")

        # remove next cycle
        if self.remove:
            self.model.schedule.remove(self)

        # remove from schedule once dropped off
        if self.dropoff_time != -1:
            self.remove = True
            


class Driver(mesa.Agent):
    """An agent with starting location and target destination"""

    def __init__(self, unique_id, model, x, y, multi_pass, max_passengers=4, step_type = StepType.QUEUE):
        self.model = model
        super().__init__(unique_id, model)
        self.type = "Driver"
        self.step_type = step_type
        self.current =  Location(x, y)

        self.current_routes = [] # list of target destinations based on passengers in car and target passenger and corrseponding passenger
        self.set_next_dest()
        self.passengers = [] # passengers actually in car
        self.max_passengers = max_passengers
        self.dest_vis = []
        self.is_src = True
        self.multi_pass = multi_pass # ridehailing or ridesharing? 

        # metrics
        self.steps_taken = -1
        self.idle_time = 0

        
    def step(self):
        if not self.current_routes and self.model.clients:
            self.set_next_dest()
        if self.current_routes:
            self.step_algo()
        else:
            #metrics
            self.idle_time += 1

    def check_arrival_lte_waiting(self, passenger, dest):
        # check if able to reach passenger in time, otherwise ignore
        passenger_arrival_constr = passenger.waiting_time + passenger.request_time
        arrival_time = self.calc_manhattan(self.current, dest) + self.model.schedule.steps
        return arrival_time <= passenger_arrival_constr


    def calc_manhattan(self, src, dest):
        return abs(src.x - dest.x) + abs(src.y - dest.y)
        

    def find_closest(self, from_loc, passengers):
        # helper functions for assigning next passenger to car when car has no passengers
        closest = passengers[0]
        min_distance = self.calc_manhattan(passengers[0].src, from_loc)
        for p_dests in passengers:
            curr_dist = self.calc_manhattan(p_dests.src, from_loc)
            if min_distance > curr_dist:
                min_distance = curr_dist
                closest = p_dests
        return closest
    
    def find_closest_waiting(self, passengers):
        # helper functions for assigning next passenger to car when car has no passengers
        most_urgent = passengers[0]
        min_waiting = passengers[0].waiting_time + passengers[0].request_time
        for passenger in passengers:
            curr_wait = passenger.waiting_time + passenger.request_time
            if min_waiting > curr_wait:
                min_waiting = curr_wait
                most_urgent = passenger
        return most_urgent
    

    def set_next_dest(self):
        # find new passengers when car has no passengers
        if self.model.clients:
            if self.step_type == StepType.WAITING:
                passenger = self.find_closest_waiting(self.model.clients)
            elif self.step_type == StepType.QUEUE:
                passenger = self.model.clients[0]
            else:
                passenger = self.find_closest(self.current, self.model.clients)
            
            self.model.clients.remove(passenger)

            # skip passenger if not able to reach passenger location in time
            if passenger.waiting_time and not self.check_arrival_lte_waiting(passenger, passenger.src):
                self.set_next_dest()
            else:
                self.current_routes.extend([(passenger.src, passenger), (passenger.dest, passenger)])
                self.is_src = True



    def move(self):
        target = self.current_routes[0][0]
        if self.current.x != target.x or self.current.y != target.y:
            self.steps_taken += 1

        if self.current.x < target.x:
            self.current = Location(self.current.x+1, self.current.y)
        elif self.current.x > target.x:
            self.current = Location(self.current.x-1, self.current.y)
        elif self.current.y < target.y:
            self.current = Location(self.current.x, self.current.y+1)
        elif self.current.y > target.y:
            self.current = Location(self.current.x, self.current.y-1)
        else:
            return

        self.model.grid.move_agent(self, (self.current.x, self.current.y))

        # pickup and drop off passengers enroute
        if self.multi_pass and len(self.passengers) < self.max_passengers:
            self.get_passengers()
       

    def is_enroute(self, from_loc, to, between):
        if from_loc.x <= between.x and between.x <= to.x or from_loc.x >= between.x and between.x >= to.x:
            if from_loc.y <= between.y and between.y <= to.y or from_loc.y >= between.y and between.y >= to.y:
                return True
            
        return False

 


    def search_square(self):
        # search between self.current and target and retrieve all passengers in this area
        target = self.current_routes[0][0]

        from_x = min(target.x, self.current.x)
        to_x = target.x if from_x == self.current.x else self.current.x

        from_y = min(target.y, self.current.y)
        to_y = target.y if from_y == self.current.y else self.current.y

        potential_passengers = []
        for i in range(from_x, to_x + 1):
            for j in range(from_y, to_y+1):
                this_cell = self.model.grid.get_cell_list_contents([(i, j)])
                potential_passengers.extend([obj for obj in this_cell if isinstance(obj, Passenger)])

        # filter out passengers that are already in current_routes
        current_route_passengers = [passenger for (_, passenger) in self.current_routes]
        area_passengers  = list(set(potential_passengers) - set(current_route_passengers))
        return area_passengers  
    

    


    def earliest_request(self, passengers):
        # helper functions for finding passenger with earliest request time
        min_passenger = passengers[0]
        min_request = passengers[0].request_time
        for passenger in passengers:
            if min_request > passenger.request_time:
                min_request = passenger.request_time
                min_passenger = passenger
        return min_passenger
                  
        
    def order_passengers(self, passengers):
        # order passengers according to strategy
        ordered_passengers = []
        while passengers:
            if self.step_type == StepType.WAITING:
                p = self.find_closest_waiting(passengers)
            elif self.step_type == StepType.QUEUE:
                p = self.earliest_request(passengers)
            else:
                p = self.find_closest(self.current, passengers)
            ordered_passengers.append(p)
            passengers.remove(p)

        return ordered_passengers
    


    def get_passengers(self):
      
        area_passengers = self.search_square()
        pending_passengers = []

        # routes = self.current_routes
        for passenger in area_passengers:
            distance = 0
            added = False
            # if drop off enroute, no disruption for existing passengers
            # if need to detour, find one such that latest arrival time satisfied, and adds least detour to car

            # check if enroute possible
            if self.is_enroute(passenger.src, self.current_routes[0][0], passenger.dest):
                distance += self.calc_manhattan(passenger.src, passenger.dest)
                if passenger.latest_arrival_time >= distance +  self.model.schedule.steps: 
                    pending_passengers.append(passenger)
                    self.current_routes.insert(0, (passenger.src, passenger))
                    self.current_routes.insert(1, (passenger.dest, passenger))
                # move on to next passenger in list
                continue

            for i in range(len(self.current_routes)-1):
                if self.is_enroute(self.current_routes[i][0], self.current_routes[i+1][0], passenger.dest): 
                        
                    distance += self.calc_manhattan(self.current_routes[i][0], passenger.dest)
                    if passenger.latest_arrival_time >= distance + self.model.schedule.steps: 
                        self.current_routes.insert(0, (passenger.src, passenger))
                        self.current_routes.insert(i+1, (passenger.dest, passenger))
                        pending_passengers.append(passenger)
                        added = True
                        break
                else:
                    distance += self.calc_manhattan(self.current_routes[i][0], self.current_routes[i+1][0])

            if added: 
                continue

            # otherwise check if can add to end of routes
            if passenger.latest_arrival_time >= distance +  self.model.schedule.steps:
                pending_passengers.append(passenger)


            # find solution with minimum detour
            # min_detour = 1000
            # for i in range(len(self.current_routes)-1):
            #     if self.is_enroute(self.current_routes[i][0], routes[i+1][0], passenger.dest): 
                        
            #         distance += self.calc_manhattan(routes[i][0], passenger.dest)
            #         if passenger.latest_arrival_time >= distance + self.model.schedule.steps: 
            #             pending_passengers.append(passenger)
            #             added = True
            #             break
            #     else:
            #         distance += self.calc_manhattan(routes[i][0], routes[i+1][0])




    

    def pickup_passenger(self):
        # TO DO: if multiple passengers, pick up correct passenger
        # get passengers on current cell
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        potential_passengers = [obj for obj in this_cell if isinstance(obj, Passenger)]

        while len(potential_passengers) > 0 and sum(client.num_people for client in potential_passengers) + len(self.passengers) <= self.max_passengers:
            passenger = potential_passengers[0]
            potential_passengers.pop(0)

            if self.current_routes[0][1] != passenger and passenger not in self.model.clients:
                # if another passenger on same cell as targeted passenger and already taken by another car
                continue

            if self.current_routes[0][1] != passenger and passenger in self.model.clients:
                # if another passenger on same cell as targeted passenger not taken yet
                self.model.clients.remove(passenger)


            self.model.grid.remove_agent(passenger)
            self.passengers.append(passenger)

            
            # remove loc from current routes
            if (self.current, passenger) in self.current_routes:
                self.current_routes.remove((self.current, passenger))

            # place destination vis
            self.is_src = False
            dest_v = DestVis(self.model.next_id(), self.model, passenger.unique_id)
            self.dest_vis.append(dest_v)
            self.model.grid.place_agent(dest_v, (passenger.dest.x, passenger.dest.y))
        

            # metrics
            passenger.pickup_time = self.model.schedule.steps

            if not self.multi_pass:
                break

       
            

    def get_dest_index(self):
        # return index of desination in list of passengers which is closest to current position
        if len(self.dest_vis) == 1:
            return 0
        index = 0
        min_distance = self.calc_manhattan(self.passengers[0].dest, self.current)
        for i, passenger in enumerate(self.passengers):
            curr_dist = self.calc_manhattan(passenger.dest, self.current)
            if min_distance > curr_dist:
                min_distance = curr_dist
                index = i
        return index



    def drop_off_passengers(self):
        
        # remove locations from current routes
        for loc, passenger in self.current_routes:
            if loc == self.current and passenger.dest == loc:
                self.current_routes.remove((self.current, passenger))
                break
        

        passenger_id = passenger.unique_id

        # Find the index of the agent with id passenger_id
        pass_index = None
        for i, client in enumerate(self.passengers):
            if client.unique_id == passenger_id:
                pass_index = i
                break

        passenger = self.passengers.pop(pass_index)
        self.model.grid.remove_agent(self.dest_vis[pass_index]) # remove dest from grid
        self.dest_vis.pop(pass_index)
        
        # metrics
        passenger.dropoff_time = self.model.schedule.steps
        if self.passengers:
            # choose next dest which is closest
            self.next_dest_index = self.get_dest_index()

        elif self.model.clients:

            self.set_next_dest()
            self.is_src = True
       


    def step_algo(self):
        # if at destination point
        if self.current.x == self.current_routes[0][0].x and self.current.y == self.current_routes[0][0].y:            
            print("Destination Reached", self.current, self.unique_id)
            if self.is_src:
                self.pickup_passenger()
                
            elif self.current_routes:
                self.drop_off_passengers()
                
            if not self.current_routes:
                print("Waiting for new client")

        if self.current_routes:
            self.move()


       

       


       


