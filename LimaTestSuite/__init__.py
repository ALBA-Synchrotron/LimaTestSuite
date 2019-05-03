import datetime
import logging
import os

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
fmt_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(fmt_str)

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


def debug(fn):
    def _decorated(*arg, **kwargs):
        logger.log(logging.DEBUG, "ENTERING '%s'(%r,%r)", fn.func_name, arg,
                   kwargs)
        ret = fn(*arg, **kwargs)
        logger.log(logging.DEBUG, "EXITING '%s'(%r,%r) got return value: %r",
                   fn.func_name, arg, kwargs, ret)
        return ret
    return _decorated


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
    return now.strftime("%Y%m%d_%H%M")


def create_test_folder(test_name, base_dir=None):
    cwd = 'tmp/LimaTestSuite'
    folder = "{0}_{1}".format(test_name, _str_date_now())
    test_path = os.path.join(cwd, folder)
    if base_dir:
        test_path = os.path.join(base_dir, test_path)
    else:
        test_path = os.path.join(os.sep, test_path)

    if not os.path.exists(test_path):
       os.makedirs(test_path)

    return test_path


def get_dict(obj, name):
    """
    Search a dictionary attribute with name _name.

    :param obj: Object where to search the dictionary
    :param name: dictionary name
    :return: the dictionary if found, None otherwise
    """
    dictionary = '_{0}'.format(name)
    try:
        d = getattr(obj, dictionary)
    except AttributeError:
        d = None
    return d

