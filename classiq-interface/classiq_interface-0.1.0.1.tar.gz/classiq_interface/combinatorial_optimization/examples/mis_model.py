import pyomo.environ as pyo
import networkx as nx


def mis_pyomo_model(graph: nx.Graph) -> pyo.ConcreteModel:
    model = pyo.ConcreteModel()
    model.Nodes = pyo.Set(initialize=list(graph.nodes))
    model.Arcs = pyo.Set(initialize=list(graph.edges))

    model.x = pyo.Var(model.Nodes, domain=pyo.Binary)

    @model.Constraint(model.Arcs)
    def independent_rule(model, node1, node2):
        return model.x[node1] + model.x[node2] <= 1

    model.cost = pyo.Objective(
        expr=sum(model.x[node] for node in model.Nodes), sense=pyo.maximize
    )

    return model
