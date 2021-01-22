from application.calcscripts.process.basedefinitions import CalculationTitle, DescriptionHead, Assumption, CheckVariable, CheckVariablesText, \
        DeclareVariable, CalcVariable, BodyText, BodyHeader, HeadCollection, SetupCollection, CalcCollection, FootCollection, AssumCollection
from application.calcscripts.process.calcmodels import AlumShapesL, AlumShapesChannel, AlumShapesCircular, AlumShapesRectangular, AlumShapesWF
from application.calcscripts.process.listoptions import alum_wf_sizes, alum_angle_sizes
from application.calcscripts.process.latexExp import *


# STATUS: Development

def create_calculation(updated_input={}):
    HeadCollection.head_instances.clear()
    AssumCollection.assum_instances.clear()
    SetupCollection.setup_instances.clear()
    CalcCollection.calc_instances.clear()
    FootCollection.foot_instances.clear()




    ###   DEFINE TITLE, DESCRIPTION, ASSUMPTIONS, AND INPUTS   ###

    CalculationTitle('Stair Column and Brace Design to ADM 2015')

    DescriptionHead("Aluminum stair platform column and lateral brace design with weight, seismic base shear, and geometry. ")

    ##

    Assumption("Seismic loads and load combinations are in accordance with ASCE 7-16")
    Assumption("Requirements of OSHA 1910.25 and ANSI 1264.1 are met")
    Assumption("Aluminum members are designed in accordance with the Aluminum Design Manual (ADM) 2015 edition")
    Assumption("Stainless steel bolts are designed in accordance with AISC Design Guide 27 2013 edition")
    Assumption("Four columns are equally loaded below a generally square platform")
    Assumption("Columns are aluminum I beams and brace members are single angles")
    Assumption("Bracing is shaped as a Warren truss with each member equally spaced through the full column height")
    Assumption("Column design is governed by compression")
    Assumption("Angle braces are designed to support full lateral load")
    Assumption("Brace is bolted with a single bolt on the longer leg (if unequal)")
    # Assumption("Bolts are ASTM F593 304 SS and Nuts are ASTM F594 304 SS")
    Assumption("Members are unwelded")
    Assumption("Torsional section properties are calculated in accordance with the AISC Design Guide 9")


    Wd = DeclareVariable('W_d', 10, 'kips', 'Tributary dead load of platform')
    Wl = DeclareVariable('W_l', 3, 'kips', 'Tributary live load of platform')
    Vs = DeclareVariable('V_s', 4, 'kips', 'Design seismic base shear for platform')
    Vv = DeclareVariable('V_v', 1, 'kips', 'Design seismic vertical load for platform')

    wp = DeclareVariable('w_p', 5, 'ft', 'Width of platform (minimum)')
    hp = DeclareVariable('h_p', 10, 'ft', 'Height of platform column from base')
    Lbc = DeclareVariable('L_{bc}', 10, 'ft', 'Column unbraced length')
    Kc = DeclareVariable('k_{c}', 1, '', 'Column effective length factor')

    sizec = DeclareVariable('Section_{c}', 'I 8 x 7.02', '', 'Column section size', input_type='select', input_options=alum_wf_sizes )
    sizeb = DeclareVariable('Section_{b}', 'L 2 1/2 x 2 1/2 x 3/8', '', 'Brace section size', input_type='select', input_options=alum_angle_sizes )
    Numb = DeclareVariable('N_b', 4, '', 'Number of equal-length brace memebers')
    Dbb = DeclareVariable('D_{bb}', 5/8, 'in', 'Bolt diameter at brace connection' )
    Dbh = DeclareVariable('D_{bh}', 13/16, 'in', 'Bolt hole diameter at brace connection' )
    de = DeclareVariable('d_e', 3, 'in', 'Minimum distance from bolt center to end of connected member' )

    Ftu = DeclareVariable('F_{tu}', 38, 'ksi', 'Aluminum tensile ultimate strength', code_ref='ADM Table A.3.3')
    Fty = DeclareVariable('F_{ty}', 35, 'ksi', 'Aluminum tensile yield strength', code_ref = 'ADM Table A.3.3')
    Fcy = DeclareVariable('F_{cy}', 35, 'ksi', 'Aluminum compressive yield strength', code_ref='ADM Table A.3.1')
    Fbu = DeclareVariable('F_{bu}', 65, 'ksi', 'Bolt tensile ultimate strength', code_ref='DG27 Table 2-4')
    kt = DeclareVariable('k_t', 1, '', 'Tension coefficient', code_ref='ADM Table A.3.3')
    E = DeclareVariable('E', 10100, 'ksi', 'Modulus of Elasticity', code_ref='ADM Table A.3.1')
    G = DeclareVariable('G', 3800, 'ksi', 'Shear modulus of elasticity', code_ref='ADM Table A.3.1')

    Pc  = DeclareVariable('\phi_c', 0.9, '', 'Resistance factor for compression', code_ref='ADM E.1')
    Pty = DeclareVariable('\phi_{ty}', 0.9, '', 'Resistance factor for tensile yielding', code_ref='ADM D.1')
    Ptr = DeclareVariable('\phi_{tr}', 0.75, '', 'Resistance factor for tensile rupture', code_ref='ADM D.1')
    Pbs = DeclareVariable('\phi_{bs}', 0.75, '', 'Resistance factor for block shear', code_ref='ADM J.7.3')
    Pb  = DeclareVariable('\phi_b', 0.75, '', 'Resistance factor for bolt strength', code_ref='DG27 9.3.4')



    ###   DO NOT DEFINE INPUTS BELOW HERE OR EDIT THE FOLLOWING SECTION   ###

    if len(updated_input)>0:
        for input_variable in DeclareVariable.instances:
            new_value = updated_input.get(input_variable.name)
            if new_value:
                input_variable._set_value(new_value)

    ###   DEFINE CALCULATION, BODY HEADER, AND BODY TEXT   ###

    k_to_lb = Variable('1000 \ \mathrm{lbs/kip}', 1000, 'lbs/kip')
    ft_to_in = Variable('12 \ \mathrm{in/ft}', 12, 'in/ft')

    BodyHeader('Buckling Constants (ADM Table B.4.2)', head_level=1) ######################################################################################
    kap = CalcVariable('\kappa', 1.0, 'ksi')

    BodyHeader('Member buckling (Intercept, Slope, and Intersection):')
    Bc = CalcVariable('B_c', Fcy*BRACKETS(1+(Fcy/(2250*kap))**(1/2)), 'ksi')
    Dc = CalcVariable('D_c', Bc/10*(Bc/E)**(1/2), 'ksi')
    Cc = CalcVariable('C_c', 0.41*Bc/Dc)

    BodyHeader('Uniform compression in flat elements (Intercept, Slope, and Intersection):')
    Bp = CalcVariable('B_p', Fcy*BRACKETS(1+(Fcy/(1500*kap))**(1/3)), 'ksi')
    Dp = CalcVariable('D_p', Bp/10*(Bp/E)**(1/2), 'ksi')
    Cp = CalcVariable('C_p', 0.41*Bp/Dp)


    BodyHeader('Load demands on members', head_level=1)
    Fosha = CalcVariable(r'\beta_{osha}', 5, '', 'Design for 5 times the service loads for OSHA compliance')
    Bu = CalcVariable('B_{u}', Vs/2 * SQRT(wp**2 + (hp/Numb)**2)/wp*k_to_lb, 'lbs', 'Maximum compressive and tensile demand in brace element due to seismic forces' )

    Pu1 = CalcVariable('P_{u1}', 1.4*Wd/4*k_to_lb, 'lbs', 'Compression demand on each column due to dead load', code_ref='ASCE 2.3.1(1)' )
    Pu2 = CalcVariable('P_{u2}', BRACKETS(Wd/4+Fosha*Wl/4)*k_to_lb, 'lbs', 'Compression demand on each column due to dead and live load', code_ref='OSHA 19.25(b)(6)' )
    Pu6 = CalcVariable('P_{u6}', BRACKETS(1.2*Wd/4+Wl/4 + Vv/4 + Vs/2*(hp/wp))*k_to_lb, 'lbs', 'Maximum compression demand on a column due to dead, live, and seismic load', code_ref='ASCE 2.3.6(6)')

    Pu = CalcVariable('P_{u}', MAX(Pu1, Pu2, Pu6), 'lbs', 'Design compression demand on column elements')

    BodyHeader('Column Member Design', head_level=1)
    BodyHeader('Section properties')
    sectionc = AlumShapesWF.objects(Size=sizec.value).first()
    Ac = CalcVariable('A_{c}', sectionc.A, 'in^2')
    bc = CalcVariable('b_{fc}', sectionc.bf, 'in')
    tfc = CalcVariable('t_{fc}', sectionc.tf, 'in')
    twc = CalcVariable('t_{wc}', sectionc.tw, 'in')
    Rc = CalcVariable('R_{c}', sectionc.R1, 'in')
    Ixc = CalcVariable('I_{xc}', sectionc.Ix, 'in^4')
    Iyc = CalcVariable('I_{yc}', sectionc.Iy, 'in^4')
    ryc = CalcVariable('r_{yc}', sectionc.ry, 'in')
    Cwc = CalcVariable('C_{wc}', sectionc.Cw, 'in^6')
    Jc = CalcVariable('J_{c}', sectionc.J, 'in^4')


    BodyHeader('Column Compression Design (ADM Chapter E)', head_level=2) ######################################################################################

    BodyHeader('Member Buckling (ADM E.2)')
    y1c = CalcVariable('\lambda_{1c}', (Bc-Fcy)/Dc, '')
    ycf = CalcVariable('\lambda_{cf}', Kc * Lbc * ft_to_in / ryc, '', 'Member slenderness ratio for flexural buckling', code_ref='ADM E.2.1')
    Fec = CalcVariable('F_{ec}', BRACKETS(PI**2*E*Cwc/(Kc*Lbc*ft_to_in)**2+G*Jc)/(Ixc+Iyc), 'ksi', 'Elastic buckling stress for torsional buckling', code_ref='ADM E.2-4'  )
    yct = CalcVariable('\lambda_{ct}', PI*SQRT(E/Fec), '', 'Member slenderness ratio for torsional buckling', code_ref='ADM E.2-3')

    yc = CalcVariable('\lambda_{c}', MAX(ycf, yct), '', 'Greatest compression member slenderness', code_ref='ADM E.2')

    if yc.result() <= y1c.result():
        CheckVariablesText(yc, '<=', y1c)
        BodyText('Member yielding controls')
        Fcc = CalcVariable('F_{cc}', Fcy, 'ksi', code_ref='ADM E.2')
    elif yc.result() < Cc.result():
        CheckVariablesText(y1c, '<', yc, '<', Cc)
        BodyText('Inelastic buckling controls')
        Fcc = CalcVariable('F_{cc}', BRACKETS(Bc-Dc*yc)*BRACKETS(0.85+0.15*(Cc-yc)/(Cc-y1c)), 'ksi', code_ref='ADM E.2')
    else:
        CheckVariablesText( yc, '>=', Cc)
        BodyText('Elastic buckling controls')
        Fcc = CalcVariable('F_{cc}', 0.85*PI**2*E/yc**2, 'ksi', code_ref='ADM E.2')
    PPncm = CalcVariable('\phi P_{ncm}', Pc*Fcc*Ac*k_to_lb , 'lbs', 'Member buckling strength', code_ref='ADM E.2-1')

    BodyHeader('Local Buckling (ADM E.3)')
    k1c = CalcVariable('k_{1c}', 0.35, '', code_ref='ADM Table B.4.3') # assume temper T6
    k2c = CalcVariable('k_{2c}', 2.27, '', code_ref='ADM Table B.4.3')
    y1e = CalcVariable('\lambda_{1e}', (Bp-Fcy)/Dp, '')
    y2e = CalcVariable('\lambda_{2e}', k1c*Bp/Dp, '')
    Fee = CalcVariable('F_{ee}', PI**2*E/(5*BRACKETS((bc-twc)/2-Rc)/tfc)**2, 'ksi', code_ref='ADM Table B.5.1')
    yeq = CalcVariable('\lambda_{eq}', PI*SQRT(E/Fee), '', code_ref='ADM B.5-11')

    if yeq.result() <= y1e.result():
        CheckVariablesText(yeq, '<=', y1e)
        BodyText('Member yielding controls')
        Fcec = CalcVariable('F_{cec}', Fcy, 'ksi', code_ref='ADM B.5.4.6')
    elif yeq.result() < y2e.result():
        CheckVariablesText(y1e, '<=', yeq, '<', y2e)
        BodyText('Inelastic buckling controls')
        Fcec = CalcVariable('F_{cec}', Bp-Dp*yeq , 'ksi', code_ref='ADM B.5.4.6')
    else:
        CheckVariablesText(yeq, '>=', y2e)
        BodyText('Elastic buckling controls')
        Fcec = CalcVariable('F_{cec}', k2c*SQRT(Bp*E)/yeq, 'ksi', code_ref='ADM B.5.4.6')
    PPnce = CalcVariable('\phi P_{nce}', Pc*Fcec*Ac*k_to_lb , 'lbs', 'Member local buckling strength', code_ref='ADM E.3-2')

    PPnc = CalcVariable('\phi P_{nc}', MIN(PPncm, PPnce), 'lbs', 'Member compressive strength')
    CheckVariable( Pu, '<=', PPnc, truestate="OK", falsestate="ERROR", result_check=True)

    BodyHeader('Brace Member Design', head_level=1)
    BodyHeader('Section properties')
    sectionb = AlumShapesL.objects(Size=sizeb.value).first()
    Ab = CalcVariable('A_{b}', sectionb.A, 'in^2')
    tb = CalcVariable('t_{b}', sectionb.t, 'in')
    bb = CalcVariable('b_{b}', sectionb.b, 'in')
    db = CalcVariable('d_{b}', sectionb.d, 'in')
    Ibx = CalcVariable('I_{bx}', sectionb.Ix, 'in^4')
    rbx = CalcVariable('r_{bx}', sectionb.rx, 'in')
    xob = CalcVariable('x_{ob}', sectionb.x, 'in')
    Iby = CalcVariable('I_{by}', sectionb.Iy, 'in^4')
    rby = CalcVariable('r_{by}', sectionb.ry, 'in')
    yob = CalcVariable('y_{ob}', sectionb.y, 'in')
    Ibz = CalcVariable('I_{bz}', sectionb.Iz, 'in^4')
    rbz = CalcVariable('r_{bz}', sectionb.rz, 'in')
    Rb = CalcVariable('R_b', sectionb.R1, 'in' )
    rbmin = CalcVariable('r_{bmin}', MIN(rbx, rby, rbz), 'in')



    BodyHeader('Brace Tensile Design (ADM Chapter D)', head_level=2) ######################################################################################
    PPbty = CalcVariable('\phi P_{bty}', Pty*Fty*Ab*k_to_lb, 'lbs', 'Tensile yielding capacity of gross member', code_ref='ADM D.2-1' )
    Abn = CalcVariable('A_{bn}', Ab-Dbh*tb , 'in^2', 'Net area of brace at connection')
    Abe = CalcVariable('A_{be}', Abn*1, 'in^2', 'Effective net area of brace at connection', code_ref='ADM D.3-1')
    PPbtr = CalcVariable('\phi P_{btr}', Ptr*Ftu*Abe/kt*k_to_lb, 'lbs', 'Tensile rupture capacity of member net section', code_ref='ADM D.2-1' )
    PPbt = CalcVariable('\phi P_{bt}', MIN(PPbty, PPbtr), 'lbs', 'Member tensile strength')
    CheckVariable( Bu, '<=', PPbt, truestate="OK", falsestate="ERROR", result_check=True)


    BodyHeader('Brace Compression Design (ADM Chapter E)', head_level=2) ######################################################################################

    BodyHeader('Member Buckling (ADM E.2)')
    Lbb = CalcVariable('L_{bb}', SQRT(wp**2 + (hp/Numb)**2), 'ft', 'Length of brace member')
    Kb = CalcVariable('K_b', 1.0, '', 'Brace member effective length factor')
    ybf = CalcVariable('\lambda_{cf}', Kb * Lbb * ft_to_in / rbmin, '', 'Member slenderness ratio for flexural buckling', code_ref='ADM E.2.1')

    if db.result() != bb.result():
        BodyText('Torsional buckling design will apply the singly symmetric method of ADM Section E.2.2(b) with the conservative modification of treating the section as an equal leg angle of the smaller leg.')

    bbmin = CalcVariable('b_{bmin}', MIN(bb,db), 'in')
    Ibmin = CalcVariable('I_{bmin}', MIN(Ibx,Iby), 'in^4')
    xobmin = CalcVariable('x_{bmin}', MIN(xob,yob), 'in')

    rob2 = CalcVariable('r_{ob}^2', 2*xobmin**2+2*Ibmin/(tb*BRACKETS(2*bbmin-tb)), 'in^2', 'Polar radius of gyration about the shear center (squared)', code_ref='ADM E.2-7')
    Hb = CalcVariable('H_b', 1 - (2*xobmin**2)/rob2, '', code_ref='ADM E.2-8')
    Ibxy = CalcVariable('I_{bxy}', tb**2/4*BRACKETS(2*bbmin**2-tb**2)-xobmin**2*tb*BRACKETS(2*bbmin-tb), 'in^4', 'Product of inertia')
    Iyp = CalcVariable('I_{byp}', Ibmin + ABS(Ibxy), 'in^4', 'Principal moment of inertia (axis of symmetry)')
    ryp = CalcVariable('r_{byp}', SQRT(Iyp/Ab), 'in')
    Jb = CalcVariable('J_b', 2*bbmin*tb**3/3, 'in^4', code_ref='DG9 Eq. 3.4')
    Cwb = CalcVariable('C_{wb}', 2*tb**3/36*(bbmin-tb/2)**3, 'in^6', code_ref='DG9 Eq. 3.34')

    Feyp = CalcVariable('F_{eyp}', PI**2*E/(Kb*Lbb*ft_to_in/ryp)**2, 'ksi', 'Elastic buckling strength about axis of symmetry', code_ref='ADM E.2-10')
    Fez  = CalcVariable('F_{ez}', ONE/(Ab*rob2)*BRACKETS(G*Jb + PI**2*E*Cwb/(Kb*Lbb*ft_to_in)**2), 'ksi', code_ref='ADM E.2-11')

    Feb = CalcVariable('F_{eb}', (Feyp + Fez)/(2*Hb)*BRACKETS(1-SQRT(1- 4*Feyp*Fez*Hb/(Feyp + Fez)**2)) , 'ksi', 'Elastic buckling stress for torsional buckling', code_ref='ADM E.2-5'  )
    ybt = CalcVariable('\lambda_{bt}', PI*SQRT(E/Feb), '', 'Member slenderness ratio for torsional buckling', code_ref='ADM E.2-3')

    ycb = CalcVariable('\lambda_{cb}', MAX(ybf, ybt), '', 'Greatest compression member slenderness', code_ref='ADM E.2')

    if ycb.result() <= y1c.result():
        CheckVariablesText(ycb, '<=', y1c)
        BodyText('Member yielding controls')
        Fcb = CalcVariable('F_{cb}', Fcy, 'ksi', code_ref='ADM E.2')
    elif ycb.result() < Cc.result():
        CheckVariablesText(y1c, '<', ycb, '<', Cc)
        BodyText('Inelastic buckling controls')
        Fcb = CalcVariable('F_{cb}', BRACKETS(Bc-Dc*ycb)*BRACKETS(0.85+0.15*(Cc-ycb)/(Cc-y1c)), 'ksi', code_ref='ADM E.2')
    else:
        CheckVariablesText( ycb, '>=', Cc)
        BodyText('Elastic buckling controls')
        Fcb = CalcVariable('F_{cb}', 0.85*PI**2*E/ycb**2, 'ksi', code_ref='ADM E.2')
    PPnbm = CalcVariable('\phi P_{nbm}', Pc*Fcb*Ab*k_to_lb , 'lbs', 'Member buckling strength', code_ref='ADM E.2-1')


    BodyHeader('Local Buckling (ADM E.3)')
    bbmax = CalcVariable('b_{bmax}', MAX(bb,db), 'in')
    Feeb = CalcVariable('F_{eeb}', PI**2*E/(5*BRACKETS(bbmax-tb-Rb)/tb)**2, 'ksi', code_ref='ADM Table B.5.1')
    yeqb = CalcVariable('\lambda_{eqb}', PI*SQRT(E/Feeb), '', code_ref='ADM B.5-11')

    if yeqb.result() <= y1e.result():
        CheckVariablesText(yeqb, '<=', y1e)
        BodyText('Member yielding controls')
        Fceb = CalcVariable('F_{ceb}', Fcy, 'ksi', code_ref='ADM B.5.4.6')
    elif yeqb.result() < y2e.result():
        CheckVariablesText(y1e, '<=', yeqb, '<', y2e)
        BodyText('Inelastic buckling controls')
        Fceb = CalcVariable('F_{ceb}', Bp-Dp*yeqb , 'ksi', code_ref='ADM B.5.4.6')
    else:
        CheckVariablesText(yeqb, '>=', y2e)
        BodyText('Elastic buckling controls')
        Fceb = CalcVariable('F_{ceb}', k2c*SQRT(Bp*E)/yeqb, 'ksi', code_ref='ADM B.5.4.6')
    PPnbe = CalcVariable('\phi P_{nbe}', Pc*Fceb*Ab*k_to_lb , 'lbs', 'Member local buckling strength', code_ref='ADM E.3-2')

    PPnb = CalcVariable('\phi P_{nb}', MIN(PPnbm, PPnbe), 'lbs', 'Member compressive strength')
    CheckVariable( Bu, '<=', PPnb, truestate="OK", falsestate="ERROR", result_check=True)


    BodyHeader('Brace Connection Design (ADM Chapter J)', head_level=2) ######################################################################################

    BodyHeader('Bearing Strength (ADM Section J.3.6)')
    Rn1 = CalcVariable('R_{n1}', de*tb*Ftu*k_to_lb, 'lbs', '')
    Rn2 = CalcVariable('R_{n2}', 2*Dbb*tb*Ftu*k_to_lb, 'lbs', '')
    PRnb = CalcVariable('\phi R_{nb}', Pb*MIN(Rn1, Rn2), 'lbs', 'Bolt bearing strength', code_ref='ADM J.3-4')
    CheckVariable( Bu, '<=', PRnb, truestate="OK", falsestate="ERROR", result_check=True)

    BodyHeader('Block Shear Strength (ADM Section J.7.3)')
    Agt = CalcVariable('A_{gt}', bbmin/2*tb , 'in^2', 'Gross tensile area of brace connection' )
    Agv = CalcVariable('A_{gv}', de*tb , 'in^2', 'Gross shear area of brace connection' )
    Ant = CalcVariable('A_{nt}', Agt - Dbh*tb/2, 'in^2')
    Anv = CalcVariable('A_{nv}', Agv - Dbh*tb/2, 'in^2')
    Fsy = CalcVariable('F_{sy}', 0.6*Fty, 'ksi', code_ref='ADM Table A.3.1')
    Fsu = CalcVariable('F_{su}', 0.6*Ftu, 'ksi', code_ref='ADM Table A.3.1')

    Anv6 = CalcVariable('0.6 \ A_{nv}', 0.6*Anv, 'in^2')

    if Ant.result() >= 0.6 * Anv.result():
        CheckVariablesText(Ant, '>=', Anv6)
        Rns = CalcVariable('R_{ns}', Fsy*Agv + Ftu*Ant/kt , 'kips', code_ref='ADM J.7-1')
    else:
        CheckVariablesText(Ant, '<', Anv6)
        Rns = CalcVariable('R_{ns}', Fsu*Anv/kt + Fty*Agt, 'kips', code_ref='ADM J.7-2')
    PRns = CalcVariable('\phi R_{ns}', Pbs*Rns * k_to_lb, 'lbs', 'Block shear strength' )
    CheckVariable( Bu, '<=', PRns, truestate="OK", falsestate="ERROR", result_check=True)


    BodyHeader('Bolt Strength Design (DG27 Chapter 9)', head_level=2) ######################################################################################
    Fnv = CalcVariable('F_{nv}', 0.45*Fbu, 'ksi', 'Bolt nominal shear strength assuming threads are not excluded from the shear plane' )
    PRn = CalcVariable('\phi R_n', Pb*Fnv*PI*(Dbb/2)**2*k_to_lb, 'lbs', 'Bolt shear strength')
    CheckVariable( Bu, '<=', PRn, truestate="OK", falsestate="ERROR", result_check=True)



    calculation_sum = {'head':HeadCollection.head_instances, 'assum': AssumCollection.assum_instances, 'setup':SetupCollection.setup_instances, 'calc':CalcCollection.calc_instances, 'foot':FootCollection.foot_instances}
    return calculation_sum
