import socket
import re
import datetime
import logging


# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


def _get_dict_key(d, value):
    try:
        ind = d.values().index(value)
    except ValueError:
        return None
    return d.keys()[ind]


def _get_dict_value(d, k):
    try:
        value = d[k.upper()]
    except KeyError:
        return None
    return value


def _str_date_now():
    now = datetime.datetime.now()
    nowstr = now.strftime("%Y%m%d_%H%M")
    return nowstr


# def dict2param(name):
#     """
#     Convert dictionary name to parameter name according to the convention:
#         dictionary: _TheNameToConvert
#         parameter: theNameToConvert
#
#     :param name: dictionary name
#     :return: lima parameter name
#     """
#     _name = re.sub(r'(?:_)([a-z])', lambda x: x.group(1).upper(), name.lower())
#     #par = '{0}'.format(_name)
#     par = '{0}'.format(name)
#     print '%s translated to %s' % (name, par)
#     return par


def get_dict(obj, name):
    """
    Search a dictionary attribute in obj.

    :param obj: Object where to search the dictionary
    :param name: dictionary name
    :return: the dictionary if found, None otherwise
    """
    _name = re.sub(r'(?:^|_)([a-z])', lambda x: x.group(1).upper(), name.lower())

    #dictionary = '_{0}'.format(_name.upper())
    dictionary = '_{0}'.format(name)
    #print "Searching constants dictionary %s:" % (dictionary)
    try:
        d = getattr(obj, dictionary)
        #print "Dictionary %s found" % dictionary
    except AttributeError:
        #print "WARNING: dictionary %s not found" % dictionary
        d = None
    return d


class ADXVSocket(object):
    def __init__(self, host, port=8100):
        """
        Class used to send the image name via socket connection for the ADXV
        application.

        :param host: hostname where the ADXV instance is running.
        :param port: communication port for the ADXV instance.
        """
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host, self.port))
        except Exception:
            print 'Error opening ADXV socket connection.'

    def send_image_name(self, filename):
        self.socket.send("load_image %s\n" % filename)
