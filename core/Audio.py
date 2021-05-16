import wave

from openal.al import *
from openal.alc import *

buffers = []


class WaveData:
    nframes = 0
    nchannels = 0
    sample_rate = 0
    sample_width = 0
    size = 0
    data = None
    format = None

    def __init__(self, filepath):
        with wave.open(filepath, "rb") as wfile:
            self.nframes = wfile.getnframes()
            self.nchannels = wfile.getnchannels()
            self.sample_rate = wfile.getframerate()
            self.sample_width = wfile.getsampwidth()
            self.size = self.nframes * self.sample_width
            self.data = wfile.readframes(self.nframes)
            self.format = WaveData.getOpenALFormat(self.nchannels, self.sample_rate)

    @staticmethod
    def getOpenALFormat(channels, sample_rate):
        if channels == 1:
            return AL_FORMAT_MONO8 if sample_rate == 1 else AL_FORMAT_MONO16
        else:
            return AL_FORMAT_STEREO8 if sample_rate == 1 else AL_FORMAT_STEREO16


class Source:
    sourceId = ctypes.c_uint(0)

    def __init__(self):
        alGenSources(1, ctypes.pointer(self.sourceId))

    def delete(self):
        self.stop()
        alDeleteSources(1, self.sourceId)

    def play(self, buffer):
        self.stop()
        buffer = ctypes.c_int(buffer.value)
        alSourcei(self.sourceId, AL_BUFFER, ctypes.c_int(buffer.value))
        self.resume()

    def pause(self):
        alSourcePause(self.sourceId)

    def resume(self):
        alSourcePlay(self.sourceId)

    def stop(self):
        alSourceStop(self.sourceId)

    def setVolume(self, volume):
        alSourcef(self.sourceId, AL_GAIN, volume)

    def setPitch(self, pitch):
        alSourcef(self.sourceId, AL_PITCH, pitch)

    def setPosition(self, x, y, z):
        alSource3f(self.sourceId, AL_POSITION, x, y, z)

    def setVelocity(self, x, y, z):
        alSource3f(self.sourceId, AL_VELOCITY, x, y, z)

    def setLooping(self, loop):
        alSourcei(self.sourceId, AL_LOOPING, AL_TRUE if loop else AL_FALSE)

    def isPlaying(self):
        isplaying = ctypes.c_int(0)
        alGetSourcei(self.sourceId, AL_SOURCE_STATE, ctypes.POINTER(ctypes.c_int)(isplaying))
        return isplaying.value == AL_PLAYING


def createContext():
    device = alcOpenDevice(None)  # gets default output device
    context = alcCreateContext(device, None)
    alcMakeContextCurrent(context)

    return context


def loadSound(file):
    buffer = ctypes.c_uint(0)
    alGenBuffers(1, ctypes.POINTER(ctypes.c_uint)(buffer))
    buffers.append(buffer)
    waveFile = WaveData(file)

    alBufferData(buffer, waveFile.format, waveFile.data, waveFile.size, waveFile.sample_rate)

    return buffer


def setListenerData(x, y, z):
    alListener3f(AL_POSITION, x, y, z)
    alListener3f(AL_VELOCITY, 0, 0, 0)


def cleanUp(context):
    for buffer in buffers:
        alDeleteBuffers(1, buffer)

    alcDestroyContext(context)


if __name__ == "__main__":
    context = createContext()

    setListenerData(0, 0, 0)
    buffer = loadSound("res/sounds/bounce.wav")
    buffer2 = loadSound("res/sounds/pink lamborghini.wav")

    source = Source()
    source2 = Source()

    source.setLooping(True)

    source.play(buffer)

    inp = None
    while inp != "q":
        inp = input()
        if inp == "p":
            if source.isPlaying():
                source.pause()
            else:
                source.resume()

        if inp == "o":
            source2.play(buffer2)

    source.delete()
    source2.delete()
    cleanUp(context)
