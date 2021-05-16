import numpy as np

import Reference
from core.Loader import TextureAtlas, RawModel


class GUI:
    def __init__(self):
        self.components = []

    def addComponent(self, c):
        self.components.append(c)

    def getComponents(self):
        return [b.getComponent() for b in self.components]


class GUIComponent:
    screenPosition = np.array([0, 0], dtype=np.float32)
    model = None

    def __init__(self, x, y, width, height):
        # defined as percentages from 0.0 - 1.0
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def update(self):
        pass

    # needed for recursion
    def getComponent(self):
        return self

    def genModel(self):
        self.model = [
            self.x, self.y,
            self.x + self.width, self.y,
            self.x + self.width, self.y + self.height,
            self.x, self.y + self.height
        ]
        self.model = np.array(self.model, dtype=np.float32)


class GUIDivision(GUIComponent):
    indices = np.array([0, 1, 3, 1, 2, 3], dtype=np.uint8)

    display = False

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

        self.components = []

    def addComponent(self, c):
        self.components.append(c)

    def setDisplayed(self, display, colour):
        self.display = True
        self.genModel()
        self.colour = colour

    def getComponent(self):
        a = []
        if self.display:
            a.append(self)
        a.extend([b.getComponent() for b in self.components])
        return a


class GUIText(GUIComponent):
    def __init__(self, font, model, width, height, scale, colour):
        super().__init__(0, 0, width, height)

        self.model = model
        self.scale = scale
        self.font = font
        self.colour = colour

    def getWidth(self):
        return self.width * self.scale

    def getHeight(self):
        return self.height * self.scale


# Holds information about a font
class FontType:
    separator = " "

    charTable = {}

    rectIndices = np.array([
        0, 1, 3,
        1, 2, 3
    ], dtype=np.uint8)

    def __init__(self, filepath):
        self.filepath = filepath
        aspectRatio = Reference.WINDOW_WIDTH / Reference.WINDOW_HEIGHT
        self.fontSheetTexture = TextureAtlas(filepath + ".png", 1, flipped=False)

        with open(filepath + ".fnt", "r") as file:
            for line in file:
                fragments = line.split(self.separator)
                if fragments[0] == "char":
                    character = Character(fragments)
                    character.normalise(self.fontSheetTexture.width, self.fontSheetTexture.height, aspectRatio)
                    self.charTable[character.ID] = character

    def constructGuiText(self, text, scale, lineSpacing, colour):
        vertices = []
        textureCoords = []
        indices = np.array([], dtype=np.uint8)  # may be too small
        iboCounter = 0
        lines = text.split("\n")
        for lineNo, line in enumerate(lines):
            cursor = 0
            lineOffset = lineNo * lineSpacing
            for charNo, char in enumerate(line):
                charInfo = self.charTable[ord(char)]
                charVertexData = [
                    cursor + charInfo.normXoffset, -charInfo.normYoffset - lineOffset,
                    cursor + charInfo.normXoffset + charInfo.normWidth2, -charInfo.normYoffset - lineOffset,
                    cursor + charInfo.normXoffset + charInfo.normWidth2,
                    -charInfo.normYoffset - charInfo.normHeight - lineOffset,
                    cursor + charInfo.normXoffset, -charInfo.normYoffset - charInfo.normHeight - lineOffset,
                ]
                vertices.extend(charVertexData)
                charTexCoords = [
                    charInfo.normX, charInfo.normY,
                    charInfo.normX + charInfo.normWidth, charInfo.normY,
                    charInfo.normX + charInfo.normWidth, charInfo.normY + charInfo.normHeight,
                    charInfo.normX, charInfo.normY + charInfo.normHeight,
                ]
                textureCoords.extend(charTexCoords)
                cursor += charInfo.normXadvance
                newIndices = self.rectIndices + 4 * iboCounter
                indices = np.append(indices, newIndices)
                iboCounter += 1

        vertices = np.array(vertices, dtype=np.float32)
        textureCoords = np.array(textureCoords, dtype=np.float32)

        width = vertices[0::2].max()
        height = vertices[1::2].min()

        model = RawModel.loadPTI(vertices, textureCoords, indices)

        return GUIText(self, model, width, height, scale, colour)


class Character:
    ID = 0
    x = 0
    y = 0
    width = 0
    height = 0
    xoffset = 0
    yoffset = 0
    xadvance = 0

    def __init__(self, lineFragments):
        for fragment in lineFragments:
            if fragment.startswith("id"):
                self.ID = int(fragment.split("=")[1])
            elif fragment.startswith("xoffset"):
                self.xoffset = int(fragment.split("=")[1])
            elif fragment.startswith("yoffset"):
                self.yoffset = int(fragment.split("=")[1])
            elif fragment.startswith("xadvance"):
                self.xadvance = int(fragment.split("=")[1])
            elif fragment.startswith("width"):
                self.width = int(fragment.split("=")[1])
            elif fragment.startswith("height"):
                self.height = int(fragment.split("=")[1])
            elif fragment.startswith("x"):
                self.x = int(fragment.split("=")[1])
            elif fragment.startswith("y"):
                self.y = int(fragment.split("=")[1])

    def normalise(self, imgWidth, imgHeight, aspectRatio):
        self.normX = self.x / imgWidth
        self.normY = self.y / imgHeight
        self.normWidth = self.width / imgWidth
        self.normHeight = self.height / imgHeight  # for tex coords
        self.normWidth2 = (self.width / imgWidth) / aspectRatio
        self.normXoffset = (self.xoffset / imgWidth) / aspectRatio
        self.normYoffset = self.yoffset / imgWidth
        self.normXadvance = (self.xadvance / imgWidth) / aspectRatio
