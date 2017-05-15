import time
import logging
from unittest import TestCase
from Lima import Core
from LimaTestSuite.LimaDetector import LimaCoreDetector


class LimaCCDBaseTestCase(TestCase):
    def __init__(self, config, debug=False, tango_mode=False):
        super(LimaCCDBaseTestCase, self).__init__()
        self.tango_mode = tango_mode
        self.test_config = config
        self.name = config.name
        if debug and not tango_mode:
            LimaCoreDetector.set_debug()
        self.logger = logging.getLogger('LimaTestSuite')

    def fail(self, msg=None):
        TestCase.fail(self, "%s FAILED with msg = %s" % (self.name, msg))

    def setUp(self):
        """
        Sets the configuration passed to the detector.

        :return: None
        """
        self.logger.debug('*** Starting test %s ***' % self.name)
        self.logger.debug('Test folder = %s' %
                          self.test_config.saving_params['directory'])
        if self.tango_mode:
            from LimaTestSuite.LimaTangoDetector import LimaTangoDetector
            self.detector = LimaTangoDetector(self.test_config)
        else:
            self.detector = LimaCoreDetector(self.test_config)
        self.detector.print_config()

    def runTest(self):
        raise NotImplementedError('You must implement it.')

    def tearDown(self):
        raise NotImplementedError('You must implement it.')


class LimaCCDAcquisitionTest(LimaCCDBaseTestCase):
    def __init__(self, config, abort=False):
        super(LimaCCDAcquisitionTest, self).__init__(config)
        self.abort = abort

    def runTest(self):
        self.detector.prepare_acq()
        self.detector.start()
        self.logger.debug('Starting acquisition')
        acq_time = self.detector.acq_time
        img_idx = self.detector.frames - 1
        counter = 0
        last_saved = 0
        while True:
            prev_acq = self.detector.last_image
            prev_saved = self.detector.last_image_saved
            acq_status = self.detector.acq_status
            self.logger.debug('Last acq %d saved %d' % (prev_acq,
                                                        prev_saved))
            self.logger.debug('Acq Status %d' % acq_status)
            if prev_saved == img_idx:
                break

            if self.abort:
                self.detector.stop()
                time.sleep(2)
                self.detector.prepare_acq()
                time.sleep(2)
                self.logger.debug("%s" % repr(self.detector.acq_status))
                break

            # Check acq finished with status Ready
            if acq_status == Core.AcqReady and prev_saved != img_idx:
                self.fail('Acquisition finished with state=READY but images '
                          'were not generated properly.')

            time.sleep(acq_time)

            # last_acq = self.ct.getStatus().ImageCounters.LastImageAcquired
            # if not (last_acq - prev_acq) and last_acq != img_idx:
            #     raise RuntimeError("Acquisition time has been exceeded.")

            # TODO review criteria to check if saving has hung
            # if counter > 5:
            if False:
                if last_saved - prev_saved < 1:
                    self.fail('Images cannot be saved.')
                counter = 0
                last_saved = self.detector.last_image_saved
            else:
                counter += 1

            # # TODO define waiting timeout in test config
            for i in range(5):
                if Core.AcqReady == self.detector.acq_status:
                    break
                time.sleep(1)
                self.logger.debug("Waiting")

        if not Core.AcqReady == self.detector.acq_status:
            self.fail('Acquisition did not finished in READY state. [S%d]' %
                      acq_status)


    def tearDown(self):
        self.logger.debug('*** Teardown for test %s ***' % self.name)
        del self.detector
