import unittest
import os
import logging
from LimaConfigHelper import LimaTestParser
from LimaTestCase import LimaCCDAcquisitionTest
from LimaTestSuite import _str_date_now

TEST_TYPES = ["acquisition", "abort"]


def run_test(filename, debug, tango):

    # Load configuration file and return tests list
    tests = LimaTestParser(filename).get_tests()
    logger = logging.getLogger('LimaTestSuite')

    # Create test suite
    test_suite = unittest.TestSuite()
    ntests = 0
    for test in tests:
        if test.type.lower() in TEST_TYPES:
            if test.type.lower() == TEST_TYPES[0]:
                case = LimaCCDAcquisitionTest(test, abort=False, debug=debug,
                                              tango_mode=tango)
            elif test.type.lower() == TEST_TYPES[1]:
                case = LimaCCDAcquisitionTest(test, abort=True, debug=debug,
                                              tango_mode=tango)
            logger.info("Adding test --> %s [r%d] [%s]" % (
                    test.name, test.repeat, test.type))
            for i in range(test.repeat):
                test_suite.addTest(case)
                ntests += 1
        else:
            logger.error("Type %s is not a valid test type." % test.type)

    logger.info('Starting %s test(s)' % ntests)
    result = unittest.TextTestRunner(verbosity=1).run(test_suite)
    errors = len(result.errors)
    failures = len(result.failures)

    logger.info('Results: Error(s) = %d, Failure(s) = %d' % ( errors, failures))
    for fail in result.failures:
        logger.info(fail[-1].split("\n")[-2])


def run():
    import argparse
    description = 'Basic unittesting for Lima detector'
    epilog = 'ctbeamlines@cells.es'

    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument("config_file", type=str, help="Test configuration file")
    parser.add_argument("--log-level", type=str, help="Activate debug")
    parser.add_argument("--path", "-p", type=str, help="Output log folder",
                        default="")
    parser.add_argument("--tango", "-t", action="store_true",
                        help="Active the tango testing layer")
    parser.add_argument("--debug-core", "-d", dest='debug_core',
                        action="store_true",
                        help="Active the tango testing layer")

    args = parser.parse_args()
    if args.log_level == 'debug':
        logger = logging.getLogger('LimaTestSuite')
        logger.setLevel(logging.DEBUG)
    path = args.path
    filename = "lima_ts_{0}.log".format(_str_date_now())
    filename = os.path.join(path, filename)
    logging.basicConfig(filename=filename)
    run_test(args.config_file, args.debug_core, args.tango)

if __name__ == "__main__":
    run()
