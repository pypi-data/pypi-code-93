
import pygame
import time
import sys


class MusicTest:

    def __init__ ( self, musicFile : str ):

        self.musicFile = musicFile
        self.hasMusic  = False
        self.volume    = 80

        # pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load( self.musicFile )
        pygame.mixer.music.set_volume( float(self.volume / 100.0) )
        pygame.mixer.music.play( loops=2 )
        print( f'Volume: {self.getVolume()}')

    def getVolume ( self ):
        self.volume = pygame.mixer.music.get_volume() * 100
        return self.volume

    @staticmethod
    def unloadMusic ( ):
        try:
            if pygame.mixer.music:
                pygame.mixer.music.unload()
            if pygame.mixer and pygame.mixer.get_init():
                pygame.mixer.quit()
        except Exception as e:
            print( f'Got exception when attempting to unload music: {e}')


if __name__ == '__main__':

    music = MusicTest(sys.argv[1])
    time.sleep(4)
    while pygame.mixer.get_busy() or pygame.mixer.music.get_busy():
        print( f'Volume: {music.getVolume()}')
        time.sleep(1)
    music.unloadMusic()
