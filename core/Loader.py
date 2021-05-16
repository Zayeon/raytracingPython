import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import *

from PIL import Image

cachedObjects = {}
cachedTextures = {}

vaos = []
vbos = []
textures = []


class OBJModel:

    def __init__(self, filepath):

        self.vertices = []
        self.textureCoords = []
        self.normals = []

        tempVertices = []
        tempNormals = []
        tempTexCoords = []

        verticesI = []
        textureCoordsI = []
        normalsI = []

        with open(filepath, "r") as file:
            for line in file:

                if line.startswith("#"):
                    continue

                fragments = line.split()
                if not fragments:
                    continue

                if fragments[0] == "v":
                    tempVertices.append(fragments[1:4])

                elif fragments[0] == "vn":
                    tempNormals.append(fragments[1:4])

                elif fragments[0] == "vt":
                    tempTexCoords.append(fragments[1:3])

                elif line.startswith("f "):
                    face_i = []
                    text_i = []
                    norm_i = []

                    for v in fragments[1:4]:
                        w = v.split('/')
                        face_i.append(int(w[0]) - 1)
                        text_i.append(int(w[1]) - 1)
                        norm_i.append(int(w[2]) - 1)

                    verticesI.append(face_i)
                    textureCoordsI.append(text_i)
                    normalsI.append(norm_i)

        verticesI = [y for x in verticesI for y in x]
        textureCoordsI = [y for x in textureCoordsI for y in x]
        normalsI = [y for x in normalsI for y in x]

        for i in verticesI:
            self.vertices.extend(tempVertices[i])

        for i in textureCoordsI:
            self.textureCoords.extend(tempTexCoords[i])

        for i in normalsI:
            self.normals.extend(tempNormals[i])

        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.textureCoords = np.array(self.textureCoords, dtype=np.float32)
        self.normals = np.array(self.normals, dtype=np.float32)

    def createRawModel(self):
        return RawModel.loadPTN(self.vertices, self.textureCoords, self.normals)

    @classmethod
    def importFile(cls, filepath):
        if filepath in cachedObjects:
            return cachedObjects[filepath]
        else:
            obj = cls(filepath)
            cachedObjects[filepath] = obj
            return obj


class RawModel:
    ID = 0
    vertexCount = 0

    def __init__(self, vertexCount):
        self.createVAO()
        self.vertexCount = vertexCount

    def createVAO(self):
        self.ID = glGenVertexArrays(1)
        vaos.append(self.ID)
        glBindVertexArray(self.ID)

    def bindIndicesBuffer(self, indices):
        iboID = glGenBuffers(1)
        vbos.append(iboID)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, iboID)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    def storeDataInAttributeList(self, attributeNumber, coordinateSize, data):
        vboID = glGenBuffers(1)
        vbos.append(vboID)
        glBindBuffer(GL_ARRAY_BUFFER, vboID)
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
        glVertexAttribPointer(attributeNumber, coordinateSize, GL_FLOAT, GL_FALSE, data.itemsize * coordinateSize,
                              ctypes.c_void_p(0))

    def unbind(self):
        glBindVertexArray(0)

    @classmethod
    def loadPI(cls, positions, indices):
        obj = cls(len(indices))
        obj.bindIndicesBuffer(indices)
        obj.storeDataInAttributeList(0, 3, positions)
        obj.unbind()

        return obj

    @classmethod
    def loadP(cls, positions):
        obj = cls(len(positions))
        obj.storeDataInAttributeList(0, 3, positions)
        obj.unbind()
        return obj

    @classmethod
    def loadPTI(cls, positions, texCoords, indices):
        obj = cls(len(indices))
        obj.bindIndicesBuffer(indices)
        obj.storeDataInAttributeList(0, 2, positions)
        obj.storeDataInAttributeList(1, 2, texCoords)
        obj.unbind()
        return obj

    @classmethod
    def loadPTN(cls, positions, texCoords, normals):
        obj = cls(len(positions))
        obj.storeDataInAttributeList(0, 3, positions)
        obj.storeDataInAttributeList(1, 2, texCoords)
        obj.storeDataInAttributeList(2, 3, normals)
        obj.unbind()
        return obj

    @classmethod
    def loadPN(cls, positions, normals):
        obj = cls(len(positions))
        obj.storeDataInAttributeList(0, 3, positions)
        obj.storeDataInAttributeList(1, 3, normals)
        obj.unbind()
        return obj

    def getID(self):
        return self.ID

    def getVertexCount(self):
        return self.vertexCount


