
from application.calcscripts.process.latexExp import Variable, Operation, Expression
from pylatexenc.latex2text import LatexNodes2Text

class HeadCollection(object):
    head_instances=[]
class AssumCollection(object):
    assum_instances=[]
class SetupCollection(object):
    setup_instances=[]
class CalcCollection(object):
    calc_instances=[]
class FootCollection(object):
    foot_instances=[]

class CalculationTitle(HeadCollection):
    """ Title of calculation sheet """
    def __init__(self, title):
        super(CalculationTitle, self).__init__()
        self.head_instances.append(self)
        self.text = title
    def __str__(self):
        return f"{self.text}"

class DescriptionHead(HeadCollection):
    """ Description text for a calculation. Displayed at the top of every calculation.
        Option to display when calc is used as a subcalc. """
    instances = []
    def __init__(self, description):
        super(DescriptionHead, self).__init__()
        self.head_instances.append(self)
        self.text = description
        self.__class__.instances.append(self)
    def __str__(self):
        return f"{self.text}"


class Assumption(AssumCollection):
    """ Declares an assumption associated with a calculation. """
    instances = []
    def __init__(self, assumption):
        super(Assumption, self).__init__()
        self.assum_instances.append(self)
        self.text = assumption
        self.__class__.instances.append(self)
        # self.append_collector()
    def __str__(self):
        return f"{self.text}"


class DeclareVariable(Variable, SetupCollection):
    """ Declares a variable with a numeric value. """
    instances = []
    def __init__(self, name, value=0, unit="", description="", code_ref = "", input_type = "text", num_step="any", min_value=None, max_value=None, input_options=None):
        self.name=name
        self.value=value
        # self.Value=value
        self.unit=unit
        self.description = description
        self.code_ref = code_ref
        self.input_type = input_type
        self.num_step = num_step
        self.min_value=min_value
        self.max_value=max_value
        self.input_options= input_options
        self.__class__.instances.append(self)
        self.setup_instances.append(self)
        self.setDisplayType()

    def strResultWithName(self):
        r"""Returns string of the result of the receiver (its formatted result) including name ending with its units

		:rtype: str

		.. code-block:: python

			>>> v1 = DeclareVariable('a_{22}',3.45,'mm', description="Section thickness")
			>>> print v1.strResultWithDescription()
			a_{22} = 3.45 \ \mathrm{mm}
		"""
        return '%s = \\ %s \\ %s'%(self.name, self.strResult(),self.unitFormat%self.unit)
    def setDisplayType(self):
        if self.input_type=="select":
            pass
        else:
            v = self.value
            try:
                float(v)
                self.input_type = "number"
                self.num_step = "any"
            except ValueError:
                self.input_type = "text"
                # self.value = f"\mathrm{{{v}}}"


class CalcVariable(Expression, CalcCollection):
    """ Declares a new variable based on an operation of variables, operations, or numbers. """
    instances = []
    def __init__(self, name, operation, unit="", description='', code_ref="", result_check=False ):
        self.name=name
        self.operation=operation
        self.unit=unit
        self.description = description
        self.code_ref = code_ref
        self.result_check=result_check
        self.__class__.instances.append(self)
        self.calc_instances.append(self)

        self.operation_float_check(operation)
        # self.operation_length = get_operation_length()


    def strResultWithDescription(self):
        r"""Returns string representation of receiver in the form "description; name = symbolicExpr"

		:rtype: str

		.. code-block:: python

			>>> v1 = Variable('a_{22}',3.45,'mm')
			>>> v2 = Variable('F',5.876934835,'kN')
			>>> v3 = Variable('F',4.34,'kN',exponent=-2)
			>>> e2 = CalcVariable('E_2',(v1+v2)/v3,'mm', description="Section thickness")
			>>> print e2.strResultWithDescription()
			Section thickness; E_2 = \frac{ {a_{22}} + {F} }{ {F} }
		"""
        if self.isSymbolic():
            return '%s = %s'%(self.name,self.operation)
        return '%s; %s = %s'%(self.description, self.name, self.operation.strSymbolic())

    def operation_float_check(self, input_operation):
        if isinstance(input_operation,(float, int)):
            self.operation = Operation('',input_operation)
        else:
            self.operation = input_operation

    def get_operation_length(self):
        latex_string = self.operation.strSubstituted()
        op_length = len(LatexNodes2Text().latex_to_text(latex_string))
        return op_length

    def unformat_operation_sub(self):
        latex_string = self.operation.strSubstituted()
        unformat_sub = LatexNodes2Text().latex_to_text(latex_string)
        return unformat_sub
    def unformat_operation_sym(self):
        latex_string = self.operation.strSymbolic()
        unformat_sym = LatexNodes2Text().latex_to_text(latex_string)
        return unformat_sym


