from datetime import datetime, timezone

from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor

from reader import GraphManager


class WireDrawUI(ShowBase):

    def init_environment(self):
        # Load the environment model.
        self.scene = self.loader.loadModel("models/environment")
        # Reparent the model to render.
        self.scene.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)

    def add_panda(self, position=(0, 0,  0), scale=(0.005, 0.005, 0.005)):
        pandaActor = Actor("models/panda",)
        pandaActor.setScale(*scale)
        pandaActor.reparentTo(self.render)
        pandaActor.setPos(*position)
        return pandaActor

    def update_graph(self, task):
        graph = self.graphmanager.graphs[self.graphmanager.present_time]
        for node in graph.vertices():
            # these are all IPs
            if node not in self.graph:
                # the graph has a node that the UI doesn't. add it.
                position = graph.vp["layout"][node]
                self.add_panda(position)
        for node in self.graph:
            try:
                graph.vertex(node)
            except ValueError:
                # the UI has a node that the graph doesn't. Remove it.
                node.removeNode()
        return task.again

    def __init__(self, graphmanager: GraphManager):
        super().__init__()
        self.init_environment()
        self.graph = list()
        self.graphmanager = graphmanager
        self.taskMgr.doMethodLater(1, self.update_graph, "update_graph")


if __name__ == "__main__":
    now = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
    manager = GraphManager(now)
    manager.start()
    app = WireDrawUI(manager)
    app.run()
