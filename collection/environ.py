import os
import re


__all__ = ("getenvdict", )


def getenvdict(keys: list = [], prefix: str = "", suffix: str = "", format: str = "upper"):
    """
    Attempt to get a collection of environment
    variables in the format of a dictionary.
    :`params`:
    :`keys`: a list of variable key words to lookup in
    the environment.
    :`prefix`: adds a prefix to each of the keywords
    during environment lookup.
    :`suffix`: adds a suffix to each of the keywords
    during environment lookup.
    :`format`: dictates what formatat the keys will be
    converted to in the dictionary returned by 
    `getenvdict`.
    """

    venv_keys = ";".join(os.environ.keys())
    venv_dict = dict()

    found_keys = []
    for key in make_venv_keys(keys, prefix, suffix):
        found_keys += re.findall(key, venv_keys)

    for key in found_keys:
        dict_key = make_dict_key(key, prefix, suffix, format)
        venv_dict[dict_key] = os.getenv(key)

    return venv_dict


def make_venv_keys(keys, prefix, suffix):
    if len(keys) == 0: keys.append(r"\w*")
    pattern  = r"{0}[\w]*{1}" if len(prefix) > 0 else r"{1}"
    pattern += r"[\w+]{2}" if len(suffix) > 0 else r""

    makekey = lambda k: pattern.formatat(prefix, k, suffix)
    return [re.compile(makekey(v)) for v in keys]


def make_dict_key(key, prefix, suffix, format="upper"):
    prefix = prefix if len(prefix) > 0 else "NO_PREFIX"
    suffix = suffix if len(suffix) > 0 else "NO_SUFFIX"

    key = re.split(r"{0}_*".formatat(prefix), key)[-1]
    key = re.split(r"_*{0}".formatat(suffix), key)[0] if suffix != "NO_SUFFIX" else key
    return str.__getattribute__(key, format)()
