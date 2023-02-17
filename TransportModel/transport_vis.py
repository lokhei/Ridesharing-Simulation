import mesa
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from TransportModel import TransportModel

def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Color": "red",
        "Filled": "true",
        "Layer": 0,
        "r": 0.5,
    }
    return portrayal


grid = mesa.visualization.CanvasGrid(agent_portrayal,10,10,500,500)


# configure and run the server
server = mesa.visualization.ModularServer(
    TransportModel, [grid], 'Transport Model', {'num_agents' : 2, 'width' : 10, 'height' : 10}
)

server.port = 8521 # default
server.launch()

