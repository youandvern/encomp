from application.calcscripts.process.basedefinitions import CalculationTitle, DescriptionHead, Assumption, CheckVariable, CheckVariablesText, \
        DeclareVariable, CalcVariable, BodyText, BodyHeader, HeadCollection, SetupCollection, CalcCollection, FootCollection, AssumCollection
from application.calcscripts.process.calcmodels import AISCSectionsRectangular
from application.calcscripts.process.listoptions import rectangular_section_sizes
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

    CalculationTitle('Rectangular HSS Compression Design')

    DescriptionHead("Single element design for pure compression.")

    ##

    Assumption("Members are in pure compression")
    Assumption("AISC manual of steel (14th ed.) controls member design")
    Assumption("Torsional unbraced length does not exceed lateral unbraced length")

    Pu = DeclareVariable('P_u', 10, 'kips', 'Ultimate compressive load')

    L = DeclareVariable('L', 4, 'ft', 'Member length')
    Kc = DeclareVariable('k_{c}', 1, '', 'Member effective length factor')

    size = DeclareVariable('Shape', 'HSS6X2X1/8', '', 'Member section size', input_type='select',
                           input_options=rectangular_section_sizes)

    Fy = DeclareVariable('F_{y}', 36, 'ksi', 'Material yield strength')
    Es = DeclareVariable('E', 29000, 'ksi', 'Modulus of Elasticity')

    Pc = DeclareVariable('\phi_c', 0.9, '', 'Resistance factor for compression', code_ref='ADM E.1')
    # Pty = DeclareVariable('\phi_{ty}', 0.9, '', 'Resistance factor for tensile yielding', code_ref='ADM D.1')

    #   DO NOT DEFINE INPUTS BELOW HERE OR EDIT THE FOLLOWING SECTION   #

    if len(updated_input) > 0:
        for input_variable in DeclareVariable.instances:
            new_value = updated_input.get(input_variable.name)
            if new_value:
                input_variable._set_value(new_value)

    #   DEFINE CALCULATION, BODY HEADER, AND BODY TEXT   #

    k_to_lb = Variable('1000 \ \mathrm{lbs/kip}', 1000, 'lbs/kip')
    ft_to_in = Variable('12 \ \mathrm{in/ft}', 12, 'in/ft')

    BodyHeader('Member Properties', head_level=1)  # ###############################################
    BodyHeader('Section Properties')
    section = AISCSectionsRectangular.objects(Size=size.value).first()
    Ag = CalcVariable('A_{g}', section.A, 'in^2')
    B = CalcVariable('B', section.B, 'in')
    b = CalcVariable('b', section.b, 'in')
    Ht = CalcVariable('Ht', section.Ht, 'in')
    h = CalcVariable('h', section.h, 'in')
    tdes = CalcVariable('t_{des}', section.tdes, 'in')
    rx = CalcVariable('r_x', section.rx, 'in')
    ry = CalcVariable('r_y', section.ry, 'in')
    blt = CalcVariable('\mathrm{b/t}', section.bltdes, '')
    hlt = CalcVariable('\mathrm{h/t}', section.hltdes, '')

    BodyHeader('Buckling Properties')
    yr = CalcVariable('\lambda_{r}', 1.40 * SQRT(Es / Fy), '', 'Element compression slenderness limit',
                      code_ref='AISC Table B4.1a')

    ymax = CalcVariable('\lambda_{max}', MAX(blt, hlt), '', 'Maximum element slenderness ratio')

    KLr = CalcVariable('\mathrm{KL/r}', Kc * L * ft_to_in / MIN(rx, ry), '', 'Member slenderness ratio')

    BodyHeader('Compressive Strength', head_level=1)  # ###############################################
    Fe = CalcVariable('F_e', PI**2 * Es / KLr**2, 'ksi', 'Elastic buckling stress', 'AISC Eq. E3-4')

    # Non-slender section
    if ymax.result() < yr.result():
        CheckVariablesText(yr, '<', ymax)
        BodyText('This member does not have slender elements.')

        ycrit = CalcVariable('\lambda_{crit}', 4.71 * SQRT(Es / Fy), '', code_ref='AISC Section E3')
        if KLr.result() <= ycrit.result():
            CheckVariablesText(KLr, '<=', ycrit)
            BodyText('Inelastic buckling controls.')
            Fcr = CalcVariable('F_{cr}', Fy * POW(0.658, Fy / Fe), 'ksi', 'Critical compressive stress', 'AISC Eq. E3-2')
        else:
            CheckVariablesText(KLr, '>', ycrit)
            BodyText('Elastic buckling controls.')
            Fcr = CalcVariable('F_{cr}', 0.877 * Fe, 'ksi', 'Critical compressive stress', 'AISC Eq. E3-3')

        Pn = CalcVariable('P_n', Fcr * Ag, 'kips', 'Nominal element compressive strength', 'AISC Eq. E3-1')

    # Slender section
    else:
        CheckVariablesText(yr, '>', ymax)
        BodyText('This member has slender elements.')

        BodyHeader('Reduced Effective Widths of Slender Elements', head_level=2, code_ref='AISC Eq. E7-17')
        if blt.result() > yr.result():
            CheckVariablesText(blt, '>', yr)
            BodyText('Side B is slender.')
            be = CalcVariable('b_e', 1.92 * tdes * SQRT(Es / Fy) * BRACKETS(1 - 0.38 / blt * SQRT(Es / Fy)), 'in',)
        else:
            CheckVariablesText(blt, '<', yr)
            BodyText('Side B is not slender.')
            be = b

        if hlt.result() > yr.result():
            CheckVariablesText(hlt, '>', yr)
            BodyText('Side Ht is slender.')
            he = CalcVariable('h_e', 1.92 * tdes * SQRT(Es / Fy) * BRACKETS(1 - 0.38 / hlt * SQRT(Es / Fy)))
        else:
            CheckVariablesText(hlt, '<', yr)
            BodyText('Side Ht is not slender.')
            he = h

        bi = CalcVariable('b_i', MAX(0, b - be), 'in', 'Ineffective length on side B')
        hi = CalcVariable('h_i', MAX(0, h - he), 'in', 'Ineffective length on side Ht')

        BodyHeader('Reduction Factor for Slender Stiffened Elements', head_level=2, code_ref='AISC Section E7.2')
        Ae = CalcVariable('A_e', Ag - bi * tdes * 2 - hi * tdes * 2, 'in^2', 'Effective cross-sectional area')
        Qa = CalcVariable('Q_a', Ae / Ag, '', 'Reduction factor for cross-section', code_ref='AISC Eq. E7-16')

    BodyHeader('Seismic Overturning Stability Check', head_level=1)
    OM = CalcVariable('OM', Vs*hp, 'kip-ft', 'Overturning moment due to seismic loading')
    RM = CalcVariable('RM', 0.9 * Wd * wp/2, 'kip-ft', 'Restoring moment due to reduced dead load')
    CheckVariable(OM, '<=', RM, truestate="OK", falsestate="ERROR", result_check=True)

    calculation_sum = {'head':HeadCollection.head_instances, 'assum': AssumCollection.assum_instances, 'setup':SetupCollection.setup_instances, 'calc':CalcCollection.calc_instances, 'foot':FootCollection.foot_instances}
    return calculation_sum
