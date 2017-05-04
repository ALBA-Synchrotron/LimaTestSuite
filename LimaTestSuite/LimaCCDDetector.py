import time
import os
import sys
from Lima import Core
from LimaTestSuite import get_dict, ADXVSocket
import logging

WAIT_TIMEOUT = 10

class SpecificDetector(object):
    def __init__(self):

        # self._AcqDefaults = {'acqExpoTime': 1,
        #                       'acqNbFrames': 10,
        #                       'acqMode': 'Single',
        #                       'triggerMode': 'Internal',
        #                       'lattencyTime': 0
        #                       }
        #
        # self._SavingDefaults = {'directory': './',
        #                          'prefix': 'img_',
        #                          'suffix': '.cbf',
        #                          'fileFormat': 'CBF',
        #                          'savingMode': 'AUTO_FRAME',
        #                          'overwritePolicy': 'OVERWRITE'
        #                          }

        self._AcqDefaults = {}
        self._SavingDefaults = {}

        # Basic Specific detector objects
        self.cam = None
        self.hwint = None

    def get_camera(self):
        """
        Mandatory method for Detector class
        :return: camera object
        """
        return self.cam

    def get_hwinterface(self):
        """
        Mandatory method for Detector class
        :return: hardware interface object
        """
        return self.hwint

    def get_acq_defaults(self):
        return self._AcqDefaults

    def get_saving_defaults(self):
        return self._SavingDefaults


class LimaDetector(object):

    def __init__(self, config):
        # The config is a LimaTestConfiguration object
        #
        # A dictionary is defined for each Lima Core constants that has
        # a discrete set of possible values. The naming convention is:
        # _<ConstantName>
        self._triggerMode = {'INTERNAL': Core.IntTrig,
                             'INTERNAL_MULTI_TRIGGER': Core.IntTrigMult,
                             'EXTERNAL_TRIGGER': Core.ExtTrigSingle,
                             'EXTERNAL_MULTI_TRIGGER': Core.ExtTrigMult,
                             'EXTERNAL_GATE': Core.ExtGate
                             }

        self._fileFormat = {'CBF': Core.CtSaving.CBFFormat,
                            'EDF': Core.CtSaving.EDF
                            }
        self._acqMode = {'SINGLE': Core.Single
                         }

        self._savingMode = {'AUTO_FRAME': Core.CtSaving.AutoFrame,
                            'MANUAL': Core.CtSaving.Manual
                            }

        self._overwritePolicy = {'OVERWRITE': Core.CtSaving.Overwrite
                                 }

        # Configuration dictionaries for the Detector class
        self._AcqConfig = {}
        self._SavingConfig = {}

        # Basic Lima object to access the detector
        self.cam = None
        self.hwi = None
        self.ct = None
        self.ct_save = None
        self.ct_acq = None

        # Just for statistics
        self.start_time = 0.0
        self.end_time = 0.0

        self.logger = logging.getLogger('LimaTestSuite')

        # OPTIONAL: External visualization software
        # self.adxv_host = adxv_host
        # if self.adxv_host:
        #     self.adxv_socket = ADXVSocket(self.adxv_host)
        #     self.logger.debug("ADXV socket communication is ON")
        # # Init the detector specific plugin
        det_type = config.det_type
        host = config.host
        port = config.port

        self.init(det_type, host, port)

        self._AcqConfig = config.acq_params
        self._SavingConfig = config.saving_params
        #self.set_default_parameters()

    def init(self, det_type, host, port):
        # We try to load a module containing the detector object
        # The class name must be follow the pattern <name>LimaDetector
        # The path relative to this file must be <name>
        # import module according to <name>
        try:
            # Export module to python path:
            p = os.path.dirname(__file__)
            mpath = os.path.abspath(os.path.join(p, det_type))
            sys.path.insert(0, mpath)
            msg = "Importing module: %s" % mpath
            self.logger.debug(msg)
            # Get class from module
            module = __import__(det_type)
            class_name = '{0}'.format(det_type)
            # Create an instance of the detector class
            det = getattr(module, class_name)(host, port)
        except Exception as e:
            msg = "ERROR: Cannot find plugin %s, %s " % (det_type, str(e))
            raise ImportError(msg)
        try:
            # Specific API from LimaDetector class
            self.cam = det.get_camera()
            self.hwi = det.get_hwinterface()
            # Common API from Lima
            # TODO Needs protection in case of problem constructing the detector
            self.ct = Core.CtControl(self.hwi)
            self.ct_acq = self.ct.acquisition()
            self.ct_save = self.ct.saving()
        except Exception as e:
            msg = "Cannot create Lima Control objects for detector, %s" % str(e)
            raise ValueError(msg)
        # Get detector default configurations provided by the specified Detector
        # class and apply it by default. If no defaults applied, the correct
        # acquisition cannot be guaranteed.
        #self._AcqConfig = det.get_acq_defaults()
        #self._SavingConfig = det.get_saving_defaults()
        #self.set_default_parameters()
        self.logger.debug("Exit init")

    def __del__(self):
        self.logger.debug("Deletting")
        del self.ct_save
        del self.ct_acq
        del self.ct
        del self.hwi
        del self.cam
        # Wait for server desconnection befor any other re-connection
        time.sleep(0.1)

    def _update_config_from_dict(self, config, params):
        """
        Update the parameters configuration with values from a configuration
        dictionary.

        :param config: configuration dictionary
        :param params: parameter structure to be filled
        :return: None
        """
        for key, value in config.iteritems():
            par = key
            msg = "Setting parameter %s = %s" % (par, value)
            self.logger.debug(msg)
            value_dict = get_dict(self, key)
            if value_dict:
                value = value_dict[value.upper()]
            # No dynamic casting required
            # _type = type(value)
            setattr(params, par, value)

    def update_acq_params(self, config):
        """
        Set the acquisition configuration from dictionary.

        :param config: acquisition configuration dictionary.
        :return: None
        """
        p = self.ct_acq.getPars()
        self._update_config_from_dict(config, p)
        self.ct_acq.setPars(p)

    def update_saving_params(self, config):
        """
        Set the saving configuration from dictionary.

        :param config: saving configuration dictionary.
        :return: None
        """
        p = self.ct_save.getParameters()
        self._update_config_from_dict(config, p)
        self.ct_save.setParameters(p)

    # def set_default_parameters(self):
    #     self.update_saving_params(self._SavingConfig)
    #     self.update_acq_params(self._AcqConfig)

    def prepare_acq(self):
        self.ct.prepareAcq()

    def set_acq_parameters(self, exp_time, frames, latency=0, trigger='Internal',
                           acq_mode='single'):

        d = {'acqExpoTime': exp_time,
             'acqNbFrames': frames,
             'acqMode': acq_mode,
             'triggerMode': trigger,
             'latencyTime': latency
             }
        self.update_acq_params(d)

    def set_saving_parameters(self, directory, prefix, suffix, format,
                              mode='auto_frame', overwrite='overwrite'):

        d = {'directory': directory,
             'prefix': prefix,
             'suffix': suffix,
             'fileFormat ': format,
             'savingMode': mode,
             'overwritePolicy': overwrite
             }
        self.update_saving_params(d)

    def print_acq_params(self):
        for k,v in self._AcqConfig.iteritems():
            self.logger.debug("Aquisition param: %s = %s" % (k, v))

    def print_saving_params(self):
        for k,v in self._AcqConfig.iteritems():
            self.logger.debug("Saving param: %s = %s" % (k, v))

    def start(self, abort=False):
        try:
            self.ct.startAcq()
