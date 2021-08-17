
import pygame
import logging
import datetime

_LOGGER = logging.getLogger(__name__)
VERSION = pygame.version.vernum


class Music:

    def __init__ ( self, musicFile : str, targetVolume : int ):

        self.musicFile     = musicFile
        self.hasMusic      = False
        self.targetVolume  = targetVolume
        self.fadeInSecs    = 0
        self.startTime     = datetime.datetime.now()
        self.currentVolume = -1

        # pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
        pygame.init()

    def loadMusic ( self ):
        # give myself a large buffer, as well (last value), otherwise playback stutters
        # pygame.mixer.init(44100, -16, True, 4096)
        pygame.mixer.init()
        pygame.mixer.music.load( self.musicFile )
        self.hasMusic = True

    @staticmethod
    def getVolume (  ) -> int:
        return int(pygame.mixer.music.get_volume() * 100)

    def setVolume ( self, volume=None ):
        if volume:
            if volume < 0:
                volume = 0
            if volume > 99:
                volume = 99
            self.targetVolume = volume
        pygame.mixer.music.set_volume( float(self.targetVolume / 100.0) )
        self.currentVolume = self.targetVolume

    def setFadeVolume ( self ):
        now = datetime.datetime.now()
        delta = (now - self.startTime).total_seconds()
        if delta >= self.fadeInSecs:
            volume = self.targetVolume
        else:
            volume = int(self.targetVolume * delta / self.fadeInSecs)
        if volume != self.currentVolume:
            pygame.mixer.music.set_volume( float(volume / 100.0) )
            self.currentVolume = volume

    def unloadMusic ( self ):
        try:
            self.hasMusic = False
            if pygame.mixer.music and VERSION[0] >= 2:
                pygame.mixer.music.unload()
            if pygame.mixer and pygame.mixer.get_init():
                pygame.mixer.quit()
        except Exception as e:
            _LOGGER.info( f'Got exception when attempting to unload music: {e}', exc_info=True)

    def playMusic ( self, nbrRepetitions : int = 0, fadeSeconds : int = 0 ):
        if not self.hasMusic:
            self.loadMusic()
        self.startTime     = datetime.datetime.now()
        self.fadeInSecs    = fadeSeconds
        self.currentVolume = -1
        pygame.mixer.music.play( loops=nbrRepetitions-1 )
        self.setFadeVolume()

    def stopMusic ( self ):
        try:
            self.currentVolume = -1
            if pygame.mixer.get_busy() and pygame.mixer.music and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            pygame.mixer.stop()
        except Exception as e:
            _LOGGER.info( f'Got exception when attempting to stop music: {e}', exc_info=True)
        self.unloadMusic()
