LimaTestsSuite package
======================
Common framework for Lima detectors to create and execute test based on
the unittest library.

Description
-----------
The LimaTestSuite is a framework with a common API to define generic and specific test for any Lima detector. It provides:

* A configuration helper class to provide detector and test parameters from a file.
* Generic `acquisition` and `abort` tests.
* API to define generic and specific tests.

Supported LimaCCD detectors
---------------------------
Until now, these are the supported detectors:

* Simulator
* Pilatus

Usage
-----
After installing the package, an entry point `limatest` is generated.
Run this application by passing the test file as argument.
```bash
limatest <test_file>
```
Each configuration file defines a single TestSuite for a single detector and each TestSuite can be composed by one or multiple TestCases.

Some examples of configuration files can be found in `examples` folder.

Extra usage information and option can be found by execution `limatest --help`.

Configuration file
------------------

The configuration file is based in the `ConfigParser` module. The file is structured in various sections. There are three mandatory section expected in any configuration file: Detector, AcqDefaults and SavingDefaults.

* In *Detector* section the type (and port and host if necessary) of the detector are specified.
* The default test values for the acquisition and saving parameters are specified in *AcqDefaults* and *SavingDefaults*, respectively.
* Any other section in the file will be interpreted as a test.
* A test section will contain a mandatory field named `type` which specifies the type of test o define.
* An optional field named `repeat` is used to indicate the number of times the test will be executed sequentially (the default value is 1).
* Other fields specified correspond to the acquisition and saving Lima parameters and will overwrite the default configuration.