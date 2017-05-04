import os
import ConfigParser
import logging
from LimaTestSuite import create_test_folder, debug


class LimaTestConfiguration(object):

    ACQ_KEYS = {'acqExpoTime': float,
                'acqNbFrames': int,
                'acqMode': str,
                'accMaxExpoTime': float,
                'concatNbFrames': int,
                'triggerMode': str,
                'latencyTime': float
                }

    SAVING_KEYS = {'directory': str,
                   'prefix': str,
                   'suffix': str,
                   'nextNumber': int,
                   'fileFormat': str,
                   'savingMode': str,
                   'overwritePolicy': str,
                   'framesPerFile': int,
                   'nbframes': int
                   }

    def __init__(self, name, type, repeat, det_type, host, port, acq, saving):
        self.name = name
        self.type = type
        self.repeat = repeat
        self.det_type = det_type
        self.host = host
        self.port = port
        self.acq_params = {}
        self.saving_params = {}
        # self.adxv_host = adxv_host
        # self.adxv_port = adxv_port

        # # Default configurations
        # acq_keys = self.ACQ_KEYS.keys()
        # self._acq_defaults = dict.fromkeys(acq_keys)
        # saving_keys = self.SAVING_KEYS.keys()
        # self._saving_defaults = dict.fromkeys(saving_keys)

        # # Update detector configuration defaults
        # self._acq_defaults.update(acq)
        # self._saving_defaults.update(saving)

        # Update detector configuration defaults
        self.acq_params.update(acq)
        self.saving_params.update(saving)

    def get_copy(self, name, type, repeat, acq, saving):
        '''Copy default configuration overwriting specific config'''
        acq_params = self.acq_params.copy()
        saving_params = self.saving_params.copy()
        acq_params.update(acq)
        saving_params.update(saving)
        return LimaTestConfiguration(name, type, repeat, self.det_type, self.host,
                                     self.port, acq_params, saving_params)

    # @property
    # def acq_defaults(self):
    #     return self._acq_defaults.copy()
    #
    # @property
    # def saving_defaults(self):
    #     return self._saving_defaults.copy()

    # def get_detector_name(self):
    #     return self.det_type
    #
    # def get_test_name(self):
    #     return self.name

    # def __repr__(self):
    #     msg = "{0}\n".format(50*"#")
    #     msg += "Test name: {0} | ".format(self.name)
    #     msg += "Test type: {0}\n".format(self.type)
    #     msg += "Detector type: {0}\n".format(self.det_type)
    #     msg += "{0}\n".format(50 * "-")
    #     msg += "Acquisition parameters:\n"
    #     for k, v in self._acq_defaults.iteritems():
    #         msg += "  {0} = {1}\n".format(k, v)
    #     msg += "{0}\n".format(50 * "-")
    #     msg += "Saving parameters:\n"
    #     for k, v in self._saving_defaults.iteritems():
    #         msg += "  {0} = {1}\n".format(k, v)
    #     msg += "{0}\n".format(50 * "#")
    #     return msg


