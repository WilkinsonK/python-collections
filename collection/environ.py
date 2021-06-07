import os
import re


__all__ = ("getenvdict", )


def getenvdict(keys: list = [], pfx: str = "", sfx: str = "", form: str = "upper"):
    """
    Attempt to get a collection of environment
    variables in the form of a dictionary.
    :`params`:
    :`keys`: a list of variable key words to lookup in
    the environment.
    :`pfx`: adds a prefix to each of the keywords
    during environment lookup.
    :`sfx`: adds a suffix to each of the keywords
    during environment lookup.
    :`form`: dictates what format the keys will be
    converted to in the dictionary returned by 
    `getenvdict`.
    """

    venv_keys = ";".join(os.environ.keys())
    venv_dict = dict()

    found_keys = []
    for key in make_venv_keys(keys, pfx, sfx):
        found_keys += re.findall(key, venv_keys)

    for key in found_keys:
        dict_key = make_dict_key(key, pfx, sfx, form)
        venv_dict[dict_key] = os.getenv(key)

    return venv_dict


def make_venv_keys(keys, pfx, sfx):
    if len(keys) == 0: keys.append(r"\w*")
    pattern  = r"{0}[\w]*{1}" if len(pfx) > 0 else r"{1}"
    pattern += r"[\w+]{2}" if len(sfx) > 0 else r""

    makekey = lambda k: pattern.format(pfx, k, sfx)
    return [re.compile(makekey(v)) for v in keys]


def make_dict_key(key, pfx, sfx, form="upper"):
    pfx = pfx if len(pfx) > 0 else "NO_PREFIX"
    sfx = sfx if len(sfx) > 0 else "NO_SUFFIX"

    key = re.split(r"{0}_*".format(pfx), key)[-1]
    key = re.split(r"_*{0}".format(sfx), key)[0] if sfx != "NO_SUFFIX" else key
    return str.__getattribute__(key, form)()
