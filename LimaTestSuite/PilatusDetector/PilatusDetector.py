import time
import logging
from LimaTestSuite.LimaDetector import Detector
from Lima import Pilatus


class PilatusDetector(Detector):
    def __init__(self, host, port):
        super(PilatusDetector, self).__init__()

        self._AcqDefaults = {'acqExpoTime': 1,
                             'acqNbFrames': 10,
                             'acqMode': 'Single',
                             'accMaxExpoTime': 1,
                             'concatNbFrames': 0,
                             'triggerMode': 'Internal',
                             'latencyTime': 0,
                             # 'AUTO_EXPO_MODE': 0 # NOT ACCESSIBLE in Simulator (at least)!
                             }

        self._SavingDefaults = {'directory': './',
                                'prefix': 'img_',
                                'suffix': '.cbf',
                                'nextNumber': 0,
                                'fileFormat': 'CBF',
                                'savingMode': 'AUTO_FRAME',
                                'overwritePolicy': 'OVERWRITE',
                                'framesPerFile': 1,
                                'nbframes': 0
                                }

        try:
            if not port:
                self.cam = Pilatus.Camera()
            else:
                self.cam = Pilatus.Camera(port)
            time.sleep(2)
            self.hwint = Pilatus.Interface(self.cam)
        except Exception, e:
            logging.error('Error initializing detector object: \n%s', e)
