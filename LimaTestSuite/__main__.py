import unittest
import os
from LimaConfigHelper import LimaTestParser
from LimaCCDTestCase import LimaCCDAquisitionTest
from LimaTestSuite import logger, _str_date_now



def run_test(filename):

    # Load configuration file and return tests list
    tests = LimaTestParser(filename).get_tests()
    logger = logging.getLogger('LimaTestSuite')

    # Create test suite
    test_suite = unittest.TestSuite()
    for test in tests:
        if test.type.lower() == "acquisition":
            case = LimaCCDAquisitionTest(test)
            test_suite.addTest(case)
            logger.info("Adding acquisition test --> %s" % test.name)
        elif test.type.lower() == "abort":
            case = LimaCCDAquisitionTest(test, True)
            test_suite.addTest(case)
            logger.info("Adding abort test --> %s" % test.name)
        else:
            logger.error("Type %s in not a valid test type." % test.type)
    logger.info('Starting %s test(s)' % len(tests))
    result = unittest.TextTestRunner(verbosity=1).run(test_suite)
    errors = len(result.errors)
    failures = len(result.failures)

    logger.info('Results: Error(s) = %d, Failure(s) = %d' % ( errors, failures))
    for fail in result.failures:
        logger.info(fail[-1].split("\n")[-2])

if __name__ == "__main__":
    import argparse
    import logging
    description = 'Basic unittesting for Lima detector'
    epilog = 'ctbeamlines@cells.es'

    parser = argparse.ArgumentParser(description=description,
                                 epilog=epilog)

    parser.add_argument("config_file", type=str, help="Test configuration file")

    parser.add_argument("--log-level", type=str, help="Activate debug")
    parser.add_argument("--path", "-p", type=str, help="Output log folder",
                        default="")

    args = parser.parse_args()

    if args.log_level == 'debug':
        logger.setLevel(logging.DEBUG)
    path = args.path
    filename = "lima_ts_{0}.log".format(_str_date_now())
    filename = os.path.join(path, filename)
    logging.basicConfig(filename=filename)
    run_test(args.config_file)
