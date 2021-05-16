import numpy as np
from pyrr import Vector3, matrix44

from core.Loader import OBJModel, TextureAtlas, TexturedModel


class Entity:

    position = Vector3([0, 0, 0])  # xyz
    textured = True

    def getModelMatrix(self):
        return matrix44.create_from_translation(self.position)


class Ellipsoid(Entity):
    radius = [1, 1, 1]  # xyz
    colour = [.1, 0.2, .4, 1]  # rgba
    textured = False

    def __init__(self):
        self.mesh = OBJModel.importFile("res/models/UnitSphere.obj")
        self.model = self.mesh.createRawModel()

    def getModelMatrix(self):
        return matrix44.create_from_translation(self.position) * matrix44.create_from_scale(np.array(self.radius))


class Tree(Entity):

    def __init__(self):
        texture = TextureAtlas.importFile("res/textures/tree.png", 1)
        texture.reflectivity = 0.1
        texture.shineDamper = 0.8
        self.mesh = OBJModel.importFile("res/models/tree.obj")
        self.model = TexturedModel(self.mesh.createRawModel(), texture)

