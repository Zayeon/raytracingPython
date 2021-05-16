import itertools

import pyrr
from OpenGL.GL import *

import Reference
from core import GUI
from core.Loader import Shader


class Light:
    position = pyrr.Vector3([0, 0, 0])
    colour = [1, 1, 1]
    attenuation = pyrr.Vector3([1, 0, 0])

    def __init__(self, position, colour, attenuation):
        self.position = position
        self.colour = colour
        self.attenuation = attenuation


class EntityRenderer:
    texturedEntityMap = {}
    colouredEntities = []

    MAX_LIGHTS = 4

    def __init__(self):
        self.entityShader = Shader("res/shaders/EntityShader.txt")
        self.texturedEntityShader = Shader("res/shaders/TexturedEntityShader.txt")

    def processEntity(self, entity):
        if not entity.textured:
            self.colouredEntities.append(entity)
        else:
            if entity.model in self.texturedEntityMap:
                self.texturedEntityMap[entity.model].append(entity)
            else:
                self.texturedEntityMap[entity.model] = [entity]

    def loadLights(self, lights):
        for i in range(self.MAX_LIGHTS):
            if i < len(lights):
                light = lights[i]
                self.entityShader.bind()
                self.entityShader.setUniform3f(f"lightPosition[{i}]", *light.position)
                self.entityShader.setUniform3f(f"lightColour[{i}]", *light.colour)

                self.texturedEntityShader.bind()
                self.texturedEntityShader.setUniform3f(f"lightPosition[{i}]", *light.position)
                self.texturedEntityShader.setUniform3f(f"lightColour[{i}]", *light.colour)
                self.texturedEntityShader.unbind()
            else:
                self.entityShader.bind()
                self.entityShader.setUniform3f(f"lightPosition[{i}]", 0, 0, 0)
                self.entityShader.setUniform3f(f"lightColour[{i}]", 0, 0, 0)

                self.texturedEntityShader.bind()
                self.texturedEntityShader.setUniform3f(f"lightPosition[{i}]", 0, 0, 0)
                self.texturedEntityShader.setUniform3f(f"lightColour[{i}]", 0, 0, 0)
                self.texturedEntityShader.unbind()

    def setup(self):

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def renderEntity(self, entity):
        self.entityShader.setUniformMat4fv("modelMatrix", entity.getModelMatrix())
        self.entityShader.setUniform4f("colour", *entity.colour)
        glBindVertexArray(entity.model.getID())
        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)
        glEnableVertexAttribArray(2)
        glDrawArrays(GL_TRIANGLES, 0, entity.model.getVertexCount())

    def setupTexturedModel(self, model):
        glBindTexture(GL_TEXTURE_2D, model.texture.getID())
        glBindVertexArray(model.rawModel.getID())
        self.texturedEntityShader.setUniform1f("shineDamper", model.texture.shineDamper)
        self.texturedEntityShader.setUniform1f("reflectivity", model.texture.reflectivity)
        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)
        glEnableVertexAttribArray(2)

    def reset(self):
        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
        glDisableVertexAttribArray(2)
        glBindVertexArray(0)

    def finish(self):
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)

        self.texturedEntityMap = {}
        self.colouredEntities = []

    def render(self, projectionMatrix, camera):
        self.setup()

        self.entityShader.bind()

        # could have a separate method to optimise
        self.entityShader.setUniformMat4fv("projMatrix", projectionMatrix)
        self.entityShader.setUniformMat4fv("viewMatrix", camera.getViewMatrix())
        self.entityShader.setUniform1f("shineDamper", 1)
        self.entityShader.setUniform1f("reflectivity", 0)

        for entity in self.colouredEntities:
            self.renderEntity(entity)

        self.reset()

        self.entityShader.unbind()

        self.texturedEntityShader.bind()
        # could have a separate method that could be called once to optimise
        self.texturedEntityShader.setUniformMat4fv("projMatrix", projectionMatrix)
        self.texturedEntityShader.setUniformMat4fv("viewMatrix", camera.getViewMatrix())

        glActiveTexture(GL_TEXTURE0)
        self.texturedEntityShader.setUniform1i("textureSampler", 0)

        for model in self.texturedEntityMap:
            self.setupTexturedModel(model)
            for entity in self.texturedEntityMap[model]:
                self.texturedEntityShader.setUniformMat4fv("modelMatrix", entity.getModelMatrix())

                glDrawArrays(GL_TRIANGLES, 0, model.rawModel.getVertexCount())

            self.reset()

        self.finish()


class GUIRenderer:

    def __init__(self):
        self.GUIShader = Shader("res/shaders/GUIShader.txt")
        self.fontShader = Shader("res/shaders/FontShader.txt")
        self.fontShader.bind()
        self.fontShader.setUniform2f("translation", 0.0, 0.0)
        self.fontShader.unbind()

    def render(self, gui):
        components = gui.getComponents()
        components = list(itertools.chain(*components))
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_DEPTH_TEST)

        for component in components:
            if isinstance(component, GUI.GUIText):
                self.fontShader.bind()
                self.fontShader.setUniform3f("colour", *component.colour)
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, component.font.fontSheetTexture.getID())
                glBindVertexArray(component.model.getID())
                glEnableVertexAttribArray(0)
                glEnableVertexAttribArray(1)
                glDrawElements(GL_TRIANGLES, component.model.getVertexCount(), GL_UNSIGNED_BYTE, None)

        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
        glBindVertexArray(0)

        glDisable(GL_BLEND)

class MasterRenderer:
    projectionMatrix = pyrr.matrix44.create_perspective_projection_matrix(
        Reference.CAMERA_FOV, Reference.WINDOW_WIDTH / Reference.WINDOW_HEIGHT, 0.1, 1000.0)

    def __init__(self):
        self.entityRenderer = EntityRenderer()
        self.guiRenderer = GUIRenderer()

    def renderScene(self, camera, entities, islands, lights):
        for entity in entities:
            self.entityRenderer.processEntity(entity)

        self.entityRenderer.loadLights(lights)

        self.entityRenderer.render(self.projectionMatrix, camera)

    def renderGUI(self, gui):
        self.guiRenderer.render(gui)
