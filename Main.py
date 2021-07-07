import glfw
import pyrr
from OpenGL.GL import *

from core import Audio, GUI, DisplayManager, RenderEngine
from core.Camera import Camera
from entities import Entities
from raytracing.RayTracer import RayTracer

window = DisplayManager.Window()

cam = Camera(window)

masterRenderer = RenderEngine.MasterRenderer()

entities = []
ellipsoid = Entities.Ellipsoid()
entities.append(ellipsoid)

tree = Entities.Tree()
entities.append(tree)
tree.position = pyrr.Vector3([0, 0, -10])

# LIGHTING
lights = []
light1 = RenderEngine.Light(pyrr.Vector3([0, 5, -5]), [1, 1, 1], [0.2, 0.2, 0.2])
lights.append(light1)

# GUI
font = GUI.FontType("res/font/arial")
myGUI = GUI.GUI()
div1 = GUI.GUIDivision(0, 0, 1, 1)
div1.display = True
text = font.constructGuiText("Hello World!", 1, 0.15, [1, 0, 0])
div1.addComponent(text)
# div2 = GUI.GUIDivision(0, 0, 1, 1)
# text2 = GUI.GUIText(0, 0, 0, 0, 1, (1, 1, 1))
# div2.addComponent(text1)
myGUI.addComponent(div1)

# AUDIO
audioContext = Audio.createContext()
Audio.setListenerData(0, 0, 0)
buffer = Audio.loadSound("res/sounds/bounce.wav")
source = Audio.Source()

# RAY TRACING
rayTracer = RayTracer(1024, 1024)

# LOOP
glClearColor(1.0, 0.0, 0.0, 1.0)
while not window.shouldClose():
    window.startFrame()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    cam.handleKeyboardInput()

    # masterRenderer.renderScene(cam, entities, [], lights)
    # masterRenderer.renderGUI(myGUI)

    rayTracer.render()

    if window.getKeyState(glfw.KEY_M) == glfw.PRESS:
        if not source.isPlaying():
            source.play(buffer)

    if window.getKeyState(glfw.KEY_P) == glfw.PRESS:
        print(cam.position)

    if window.getKeyState(glfw.KEY_ESCAPE) == glfw.PRESS:
        window.setCursorLock(False)

    window.updateDisplay()

# renderEngine.cleanUp() TODO: reminder to fix this
source.delete()
Audio.cleanUp(audioContext)
glfw.terminate()
exit(0)
