import unittest
import logging
from LimaConfigHelper import LimaTestParser
from LimaCCDTestCase import LimaCCDAquisitionTest


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
            logger.debug("Adding acquisition test %s" % test.name)
        else:
            logger.error("Type %s in not a valid test type." % test.type)

    result = unittest.TextTestRunner().run(test_suite)
    errors = len(result.errors)
    failures = len(result.failures)

    print '\n' * 2, '=' * 80
    print 'Results '
    print 'Error: ', errors
    print 'Failures: ', failures


if __name__ == "__main__":
    import argparse
    description = 'Basic unittesting for Lima detector'
    epilog = 'CTBeamlines'

    parser = argparse.ArgumentParser(description=description,
                                 epilog=epilog)

    parser.add_argument("config_file", type=str, help="Test configuration file")

    parser.add_argument("--lima-debug", action="store_true", help="Activate lima debug")
    args = parser.parse_args()

    run_test(args.config_file)
