from application.calcscripts.process.basedefinitions import CalculationTitle, DescriptionHead, Assumption, \
        DeclareVariable, CalcVariable, BodyText, BodyHeader, HeadCollection, SetupCollection, CalcCollection, FootCollection, AssumCollection
from application.calcscripts.process.calcmodels import FaASCE710
from application.calcscripts.process.latexExp import *


# STATUS: Testing

def create_calculation(updated_input={}):
    HeadCollection.head_instances.clear()
    AssumCollection.assum_instances.clear()
    SetupCollection.setup_instances.clear()
    CalcCollection.calc_instances.clear()
    FootCollection.foot_instances.clear()



    ###   DEFINE TITLE, DESCRIPTION, ASSUMPTIONS, AND INPUTS   ###

    CalculationTitle('Pythagorean Theorem Calculator')

    DescriptionHead("Takes the two side lengths of a right triangle and calculates the length of the hypotenuse")

    Assumption("Right triangle")
    Assumption("Measured in inches")

    a = DeclareVariable('A', 333, 'in', 'Length of side A')
    b = DeclareVariable('B', 444, 'in', 'Length of side B')


    ###   DO NOT DEFINE INPUTS BELOW HERE OR EDIT THE FOLLOWING SECTION   ###

    if len(updated_input)>0:
        for input_variable in DeclareVariable.instances:
            new_value = updated_input.get(input_variable.name)
            if new_value:
                input_variable._set_value(new_value)

    ###   DEFINE CALCULATION, BODY HEADER, AND BODY TEXT   ###


    c = CalcVariable('C', SQRT(POW(a,2) + POW(b,2)), 'in', result_check=True)

    c2 = CalcVariable('C_2', 2*c, 'in', result_check=True)

    # c = CalcVariable('C', SQRT(POW(a,2) + POW(a,2)), 'in', result_check=True)
    #
    # c2 = CalcVariable('C_2', 4*c, 'in', result_check=True)





    calculation_sum = {'head':HeadCollection.head_instances, 'assum': AssumCollection.assum_instances, 'setup':SetupCollection.setup_instances, 'calc':CalcCollection.calc_instances, 'foot':FootCollection.foot_instances}
    return calculation_sum
