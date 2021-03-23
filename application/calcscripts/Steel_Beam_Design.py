from application.calcscripts.process.basedefinitions import CalculationTitle, DescriptionHead, Assumption, CheckVariable, \
        DeclareVariable, CalcVariable, BodyText, BodyHeader, HeadCollection, SetupCollection, CalcCollection, FootCollection, AssumCollection
from application.calcscripts.process.calcmodels import AISCSectionsWF
from application.calcscripts.process.listoptions import wf_section_sizes
from application.calcscripts.process.latexExp import *


# STATUS: Completed, Production Ready

def create_calculation(updated_input={}):
    HeadCollection.head_instances.clear()
    AssumCollection.assum_instances.clear()
    SetupCollection.setup_instances.clear()
    CalcCollection.calc_instances.clear()
    FootCollection.foot_instances.clear()




    ###   DEFINE TITLE, DESCRIPTION, ASSUMPTIONS, AND INPUTS   ###

    CalculationTitle('Simply Supported Beam Design')

    DescriptionHead("With beam loading demands, span, section size, and deflection requirements design a simply supported beam using the AISC Manual")

    ##

    Assumption("AISC 14th Edition controls design")
    Assumption("Beam is subject to only Dead and Live loads")
    Assumption("ASCE 7-16 gravity load combinations control design")
    # Assumption("Beam is fully braced along it's length")
    Assumption("Beam section is compact for flexure")
    Assumption("Uniform loads are constant along the entire length")
    Assumption("Beam web is unstiffened")

    wud = DeclareVariable('W_{ud}', 1.8, 'kips/ft', 'Uniform Dead Load' )
    wul = DeclareVariable('W_{ul}', 1.5, 'kips/ft', 'Uniform Live Load' )
    Lb = DeclareVariable('L', 20, 'ft', 'Beam span')
    Lbu = DeclareVariable('L_b', 20, 'ft', 'Beam unbraced length')
    section = DeclareVariable('Section', 'W18X35', '', 'Beam section size', input_type='select', input_options=wf_section_sizes )
    dliml = DeclareVariable('X_{lim,l}', 360, '', 'Member deflection limit under live loads (L/X)')
    dlim = DeclareVariable('X_{lim}', 240, '', 'Member deflection limit under all loads (L/X)')

    Fy = DeclareVariable('F_{y}', 50, 'ksi', 'Steel yield strength')
    Fu = DeclareVariable('F_{u}', 65, 'ksi', 'Steel ultimate strength')
    E = DeclareVariable('E', 29000, 'ksi', 'Modulus of Elasticity')

    Cb = DeclareVariable('C_b', 1.0, '', 'Lateral-torsional buckling modification factor', code_ref='AISC F1(3)')



    ###   DO NOT DEFINE INPUTS BELOW HERE OR EDIT THE FOLLOWING SECTION   ###

    if len(updated_input)>0:
        for input_variable in DeclareVariable.instances:
            new_value = updated_input.get(input_variable.name)
            if new_value:
                input_variable._set_value(new_value)

    ###   DEFINE CALCULATION, BODY HEADER, AND BODY TEXT   ###

    k_to_lb = Variable('1000 \ \mathrm{lbs/kip}', 1000, 'lbs/kip')
    ft_to_in = Variable('12 \ \mathrm{in/ft}', 12, 'in/ft')


    BodyHeader('Beam Section Properties', head_level=1)
    sectionb = AISCSectionsWF.objects(Size=section.value).first()
    b = CalcVariable('b', sectionb.bf, 'in')
    d = CalcVariable('d', sectionb.d, 'in')
    tf = CalcVariable('t_f', sectionb.tf, 'in')
    tw = CalcVariable('t_w', sectionb.tw, 'in')
    Ix = CalcVariable('I_x', sectionb.Ix, 'in^4')
    Sx = CalcVariable('S_x', sectionb.Sx, 'in^3')
    Zx = CalcVariable('Z_x', sectionb.Zx, 'in^3')
    ry = CalcVariable('r_{y}', sectionb.ry, 'in')
    rts = CalcVariable('r_{ts}', sectionb.rts, 'in')
    J = CalcVariable('J', sectionb.J, 'in^4')
    ho = CalcVariable('h_o', sectionb.ho, 'in')
    bfl2tf = CalcVariable('b_f/2t_f', sectionb.bfl2tf, '')
    hltw = CalcVariable('h/t_w', sectionb.hltw, '')


    BodyHeader('Member Deflection', head_level=1)
    BodyHeader('Live load deflection', head_level=2)
    dallowl = CalcVariable('\delta_{allow,l}', Lb*ft_to_in/dliml, 'in')
    delasticl = CalcVariable('\delta_{elastic,l}', 5*wul*Lb**4*ft_to_in**3/(384*E*Ix), 'in')
    CheckVariable( delasticl, '<=', dallowl)

    BodyHeader('Combined load deflection', head_level=2)
    dallow = CalcVariable('\delta_{allow}', Lb*ft_to_in/dlim, 'in')
    delastic = CalcVariable('\delta_{elasticl}', 5*BRACKETS(wul+wud)*Lb**4*ft_to_in**3/(384*E*Ix), 'in')
    CheckVariable( delastic, '<=', dallow)


    BodyHeader('Ultimate Load Demands', head_level=1)
    BodyHeader('ASCE Load Combinations', head_level=2)
    Wu1 = CalcVariable('W_{u1}', 1.4*wud, 'kips/ft', code_ref='ASCE 2.3.1(1)')
    Wu2 = CalcVariable('W_{u2}', 1.2*wud+1.6*wul, 'kips/ft', code_ref='ASCE 2.3.1(2)')
    Wu = CalcVariable('W_u', MAX(Wu1, Wu2), 'Controlling load combination')

    BodyHeader('Beam Section Demands', head_level=2)
    Vu = CalcVariable('V_u', Wu*Lb/2, 'kips', 'Beam shear demand')
    Mu = CalcVariable('M_u', Wu*Lb**2/8, 'kip-ft', 'Beam moment demand')


    BodyHeader('Beam Shear Capacity', head_level=1)
    yv = CalcVariable('\lambda_{v}', 2.24*SQRT(E/Fy), '', 'I-shaped member web slenderness factor', code_ref='AISC G2.1(a)')
    if hltw.result() <= yv.result():
        CheckVariablesText(hltw, '<=', yv)
        Pv = CalcVariable('\phi_{v}', 1.0, '', 'Shear resistance factor', code_ref='AISC G2.1(a)')
        Cv = CalcVariable('C_v', 1.0, '', 'Web shear factor', code_ref='AISC Eq. G2-2')

    else:
        CheckVariablesText(hltw, '>', yv)
        Pv = CalcVariable('\phi_{v}', 0.9, '', 'Shear resistance factor', code_ref='AISC G1')
        if hltw.result() > 260:
            hltlim = CalcVariable('h/t_{wlim}', 260, '')
            c1 = CheckVariable( hltw, '<', hltlim, code_ref='AISC G2.1(b)(i)')
            Cv = CalcVariable('C_v', 0.0, '', 'Web shear factor')
        else:
            kv = CalcVariable('k_v', 5, '', code_ref='AISC G2.1(i)')

            yv1 = CalcVariable('\lambda_{v1}', 1.10*SQRT(kv*E/Fy), '', 'Alternative member web compactness factor', code_ref='AISC G2.1(b)(i)')
            yv2 = CalcVariable('\lambda_{v2}', 1.37*SQRT(kv*E/Fy), '', 'Alternative member web slenderness factor', code_ref='AISC G2.1(b)(iii)')

            if hltw.result() <= yv1.result():
                CheckVariablesText(hltw, '<=', yv1)
                Cv = CalcVariable('C_v', 1.0, '', 'Web shear factor', code_ref='AISC Eq. G2-3')
            elif hltw.result() > yv2.result():
                CheckVariablesText(hltw, '>', yv2)
                Cv = CalcVariable('C_v', 1.51*kv*E/(hltw**2*Fy), '', 'Web shear factor', code_ref='AISC Eq. G2-5')
            else:
                CheckVariablesText(yv1, '<', hltw, '<=', yv2)
                Cv = CalcVariable('C_v', 1.10*SQRT(kv*E/Fy)/hltw, '', 'Web shear factor', code_ref='AISC Eq. G2-4')

    Aw = CalcVariable('A_w', d*tw, 'in^2', 'Area of web considered for shear resistance')
    PVn = CalcVariable('\phi V_n', Pv*0.6*Fy*Aw*Cv, 'kips', 'Design shear strength of the section', code_ref='AISC Eq. G2-1')
    CheckVariable(Pu, '<=', PVn)


    BodyHeader('Beam Flexural Capacity', head_level=1)
    Pb = CalcVariable('\phi_{b}', 0.9, '', 'Flexural resistance factor', code_ref='AISC F1(1)')

    BodyHeader('Section Compactness', head_level=2)
    ypf = CalcVariable('\lambda_{pf}', 0.38*SQRT(E/Fy), '', code_ref='AISC Table B4.1b(10)')
    CheckVariable(bfl2tf, '<=', ypf, truestate="Flange is compact", falsestate="ERROR:Flange is not compact", result_check=False)

    ypw = CalcVariable('\lambda_{pw}', 3.76*SQRT(E/Fy), '', code_ref='AISC Table B4.1b(15)')
    CheckVariable(hltw, '<=', ypw, truestate="Web is compact", falsestate="ERROR:Web is not compact", result_check=False)

    BodyHeader('Plastic Moment Strength', head_level=2)
    Mp = CalcVariable('M_{p}', Fy*Zx/ft_to_in, 'kip-ft', 'nominal plastic moment strength', code_ref='AISC Eq. F2-1')

    BodyHeader('Yielding Strength', head_level=2)
    Mny = CalcVariable('M_{ny}', Mp, 'kip-ft', code_ref='AISC Eq. F2-1')

    BodyHeader('Lateral-Torsional Buckling', head_level=2)
    Lp = CalcVariable('L_{p}', 1.76*ry*SQRT(E/Fy)/ft_to_in, 'ft', code_ref='AISC Eq. F2-5')
    cc = CalcVariable('c', 1.0, '', code_ref='AISC Eq. F2-8a')
    Lr = CalcVariable('L_{r}', 1.95*rts/ft_to_in*E/(0.7*Fy)*SQRT(J*cc/(Sx*ho) + SQRT((J*cc/(Sx*ho))**2 + 6.76*(0.7*Fy/E)**2)), 'ft', code_ref='AISC Eq. F2-6')

    if Lbu.result() <= Lp.result():
        CheckVariablesText(Lbu, "<=", Lp)
        Mnl = CalcVariable('M_{nltb}', Mp, 'kip-ft', 'The limit state of lateral-torsional buckling does not apply', code_ref='AISC F2.2(a)')
    elif Lbu.result() > Lr.result():
        CheckVariablesText(Lbu, ">", Lr)
        Fcr = CalcVariable('F_{cr}', Cb*PI**2*E/(Lbu*ft_to_in/rts)**2 + SQRT(1 + 0.078*J*cc/(Sx*ho)*(Lbu*ft_to_in/rts)**2), 'ksi', code_ref='AISC Eq. F2-4')
        Mncr = CalcVariable('M_{ncr}', Fcr*Sx/ft_to_in, 'kip-ft', code_ref='AISC F2.2(c)')
        Mnl = CalcVariable('M_{nltb}', MIN(Mncr, Mp), 'kip-ft', code_ref='AISC Eq. F2-3')
    else:
        CheckVariablesText(Lp, '<', Lbu, "<=", Lr)
        Mncr = CalcVariable('M_{ncr}', Cb*BRACKETS(Mp - BRACKETS(Mp-0.7*Fy*Sx/ft_to_in)*(Lbu-Lp)/(Lr-Lp)) , 'kip-ft', code_ref='AISC F2.2(b)')
        Mnl = CalcVariable('M_{nltb}', MIN(Mncr, Mp), 'kip-ft', code_ref='AISC Eq. F2-2')

    BodyHeader('Controlling Strength', head_level=2)
    PMn = CalcVariable('\phi M_n', Pb * MIN(Mny, Mnl), 'kip-ft', 'Design flexural strength of the section')
    CheckVariable(Mu, '<=', PMn)


    calculation_sum = {'head':HeadCollection.head_instances, 'assum': AssumCollection.assum_instances, 'setup':SetupCollection.setup_instances, 'calc':CalcCollection.calc_instances, 'foot':FootCollection.foot_instances}
    return calculation_sum
