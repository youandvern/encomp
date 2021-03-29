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

    CalculationTitle('AISC Steel Handrail Flexure')

    DescriptionHead("Flexural design for carbon steel handrail.")

    Assumption("Carbon steel pipe section")
    Assumption("AISC steel construction manual 14th edition, specification section F.8")
    Assumption("OSHA 1910.23 loading")
    Assumption("Compact section is selected")
    Assumption("End span controls design")


    wh = DeclareVariable('w_h', 50, 'lbs/ft', 'Uniform horizontal load in ASCE 7-10 Section 4.5.1')
    Le = DeclareVariable('L_e', 3.8, 'ft', 'Maximum post spacing for end posts')
    ku = DeclareVariable('k_u', 8, '', 'Bending moment constant for uniform load on single span')
    OD = DeclareVariable('D_{outer}',1.9, 'in', 'Outer diameter of handrail pipe section')
    tdes = DeclareVariable('t_{design}', 0.186, 'in', 'Design thickness of handrail pipe section')
    Fy = DeclareVariable('F_y', 35000, 'psi', 'Minimum yield strength of A53 Grade B steel')
    Em = DeclareVariable('E', 29000000, 'psi', 'Modulus of elasticity for carbon steel')
    Zx = DeclareVariable('Z_x', 0.421, 'in^3', 'Plastic section modulus')
    Om = DeclareVariable('\Omega', 1.67, '', 'Flexure safety factor in AISC specification section F.1' )

    ###   DO NOT DEFINE INPUTS BELOW HERE OR EDIT THE FOLLOWING SECTION   ###

    if len(updated_input)>0:
        for input_variable in DeclareVariable.instances:
            new_value = updated_input.get(input_variable.name)
            if new_value:
                input_variable._set_value(new_value)

    ###   DEFINE CALCULATION, BODY HEADER, AND BODY TEXT   ###


    Dt = CalcVariable('D/t', OD/tdes, '')
    srmax = CalcVariable('S_{max}', 0.45*Em/Fy, '', 'Maximum allowable slenderness ratio')
    srcom = CalcVariable('S_{compact}', 0.07*Em/Fy, '', 'Slenderness ratio for compact sections')

    comcheck = CalcVariable(Dt.name + "<", srcom, '', 'Check for section compactness')

    Mp = CalcVariable('M_p', Fy*Zx, 'lb-in', 'Plastic moment capacity')
    Ma = CalcVariable('M_a', Mp/Om, 'lb-in', 'Allowable bending moment', result_check=True)

    Ms = CalcVariable('M_s', wh*12*POW(Le, 2)/ku, 'lb-in', 'Service level moment demand', result_check=True)

    if float(Ms) <= float(Ma):
        BodyHeader('Demand is less than capacity, design is OK')
    else:
        BodyHeader('Demand is greater than capacity, design fails')

    calculation_sum = {'head':HeadCollection.head_instances, 'assum': AssumCollection.assum_instances, 'setup':SetupCollection.setup_instances, 'calc':CalcCollection.calc_instances, 'foot':FootCollection.foot_instances}
    return calculation_sum
