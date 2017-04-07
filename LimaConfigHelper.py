import os
import ConfigParser
import logging


class LimaDetectorConfiguration(object):

    def __init__(self, name , type, host=None, port=None):
        self.name = name
        self.type = type
        self.host = host
        self.port = port


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

    def __init__(self, t_name, t_type, d_name, acq, saving):
        self.name = t_name
        self.detector = d_name
        self.type = t_type
        self.acq_params = {}
        self.saving_params = {}

        # Default configurations
        acq_keys = self.ACQ_KEYS.keys()
        self._acq_defaults = dict.fromkeys(acq_keys)
        saving_keys = self.SAVING_KEYS.keys()
        self._saving_defaults = dict.fromkeys(saving_keys)

        # Update detector configuration defaults
        self._acq_defaults.update(acq)
        self._saving_defaults.update(saving)

    def get_acq_params(self):
        return self._acq_defaults.copy()

    def get_saving_params(self):
        return self._saving_defaults.copy()

    def get_detector_name(self):
        return self.detector

    def get_test_name(self):
        return self.name

    def __repr__(self):
        msg = "{0}\n".format(50*"#")
        msg += "Test name: {0} | ".format(self.name)
        msg += "Test type: {0}\n".format(self.type)
        msg += "Detector name: {0}\n".format(self.detector)
        msg += "{0}\n".format(50 * "-")
        msg += "Acquisition parameters:\n"
        for k, v in self._acq_defaults.iteritems():
            msg += "  {0} = {1}\n".format(k, v)
        msg += "{0}\n".format(50 * "-")
        msg += "Saving parameters:\n"
        for k, v in self._saving_defaults.iteritems():
            msg += "  {0} = {1}\n".format(k, v)
        msg += "{0}\n".format(50 * "#")
        return msg


class LimaTestParser(object):
    """
    Class used to translate the information from the configuration file to
    the unit test cases.

    :param filename: name of the configuration file
    """
    def __init__(self, filename):
        self.logger = logging.getLogger('LimTestSuite')
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

    def load_default_test(self):
        """
        Load info about detector and default test configuration.
        """
        det_name = self.config.get(self.default_sections['Detector'], 'name')

        acq = {}
        saving = {}
        acq_section = self.default_sections['Acq']
        saving_section = self.default_sections['Saving']

        try:
            for param, t in LimaTestConfiguration.ACQ_KEYS.iteritems():
                value = t(self.config.get(acq_section, param))
                acq.update({param: value})

            for param, t in LimaTestConfiguration.SAVING_KEYS.iteritems():
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
        else:
            self.logger.debug("Default configuration loaded successfully")

        self.default_test = LimaTestConfiguration('default', 'd_type', det_name, acq, saving)

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

    def load_test(self, t_name):
        """
        Load a test from configuration file.
        :param config:
        :return:
        """
        acq = {}
        saving = {}
        t_type = None

        acq_keys = LimaTestConfiguration.ACQ_KEYS.keys()
        saving_keys = LimaTestConfiguration.SAVING_KEYS.keys()

        t_dict = dict(self.config.items(t_name))
        for key, value in t_dict.iteritems():
            if key in acq_keys:
                _value = LimaTestConfiguration.ACQ_KEYS[key](value)
                acq.update({key: _value})
            elif key in saving_keys:
                _value = LimaTestConfiguration.SAVING_KEYS[key](value)
                saving.update({key: _value})
            elif key == "type":
                t_type = value
            else:
                msg = 'Non valid test key <%s> found in test %s' % (key, t_name)
                raise Exception(msg)

        if self.default_test and t_type:
            acq_params = self.default_test.get_acq_params()
            saving_params = self.default_test.get_saving_params()
            acq_params.update(acq)
            saving_params.update(saving)
            d_name = self.default_test.get_detector_name()
            test = LimaTestConfiguration(t_name, t_type, d_name, acq_params, saving_params)
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