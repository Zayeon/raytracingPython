# Tutorial from: https://antongerdelan.net/opengl/compute.html

import numpy as np
from OpenGL.GL import *
from core.Loader import Shader, RawModel, TextureAtlas
class RayTracer:
    def __init__(self, texWidth, texHeight):
        self.texWidth = texWidth
        self.texHeight = texHeight

        # Creating a test texture
        # self.testTex = TextureAtlas.importFile("res/textures/example.jpg", 1)

        # Generating a texture the compute shader can output to
        self.texOutput = glGenTextures(1)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texOutput)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, texWidth, texHeight, 0, GL_RGBA, GL_FLOAT, None)

        # To write to a texture we use image storing
        glBindImageTexture(0, self.texOutput, 0, GL_FALSE, 0, GL_WRITE_ONLY, GL_RGBA32F)

        # Getting Max Work Groups
        # workGroupCounts = [None, None, None]
        # workGroupCounts[0] = glGetIntegeri_v(GL_MAX_COMPUTE_WORK_GROUP_COUNT, 0)
        # workGroupCounts[1] = glGetIntegeri_v(GL_MAX_COMPUTE_WORK_GROUP_COUNT, 1)
        # workGroupCounts[2] = glGetIntegeri_v(GL_MAX_COMPUTE_WORK_GROUP_COUNT, 2)

        with open("raytracing\\BasicComputeShader.txt") as file:
            shaderSource = file.read()

        rayShader = glCreateShader(GL_COMPUTE_SHADER)
        glShaderSource(rayShader, shaderSource)
        glCompileShader(rayShader)

        if glGetShaderiv(rayShader, GL_COMPILE_STATUS) != GL_TRUE:
            info = glGetShaderInfoLog(rayShader)
            raise RuntimeError('Shader compilation failed: %s' % info)

        self.rayProgram = glCreateProgram()
        glAttachShader(self.rayProgram, rayShader)
        glLinkProgram(self.rayProgram)

        if glGetProgramiv(self.rayProgram, GL_LINK_STATUS) != GL_TRUE:
            info = glGetProgramInfoLog(self.rayProgram)
            glDeleteProgram(self.rayProgram)
            glDeleteShader(rayShader)
            raise RuntimeError('Error linking program: %s' % info)

        # Creating the quad to draw using texture from compute shader
        self.quadShader = Shader("raytracing\\QuadShader.txt")
        vertices = np.array([
            -1, -1,
            -1, 1,
            1, 1,
            1, -1
        ], dtype=np.float32)
        texCoords = np.array([
            0, 0,
            0, 1,
            1, 1,
            1, 0
        ], dtype=np.float32)
        quadIndices = np.array([
            0, 1, 3,
            1, 2, 3
        ], dtype=np.uint8)

        self.quadModel = RawModel.loadPTI(vertices, texCoords, quadIndices)


    def render(self):
        # Run compute shader
        glUseProgram(self.rayProgram)
        glDispatchCompute(self.texWidth, self.texHeight, 1)

        # Make sure writing to image has finished before read
        glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)

        # Normal Rendering
        self.quadShader.bind()
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texOutput)
        # glBindTexture(GL_TEXTURE_2D, self.testTex.getID())
        glBindVertexArray(self.quadModel.getID())
        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)
        glDrawElements(GL_TRIANGLES, self.quadModel.getVertexCount(), GL_UNSIGNED_BYTE, None)





