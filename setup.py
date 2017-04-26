from setuptools import setup, find_packages

setup(
    name="LimaTestSuite",
    version="0.1",
    packages=find_packages(),

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=[],

    package_data={},

    # metadata for upload to PyPI
    author="CTBeamlines",
    author_email="ctbeamlines@cells.es",
    description="framework for testing lima plugin detectors",
    license="GPL3",
    url="http://www.cells.es",
    entry_points={
        'console_scripts': [
            'limatest = LimaTestSuite.__main__:run',
        ]
    }
)