class CheckVariable(CalcCollection):
    """ Outline for design checks"""

    def __init__(self, a, op, b, truestate="OK", falsestate="ERROR", description="", code_ref="", result_check=True):
        self.a = a
        self.op = op
        self.b = b
        self.truestate = truestate
        self.falsestate = falsestate
        self.description = description
        self.code_ref = code_ref
        self.result_check = result_check
        self.unit = ""
        self.name = self.strSymbolic
        self.passfail = "fail"
        self.calc_instances.append(self)

    def result(self):
        OPERATORS = {'<': 'lt', '<=': 'le', '=': 'eq', '!=': 'ne', '==': 'eq', '>': 'gt', '>=': 'ge'}
        try:
            anum = float(self.a)
            bnum = float(self.b)
            method = f'__{OPERATORS[self.op]}__'
            boolresult = getattr(anum, method)(bnum)
            if boolresult:
                self.passfail = "pass"
                return self.truestate
            else:
                self.passfail = "fail"
                return self.falsestate
        except:
            return f"Failed to compare {self.a} and {self.b} with operator {self.op}"

    def strSymbolic(self):
        TECHATORS = {'<': '<', '<=': '\leq', '=': '=', '!=': r'\neq', '==': '=', '>': '>', '>=': '\geq'}
        if isinstance(self.a, (float, int)) and isinstance(self.b, (float, int)):
            return ""
        elif isinstance(self.a, (float, int)):
            return f"\ {self.a} & \ {TECHATORS[self.op]} \ {self.b.strSymbolic()}"
        elif isinstance(self.b, (float, int)):
            return f"\ {self.a.strSymbolic()} & \ {TECHATORS[self.op]} \ {self.b}"
        else:
            return f"\ {self.a.strSymbolic()} & \ {TECHATORS[self.op]} \ {self.b.strSymbolic()}"

    def strSubstituted(self):
        TECHATORS = {'<': '<', '<=': '\leq', '=': '=', '!=': r'\neq', '==': '=', '>': '>', '>=': '\geq'}
        if isinstance(self.a, (float, int)) and isinstance(self.b, (float, int)):
            return f"\ {self.a} & \ {TECHATORS[self.op]} \ {self.b}"
        elif isinstance(self.a, (float, int)):
            return f"\ {self.a} & \ {TECHATORS[self.op]} \ {self.b.strResultWithUnit()}"
        elif isinstance(self.b, (float, int)):
            return f"\ {self.a.strResultWithUnit()} & \ {TECHATORS[self.op]} \ {self.b}"
        else:
            return f"\ {self.a.strResultWithUnit()} & \ {TECHATORS[self.op]} \ {self.b.strResultWithUnit()}"

