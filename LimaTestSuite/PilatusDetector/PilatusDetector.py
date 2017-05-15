import logging
from LimaTestSuite.LimaDetector import SpecificDetector
from Lima import Pilatus


class PilatusDetector(SpecificDetector):
    def __init__(self, host, port):
        super(PilatusDetector, self).__init__()
        self.logger = logging.getLogger('LimaTestSuite')
        try:
            if not port:
                self.cam = Pilatus.Camera()
            else:
                self.cam = Pilatus.Camera(port)
            self.hwint = Pilatus.Interface(self.cam)
            self.logger.debug("CAM %s HWI %s" % (self.cam, self.hwint))
        except Exception, e:
            self.logger.error('Error initializing detector object: \n%s', e)
