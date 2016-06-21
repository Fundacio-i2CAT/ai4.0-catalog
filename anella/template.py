
import re
from string import Template

delimiter = '$'
idpattern = r'[_a-z][_a-z0-9]*'

pattern = r"""
%(delim)s(?:
  (?P<escaped>%(delim)s) |   # Escape sequence of two delimiters
  (?P<named>%(id)s)      |   # delimiter and a Python identifier
  {(?P<braced>%(id)s)}   |   # delimiter and a braced identifier
  (?P<invalid>)              # Other ill-formed delimiter exprs
)
""" % {'delim' : re.escape(delimiter),
       'id'    : idpattern,
      }
pattern = re.compile(pattern, re.IGNORECASE | re.VERBOSE)

operators = ['or', 'and', '+', '*']

def is_template(template):
    if not template or not isinstance(template,str):
        return False

    return len( [ mat[1] or mat[2] for mat in re.findall(pattern, template) if mat[1] or mat[2] ] )

def is_variable(template):
    if not template or not isinstance(template,str):
        return False

    return len( [ mat[1] for mat in re.findall(pattern, template) if mat[1] ] )==1
#     return is_template(template) and len(template.split('$'))==2

def get_parameters(template):
    if not template or not isinstance(template,str):
        return None

    # return [ mat[1] for mat in re.findall(pattern, template) if mat[1] ]
    return [ mat[1] or mat[2] for mat in re.findall(pattern, template) if mat[1] or mat[2] ]


def invalid(template, mo):
    i = mo.start('invalid')
    lines = template[:i].splitlines(True)
    if not lines:
        colno = 1
        lineno = 1
    else:
        colno = i - len(''.join(lines[:-1]))
        lineno = len(lines)
    raise ValueError('Invalid placeholder in string: line %d, col %d' % (lineno, colno))