#            self.start_time = time.time()
        except Exception, e:
            raise RuntimeError('Error starting acquisition:\n%s', e)

        # if not Core.AcqRunning == self.ct.getStatus().AcquisitionStatus:
        #     raise RuntimeError("Acquisition cannot not start.")


        self.logger.debug('Starting acquisition')
        # last_img_sent = -1
        # last_img = self.ct.getStatus().ImageCounters.LastImageSaved
        period = self.ct_acq.getAcqExpoTime() + self.ct_acq.getLatencyTime()
        img_idx = self.ct_acq.getAcqNbFrames() - 1

        counter = 0
        last_saved = 0

        while True:
            prev_acq = self.ct.getStatus().ImageCounters.LastImageAcquired
            prev_saved = self.ct.getStatus().ImageCounters.LastImageSaved
            acq_status = self.ct.getStatus().AcquisitionStatus
            self.logger.debug("Last acq %d saved %d" % (prev_acq, prev_saved))
            self.logger.debug("Acq Status %d" % acq_status)

            if prev_saved == img_idx:
                break

            if abort:
                self.stop()
                time.sleep(3)
                self.logger.debug("%s" % repr(self.ct.getStatus()))
                break

            # Check acq finished with status Ready
            if Core.AcqReady == acq_status and prev_saved != img_idx:
                raise RuntimeError(
                    "Acquisition finished with state=READY but images were not"
                    " generated properly.")

            time.sleep(period)
            last_acq = self.ct.getStatus().ImageCounters.LastImageAcquired
            # if not (last_acq - prev_acq) and last_acq != img_idx:
            #     raise RuntimeError("Acquisition time has been exceeded.")

            # TODO review criteria to check if saving has hung
            #if counter > 5:
            if False:
                if last_saved - prev_saved < 1:
                    raise RuntimeError("Images cannot be saved.")
                counter = 0
                last_saved = self.ct.getStatus().ImageCounters.LastImageSaved
            else:
                counter += 1


            # if self.adxv_host and last_img_sent < last_img:
            #     last_img_sent = last_img
            #     fn = self.get_last_filename()
            #     self.adxv_socket.send_image_name(fn)
            #     self.logger.debug('sending image %s' % fn)
            # else:
            #     self.logger.debug("%s" % repr(self.ct.getStatus()))
            
        # TODO define waiting timeout in test config
        for i in range(WAIT_TIMEOUT):
            if Core.AcqReady == self.ct.getStatus().AcquisitionStatus:
                break
            time.sleep(1)
            self.logger.debug("Waiting")

        acq_status = self.ct.getStatus().AcquisitionStatus
        if not Core.AcqReady == acq_status:
            raise RuntimeError("Acquisition did not finished in READY state." +
                               " [S%d]" % acq_status)

    def stop(self):
        try:
            self.ct.stopAcq()
        except Exception, e:
            raise RuntimeError('Error stopping acquisition:\n%s', e)

    def status(self):
        try:
            return self.ct.Status()
        except Exception, e:
            raise RuntimeError('Error requesting detector status:\n%s', e)


    @staticmethod
    def set_debug(debug=True):
        if debug:
            Core.DebParams.setTypeFlags(0xff)
            Core.DebParams.setModuleFlags(0xffff)
        else:
            Core.DebParams.setTypeFlags(0x00)
            Core.DebParams.setModuleFlags(0x0000)

    # def get_last_filename(self):
    #     saving_parameters = self.ct_save().getParameters()
    #     last_image_saved = self.ct.getStatus().ImageCounters.LastImageSaved
    #     directory = saving_parameters.directory
    #     prefix = saving_parameters.prefix
    #     suffix = saving_parameters.suffix
    #     number = str(last_image_saved).zfill(4)
    #     filename = prefix + number + suffix
    #     return os.path.join(directory, filename)
