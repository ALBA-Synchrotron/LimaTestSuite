import time
import PyTango
from Lima import Core
from LimaTestSuite.LimaDetector import LimaDetector


class LimaTangoDetector(LimaDetector):
    _tango_tmode = {'INTERNAL': 'INTERNAL_TRIGGER',
                    'INTERNAL_MULTI_TRIGGER': 'INTERNAL_TRIGGER_MULTI',
                    'EXTERNAL_TRIGGER': 'EXTERNAL_TRIGGER',
                    'EXTERNAL_MULTI_TRIGGER': 'EXTERNAL_TRIGGER_MULTI',
                    'EXTERNAL_GATE': 'EXTERNAL_GATE',
                    }

    def init_hw(self):
        self.device = PyTango.DeviceProxy(self._config.device_name)


    def __del__(self):
        self.logger.debug("Deleting")
        # Wait for server to disconnect before any other re-connection
        time.sleep(0.1)

    def write_config_hw(self):
        """
        Set the acquisition configuration from dictionary.

        :param config: acquisition configuration dictionary.
        :return: None
        """
        # Acquisition parameters
        exp_time = self._AcqConfig['acqExpoTime']
        frames = self._AcqConfig['acqNbFrames']
        acq_mode = self._AcqConfig['acqMode']
        trigger_mode = self._tango_tmode[self._AcqConfig['triggerMode'].upper()]
        latency_time = self._AcqConfig['latencyTime']
        acc_expo_time = self._AcqConfig['accMaxExpoTime']
        concat_frames = self._AcqConfig['concatNbFrames']

        
        self.device.write_attribute('acq_nb_frames', frames)
        self.device.write_attribute('acq_expo_time', exp_time)
        self.device.write_attribute('latency_time', latency_time)
        self.device.write_attribute('acq_trigger_mode', trigger_mode)
        self.device.write_attribute('acq_mode', acq_mode)
        self.device.write_attribute('acc_max_expo_time', acc_expo_time)
        self.device.write_attribute('concat_nb_frames', concat_frames)

        # Saving parameters
        directory = self._SavingConfig['directory']
        prefix = self._SavingConfig['prefix']
        suffix = self._SavingConfig['suffix']
        next_nb = self._SavingConfig['nextNumber']
        file_format = self._SavingConfig['fileFormat']
        saving_mode = self._SavingConfig['savingMode']
        overwrite = self._SavingConfig['overwritePolicy']
        frames_file = self._SavingConfig['framesPerFile']

        # TODO ask to the mailing list how to set this value
        nb_frames = self._SavingConfig['nbframes']

        self.device.write_attribute('saving_directory', directory)
        self.device.write_attribute('saving_prefix', prefix)
        self.device.write_attribute('saving_suffix', suffix)
        self.device.write_attribute('saving_format', file_format)
        self.device.write_attribute('saving_frame_per_file', frames_file)
        self.device.write_attribute('saving_mode', saving_mode)
        self.device.write_attribute('saving_overwrite_policy', overwrite)
        self.device.write_attribute('saving_next_number', next_nb)

    def prepare_acq(self):
        self.device.prepareAcq()

    def start(self):
        self.device.startAcq()

    def stop(self):
        self.device.stopAcq()

    @LimaDetector.acq_time.getter
    def acq_time(self):
        exp_time = self.device.read_attribute('acq_expo_time').value
        latency = self.device.read_attribute('latency_time').value

        return exp_time+latency

    @LimaDetector.frames.getter
    def frames(self):
        return self.device.read_attribute('acq_nb_frames').value

    @LimaDetector.last_image.getter
    def last_image(self):
        return self.device.read_attribute('last_image_acquired').value

    @LimaDetector.last_image_saved.getter
    def last_image_saved(self):
        return self.device.read_attribute('last_image_saved').value

    @LimaDetector.acq_status.getter
    def acq_status(self):
        tango_status = self.device.read_attribute('acq_status').value
        status = Core.AcqReady
        if tango_status == 'Ready':
            status = Core.AcqReady
        elif tango_status == 'Running':
            status = Core.AcqRunning
        elif tango_status == 'Fault':
            status = Core.AcqFault
        return status

    @LimaDetector.status.getter
    def status(self):
        return self.device.read_attribute('acq_status_fault_error').value

