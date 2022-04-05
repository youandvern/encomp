from application.calcscripts.process.basedefinitions import CalculationTitle, DescriptionHead, Assumption, \
    CheckVariable, CheckVariablesText, \
    DeclareVariable, CalcVariable, BodyText, BodyHeader, HeadCollection, SetupCollection, CalcCollection, \
    FootCollection, AssumCollection
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

    CalculationTitle('Rectangular HSS Flexural Design')

    DescriptionHead("Simply supported member design in pure bending.")

    ##

    Assumption("Members are in pure compression")
    Assumption("AISC manual of steel (14th ed.) controls member design")
    Assumption("Torsional unbraced length does not exceed lateral unbraced length")

    Wu = DeclareVariable('w_u', 10, 'plf', 'Ultimate linear load on member')

    L = DeclareVariable('L', 4, 'ft', 'Member length')
    size = DeclareVariable('Shape', 'HSS6X2X1/8', '', 'Member section size', input_type='select',
                           input_options=rectangular_section_sizes)

    Fy = DeclareVariable('F_{y}', 36, 'ksi', 'Material yield stress')
    Es = DeclareVariable('E', 29000, 'ksi', 'Modulus of elasticity')
    dlim = DeclareVariable('X_{lim}', 360, '', 'Member deflection limit under all loads (L/X)')

    Pf = DeclareVariable('\phi_f', 0.9, '', 'Resistance factor for flexural design')

    #   DO NOT DEFINE INPUTS BELOW HERE OR EDIT THE FOLLOWING SECTION   #

    if len(updated_input) > 0:
        for input_variable in DeclareVariable.instances:
            new_value = updated_input.get(input_variable.name)
            if new_value:
                input_variable._set_value(new_value)

    #   DEFINE CALCULATION, BODY HEADER, AND BODY TEXT   #

    k_to_lb = Variable('1000 \ \mathrm{lbs/kip}', 1000, 'lbs/kip')
    ft_to_in = Variable('12 \ \mathrm{in/ft}', 12, 'in/ft')

    BodyHeader('Member Properties', head_level=2)  # ###############################################
    section = AISCSectionsRectangular.objects(AISC_name=size.value).first()
    Ag = CalcVariable('A_{g}', section.A, 'in^2')
    B = CalcVariable('B', section.B, 'in')
    b = CalcVariable('b', section.b, 'in')
    Ht = CalcVariable('Ht', section.Ht, 'in')
    h = CalcVariable('h', section.h, 'in')
    tdes = CalcVariable('t_{des}', section.tdes, 'in')
    Ix = CalcVariable('I_x', section.Ix, 'in^4')
    Sx = CalcVariable('S_x', section.Sx, 'in^3')
    Zx = CalcVariable('Z_x', section.Zx, 'in^3')
    blt = CalcVariable('\mathrm{b/t}', section.bltdes, '')
    hlt = CalcVariable('\mathrm{h/t}', section.hltdes, '')

    BodyHeader('Yielding', head_level=2)  # ###############################################
    Mny = CalcVariable('M_{ny}', Fy * Zx, 'kip-in', 'Nominal plastic flexural capacity', code_ref='AISC Eq. F7-1')

    BodyHeader('Flange Local Buckling', head_level=2)
    yp = CalcVariable('\lambda_p', 1.12 * SQRT(Es / Fy), '', 'Compact limiting width-to-thickness ratio for flanges',
                      code_ref='AISC Table B4.1b(17)')
    yr = CalcVariable('\lambda_r', 1.40 * SQRT(Es / Fy), '', 'Slender limiting width-to-thickness ratio for flanges',
                      code_ref='AISC Table B4.1b(17)')

    if blt.result() < yp.result():
        CheckVariable(blt, '<', yp, truestate='Compact', falsestate='NonCompact', result_check=False)
        BodyText('For compact sections, flange local buckling does not apply', code_ref='AISC Section F7.2(a)')
        Mnfb = CalcVariable('M_{nfb}', Mny, 'kip-in')

    elif blt.result() < yr.result():
        CheckVariable(blt, '<', yp, truestate='Compact', falsestate='NonCompact', result_check=False)
        CheckVariable(blt, '<', yr, truestate='NonCompact', falsestate='Slender', result_check=False)
        Mnfb = CalcVariable('M_{nfb}', Mny - BRACKETS(Mny - Fy * Sx) * BRACKETS(3.57 * blt * SQRT(Fy / Es) - 4.0),
                             'kip-in',
                             'Nominal flexural capacity due to flange local buckling',
                             code_ref='AISC Eq. F7-2')
    else:
        CheckVariable(blt, '<', yr, truestate='NonCompact', falsestate='Slender', result_check=False)
        be = CalcVariable('b_e', 1.92 * tdes * SQRT(Es / Fy) * BRACKETS(1 - 0.38 / blt * SQRT(Es / Fy)),
                          'in',
                          'Effective width of slender flange',
                          code_ref='AISC Eq. F7-4')

        Ired = CalcVariable('I_{red}', 2 * (b - be) * tdes * (h / 2) ** 2,
                            'in^4',
                            'Reduced area moment of inertia due to slender flange')

        Se = CalcVariable('S_e', Sx - 2 * Ired / Ht, 'in^3', 'Effective section modulus due to slender flange')

        Mnfb = CalcVariable('M_{nfb}', Fy * Se, 'kip-in', 'Nominal flexural capacity due to flange local buckling',
                            code_ref='AISC Eq. F7-3')

    BodyHeader('Web Local Buckling', head_level=2)
    ypw = CalcVariable('\lambda_{pw}', 2.42 * SQRT(Es / Fy), '', 'Compact limiting width-to-thickness ratio for webs',
                      code_ref='AISC Table B4.1b(19)')
    yrw = CalcVariable('\lambda_{rw}', 5.70 * SQRT(Es / Fy), '', 'Slender limiting width-to-thickness ratio for webs',
                      code_ref='AISC Table B4.1b(19)')

    if hlt.result() < ypw.result():
        CheckVariable(hlt, '<', ypw, truestate='Compact', falsestate='NonCompact', result_check=False)
        BodyText('For compact sections, web local buckling does not apply', code_ref='AISC Section F7.3(a)')
        Mnwb = CalcVariable('M_{nwb}', Mny, 'kip-in')

    elif hlt.result() < yrw.result():
        CheckVariable(hlt, '<', ypw, truestate='Compact', falsestate='NonCompact', result_check=False)
        CheckVariable(hlt, '<', yrw, truestate='NonCompact', falsestate='Slender', result_check=False)
        Mnwb = CalcVariable('M_{nwb}', Mny - BRACKETS(Mny - Fy * Sx) * BRACKETS(0.305 * hlt * SQRT(Fy / Es) - 0.738),
                            'kip-in',
                            'Nominal flexural capacity due to web local buckling',
                            code_ref='AISC Eq. F7-5')
    else:
        CheckVariable(hlt, '<', yrw, truestate='NonCompact', falsestate='Slender', result_check=True)
        Mnwb = CalcVariable('M_{nwb}', 0, 'kip-in', 'Slender webs are not allowed in flexure',
                            code_ref='AISC Eq. F7-3')

    BodyHeader('Member Demand vs. Capacity Check', head_level=2)
    Mn = CalcVariable('M_n', MIN(Mny, Mnfb, Mnwb), 'kip-in', 'Nominal controlling flexural capacity')
    PMn = CalcVariable('\phi M_n', Pf * Mn / ft_to_in, 'kip-ft', 'Design member flexural capacity', result_check=True)
    Mu = CalcVariable('M_u', Wu * L ** 2 / (8 * k_to_lb), 'kip-ft', 'Beam moment demand')
    CheckVariable(Mu, '<=', PMn, truestate="OK", falsestate="ERROR", result_check=True)

    BodyHeader('Member Deflection Check', head_level=2)
    dallow = CalcVariable('\delta_{allow}', L * ft_to_in / dlim, 'in')
    delastic = CalcVariable('\delta_{elastic}', 5 * Wu * L ** 4 * ft_to_in ** 3 / (384 * Es * Ix * k_to_lb), 'in')
    CheckVariable(delastic, '<=', dallow)

    return {
        'head': HeadCollection.head_instances,
        'assum': AssumCollection.assum_instances,
        'setup': SetupCollection.setup_instances,
        'calc': CalcCollection.calc_instances,
        'foot': FootCollection.foot_instances,
    }
