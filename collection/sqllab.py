import io
import re
import string

from typing import List


# initialize a string of chars, that are printable, that does not
# include whitespace or escape characters.
CHARS = string.ascii_letters + string.punctuation + string.digits


def load_sql(fp, encoding="utf8"):
    """
    Read the contents of a given file path
    returned as a string literal.
    """

    if isinstance(fp, io.BytesIO):
        return str(fp.getvalue(), encoding=encoding)
    return str(fp.read(), encoding=encoding)


def dump_sql(fp, query: str, encoding="utf8"):
    """
    Write a given query into a file path.
    """

    query = ljustify_sql(query)

    for line in query:
        fp.write(bytes(line, encoding=encoding))
    return fp


def ljustify_sql(query: str, joinlines=False):
    """
    Remove any excess left-leading whitespace
    from a given query without defacing any of the
    SQL contained in the string.
    """

    query = query.splitlines(keepends=True)

    ref = multiline_refpoint(query)
    query = [remove_excess(l, ref) for l in query]

    if joinlines:
        return "".join(query)
    return query


def get_refpoint(line: str):
    """
    Get the whitespace reference point
    (length of left-leading whitespace)
    on a given line from a query.
    """

    refpoint = 0
    while " "*refpoint == line[:refpoint]:
        refpoint += 1
    return refpoint - 1


def multiline_refpoint(lines: List[str]):
    """
    Using `get_refpoint`, get the shortest
    reference point that is not from any
    empty lines.
    """

    def is_empytline(line):
        if CHARS in line: return False
        return True

    if is_empytline(lines[0]): lines.pop(0)
    if is_empytline(lines[-1]): lines.pop(-1)

    lines = [get_refpoint(l) for l in lines if l[0] != "\n"]
    return min(lines)


def remove_excess(line: str, refpoint: int):
    """
    Remove any excess whitespace in a given line
    from a query.
    """

    contains = lambda line, chars: any([c in line for c in chars])
    while contains(line[:refpoint], CHARS):
        refpoint -= 1
    return line[refpoint:]


def is_sql_file(filename: str):
    return re.match(r"\w*\.sql", filename) != None
