import glfw
from OpenGL.GL import *

import Reference


class Window:
    w_width = Reference.WINDOW_WIDTH
    w_height = Reference.WINDOW_HEIGHT

    onCursorMethods = []

    def __init__(self):
        # initialize glfw
        if not glfw.init():
            glfw.terminate()
            exit(0)

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

        # glfw.window_hint(glfw.RESIZABLE, GL_FALSE)
        self.windowID = glfw.create_window(self.w_width, self.w_height, "My OpenGL window", None, None)

        if not self.windowID:
            glfw.terminate()
            exit(0)

        glfw.make_context_current(self.windowID)

        print("Supported GLSL version is: ", glGetString(GL_SHADING_LANGUAGE_VERSION))

        glfw.set_window_size_callback(self.windowID, self.onWindowResize)
        glfw.set_cursor_pos_callback(self.windowID, self.onCursorMove)
        glfw.set_input_mode(self.windowID, glfw.CURSOR, glfw.CURSOR_DISABLED)

        self.lastFrame = glfw.get_time()
        self.deltaTime = 0

    # glfw methods
    def onWindowResize(self, window, width, height):
        self.w_width = width
        self.w_height = height
        glViewport(0, 0, width, height)

    def startFrame(self):
        glfw.poll_events()
        currentTime = glfw.get_time()
        Reference.deltaTime = currentTime - self.lastFrame
        self.lastFrame = currentTime

    def updateDisplay(self):
        glfw.swap_buffers(self.windowID)

    def shouldClose(self):
        return glfw.window_should_close(self.windowID)

    def onCursorMove(self, window, xpos, ypos):
        for method in self.onCursorMethods:
            method(xpos, ypos)

    def getCursorPos(self):
        return glfw.get_cursor_pos(self.windowID)

    def bindCursorMove(self, method):
        self.onCursorMethods.append(method)

    def getKeyState(self, key):
        return glfw.get_key(self.windowID, key)

    def setCursorLock(self, lock):
        glfw.set_input_mode(self.windowID, glfw.CURSOR, glfw.CURSOR_DISABLED if lock else glfw.CURSOR_NORMAL)
