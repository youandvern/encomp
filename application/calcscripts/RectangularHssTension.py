from application.calcscripts.process.basedefinitions import CalculationTitle, DescriptionHead, Assumption, CheckVariable, CheckVariablesText, \
        DeclareVariable, CalcVariable, BodyText, BodyHeader, HeadCollection, SetupCollection, CalcCollection, FootCollection, AssumCollection
from application.calcscripts.process.calcmodels import AISCSectionsRectangular
from application.calcscripts.process.listoptions import rectangular_section_sizes, hss_load_applied_sides
from application.calcscripts.process.latexExp import *


# STATUS: Development

def create_calculation(updated_input=None):
    if updated_input is None:
        updated_input = {}
    HeadCollection.head_instances.clear()
    AssumCollection.assum_instances.clear()
    SetupCollection.setup_instances.clear()
    CalcCollection.calc_instances.clear()
    FootCollection.foot_instances.clear()

    #   DEFINE TITLE, DESCRIPTION, ASSUMPTIONS, AND INPUTS   #

    CalculationTitle('Rectangular HSS Tension Design')

    DescriptionHead("Single member design for pure tension.")

    ##

    Assumption("Members are in pure tension")
    Assumption("AISC manual of steel (14th ed.) controls member design")
    Assumption("Loads are applied through welds on one or all sides as specified below")
    Assumption("Member elements do not have slots or holes to create the connection")

    Pu = DeclareVariable('P_u', 10, 'kips', 'Ultimate tension load')
    Swa = DeclareVariable('Side', hss_load_applied_sides[0], '',
                          'Cross-sectional element to which the loading is applied',
                          input_type='select',
                          input_options=hss_load_applied_sides)

    size = DeclareVariable('Shape', 'HSS6X2X1/8', '', 'Member section size', input_type='select',
                           input_options=rectangular_section_sizes)

    Fy = DeclareVariable('F_{y}', 36, 'ksi', 'Material yield stress')
    Fu = DeclareVariable('F_{u}', 58, 'ksi', 'Material rupture stress')

    U = DeclareVariable('U', 1.0, '', 'Shear lag factor', code_ref='AISC Table D3.1')
    Pty = DeclareVariable('\phi_y', 0.9, '', 'Resistance factor for tensile yielding', code_ref='AISC Section D2(a)')
    Ptr = DeclareVariable('\phi_r', 0.75, '', 'Resistance factor for tensile rupture', code_ref='AISC Section D2(b)')

    #   DO NOT DEFINE INPUTS BELOW HERE OR EDIT THE FOLLOWING SECTION   #

    if len(updated_input) > 0:
        for input_variable in DeclareVariable.instances:
            new_value = updated_input.get(input_variable.name)
            if new_value:
                input_variable._set_value(new_value)

    #   DEFINE CALCULATION, BODY HEADER, AND BODY TEXT   #

    k_to_lb = Variable('1000 \ \mathrm{lbs/kip}', 1000, 'lbs/kip')
    ft_to_in = Variable('12 \ \mathrm{in/ft}', 12, 'in/ft')

    BodyHeader('Section Properties', head_level=1)  # ###############################################
    section = AISCSectionsRectangular.objects(AISC_name=size.value).first()
    Ag = CalcVariable('A_{g}', section.A, 'in^2')
    B = CalcVariable('B', section.B, 'in')
    Ht = CalcVariable('Ht', section.Ht, 'in')
    tdes = CalcVariable('t_{des}', section.tdes, 'in')

    BodyHeader('Tensile Yield Strength', head_level=1)  # ###############################################
    Pny = CalcVariable('P_{ny}', Fy * Ag, 'kips', 'Nominal member tensile yield strength', 'AISC Eq. D2-1')
    PPny = CalcVariable('\phi P_{ny}', Pty * Pny, 'kips', 'Design member tensile yield capacity', result_check=False)

    BodyHeader('Tensile Rupture Strength', head_level=1)  # ###############################################
    if Swa.value == hss_load_applied_sides[0]:
        An = CalcVariable('A_n', Ag, 'in^2', 'Net area at connection', code_ref='AISC Section B4.3')
    elif Swa.value == hss_load_applied_sides[1]:
        An = CalcVariable('A_n', B * tdes, 'in^2', 'Net area at connection', code_ref='AISC Table D3.1(3)')
    else:
        An = CalcVariable('A_n', Ht * tdes, 'in^2', 'Net area at connection', code_ref='AISC Table D3.1(3)')

    Ae = CalcVariable('A_e', An * U, 'in^2', 'Effective net area', code_ref='AISC Eq. D3-1')
    Pnr = CalcVariable('P_{nr}', Fu * Ae, 'kips', 'Nominal member tensile rupture strength', 'AISC Eq. D2-2')
    PPnr = CalcVariable('\phi P_{nr}', Ptr * Pnr, 'kips', 'Design member rupture yield capacity', result_check=False)

    BodyHeader('Member Demand vs. Capacity Check', head_level=1)
    PPn = CalcVariable('\phi P_n', MIN(PPny, PPnr), 'kips', 'Controlling member tensile capacity', result_check=True)
    CheckVariable(Pu, '<=', PPn, truestate="OK", falsestate="ERROR", result_check=True)

    return {
        'head': HeadCollection.head_instances,
        'assum': AssumCollection.assum_instances,
        'setup': SetupCollection.setup_instances,
        'calc': CalcCollection.calc_instances,
        'foot': FootCollection.foot_instances,
    }