class CheckVariablesText(CalcCollection):
    """ Outline for design check documentation"""

    def __init__(self, a, op, b, op1=None, c=None,  code_ref="", description=''):
        self.a = a
        self.op = op
        self.b = b
        self.op1 = op1
        self.c = c
        self.description = description
        self.code_ref = code_ref
        self.result_check = False
        self.unit = ""
        self.calc_instances.append(self)

    def strSymbolic(self):
        TECHATORS = {'<': '<', '<=': '\leq', '=': '=', '!=': r'\neq', '==': '=', '>': '>', '>=': '\geq'}
        all_inputs = [self.a, self.b, self.c]
        str_inputs = []

        for input in all_inputs:
            if input:
                try:
                    str_input = input.name
                except:
                    try:
                        str_input = input.strSymbolic()
                    except:
                        str_input = str(input)
            else:
                str_input = str(input)
            str_inputs.append(str_input)

        if self.op1 and self.c:
            return f"{str_inputs[0]} \ {TECHATORS[self.op]} \ {str_inputs[1]} \ {TECHATORS[self.op1]}  \ {str_inputs[2]}"
        else:
            return f"{str_inputs[0]} \ {TECHATORS[self.op]} \ {str_inputs[1]}"



class BodyText(CalcCollection):
    """ Displays text explanation in the body of a calculation document. """
    instances = []
    def __init__(self, text, code_ref=""):
        self.text = text
        self.description = self.text
        self.code_ref = code_ref
        self.__class__.instances.append(self)
        self.calc_instances.append(self)
    def __str__(self):
        return f"{self.text}"


class BodyHeader(CalcCollection):
    """ Displays larger text in the body of a calculation document. """
    instances = []
    def __init__(self, text, head_level = 3, code_ref=""):
        self.text = text
        self.description = self.text
        self.code_ref = code_ref
        self.head_level = head_level # 1, 2, or 3
        self.__class__.instances.append(self)
        self.calc_instances.append(self)
    def __str__(self):
        return f"{self.text}"

class DeclareTable(SetupCollection):
    """ Declares a table style input with a numeric values and headers.
        Table to be 2 dimensional with first row headers, units are 1 dimensional array (length = table column #s).
    """
    instances = []
    def __init__(self, name, value=[[]], unit=[], description="", code_ref = "", input_type = "table", num_step="any", min_value=None, max_value=None, input_options=None):
        self.name=name
        self.value=value
        # self.Value=value
        self.unit=unit
        self.description = description
        self.code_ref = code_ref
        self.input_type = input_type
        self.num_step = num_step
        self.min_value=min_value
        self.max_value=max_value
        self.input_options= input_options
        self.unitFormat = r'\mathrm{%s}'
        self.__class__.instances.append(self)
        self.setup_instances.append(self)

    def _set_value(self,v):
    	if v is None:
    		self.value = [[]]
    	else:
    		self.value = v

    def strResultWithName(self):
        r"""Returns string of the result of the receiver (its formatted result) including name ending with its units

		:rtype: str

		.. code-block:: python

			>>> v1 = DeclareVariable('a_{22}',3.45,'mm', description="Section thickness")
			>>> print v1.strResultWithDescription()
			a_{22} = 3.45 \ \mathrm{mm}
		"""
        return '%s = \\ %s \\ %s'%(self.name, self.value, self.unitFormat%self.unit)

class CalcTable(CalcCollection):
    """ Declares a table style input with a numeric values and headers.
        Table to be 2 dimensional with first row headers, units are 1 dimensional array (length = table column #s).
    """
    instances = []
    def __init__(self, name, value=[[]], unit=[], description="", code_ref = "", result_check=False):
        self.name=name
        self.value=value
        # self.Value=value
        self.unit=unit
        self.description = description
        self.code_ref = code_ref
        self.unitFormat = r'\mathrm{%s}'
        self.result_check=result_check
        self.__class__.instances.append(self)
        self.calc_instances.append(self)

    def strResultWithName(self):
        r"""Returns string of the result of the receiver (its formatted result) including name ending with its units

		:rtype: str

		.. code-block:: python

			>>> v1 = DeclareVariable('a_{22}',3.45,'mm', description="Section thickness")
			>>> print v1.strResultWithDescription()
			a_{22} = 3.45 \ \mathrm{mm}
		"""
        return '%s = \\ %s \\ %s'%(self.name, self.value, self.unitFormat%self.unit)
    def result(self):
        return self.value 
