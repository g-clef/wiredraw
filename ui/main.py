from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor

from subprocess import GraphManager


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
        pandaActor = Actor("models/panda-model",)
        pandaActor.setScale(*scale)
        pandaActor.reparentTo(self.render)
        pandaActor.setPos(*position)
        return pandaActor

    def __init__(self):
        super().__init__()
        self.init_environment()
        self.graph = list()
        for count in range(0,3):
            new_panda = self.add_panda((count*10, count*10, count*10))
            self.graph.append(new_panda)


if __name__ == "__main__":
    app = WireDrawUI()
    child
    app.run()
