import time
import logging
from LimaTestSuite.LimaCCDDetector import SpecificDetector
from Lima import Pilatus


class PilatusDetector(SpecificDetector):
    def __init__(self, host, port):
        super(PilatusDetector, self).__init__()

        try:
            if not port:
                self.cam = Pilatus.Camera()
            else:
                self.cam = Pilatus.Camera(port)
            self.hwint = Pilatus.Interface(self.cam)
            self.logger.debug("CAM %s HWI %s" % (self.cam, self.hwint))
        except Exception, e:
            logging.error('Error initializing detector object: \n%s', e)

