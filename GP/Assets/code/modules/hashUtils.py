"""
dicthash.dicthash
=============

A module implementing an md5 hash function for (nested) dictionaries.

Functions
---------

generate_hash_from_dict - generate an md5 hash from a (nested)
dictionary

"""

# from future.builtins import str
import hashlib
import warnings
FLOAT_FACTOR = 1e15
FLOOR_SMALL_FLOATS = False

# user warnings are printed to sys.stdout
warnings.simplefilter('default', category=UserWarning)

try:
    basestring  # attempt to evaluate basestring
except NameError:
    basestring = str


def _save_convert_float_to_int(x):
    """
    Convert a float x to an integer. Avoid rounding errors on different
    platforms by shifting the floating point behind the last relevant
    digit.

    Parameters
    ----------
    x : float
        Float to be converted.
    """
    if abs(x) > 0. and abs(x) < 1. / FLOAT_FACTOR:
        if not FLOOR_SMALL_FLOATS:
            raise ValueError('Float too small for safe conversion to '
                             'integer.')
        else:
            x = 0.
            warnings.warn('Float too small for safe conversion to'
                          'integer. Rounding down to zero.', UserWarning)
    return int(x * FLOAT_FACTOR)


def _unpack_value(value, prefix='', whitelist=None, blacklist=None):
    """
    Unpack values from a data structure and convert to string. Call
    the corresponding functions for dict or iterables or use simple
    string conversion for scalar variables.

    Parameters
    ----------
    value : dict, iterable, scalar variable
        Value to be unpacked.
    prefix : str, optional
        Prefix to preprend to resulting string. Defaults to empty
        string.
    """

    try:
        return _generate_string_from_dict(value,
                                          blacklist=blacklist,
                                          whitelist=whitelist,
                                          prefix=prefix + 'd')
    except AttributeError:
        # not a dict
        try:
            return prefix + _generate_string_from_iterable(value, prefix='i')
        except TypeError:
            # not an iterable
            if isinstance(value, float):
                return prefix + str(_save_convert_float_to_int(value))
            else:
                return prefix + str(value)


def _generate_string_from_iterable(l, prefix=''):
    """
    Convert an iterable to a string, by extracting every value. Takes
    care of proper handling of floats to avoid rounding errors.

    Parameters
    ----------
    l : iterable
        Iterable to be converted.
    """

    # we need to handle strings separately to avoid infinite recursion
    # due to their iterable property
    if isinstance(l, basestring):
        return ''.join((prefix, str(l)))
    else:
        return ''.join(_unpack_value(value, prefix='') for value in l)


def _generate_string_from_dict(d, blacklist, whitelist, prefix=''):
    """
    Convert a dictionary to a string, by extracting every key value
    pair. Takes care of proper handling of floats, iterables and nested
    dictionaries.

    Parameters
    ----------
    d : dict
        Dictionary to be converted
    blacklist : list
        List of keys to exclude from conversion. Blacklist overrules
        whitelist, i.e., keys appearing in the blacklist will
        definitely not be used.
    whitelist: list
        List of keys to include in conversion.
    """
    if whitelist is None:
        whitelist = list(d.keys())
    if blacklist is not None:
        whitelist = set(whitelist).difference(blacklist)
    # Sort whitelist according to the keys converted to str
    if len(whitelist) > 0:
        return ''.join(_unpack_value(d[key],
                                     whitelist=filter_blackwhitelist(whitelist, key),
                                     blacklist=filter_blackwhitelist(blacklist, key),
                                     prefix=prefix + str(key)) for
                       key in sorted(filter_blackwhitelist(whitelist, None), key=str))
    else:
        return ''


def generate_hash_from_dict(d, blacklist=None, whitelist=None,
                            raw=False):
    """
    Generate an md5 hash from a (nested) dictionary.

    Takes care of extracting nested dictionaries, iterables and
    avoids rounding errors of floats. Makes sure keys are read in a
    unique order. A blacklist of keys can be passed, that can contain
    keys which should be excluded from the hash. If a whitelist is
    given, only keys appearing in the whitelist are used to generate
    the hash. All strings are converted to unicode, i.e., the hash
    does not distinguish between strings provided in ascii or unicode
    format. Lists, np.ndarrays and tuples are treated equally, i.e., an
    array-like item [1,2,3], np.array([1,2,3]) or (1,2,3) will lead
    to the same hash if they are of the same type.

    Parameters
    ----------
    d : dict
        Dictionary to compute the hash from.
    blacklist : list, optional
        List of keys which *are not* used for generating the hash.
        Keys of subdirectories can be provided by specifying
        the full path of keys in a tuple.
        If None, no keys will be ignored.
    whitelist : list, optional
        List of keys which *are* used for generating the hash.
        Keys of subdirectories can be provided by specifying
        the full path of keys in a tuple.
        If None, all keys will be used.
        Blacklist overrules whitelist, i.e., keys appearing in the
        blacklist will definitely not be used.
    raw : bool, optional
          if True, return the unhashed string.

    Returns
    -------
    : string
      The hash generated from the dictionary, or the unhashed string if
      raw is True.

    Example
    -------
    >>> from_ _dicthash import generate_hash_from_dict
    >>> d = {'a': 'asd', 'b': 0.12, 3: {'c': [3, 4, 5]}}
    >>> generate_hash_from_dict(d)
    'd748bbf148db514911ed0bf215729d01'

    """
    if not isinstance(d, dict):
        raise TypeError('Please provide a dictionary.')

    if blacklist is not None:
        validate_blackwhitelist(d, blacklist)
    if whitelist is not None:
        validate_blackwhitelist(d, whitelist)
    raw_string = _generate_string_from_dict(d, blacklist, whitelist, prefix='d')
    if raw:
        return raw_string
    else:
        return hashlib.md5(raw_string.encode('utf-8')).hexdigest()


def validate_blackwhitelist(d, l):
    """
    Validate that all entries in black/whitelist l, appear in the
    dictionary d

    Parameters
    ----------
    d : dict
        Dictionary to use for validation.
    l : list
        Blacklist or whitelist to validate.
    """
    for key in l:
        if isinstance(key, tuple):
            k = key[0]
        else:
            k = key
        if k not in d:
            raise KeyError('Key "{key}" not found in dictionary. '
                           'Invalid black/whitelist.'.format(key=key))
        if isinstance(key, tuple) and len(key) > 1:
            validate_blackwhitelist(d[key[0]], [key[1:]])


def filter_blackwhitelist(l, key):
    """
    Filter black/whitelist for the keys that belong to the
    subdirectory which is embedded into the nested dictionary
    structure with the given key.

    Three different cases:
    - if l is None, then return none
    - if key is None, then we are at the top-level dictionary, thus
      include all scalar keys and the first element of tuples.
    - if key is not None, then return only the keys that are tuples
      where the first element of the tuple matches the given key

    Parameters
    ----------
    l : list
        Black- or whitelist to filter
    key : scalar variable or None
        Key to filter for. See above for the behavior if key is None
    """
    if l is None:
        return None
    else:
        fl = []
        for k in l:
            if isinstance(k, tuple):
                if key is not None and k[0] == key:
                    if len(k) == 2:
                        fl.append(k[1])
                    else:
                        fl.append(k[1:])
                elif key is None:
                    fl.append(k[0])
            elif key is None:
                fl.append(k)
        if len(fl) == 0:
            return None
        else:
            return fl