class TexturedModel:
    def __init__(self, model, texture):
        self.rawModel = model
        self.texture = texture

    def getID(self):
        return self.rawModel.getID()


class Shader:
    uniforms = {}

    def __init__(self, filepath):
        self.createShader(filepath)

    def createShader(self, filepath):
        vertexShaderCode = ""
        fragmentShaderCode = ""
        writingToVertex = True
        with open(filepath, "r") as file:
            for line in file:
                if line.startswith("##VERTEX"):
                    writingToVertex = True
                elif line.startswith("##FRAGMENT"):
                    writingToVertex = False
                else:
                    if writingToVertex:
                        vertexShaderCode += line
                    else:
                        fragmentShaderCode += line

        self.ID = glCreateProgram()
        vs_id = self.addShader(vertexShaderCode, GL_VERTEX_SHADER)
        frag_id = self.addShader(fragmentShaderCode, GL_FRAGMENT_SHADER)

        glAttachShader(self.ID, vs_id)
        glAttachShader(self.ID, frag_id)
        glLinkProgram(self.ID)

        if glGetProgramiv(self.ID, GL_LINK_STATUS) != GL_TRUE:
            info = glGetProgramInfoLog(self.ID)
            glDeleteProgram(self.ID)
            glDeleteShader(vs_id)
            glDeleteShader(frag_id)
            raise RuntimeError('Error linking program: %s' % (info))
        glDeleteShader(vs_id)
        glDeleteShader(frag_id)

    def addShader(self, source, shaderType):
        try:
            shader_id = glCreateShader(shaderType)
            glShaderSource(shader_id, source)
            glCompileShader(shader_id)
            if glGetShaderiv(shader_id, GL_COMPILE_STATUS) != GL_TRUE:
                info = glGetShaderInfoLog(shader_id)
                raise RuntimeError('Shader compilation failed: %s' % (info))
            return shader_id
        except:
            glDeleteShader(shader_id)
            raise

    def getUniformLocation(self, name):
        # if not name in self.uniforms:
        #     location = glGetUniformLocation(self.ID, name)
        #     self.uniforms[name] = location
        # else:
        #     location = self.uniforms[name]
        location = glGetUniformLocation(self.ID, name)
        return location

    def bind(self):
        glUseProgram(self.ID)

    def unbind(self):
        glUseProgram(0)

    def setUniform4f(self, name, v1, v2, v3, v4):
        location = self.getUniformLocation(name)
        glUniform4f(location, v1, v2, v3, v4)

    def setUniform3f(self, name, v1, v2, v3):
        location = self.getUniformLocation(name)
        glUniform3f(location, v1, v2, v3)

    def setUniform2f(self, name, v1, v2):
        location = self.getUniformLocation(name)
        glUniform2f(location, v1, v2)

    def setUniform1f(self, name, v1):
        location = self.getUniformLocation(name)
        glUniform1f(location, v1)

    # def setUniform4fv(self, name, v):
    #    self.bind()
    #    location = self.getUniformLocation(name)
    #    glUniform4f(location, v1, v2, v3, v4)
    #    self.unbind()

    def setUniformMat4fv(self, name, mat):
        location = self.getUniformLocation(name)
        glUniformMatrix4fv(location, 1, GL_FALSE, mat)

    def setUniform1i(self, name, value):
        location = self.getUniformLocation(name)
        glUniform1i(location, value)


class TextureAtlas:
    ID = 0
    nTextures = 0

    shineDamper = 1
    reflectivity = 0

    def __init__(self, filepath, nTextures, flipped=True):
        self.nTextures = nTextures

        image = Image.open(filepath)
        if flipped:
            image = image.transpose(Image.FLIP_TOP_BOTTOM)

        imageData = image.convert("RGBA").tobytes()

        self.width = image.width
        self.height = image.height

        self.ID = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.ID)
        # Set the texture wrapping parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        # Set texture filtering parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # TODO: add mip-mapping and anisotropic filtering

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, imageData)

        glBindTexture(GL_TEXTURE_2D, 0)

        textures.append(self.ID)

    def getID(self):
        return self.ID

    @classmethod
    def importFile(cls, filepath, nTextures):
        if filepath in cachedTextures:
            return cachedTextures[filepath]
        else:
            tex = cls(filepath, nTextures)
            cachedTextures[filepath] = tex
            return tex


def cleanUp():
    for vao in vaos:
        glDeleteVertexArrays(1, vao)
    for vbo in vbos:
        glDeleteBuffers(vbo)

    # textures
    # shaders
