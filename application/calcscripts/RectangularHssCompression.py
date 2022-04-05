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

    DescriptionHead("Single member design for pure compression.")

    ##

    Assumption("Members are in pure compression")
    Assumption("AISC manual of steel (14th ed.) controls member design")
    Assumption("Torsional unbraced length does not exceed lateral unbraced length")

    Pu = DeclareVariable('P_u', 10, 'kips', 'Ultimate compressive load')

    L = DeclareVariable('L', 4, 'ft', 'Member length')
    Kc = DeclareVariable('k_{c}', 1, '', 'Member effective length factor')

    size = DeclareVariable('Shape', 'HSS6X2X1/8', '', 'Member section size', input_type='select',
                           input_options=rectangular_section_sizes)

    Fy = DeclareVariable('F_{y}', 36, 'ksi', 'Material yield stress')
    Es = DeclareVariable('E', 29000, 'ksi', 'Modulus of elasticity')

    Pc = DeclareVariable('\phi_c', 0.9, '', 'Resistance factor for compression')

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
    section = AISCSectionsRectangular.objects(AISC_name=size.value).first()
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

    CheckVariable(ymax, '<', yr, truestate="Non-Slender", falsestate="Slender", result_check=False)

    # Non-slender section
    if ymax.result() < yr.result():
        ycrit = CalcVariable('\lambda_{crit}', 4.71 * SQRT(Es / Fy), '', code_ref='AISC Section E3')
        if KLr.result() <= ycrit.result():
            CheckVariablesText(KLr, '<=', ycrit)
            BodyText('Inelastic buckling controls.')
            Fcr = CalcVariable('F_{cr}', Fy * POW(0.658, Fy / Fe), 'ksi', 'Critical compressive stress', 'AISC Eq. E3-2')
        else:
            CheckVariablesText(KLr, '>', ycrit)
            BodyText('Elastic buckling controls.')
            Fcr = CalcVariable('F_{cr}', 0.877 * Fe, 'ksi', 'Critical compressive stress', 'AISC Eq. E3-3')

        Pn = CalcVariable('P_n', Fcr * Ag, 'kips', 'Nominal member compressive strength', 'AISC Eq. E3-1')

    # Slender section
    else:
        EWC = Variable('0.38', 0.38)  # Effective width constant
        BodyHeader('Reduced Effective Widths of Slender Elements', head_level=2, code_ref='AISC Eq. E7-18')
        if blt.result() > yr.result():
            CheckVariablesText(blt, '>', yr)
            BodyText('Side B is slender.')
            be = CalcVariable('b_e', 1.92 * tdes * SQRT(Es / Fy) * BRACKETS(1 - EWC / blt * SQRT(Es / Fy)), 'in',)
        else:
            CheckVariablesText(blt, '<', yr)
            BodyText('Side B is not slender.')
            be = CalcVariable('b_e', b, 'in',)

        if hlt.result() > yr.result():
            CheckVariablesText(hlt, '>', yr)
            BodyText('Side Ht is slender.')
            he = CalcVariable('h_e', 1.92 * tdes * SQRT(Es / Fy) * BRACKETS(1 - EWC / hlt * SQRT(Es / Fy)))
        else:
            CheckVariablesText(hlt, '<', yr)
            BodyText('Side Ht is not slender.')
            he = CalcVariable('h_e', h, 'in',)

        bi = CalcVariable('b_i', MAX(0, b - be), 'in', 'Ineffective length on side B')
        hi = CalcVariable('h_i', MAX(0, h - he), 'in', 'Ineffective length on side Ht')

        BodyHeader('Reduction Factor for Slender Stiffened Elements', head_level=2, code_ref='AISC Section E7.2')
        Ae = CalcVariable('A_e', Ag - bi * tdes * 2 - hi * tdes * 2, 'in^2', 'Effective cross-sectional area')
        Qa = CalcVariable('Q_a', Ae / Ag, '', 'Reduction factor for cross-section', code_ref='AISC Eq. E7-16')

        BodyHeader('Nominal Compressive Strength', head_level=2, code_ref='AISC Section E7')

        ycrit = CalcVariable('\lambda_{crit}', 4.71 * SQRT(Es / (Qa * Fy)), '')
        if KLr.result() <= ycrit.result():
            CheckVariablesText(KLr, '<=', ycrit)
            BodyText('Inelastic buckling controls.')
            Fcr = CalcVariable('F_{cr}', Qa * Fy * POW(0.658, Qa * Fy / Fe), 'ksi', 'Critical compressive stress',
                               'AISC Eq. E7-2')
        else:
            CheckVariablesText(KLr, '>', ycrit)
            BodyText('Elastic buckling controls.')
            Fcr = CalcVariable('F_{cr}', 0.877 * Fe, 'ksi', 'Critical compressive stress', 'AISC Eq. E7-3')

        Pn = CalcVariable('P_n', Fcr * Ag, 'kips', 'Nominal member compressive strength', 'AISC Eq. E7-1')

    BodyHeader('Member Demand vs. Capacity Check', head_level=1)
    PPn = CalcVariable('\phi P_n', Pc * Pn, 'kips', 'Design member compressive capacity', result_check=True)
    CheckVariable(Pu, '<=', PPn, truestate="OK", falsestate="ERROR", result_check=True)

    return {
        'head': HeadCollection.head_instances,
        'assum': AssumCollection.assum_instances,
        'setup': SetupCollection.setup_instances,
        'calc': CalcCollection.calc_instances,
        'foot': FootCollection.foot_instances,
    }