class LimaTestParser(object):
    """
    Class used to translate the information from the configuration file to
    the unit test cases.

    :param filename: name of the configuration file
    """
    def __init__(self, filename):
        self.logger = logging.getLogger('LimaTestSuite')
        self.config = ConfigParser.RawConfigParser()
        self.config.optionxform = str  # preserve Capitals
        self.filename = filename
        if not os.path.isfile(filename):
            msg = "Configuration file %s does not exists." % filename
            raise IOError(msg)
        self.config.read(filename)

        self.default_sections = {'Detector': 'Detector',
                                 'Acq': 'AcqDefaults',
                                 'Saving': 'SavingDefaults'
                                 }

        self.default_test = None
        self.tests = []

        self.load_default_test()
        self.load_tests()

    @debug
    def load_default_test(self):
        """
        Load info about detector and default test configuration.
        """
        self.logger.debug("Loading default configuration")
        det_type = self.config.get(self.default_sections['Detector'], 'type')
        det_type += 'Detector'
        host = eval(self.config.get(self.default_sections['Detector'], 'host'))
        port = eval(self.config.get(self.default_sections['Detector'], 'port'))

        # adxv_host = self.config.get(self.default_sections['ADXV'], 'host')
        # adxv_port = self.config.get(self.default_sections['ADXV'], 'port')

        acq = {}
        saving = {}
        acq_section = self.default_sections['Acq']
        saving_section = self.default_sections['Saving']

        try:
            for param, t in LimaTestConfiguration.ACQ_KEYS.iteritems():
                value = t(self.config.get(acq_section, param))
                acq.update({param: value})

            for param, t in LimaTestConfiguration.SAVING_KEYS.iteritems():
                if param.lower() == 'directory':
                    continue
                value = t(self.config.get(saving_section, param))
                saving.update({param: value})

        except Exception as e:
            msg = 'Parameter not supplied in default configuration'
            self.logger.warning('%s\n%s' % (e, msg))
            return None

        # Check no None value is present in default detector configuration:
        if any(v == None for v in acq.values()) or \
           any(v == None for v in saving.values()):
            self.logger.warning("The default values set is not complete")
            return None

        self.default_test = LimaTestConfiguration('', None, 1, det_type, host,
                                                  port, acq, saving)
        if self.default_test is not None:
            self.logger.debug("Default configuration loaded successfully")
        else:
            self.logger.error("Error loading default configuration")


    def _get_tests_list(self):
        # Get the test names from cfg file ( i.e. section names)
        tests_names = [s for s in self.config.sections()
                       if s not in self.default_sections.values()]
        return tests_names

    def load_tests(self):
        """
        Load each test configuration create a test by updating default test.
        :return: None
        """
        for test in self._get_tests_list():
            t = self.load_test(test)
            self.tests.append(t)

    def load_test(self, name):
        """
        Load a test from configuration file.
        :param config:
        :return:
        """
        acq = {}
        saving = {}
        t_type = None
        t_repeat = 1

        acq_keys = LimaTestConfiguration.ACQ_KEYS.keys()
        saving_keys = LimaTestConfiguration.SAVING_KEYS.keys()

        t_dict = dict(self.config.items(name))
        self.logger.debug('Loading test %s values...' % name)
        for key, value in t_dict.iteritems():
            self.logger.debug('Updating value: %s = %s' % (key, value))
            if key in acq_keys:
                _value = LimaTestConfiguration.ACQ_KEYS[key](value)
                acq.update({key: _value})
            elif key in saving_keys:
                if key.lower() == 'directory':
                    self.logger.debug('directory is assigned automatically')
                else:
                    _value = LimaTestConfiguration.SAVING_KEYS[key](value)
                    saving.update({key: _value})
            elif key == "type":
                t_type = value
            elif key == "repeat":
                t_repeat = int(value)
            else:
                msg = 'Non valid test key <%s> found in test %s' % (key, name)
                raise Exception(msg)

        path = create_test_folder(name)
        saving.update({'directory': path})
        self.logger.debug("Test directory is %s" % path)

        if self.default_test and t_type:
            test = self.default_test.get_copy(name, t_type, t_repeat, acq, saving)
        else:
            msg = 'Non valid test found, please review config file [%s, %s]' % \
                (str(self.default_test), str(t_type))
            raise Exception(msg)

        return test


    def get_tests(self):
        return self.tests



if __name__ == "__main__":
    import argparse
    description = 'Basic unittesting for Lima detector'
    epilog = 'CTBeamlines'

    parser = argparse.ArgumentParser(description=description,
                                 epilog=epilog)

    parser.add_argument("config_file", type=str, help="Test configuration file")

    parser.add_argument("--debug", action="store_true", help="Activate lima debug")
    args = parser.parse_args()
    LimaTestParser(args.config_file)
