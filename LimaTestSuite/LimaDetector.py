import time
import os
import sys
import logging
from Lima import Core
from LimaTestSuite import get_dict

class SpecificDetector(object):
    def __init__(self):
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

    def __init__(self, config,):
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
                            'CBF_MINI_HEADER': Core.CtSaving.CBFMiniHeader,
                            'EDF': Core.CtSaving.EDF,
                            'EDF_CONCAT': Core.CtSaving.EDFConcat,
                            'EDF_GZ': Core.CtSaving.EDFGZ,
                            'EDF_LZ4': Core.CtSaving.EDFLZ4,
                            'HDF5': Core.CtSaving.HDF5,
                            'NXS': Core.CtSaving.NXS,
                            'RAW': Core.CtSaving.RAW,
                            'TIFF': Core.CtSaving.TIFFFormat,
                            'FITZ': Core.CtSaving.FITS
                            }
        self._acqMode = {'SINGLE': Core.Single
                         }

        self._savingMode = {'AUTO_FRAME': Core.CtSaving.AutoFrame,
                            'MANUAL': Core.CtSaving.Manual
                            }

        self._overwritePolicy = {'OVERWRITE': Core.CtSaving.Overwrite
                                 }
        # Configuration test
        self._config = config

        # Configuration dictionaries for the Detector class
        self._AcqConfig = config.acq_params
        self._SavingConfig = config.saving_params

        # Just for statistics
        self.start_time = 0.0
        self.end_time = 0.0

        self.logger = logging.getLogger('LimaTestSuite')

        # Initialize the HW
        self.init_hw()
        self.write_config_hw()


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
            setattr(params, par, value)

    def set_acq_parameters(self, exp_time, frames, latency=0,
                           trigger='Internal', acq_mode='single'):

        d = {'acqExpoTime': exp_time,
             'acqNbFrames': frames,
             'acqMode': acq_mode,
             'triggerMode': trigger,
             'latencyTime': latency
             }
        self._AcqConfig.update(d)
        self.write_config_hw()

    def set_saving_parameters(self, directory, prefix, suffix, img_format,
                              mode='auto_frame', overwrite='overwrite'):
        d = {'directory': directory,
             'prefix': prefix,
             'suffix': suffix,
             'fileFormat ': img_format,
             'savingMode': mode,
             'overwritePolicy': overwrite
             }
        self._SavingConfig.update(d)
        self.write_config_hw()

    def print_config(self):
        for k, v in self._AcqConfig.iteritems():
            self.logger.debug("Acquisition param: %s = %s" % (k, v))

        for k, v in self._AcqConfig.iteritems():
            self.logger.debug("Saving param: %s = %s" % (k, v))

    @property
    def acq_status(self):
        raise NotImplemented('You should implement it')

    @property
    def acq_time(self):
        raise NotImplemented('You should implement it')

    @property
    def frames(self):
        raise NotImplemented('You should implement it')

    @property
    def last_image(self):
        raise NotImplemented('You should implement it')

    @property
    def last_image_saved(self):
        raise NotImplemented('You should implement it')

    @property
    def status(self):
        raise NotImplemented('You should implement it')

    def init_hw(self):
        raise NotImplemented('You should implement it')

    def write_config_hw(self):
        raise NotImplemented('You should implement it')

    def start(self):
        raise NotImplemented('You should implement it')

    def stop(self):
        raise NotImplemented('You should implement it')


class LimaCoreDetector(LimaDetector):

    def init_hw(self,):
        # We try to load a module containing the detector object
        # The class name must be follow the pattern <name>LimaDetector
        # The path relative to this file must be <name>
        # import module according to <name>
        # Basic Lima object to access the detector
        self.cam = None
        self.hwi = None
        self.ct = None
        self.ct_save = None
        self.ct_acq = None

        try:
            det_type = self._config.det_type
            host = self._config.host
            port = self._config.port
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

    def __del__(self):
        self.logger.debug("Deleting")
        del self.ct_save
        del self.ct_acq
        del self.ct
        del self.hwi
        del self.cam
        # Wait for server to disconnect before any other re-connection
        time.sleep(0.1)

    def write_config_hw(self):
        """
        Set the acquisition configuration from dictionary.

        :param config: acquisition configuration dictionary.
        :return: None
        """
        acq_parms = self.ct_acq.getPars()
        self._update_config_from_dict(self._AcqConfig, acq_parms)
        self.ct_acq.setPars(acq_parms)

        saving_params = self.ct_save.getParameters()
        self._update_config_from_dict(self._SavingConfig, saving_params)
        self.ct_save.setParameters(saving_params)

    def prepare_acq(self):
        self.ct.prepareAcq()

    def start(self):
        self.ct.startAcq()

    def stop(self):
        self.ct.stopAcq()

    @LimaDetector.acq_time.getter
    def acq_time(self):
        return self.ct_acq.getAcqExpoTime() + self.ct_acq.getLatencyTime()

    @LimaDetector.frames.getter
    def frames(self):
        return self.ct_acq.getAcqNbFrames() - 1

    @LimaDetector.last_image.getter
    def last_image(self):
        return self.ct.getStatus().ImageCounters.LastImageAcquired

    @LimaDetector.last_image_saved.getter
    def last_image_saved(self):
        return self.ct.getStatus().ImageCounters.LastImageSaved

    @LimaDetector.acq_status.getter
    def acq_status(self):
        return self.ct.getStatus().AcquisitionStatus

    @LimaDetector.status.getter
    def status(self):
        return self.ct.Status()


    @staticmethod
    def set_debug(debug=True):
        if debug:
            Core.DebParams.setTypeFlags(0xff)
            Core.DebParams.setModuleFlags(0xffff)
        else:
            Core.DebParams.setTypeFlags(0x00)
            Core.DebParams.setModuleFlags(0x0000)

