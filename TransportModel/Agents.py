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
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = "dest_vis"



class Passenger(mesa.Agent):
    """An agent with starting location and target destination"""

    def __init__(self, unique_id, model, grid_width, grid_height, x, y, step, seed, num_people = 1):
        super().__init__(unique_id, model)
        self.type = "Passenger"
        self.src = Location(x, y)
        self.dest = Location(seed.randrange(grid_width),seed.randrange(grid_height))
        while self.src == self.dest:
            self.dest = Location(seed.randrange(grid_width),seed.randrange(grid_height))
        self.num_people = num_people
        print(f"Agent {unique_id}: {self.src} to {self.dest}")
        self.waiting_time =  self.random.randint(10,40) # follow normal distribution instead??

        self.remove = False

        # for metrics
        self.request_time = step
        self.pickup_time = -1
        self.dropoff_time = -1
        self.latest_arrival_time = self.request_time + self.waiting_time




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
            



class Car(mesa.Agent):
    """An agent with starting location and target destination"""

    def __init__(self, unique_id, model, x, y, multi_pass, max_passengers=4, step_type = StepType.QUEUE):
        self.model = model
        super().__init__(unique_id, model)
        self.type = "Car"
        self.step_type = step_type
        self.current =  Location(x, y)
        self.current_passenger = None
        self.is_waiting = False
        self.current_routes = [] # list of target destinations based on passengers in car and target passenger
        self.set_next_dest()
        self.passengers = []
        self.max_passengers = max_passengers
        self.dest_vis = []
        self.is_src = True
        self.multi_pass = multi_pass # ridehailing or ridesharing? 
        self.next_dest_index = 0

        # metrics
        self.steps_taken = -1
        self.idle_time = 0

        

    def check_arrival_lte_waiting(self, passenger, dest):
        # check if able to reach passenger in time, otherwise ignore
        passenger_arrival_constr = passenger.waiting_time + passenger.request_time
        arrival_time = self.calc_manhattan(self.current, dest) + self.model.schedule.steps
        return arrival_time <= passenger_arrival_constr



    def calc_manhattan(self, src, dest):
        return abs(src.x - dest.x) + abs(src.y - dest.y)
        

    def find_closest(self, from_loc):
        # helper functions for assigning next passenger to car when car has no passengers
        closest = self.model.clients[0]
        min_distance = self.calc_manhattan(self.model.clients[0].src, from_loc)
        for p_dests in self.model.clients:
            curr_dist = self.calc_manhattan(p_dests.src, from_loc)
            if min_distance > curr_dist:
                min_distance = curr_dist
                closest = p_dests
        self.model.clients.remove(closest)
        return closest
    
    def find_closest_waiting(self):
        # helper functions for assigning next passenger to car when car has no passengers
        most_urgent = self.model.clients[0]
        min_waiting = self.model.clients[0].waiting_time + self.model.clients[0].request_time
        for passenger in self.model.clients:
            curr_wait = passenger.waiting_time + passenger.request_time
            if min_waiting > curr_wait:
                min_waiting = curr_wait
                most_urgent = passenger
        self.model.clients.remove(most_urgent)
        return most_urgent
    


    def set_next_dest(self):
        # find new passengers when car has no passengers
        if self.model.clients:
            if self.step_type == StepType.WAITING:
                passenger = self.find_closest_waiting()
            elif self.step_type == StepType.QUEUE:
                passenger = self.model.clients[0]
                self.model.clients.pop(0)
            else:
                passenger = self.find_closest(self.current)

            # skip passenger if not able to reach passenger location in time
            if passenger.waiting_time and not self.check_arrival_lte_waiting(passenger, passenger.src):
                self.set_next_dest()
            else:
                self.current_passenger = passenger
                self.current_routes.extend([passenger.src, passenger.dest])
                self.is_waiting = False
                self.is_src = True

        else:
            self.is_waiting = True


    def find_targets(self, detour_lim = 0):
        targets = []
        detour = 0
        prospectives = self.find_prospectives()
        for client in prospectives:
            if self.current.x == client.dest.x:
                targets.append(client)
            elif self.current.y == client.dest.y:
                targets.append(client)
        return targets


        
    def find_prospectives(self):
        # find prospective passengers which are enroute to next dest
        prospectives = []
        for client in self.model.clients:
            # if between current and dest
            if ((client.dest.x <= self.current.x and client.dest.x >= self.next_dest.x) \
                or (client.dest.x <= self.current.x and client.dest.x >= self.next_dest.x)) \
                    and ((client.dest.y <= self.current.y and client.dest.y >= self.next_dest.y) \
                or (client.dest.y <= self.current.y and client.dest.y >= self.next_dest.y)):

                prospectives.append(client)

        for p in prospectives:
            print(p.dest)

        return prospectives
    
                


    def move(self):
        target = self.current_routes[0]
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

        if self.multi_pass and (self.current.x != target.x or self.current.y != target.y):
            self.pickup_passenger(pass_thru=True)
       
        
    def step(self):
        if self.is_waiting and self.model.clients:
            self.set_next_dest()
        if not self.is_waiting:
            self.step_algo()
        else:
            #metrics
            self.idle_time += 1


    
    

    def get_closest_from_list(self, list, from_loc):
        closest = list[0]
        min_distance = self.calc_manhattan(list, from_loc)
        for p_dests in list:
            curr_dist = self.calc_manhattan(p_dests.src, from_loc)
            if min_distance > curr_dist:
                min_distance = curr_dist
                closest = p_dests
        return closest
    


    def is_enroute(self, from_loc, to, between):
        if from_loc.x <= between.x and between.x <= to.x or from_loc.x >= between.x and between.x >= to.x:
            if from_loc.y <= between.y and between.y <= to.y or from_loc.y >= between.y and between.y >= to.y:
                return True
            
        return False


    def get_routes(self, to_add):
        # add passenger to route and calculate total distance
        # see if will exceed any of the passenger max arrival time

        # while passengers not empty, find closest, add 
        entries = []
        dests = []
        from_loc = self.current
        while entries:
            closest = self.get_closest_from_list(entries, from_loc)
            from_loc = closest
            entries.remove(closest)
            dests.append(closest)
        return True



    def order_locations(self, passenger):

        distance = 0
        for i in range(len(self.current_routes)-1):
            if self.is_enroute(self.current_routes[i], self.current_routes[i+1], passenger.dest): # if drop off enroute, arrival time for other passengers don't change
                # check latest arival time satisfied
                if passenger.latest_arrival_time >= distance:
                    self.current_routes.insert(i+1, passenger.dest)
                    return True

            else:
                distance += self.calc_manhattan(self.current_routes[i], self.current_routes[i+1])

        # check if adding passenger to end of list satisfises passenger
        if passenger.latest_arrival_time >= distance +  self.model.schedule.steps:
            self.current_routes.append(passenger.dest)
            return True
 
        
        # TO DO: figure out where to add passenger otherwise detour a little and add passenger

        return False



    def pickup_passenger(self, pass_thru=False):
        # get passengers on current cell
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        potential_passengers = [obj for obj in this_cell if isinstance(obj, Passenger)]

        while len(potential_passengers) > 0 and sum(client.num_people for client in potential_passengers) + len(self.passengers) < self.max_passengers:
            passenger = potential_passengers[0]
            potential_passengers.pop(0)

            if pass_thru and passenger not in self.model.clients: # other cars already dealing with enroute passenger
                continue

            if not pass_thru and self.current_passenger != passenger and passenger not in self.model.clients:
                # if another passenger on same cell as targeted passenger and already taken by another car
                continue

            add_passenger = None
            if self.current_passenger != passenger:
                add_passenger = self.order_locations(passenger)

            if add_passenger is False: # if dest not en-route, don't pick up
                continue


            if not pass_thru and self.current_passenger != passenger and passenger in self.model.clients:
                # if another passenger on same cell as targeted passenger not taken yet
                self.model.clients.remove(passenger)


            self.model.grid.remove_agent(passenger)
            self.passengers.append(passenger)

            if not pass_thru:
                # place destination vis and set next destinations
                if self.current in self.current_routes:
                    self.current_routes.remove(self.current)

                self.is_src = False
                dest_v = DestVis(self.model.next_id(), self)
                self.dest_vis.append(dest_v)
                self.model.grid.place_agent(dest_v, (passenger.dest.x, passenger.dest.y))
            
            else: # pick up passengers along the way
                self.model.clients.remove(passenger)
                dest_v = DestVis(self.model.next_id(), self)
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
        
        passenger = self.passengers.pop(self.next_dest_index) # remove passenger from car
        self.model.grid.remove_agent(self.dest_vis[self.next_dest_index]) # remove dest from grid
        self.dest_vis.pop(self.next_dest_index)

        self.current_routes.remove(self.current)
        
        # metrics
        passenger.dropoff_time = self.model.schedule.steps
        if self.passengers:
            # choose next dest which is closest
            self.next_dest_index = self.get_dest_index()
        elif self.model.clients:

            self.set_next_dest()
            self.is_src = True
        else: # if no passengers on car and no waiting clients
            self.is_waiting = True
       


    def step_algo(self):

        # if at destination point
        if self.current.x == self.current_routes[0].x and self.current.y == self.current_routes[0].y:            
            print("Destination Reached", self.current)
            if self.is_src:
                self.pickup_passenger()
                
            elif not self.is_waiting:
                self.drop_off_passengers()
                
            if self.is_waiting:
                print("Waiting for new client")

        if not self.is_waiting:
            self.move()

   
    

       

       


       


