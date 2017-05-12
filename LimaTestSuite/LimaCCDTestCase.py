from unittest import TestCase
from LimaTestSuite.LimaCCDDetector import LimaDetector
import logging


class LimaCCDBaseTestCase(TestCase):
    def __init__(self, config, debug=False):
        super(LimaCCDBaseTestCase, self).__init__()
        self.test_config = config
        self.name = config.name
        if debug:
            LimaDetector.set_debug()
        self.logger = logging.getLogger('LimaTestSuite')

    def setUp(self):
        """
        Sets the configuration passed to the detector.

        :return: None
        """
        self.logger.debug('*** Starting test %s ***' % self.name)
        self.logger.debug('Test folder = %s' %
                          self.test_config.saving_params['directory'])
        self.detector = LimaDetector(self.test_config)
        self.detector.update_acq_params(self.test_config.acq_params)
        self.detector.update_saving_params(self.test_config.saving_params)
        self.detector.print_acq_params()
        self.detector.print_saving_params()
        self.detector.prepare_acq()

    def runTest(self):
        raise NotImplementedError('You must implement it.')

    def tearDown(self):
        raise NotImplementedError('You must implement it.')


class LimaCCDAcquisitionTest(LimaCCDBaseTestCase):
    def __init__(self, config, abort=False):
        super(LimaCCDAcquisitionTest, self).__init__(config)
        self.abort = abort

    def runTest(self):
        try:
            self.detector.start(self.abort)
        except RuntimeError as e:
            self.fail("%s FAILED with msg = %s" % (self.name, str(e)))

    def tearDown(self):
        self.logger.debug('*** Teardown for test %s ***' % self.name)
        del self.detector
