from math import sin, cos, radians

import glfw
import numpy as np
import pyrr

import Reference


class Camera:
    cameraSpeed = 5

    pitch = 0
    yaw = -90

    sensitivity = 0.05

    def __init__(self, window):
        self.position = pyrr.Vector3([0, 0, 0.1], dtype=np.float32)
        self.target = pyrr.Vector3([0, 0, 0], dtype=np.float32)
        self.cameraUp = pyrr.Vector3([0, 1, 0], dtype=np.float32)
        self.cameraFront = pyrr.Vector3([0, 0, -1], dtype=np.float32)
        # the Gram-Schmidt process
        self.direction = pyrr.vector3.normalize(self.position - self.target)
        self.cameraRight = pyrr.vector3.normalize(
            pyrr.vector3.cross(pyrr.Vector3([0, 1, 0], dtype=np.float32), self.direction))
        self.cameraUp = pyrr.vector3.normalize(pyrr.vector3.cross(self.direction, self.cameraRight))
        self.window = window
        window.bindCursorMove(self.updateRotationWithCursor)
        cpos = window.getCursorPos()
        self.lastX = cpos[0]
        self.lastY = cpos[1]

    def handleKeyboardInput(self):
        speed = self.cameraSpeed * Reference.deltaTime

        if self.window.getKeyState(glfw.KEY_W) == glfw.PRESS:
            self.position += speed * self.cameraFront

        if self.window.getKeyState(glfw.KEY_S) == glfw.PRESS:
            self.position -= speed * self.cameraFront

        if self.window.getKeyState(glfw.KEY_A) == glfw.PRESS:
            self.position -= speed * pyrr.vector3.normalize(
                pyrr.vector3.cross(self.cameraFront, self.cameraUp))

        if self.window.getKeyState(glfw.KEY_D) == glfw.PRESS:
            self.position += speed * pyrr.vector3.normalize(
                pyrr.vector3.cross(self.cameraFront, self.cameraUp))

        if self.window.getKeyState(glfw.KEY_SPACE) == glfw.PRESS:
            self.position[1] += speed

        if self.window.getKeyState(glfw.KEY_LEFT_CONTROL) == glfw.PRESS:
            self.position[1] -= speed

    def getViewMatrix(self):
        return pyrr.matrix44.create_look_at(self.position, self.position + self.cameraFront, self.cameraUp)

    def updateRotationWithCursor(self, xpos, ypos):
        deltaX = xpos - self.lastX
        deltaY = self.lastY - ypos
        self.lastX = xpos
        self.lastY = ypos

        deltaX *= self.sensitivity
        deltaY *= self.sensitivity

        self.yaw += deltaX
        self.pitch += deltaY

        if self.pitch > 89:
            self.pitch = 89
        elif self.pitch < -89:
            self.pitch = -89

        front = pyrr.Vector3([
            cos(radians(self.pitch)) * cos(radians(self.yaw)),
            sin(radians(self.pitch)),
            cos(radians(self.pitch)) * sin(radians(self.yaw))
        ])

        self.cameraFront = pyrr.vector3.normalize(front)
        self.cameraRight = pyrr.vector3.normalize(
            pyrr.vector3.cross(pyrr.Vector3([0, 1, 0], dtype=np.float32), self.direction))
        self.cameraUp = pyrr.vector3.normalize(pyrr.vector3.cross(self.direction, self.cameraRight))
