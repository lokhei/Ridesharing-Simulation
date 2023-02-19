import mesa
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from TransportModel import TransportModel, Car, Passenger

def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Color": "red",
        "Filled": "true",
        "Layer": 0,
        "r": 0.5,
    }
    if type(agent) is Car:
        portrayal["Shape"] = "Images\icons8-people-in-car-side-view-50.png"
        
    elif type(agent) is Passenger:
        portrayal["Shape"] = "Images\icons8-body-type-short-50.png"
    return portrayal


grid = mesa.visualization.CanvasGrid(agent_portrayal,10,10,500,500)


# configure and run the server
server = mesa.visualization.ModularServer(
    TransportModel, [grid], 'Transport Model', {'num_passengers' : 1, 'num_cars': 1, 'width' : 10, 'height' : 10}
)

server.port = 8521 # default
server.launch()

