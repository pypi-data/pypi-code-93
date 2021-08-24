from concurrent.futures import ThreadPoolExecutor
from convisoappsec.common.docker import SCSCommon
from transitions import Machine
from transitions.extensions.states import Timeout
from transitions.extensions.states import add_state_features
import time
import random


@add_state_features(Timeout)
class ScannerMachine(Machine):
    pass

class Unit:

    def __init__(self, token, scanner, logger, timeout):
        self.logger = logger
        self.token = token
        self.scanner = scanner if isinstance(scanner, SCSCommon) else self._instanciate_scanner(scanner)

        self.name = self.scanner.name
        self.states = [
            'waiting',
            {'name': 'pulling', 'timeout': timeout, 'on_timeout': self._on_timeout},
            {'name': 'running', 'timeout': timeout, 'on_timeout': self._on_timeout},
            {'name': 'sending', 'timeout': timeout, 'on_timeout': self._on_timeout},
            'done'
        ]
        self.machine = ScannerMachine(model=self, states=self.states, initial='waiting')
        self.machine.add_ordered_transitions()
        self._set_callbacks()
        self.to_waiting()

    def _set_callbacks(self):
        self.machine.on_enter_waiting('_on_waiting')
        self.machine.on_enter_pulling('_on_pulling')
        self.machine.on_enter_running('_on_running')
        self.machine.on_enter_sending('_on_sending')
        self.machine.on_enter_done('_on_done')

    def _instanciate_scanner(self, data):
        return SCSCommon(**data,
                    token=self.token,
                    logger=self.logger,
                )

    def _on_timeout(self):
        self.logger.debug('Scanner {} timeout on state {}'.format(
            self.name, self.state
        ))

    def _on_waiting(self):
        self.logger.debug('Scanner {} entered on {} state'.format(
            self.name, self.state
        ))
    
    def _on_pulling(self):
        self.logger.debug('Scanner {} entered on {} state'.format(
            self.name, self.state
        ))
        self.logger.info('   Pulling {} image'.format(self.name))
        image = self.scanner.pull()
        if image:
            self.logger.debug('Image: {}'.format(image))
            self.next_state()
        else:
            raise RuntimeError("Image not found.")

    def _on_running(self):
        self.logger.info('   Scanner {} is running.'.format(
            self.scanner.repository_name, self.state
        ))
        self.scanner.run()
        self.end_time = time.time()
        self.logger.debug('Total execution time for {} was {:2f}'.format(
            self.scanner.repository_name,
            self.end_time - self.start_time
        ))
        status_code = self.scanner.wait()
        self.logger.info('   Scanner {}@{} returned status code {}'.format(
            self.scanner.repository_name,
            self.name,
            status_code
        ))
        self.next_state()
    
    def _on_sending(self):
        self.logger.debug('Scanner {} entered on {} state'.format(
            self.name, self.state
        ))
        self.results = self.scanner.collect_artifacts()
        self.next_state()
    
    def _on_done(self):
        self.logger.debug('Scanner {} entered on {} state'.format(
            self.scanner.repository_name, self.state
        ))
        self.scanner.container.remove(v=True, force=True)

    def start(self):
        self.start_time = time.time()
        self.to_pulling()
    


class Box:
    


    def __init__(self, token, scanner_data, logger, timeout, max_workers=5):
        self.token = token
        self.logger = logger
        self.max_workers=max_workers
        self.scanners = [
            Unit(
                token=token,
                scanner=scanner,
                logger=logger,
                timeout=timeout
            )
        for scanner in scanner_data.values()]

    def run(self):
        self.logger.debug("Starting Execution")
        with ThreadPoolExecutor(max_workers=self.max_workers) as exeggutor:
            for scanner in self.scanners:
                exeggutor.submit(scanner.start)
