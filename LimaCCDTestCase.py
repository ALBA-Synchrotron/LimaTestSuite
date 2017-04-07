from unittest import TestCase
from LimaTestSuite.LimaCCDDetector import LimaDetector
import logging


class LimaCCDBaseTestCase(TestCase):
    def __init__(self, config, host=None, port=None, adxv_host=False, debug=False):
        super(LimaCCDBaseTestCase, self).__init__()
        self.test_config = config
        det_name = self.test_config.get_detector_name()
        self.name = self.test_config.get_test_name()
        if debug:
            LimaDetector.set_debug()
        self.det_name = det_name + 'Detector'
        self.detector = LimaDetector(self.det_name, host, port, adxv_host)

        self.output_info = {'Time': '',
                            'TestName': '',
                            'setUpPassed': '',
                            'tearDownPassed': '', }
        self.logger = logging.getLogger('LimaTestSuite')

    def setUp(self):
        """
        Sets the configuration passed to the detector.

        :return: None
        """
        self.logger.info('*** Starting test %s ***' % self.name)
        self.detector.update_acq_params(self.test_config.get_acq_params())
        self.detector.update_saving_params(self.test_config.get_saving_params())
        self.detector.print_acq_params()
        self.detector.print_saving_params()
        self.detector.prepare_acq()

    def runTest(self):
        raise NotImplementedError('You must implement it.')

    def tearDown(self):
        raise NotImplementedError('You must implement it.')


class LimaCCDAquisitionTest(LimaCCDBaseTestCase):
    def __init__(self, config, host=None, port=None, adxv_host=False, debug=False):
        super(LimaCCDAquisitionTest, self).__init__(config, host, port, adxv_host, debug)

    def runTest(self):
        self.detector.start()

    def tearDown(self):
        self.logger.info('*** Teardown for test %s ***' % self.name)