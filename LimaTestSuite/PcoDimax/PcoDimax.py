import logging
from LimaTestSuite.LimaDetector import SpecificDetector
from Lima import Pco


class PcoDimaxDetector(SpecificDetector):
    def __init__(self, host, port):
        super(PcoDimaxDetector, self).__init__()
        self.logger = logging.getLogger('LimaTestSuite')
        try:
            if not port:
                self.cam = Pco.Camera()
            else:
                self.cam = Pco.Camera(port)
            self.hwint = Pco.Interface(self.cam)
            self.logger.debug("CAM %s HWI %s" % (self.cam, self.hwint))
        except Exception as e:
            self.logger.error('Error initializing detector object: \n%s', e)
