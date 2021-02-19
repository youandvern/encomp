from application.calcscripts.process.basedefinitions import CalculationTitle, DescriptionHead, Assumption, CheckVariable, CheckVariablesText, \
        DeclareVariable, CalcVariable, BodyText, BodyHeader, HeadCollection, SetupCollection, CalcCollection, FootCollection, AssumCollection
from application.calcscripts.process.calcmodels import AlumShapesL, AlumShapesChannel, AlumShapesCircular, AlumShapesRectangular, AlumShapesWF
from application.calcscripts.process.listoptions import alum_channel_sizes, alum_rectangular_sizes, alum_angle_sizes
from application.calcscripts.process.latexExp import *

# STATUS: Completed, Production Ready
def create_calculation(updated_input={}):
    HeadCollection.head_instances.clear()
    AssumCollection.assum_instances.clear()
    SetupCollection.setup_instances.clear()
    CalcCollection.calc_instances.clear()
    FootCollection.foot_instances.clear()




    ###   DEFINE TITLE, DESCRIPTION, ASSUMPTIONS, AND INPUTS   ###

    CalculationTitle('Aluminum Stair Design')

    DescriptionHead("Aluminum stairs designed in accordance with the Aluminum Design Manual.")

    ## SEE WOODBRIDGE CT. DESIGN DRAWINGS FOR GEOMETRY ASSUMPTIONS OF STAIR

    Assumption("Aluminum Design Manual (ADM) 2015 version controls member design")
    Assumption("All aluminum sections share the same mechanical properties")
    Assumption("Temper requirements of ADM Table B.4.2 are met")
    Assumption("Cross sections are all unwelded")
    Assumption("Requirements of OSHA 1910.25 and ANSI 1264.1 are met")

    LL = DeclareVariable('LL', 40, 'psf', 'Live load on stairs (ASCE 7-16 Table 4.3-1)')
    LC = DeclareVariable('LL_c', 300, 'lbs', 'Concentrated load on stair elements (ASCE 7-16 Table 4.3-1)')
    DL = DeclareVariable('DL', 10, 'psf', 'Dead load of grating and misc.')
    Wtr = DeclareVariable('W_{tr}', 2.5, 'ft', 'Stair tread width')

    Wtp = DeclareVariable('W_{tp}', 6, 'ft', 'Width of top platform (perpendicular to stringer)')
    Ltp = DeclareVariable('L_{tp}', 5.5, 'ft', 'Length of top platform (parallel to stringer)')


    Ftu = DeclareVariable('F_{tu}', 38, 'ksi', 'Tensile ultimate strength', code_ref='ADM Table A.3.3')
    Fty = DeclareVariable('F_{ty}', 35, 'ksi', 'Tensile yield strength', code_ref = 'ADM Table A.3.3')
    Fcy = DeclareVariable('F_{cy}', 35, 'ksi', 'Compressive yield strength', code_ref='ADM Table A.3.1')
    kt = DeclareVariable('k_t', 1, '', 'Tension coefficient', code_ref='ADM Table A.3.3')
    E = DeclareVariable('E', 10100, 'ksi', 'Modulus of Elasticity', code_ref='ADM Table A.3.1')
    G = DeclareVariable('G', 3800, 'ksi', 'Shear modulus of elasticity', code_ref='ADM Table A.3.1')

    Pby = DeclareVariable('\phi_{by}', 0.9, '', 'Flexural resistance factor for yielding', code_ref='ADM F.1')
    Pbr = DeclareVariable('\phi_{br}', 0.75, '', 'Flexural resistance factor for rupture', code_ref='ADM F.1')
    Pc  = DeclareVariable('\phi_c', 0.9, '', 'Resistance factor for compression', code_ref='ADM E.1')
    dlim = DeclareVariable('X_{lim}', 360, '', 'Member deflection limit (L/X)')

    sizesc = DeclareVariable('Section_{sc}', 'C 8 X 4.25', '', 'Stair stringer channel section size', input_type='select', input_options=alum_channel_sizes )
    Ksc = DeclareVariable('k_{sc}', 1, '', 'Stair stringer effective length factor')
    Lsc = DeclareVariable('L_{usc}', 12.75, 'ft', 'Unsupported length of stair stringer')
    Lbsc = DeclareVariable('L_{bsc}', 12.75, 'ft', 'Unbraced length of stair stringer')
    asc = DeclareVariable(r'\alpha _{sc}', 45, 'deg', 'Angle of stringer from horizon' )

    sizepc = DeclareVariable('Section_{pc}', 'C 8 X 4.25', '', 'Platform channel section size', input_type='select', input_options=alum_channel_sizes )
    sizepr = DeclareVariable('Section_{pr}', 'RT 8 x 3 x 1/4', '', 'Platform rectangular tube section size', input_type='select', input_options=alum_rectangular_sizes )

    LLHR = DeclareVariable('LL_{hr}', 200, 'lbs', 'Maximum load on handrail post')
    HHR = DeclareVariable('h_{hr}', 42, 'in', 'Height of handrail')


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

    BodyHeader('Shear in flat elements (Intercept, Slope, and Intersection):')
    Fsy = CalcVariable('F_{sy}', 0.6*Fty, 'ksi', code_ref="ADM Table A.3.1")
    Fsu = CalcVariable('F_{su}', 0.6*Ftu, 'ksi', code_ref="ADM Table A.3.1")
    Bs = CalcVariable('B_s', Fsy*BRACKETS(1+(Fsy/(800*kap))**(1/3)), 'ksi')
    Ds = CalcVariable('D_s', Bs/10*(Bs/E)**(1/2), 'ksi')
    Cs = CalcVariable('C_s', 0.41*Bs/Ds)


    BodyHeader('Stair Stringer Design', head_level=1)
    BodyHeader('Section properties')
    sectionsc = AlumShapesChannel.objects(Size=sizesc.value).first()
    twsc = CalcVariable('t_{wsc}', sectionsc.tw, 'in')
    tfsc = CalcVariable('t_{fsc}', sectionsc.tf, 'in')
    bsc = CalcVariable('b_{sc}', sectionsc.b, 'in')
    dsc = CalcVariable('d_{sc}', sectionsc.d, 'in')
    Rsc = CalcVariable('R_{sc}', sectionsc.R1, 'in')
    wswsc = CalcVariable('SW_{sc}', sectionsc.W,'lbs/ft')
    Asc = CalcVariable('A_{sc}', sectionsc.A, 'in^2')
    Ssc = CalcVariable('S_{xsc}', sectionsc.Sx, 'in^3')
    Zsc = CalcVariable('Z_{xsc}', sectionsc.b*sectionsc.d**2/4-(sectionsc.b-sectionsc.tw)*(sectionsc.d-2*sectionsc.tf)**2/4, 'in^3') # Z for channel shape
    Ixsc = CalcVariable('I_{xsc}', sectionsc.Ix, 'in^4')
    rxsc = CalcVariable('r_{xsc}', sectionsc.rx, 'in')
    Iysc = CalcVariable('I_{ysc}', sectionsc.Iy, 'in^4')
    rysc = CalcVariable('r_{ysc}', sectionsc.ry, 'in')
    xsc = CalcVariable('x_{sc}', sectionsc.x, 'in')
    exsc = CalcVariable('e_{xsc}', 3*tfsc*(bsc-twsc/2)**2/(BRACKETS(dsc-tfsc)*twsc+6*BRACKETS(bsc-twsc/2)*tfsc), 'in', 'Shear center measured from web centerline' ) # for channel shape from CERM
    x0sc = CalcVariable('x_{0sc}', exsc + xsc - twsc/2, 'in')
    y0sc = CalcVariable('y_{0sc}', 0, 'in')
    Jsc = CalcVariable('J_{sc}', Ixsc+Iysc, 'in^4')
    Cwsc = CalcVariable('C_{wsc}', (1/6)*(dsc-tfsc)**2*(bsc-twsc/2)**2*tfsc*BRACKETS(bsc-twsc/2-3*exsc)+exsc**2*Ixsc,'in^6') # for channel shape per AISC Design Guide 9


    BodyHeader('Stair Stringer Load Demands', head_level=2) ######################################################################################
    asc_R = CalcVariable(r'\alpha _{sc.rad}', asc*PI/180, 'radians')
    Fosha = CalcVariable(r'\beta_{osha}', 5, '', 'Design for 5 times the service loads for OSHA compliance')
    wdsc = CalcVariable('w_{dsc}', DL*Wtr/2+wswsc,'lsb/ft', 'Distributed dead load on stringer')
    wsc = CalcVariable('w_{sc}', LL*Wtr/2+wdsc,'lbs/ft', 'Distributed dead and live load on stringer')

    Mdsc = CalcVariable('M_{dsc}', Fosha*wsc*Lsc**2*COS(asc_R)/8, 'lbs-ft', 'Factored moment due to uniform live load')
    Mcsc = CalcVariable('M_{csc}', Fosha*BRACKETS(wdsc*Lsc**2*COS(asc_R)/8 + LC*Lsc/4), 'lbs-ft', 'Factored moment due to concentrated live load' )
    Musc = CalcVariable('M_{usc}', MAX(Mdsc, Mcsc), 'lbs-ft', 'Factored design moment on stringer')

    Pdsc = CalcVariable('P_{dsc}', Fosha*wsc*Lsc*COS(asc_R), 'lbs', 'Factored axial load due to uniform live load')
    Pcsc = CalcVariable('P_{csc}', Fosha*BRACKETS(wdsc*Lsc*COS(asc_R)*SIN(asc_R) + LC), 'lbs', 'Factored axial load due to concentrated live load' ) #Fosha*BRACKETS(wdsc*Lsc*COS(asc) + LC)
    Pusc = CalcVariable('P_{usc}', MAX(Pdsc, Pcsc), 'lbs', 'Factored design axial load on stringer')

    Rusc = CalcVariable('R_{usc}', wsc*COS(asc_R)*Lsc/2, 'lbs', 'End reaction due to stringer dead and uniform live load')
    Rcsc = CalcVariable('R_{csc}', wdsc*COS(asc_R)*Lsc/2 + LC, 'lbs', 'End reaction due to stringer dead and concentrated live load (at end)')
    Resc = CalcVariable('R_{esc}', MAX(Rusc, Rcsc), 'lbs', 'Unfactored stringer end reaction')

    Vusc = CalcVariable('V_{usc}', Fosha*Resc, 'lbs', 'Factored maximum shear demand')
    Tusc = CalcVariable('T_{usc}', Fosha*LLHR*HHR, 'lbs-in', 'Factored torsion demand due to handrail loading')


    BodyHeader('Stair Stringer Deflections', head_level=2) ######################################################################################
    dallow = CalcVariable('\delta_{allow}', Lsc*ft_to_in/dlim, 'in')
    delastic = CalcVariable('\delta_{elastic}', 5*wsc/k_to_lb*Lsc**4*ft_to_in**3/(384*E*Ixsc), 'in')
    CheckVariable( delastic, '<=', dallow)


    BodyHeader('Stair Stringer Compression Design (ADM Chapter E)', head_level=2) ######################################################################################

    BodyHeader('Member Buckling (ADM E.2)')
    y1c = CalcVariable('\lambda_{1c}', (Bc-Fcy)/Dc, '')
    ycf = CalcVariable('\lambda_{cf}', Ksc * Lbsc * ft_to_in / rysc, '', 'Member slenderness ratio for flexural buckling', code_ref='ADM E.2.1')
    r0sc = CalcVariable('r_{0sc}', SQRT(x0sc**2+y0sc**2+(Ixsc+Iysc)/Asc), 'in', code_ref='ADM E.2-7')
    Hsc = CalcVariable('H_{sc}', 1-(x0sc**2+y0sc**2)/r0sc**2, '', code_ref='ADM E.2-8')
    Fexsc = CalcVariable('F_{exsc}', PI**2*E/(Ksc*Lbsc*ft_to_in/rxsc )**2, 'ksi', code_ref='ADM E.2-9'  )
    Fezsc = CalcVariable('F_{ezsc}', ONE/(Asc*r0sc**2)*BRACKETS(G*Jsc+PI**2*E*Cwsc/(Ksc * Lbsc*ft_to_in )**2), 'ksi', code_ref='ADM E.2-11'  )
    Fesc = CalcVariable('F_{esc}', (Fexsc+Fezsc)/(2*Hsc)*BRACKETS (1-SQRT(1-4*Fexsc*Fezsc*Hsc/(Fexsc+Fezsc)**2)), 'ksi', 'Elastic buckling stress for torsional buckling where x is the axis of symmetry', code_ref='ADM E.2-5'  )
    yct = CalcVariable('\lambda_{ct}', PI*SQRT(E/Fesc), '', 'Member slenderness ratio for torsional buckling', code_ref='ADM E.2-3')

    yc = CalcVariable('\lambda_{c}', MAX(ycf, yct), '', 'Greatest compression member slenderness', code_ref='ADM E.2')

    if yc.result() <= y1c.result():
        CheckVariablesText(yc, '<=', y1c)
        BodyText('Member yielding controls')
        Fcsc = CalcVariable('F_{csc}', Fcy, 'ksi', code_ref='ADM E.2')
    elif yc.result() < Cc.result():
        CheckVariablesText(y1c, '<', yc, '<', Cc)
        BodyText('Inelastic buckling controls')
        Fcsc = CalcVariable('F_{csc}', BRACKETS(Bc-Dc*yc)*BRACKETS(0.85+0.15*(Cc-yc)/(Cc-y1c)), 'ksi', code_ref='ADM E.2')
    else:
        CheckVariablesText( yc, '>=', Cc)
        BodyText('Elastic buckling controls')
        Fcsc = CalcVariable('F_{csc}', 0.85*PI**2*E/yc**2, 'ksi', code_ref='ADM E.2')
    PPncm = CalcVariable('\phi P_{ncm}', Pc*Fcsc*Asc*k_to_lb , 'lbs', 'Member buckling strength', code_ref='ADM E.2-1')

    BodyHeader('Local Buckling (ADM E.3)')
    k1c = CalcVariable('k_{1c}', 0.35, '', code_ref='ADM Table B.4.3') # assume temper T6
    k2c = CalcVariable('k_{2c}', 2.27, '', code_ref='ADM Table B.4.3')
    y1e = CalcVariable('\lambda_{1e}', (Bp-Fcy)/Dp, '')
    y2e = CalcVariable('\lambda_{2e}', k1c*Bp/Dp, '')
    Fee = CalcVariable('F_{ee}', PI**2*E/(5*BRACKETS(bsc-twsc-Rsc)/tfsc)**2, 'ksi', code_ref='ADM Table B.5.1')
    yeq = CalcVariable('\lambda_{eq}', PI*SQRT(E/Fee), '', code_ref='B.5-11')

    if yeq.result() <= y1e.result():
        CheckVariablesText(yeq, '<=', y1e)
        BodyText('Member yielding controls')
        Fcesc = CalcVariable('F_{cesc}', Fcy, 'ksi', code_ref='ADM B.5.4.6')
    elif yeq.result() < y2e.result():
        CheckVariablesText(y1e, '<=', yeq, '<', y2e)
        BodyText('Inelastic buckling controls')
        Fcesc = CalcVariable('F_{cesc}', Bp-Dp*yeq , 'ksi', code_ref='ADM B.5.4.6')
    else:
        CheckVariablesText(yeq, '>=', y2e)
        BodyText('Elastic buckling controls')
        Fcesc = CalcVariable('F_{cesc}', k2c*SQRT(Bp*E)/yeq, 'ksi', code_ref='ADM B.5.4.6')
    PPnce = CalcVariable('\phi P_{nce}', Pc*Fcesc*Asc*k_to_lb , 'lbs', 'Member local buckling strength', code_ref='ADM E.3-2')

    BodyHeader('Controlling Strength')
    PPnsc = CalcVariable('\phi P_{nsc}', MIN(PPncm, PPnce), 'lbs', 'Member compressive strength')
    c1 = CheckVariable( Pusc, '<=', PPnsc, truestate="OK", falsestate="ERROR", result_check=True)



    BodyHeader('Stair Stringer Flexural Design (ADM Chapter F)', head_level=2) ######################################################################################

    BodyHeader('Yielding and Rupture (ADM F.2)')
    Mnp = CalcVariable('M_{np}', MIN(Zsc*Fcy, 1.5*Ssc*Fty, 1.5*Ssc*Fcy)*(k_to_lb/ft_to_in),'lbs-ft', 'Yield limit state nominal moment capacity',code_ref='ADM F.2')
    PMnp = CalcVariable('\phi M_{np}', Pby*Mnp,'lbs-ft')
    PMnu = CalcVariable('\phi M_{nu}', Pbr*Zsc*Ftu/kt*(k_to_lb/ft_to_in), 'lbs-ft', 'Rupture limit state moment capacity', code_ref='ADM F.2-1' )

    BodyHeader('Local Buckling (ADM F.3.2)')
    k1b = CalcVariable('k_1b', 0.5, '', code_ref='ADM Table B.4.3')
    k2b = CalcVariable('k_2b', 2.04, '', code_ref='ADM Table B.4.3')
    if yeq.result() <= y1e.result():
        CheckVariablesText(yeq, '<=', y1e)
        BodyText('Member yielding controls')
        Fbsc = CalcVariable('F_{bsc}', Mnp/Ssc*(ft_to_in/k_to_lb), 'ksi', code_ref='ADM B.5.5.5')
    elif yeq.result() < Cp.result():
        CheckVariablesText(y1e, '<', yeq, '<', Cp)
        BodyText('Inelastic buckling controls')
        Fbsc = CalcVariable('F_{bsc}', Mnp/Ssc*(ft_to_in/k_to_lb)-BRACKETS(Mnp/Ssc*(ft_to_in/k_to_lb)-PI**2*E/Cp**2)*(yeq-y1e)/(Cp-y1e) , 'ksi', code_ref='ADM B.5.5.5')
    else:
        CheckVariablesText(yeq, '>=', Cp)
        BodyText('Post-buckling controls')
        Fbsc = CalcVariable('F_{bsc}', k2b*SQRT(Bp*E)/yeq, 'ksi', code_ref='ADM B.5.5.5')
    PMnlb = CalcVariable('\phi M_{nlb}', Pby*Fbsc*Ssc*(k_to_lb/ft_to_in), 'lbs-ft', 'Local buckling limit state moment capacity', code_ref='ADM F.3-2')

    BodyHeader('Lateral-Torsional Buckling (ADM F.4)')
    Cb = CalcVariable('C_b', 1.0, '', code_ref='ADM F.4.1(a)')
    ryesc = CalcVariable('r_{yesc}', SQRT(SQRT(Iysc)/Ssc*SQRT(Cwsc+0.038*Jsc*(Lbsc*ft_to_in)**2)), 'in', code_ref='ADM F.4-4')
    ybsc = CalcVariable('\lambda_{bsc}', Lbsc*ft_to_in/(ryesc*SQRT(Cb)), '', code_ref='ADM F.4-3')

    if ybsc.result() < Cc.result():
        CheckVariablesText(ybsc, '<', Cc)
        BodyText('Inelastic lateral torsional buckling controls')
        PMnmb = CalcVariable('\phi M_{nmb}',Pby*(Mnp*BRACKETS(1-ybsc/Cc)+PI**2*E*ybsc*Ssc/Cc**3*(k_to_lb/ft_to_in)), 'lbs-ft', 'Lateral torsional buckling moment capacity', code_ref='ADM F.4')
    else:
        CheckVariablesText(ybsc, '>=', Cc)
        BodyText('Elastic lateral torsional buckling controls')
        PMnmb = CalcVariable('\phi M_{nmb}', Pby*PI**2*E*Ssc/ybsc**2*k_to_lb/ft_to_in, 'lbs-ft', 'Lateral torsional buckling moment capacity', code_ref='ADM F.4')

    BodyHeader('Controlling Strength')
    PMnsc = CalcVariable('\phi M_{nsc}', MIN(PMnp, PMnu, PMnlb,  PMnmb), 'lbs-ft', 'Member moment strength')
    CheckVariable( Musc, '<=', PMnsc, truestate="OK", falsestate="ERROR", result_check=True)



    BodyHeader('Stair Stringer Shear and Torsion Design (ADM Chapter H.2)', head_level=2) ######################################################################################
    BodyText("Member shear stresses due to torsion are calculated in accordance with AISC Design Guide 9 and Roark's Formulas for Stress and Strain, 7th ed.")

    BodyHeader("Torsional Properties")
    KT = CalcVariable('K_T', 2*(bsc*tfsc)**3/3 + BRACKETS(dsc-2*tfsc)*twsc**3/3, 'in^4', 'Torsional Constant', code_ref='DG9 3.4' )
    BT = CalcVariable(r'\beta_{T}', SQRT(KT*G/(Cwsc*E)), 'in^{-1}', code_ref="Roark's Table 10.3" )

    BodyHeader("Elastic Deformations due to Torsion (Roark's Table 10.3.1g)")
    Opmax = CalcVariable(r"\theta'_{max}", Tusc/(2*Cwsc*E*k_to_lb*BT**2)*BRACKETS(1-ONE/(COSH((BT*Lsc*ft_to_in)/4))), 'in^{-1}')
    # Oppmax = CalcVariable(r"\theta''_{max)}", Tusc/(2*Cwsc*E*k_to_lb*BT)*TANH((BT*Lsc*ft_to_in)/2), 'in^{-2}')
    Opppmax = CalcVariable(r"\theta'''_{max}", Tusc/(2*Cwsc*E*k_to_lb), 'in^{-3}')
    BodyHeader("Torsional Shear Stresses (Roark's Table 10.2.1)")
    tT = CalcVariable('t_T', MAX(twsc, tfsc), 'in')
    bT = CalcVariable('b_T', bsc-twsc/2, 'in')
    hT = CalcVariable('h_T', dsc - tfsc, 'in')
    Ttmax = CalcVariable(r"\tau_{Tmax}", tT*G*Opmax, 'ksi' )
    Twmax = CalcVariable(r"\tau_{Wmax}", (hT*bT**2)/4 * ((hT+3*bT)/(hT+6*bT))**2 * E * Opppmax, 'ksi')
    BodyText('The torsional and warping stresses reach maximum values at different points along the beam. The total maximum shear stress due to torsion is conservatively calculated as the sum of torsion and warping.')
    Ttw = CalcVariable(R"\tau_{TW}", Ttmax + Twmax, 'ksi')

    Avsc = CalcVariable('A_{vsc}', dsc*twsc, 'in^2', code_ref='ADM G.2-3')
    Ttsc = CalcVariable(r"\tau_{usc}", Vusc/Avsc/k_to_lb + Ttw, 'ksi', 'Total shear stress demand on member')

    BodyHeader('Web Shear Capacity (ADM G.2)')
    PVnu = CalcVariable('\phi V_{nu}', Pbr*Fsu/kt,'lbs-ft', 'Rupture limit state shear capacity',code_ref='ADM G.2-1')

    yv = CalcVariable('b/t', (dsc-2*tfsc)/twsc, '')
    y1v = CalcVariable('\lambda_{1v}', (Bs-Fsy)/(1.25*Ds), '')
    y2v = CalcVariable('\lambda_{2v}', Cs/1.25, '')

    if yv.result() <= y1v.result():
        CheckVariablesText(yv, '<=', y1v)
        BodyText('Shear yielding controls')
        Vny = CalcVariable('V_{ny}',Fsy, 'ksi')
    elif yv.result() < y2v.result():
        CheckVariablesText(y1v, '<', yv, '<', y2v)
        BodyText('Inelastic buckling controls')
        Vny = CalcVariable('V_{ny}', Bs - 1.25*Ds*yv , 'ksi')
    else:
        CheckVariablesText(yv, '>=', y2v)
        BodyText('Elastic buckling controls')
        Vny = CalcVariable('V_{ny}', (PI**2*E)/(1.25*yv), 'ksi')
    PVny = CalcVariable('\phi V_{ny}', Pby*Vny, 'ksi', 'Yield or buckling limit state shear capacity')

    BodyHeader('Controlling Shear Strength')
    PVsc = CalcVariable('\phi V_{sc}', MIN(PVnu, PVny), 'ksi', 'Member shear strength')
    CheckVariable( Ttsc, '<=', PVsc, truestate="OK", falsestate="ERROR", result_check=True)

    BodyHeader('Stair Stringer Combined Axial and Flexural Design', head_level=2) ######################################################################################
    # dcrp = CalcVariable('DCR_P', Pusc/PPnsc, '', 'Demand-capacity-ratio for axial load design')
    # dcrm = CalcVariable('DCR_M', Musc/PMnsc, '', 'Demand-capacity-ratio for flexural design')
    dcrcom = CalcVariable('DCR_{PM}', Pusc/PPnsc + Musc/PMnsc, '', 'Combined axial and flexural demand-capacity-ratio for member design', code_ref='H.1-1')
    CheckVariable( dcrcom, '<=', 1, truestate="OK", falsestate="ERROR", description="", code_ref="", result_check=True)
    dcrall = CalcVariable('DCR_{ALL}', Pusc/PPnsc + (Musc/PMnsc)**2 + (Ttsc/PVsc)**2, '', 'Combined axial, flexural, and shear/torsion demand-capacity-ratio for member design', code_ref='H.3-1')
    CheckVariable( dcrall, '<=', 1, truestate="OK", falsestate="ERROR", description="", code_ref="", result_check=True)

    # Platform rectangular member design       ###########################################################################################################

    BodyHeader('Platform rectangular main beam design (perpendicular to stringer)', head_level=1) # length = L_TP
    BodyHeader('Section properties')
    sectionpr = AlumShapesRectangular.objects(Name=sizepr.value).first()
    wswpr = CalcVariable('SW_{pr}', sectionpr.W, 'lb/ft')
    bpr = CalcVariable('b_{pr}', sectionpr.b, 'in')
    tpr = CalcVariable('t_{pr}', sectionpr.t, 'in')
    Spr = CalcVariable('S_{xpr}', sectionpr.Sx, 'in^3')
    Zpr = CalcVariable('Z_{xpr}', sectionpr.Zx, 'in^3')
    Ixpr = CalcVariable('I_{xpr}', sectionpr.Ix, 'in^4')
    rxpr = CalcVariable('r_{xpr}', sectionpr.rx, 'in')
    Iypr = CalcVariable('I_{ypr}', sectionpr.Iy, 'in^4')
    rypr = CalcVariable('r_{ypr}', sectionpr.ry, 'in')
    Jpr = CalcVariable('J_{pr}', sectionpr.J, 'in^4')


    BodyHeader('Platform Main Beam Load Demands', head_level=2) ######################################################################################
    Lpr = CalcVariable('L_{pr}', Wtp, 'ft', 'Length of main beam (max)')
    apr = CalcVariable('a_{pr}', (Lpr-Wtr)/2, 'ft', 'Average distance from stringer load to end of beam')
    wpr = CalcVariable('w_{dpr}', BRACKETS(DL+LL)*Ltp/2+wswpr,'lsb/ft', 'Distributed load on main beam')
    # Resc
    BodyText('Conservatively assume stair stringer reactions are centered on the main beam. Distance between reactions will be equal to the stair tread width.')
    Mupr = CalcVariable('M_{upr}', Fosha*BRACKETS(wpr*Lpr**2/8 + Resc*apr), 'lbs-ft', 'Factored moment on main beam')

    Repr = CalcVariable('R_{epr}', wpr*Lpr/2 + Resc, 'lbs', 'Unfactored main beam end reaction')


    BodyHeader('Platform Main Beam Deflections', head_level=2) ######################################################################################
    dallow = CalcVariable('\delta_{allow}', Lpr*ft_to_in/dlim, 'in')
    delastic = CalcVariable('\delta_{elastic}', 5*wpr/k_to_lb*Lpr**4*ft_to_in**3/(384*E*Ixpr) + Resc/k_to_lb/(24*E*Ixpr)*BRACKETS(3*Lpr**2*apr-4*apr**3)*ft_to_in**2, 'in')
    CheckVariable( delastic, '<=', dallow)




    BodyHeader('Platform Main Beam Flexural Design (ADM Chapter F)', head_level=2) ######################################################################################

    BodyHeader('Yielding and Rupture (ADM F.2)')
    Mnp = CalcVariable('M_{np}', MIN(Zpr*Fcy, 1.5*Spr*Fty, 1.5*Spr*Fcy)*(k_to_lb/ft_to_in),'lbs-ft', 'Yield limit state nominal moment capacity',code_ref='ADM F.2')
    PMnp = CalcVariable('\phi M_{np}', Pby*Mnp,'lbs-ft')
    PMnu = CalcVariable('\phi M_{nu}', Pbr*Zpr*Ftu/kt*(k_to_lb/ft_to_in), 'lbs-ft', 'Rupture limit state moment capacity', code_ref='ADM F.2-1' )


    BodyHeader('Local Buckling (ADM F.3.2)')
    Feer = CalcVariable('F_{eer}', PI**2*E/(1.6*BRACKETS(bpr-2*tpr)/tpr)**2, 'ksi', code_ref='ADM Table B.5.1')
    yeqr = CalcVariable('\lambda_{eqr}', PI*SQRT(E/Feer), '', code_ref='B.5-15')

    if yeqr.result() <= y1e.result():
        CheckVariablesText(yeqr, '<=', y1e)
        BodyText('Member yielding controls')
        Fbpr = CalcVariable('F_{bpr}', Mnp/Spr*(ft_to_in/k_to_lb), 'ksi', code_ref='ADM B.5.5.5')
    elif yeqr.result() < Cp.result():
        CheckVariablesText(y1e, '<', yeqr, '<', Cp)
        BodyText('Inelastic buckling controls')
        Fbpr = CalcVariable('F_{bpr}', Mnp/Spr*(ft_to_in/k_to_lb)-BRACKETS(Mnp/Spr*(ft_to_in/k_to_lb)-PI**2*E/Cp**2)*(yeqr-y1e)/(Cp-y1e) , 'ksi', code_ref='ADM B.5.5.5')
    else:
        CheckVariablesText(yeqr, '>=', Cp)
        BodyText('Post-buckling controls')
        Fbpr = CalcVariable('F_{bpr}', k2b*SQRT(Bp*E)/yeqr, 'ksi', code_ref='ADM B.5.5.5')
    PMnlb = CalcVariable('\phi M_{nlb}', Pby*Fbpr*Spr*(k_to_lb/ft_to_in), 'lbs-ft', 'Local buckling limit state moment capacity', code_ref='ADM F.3-2')

    BodyHeader('Lateral-Torsional Buckling (ADM F.4)')
    Cb = CalcVariable('C_b', 1.0, '', code_ref='ADM F.4.1(a)')
    ybpr = CalcVariable('\lambda_{bpr}', 2.3*SQRT(Lpr*Spr/(Cb*SQRT(Iypr*Jpr))), '', code_ref='ADM F.4-6')

    if ybpr.result() < Cc.result():
        CheckVariablesText(ybpr, '<', Cc)
        BodyText('Inelastic lateral torsional buckling controls')
        PMnmb = CalcVariable('\phi M_{nmb}',Pby*(Mnp*BRACKETS(1-ybpr/Cc)+PI**2*E*ybpr*Spr/Cc**3*(k_to_lb/ft_to_in)), 'lbs-ft', 'Lateral torsional buckling moment capacity', code_ref='ADM F.4')
    else:
        CheckVariablesText(ybpr, '>=', Cc)
        BodyText('Elastic lateral torsional buckling controls')
        PMnmb = CalcVariable('\phi M_{nmb}', Pby*PI**2*E*Spr/ybpr**2*k_to_lb/ft_to_in, 'lbs-ft', 'Lateral torsional buckling moment capacity', code_ref='ADM F.4')

    BodyHeader('Controlling Strength')
    PMnpr = CalcVariable('\phi M_{npr}', MIN(PMnp, PMnu, PMnlb,  PMnmb), 'lbs-ft', 'Member moment strength')
    CheckVariable( Mupr, '<=', PMnpr, truestate="OK", falsestate="ERROR", result_check=True)



    # Platform channel member design       ###########################################################################################################

    BodyHeader('Platform Channel Beam Design', head_level=1)
    BodyHeader('Section properties')
    sectionpc = AlumShapesChannel.objects(Size=sizepc.value).first()
    twpc = CalcVariable('t_{wpc}', sectionpc.tw, 'in')
    tfpc = CalcVariable('t_{fpc}', sectionpc.tf, 'in')
    bpc = CalcVariable('b_{pc}', sectionpc.b, 'in')
    dpc = CalcVariable('d_{pc}', sectionpc.d, 'in')
    Rpc = CalcVariable('R_{pc}', sectionpc.R1, 'in')
    wswpc = CalcVariable('SW_{pc}', sectionpc.W,'lbs/ft')
    Apc = CalcVariable('A_{pc}', sectionpc.A, 'in^2')
    Spc = CalcVariable('S_{xpc}', sectionpc.Sx, 'in^3')
    Zpc = CalcVariable('Z_{xpc}', sectionpc.b*sectionpc.d**2/4-(sectionpc.b-sectionpc.tw)*(sectionpc.d-2*sectionpc.tf)**2/4, 'in^3') # Z for channel shape
    Ixpc = CalcVariable('I_{xpc}', sectionpc.Ix, 'in^4')
    rxpc = CalcVariable('r_{xpc}', sectionpc.rx, 'in')
    Iypc = CalcVariable('I_{ypc}', sectionpc.Iy, 'in^4')
    rypc = CalcVariable('r_{ypc}', sectionpc.ry, 'in')
    xpc = CalcVariable('x_{pc}', sectionpc.x, 'in')
    expc = CalcVariable('e_{xpc}', 3*tfpc*(bpc-twpc/2)**2/(BRACKETS(dpc-tfpc)*twpc+6*BRACKETS(bpc-twpc/2)*tfpc), 'in', 'Shear center measured from web centerline' ) # for channel shape from CERM
    x0pc = CalcVariable('x_{0pc}', expc + xpc - twpc/2, 'in')
    y0pc = CalcVariable('y_{0pc}', 0, 'in')
    Jpc = CalcVariable('J_{pc}', Ixpc+Iypc, 'in^4')
    Cwpc = CalcVariable('C_{wpc}', (1/6)*(dpc-tfpc)**2*(bpc-twpc/2)**2*tfpc*BRACKETS(bpc-twpc/2-3*expc)+expc**2*Ixpc,'in^6') # for channel shape per AISC Design Guide 9


    BodyHeader('Platform Channel Beam Load Demands', head_level=2) ######################################################################################
    Lpc = CalcVariable('L_{pc}', Ltp, 'ft', 'Length of platform channel beam (max)')
    wdpc = CalcVariable('w_{dpc}', DL*Wtp/2+wswpc,'lbs/ft', 'Distributed dead load on platform channel beam')
    wpc = CalcVariable('w_{pc}', LL*Wtp/2+wdpc,'lbs/ft', 'Distributed dead and live load on platform channel beam')

    Mdpc = CalcVariable('M_{dpc}', Fosha*wpc*Lpc**2/8, 'lbs-ft', 'Factored moment due to uniform live load')
    Mcpc = CalcVariable('M_{cpc}', Fosha*BRACKETS(wdpc*Lpc**2/8 + LC*Lpc/4), 'lbs-ft', 'Factored moment due to concentrated live load' )
    Mupc = CalcVariable('M_{upc}', MAX(Mdpc, Mcpc), 'lbs-ft', 'Factored design moment on platform channel beam')

    Rupc = CalcVariable('R_{upc}', wpc*Lpc/2, 'lbs', 'End reaction due to platform channel beam dead and uniform live load')
    Rcpc = CalcVariable('R_{cpc}', wdpc*Lpc/2 + LC, 'lbs', 'End reaction due to platform channel beam dead and concentrated live load (at end)')
    Repc = CalcVariable('R_{epc}', MAX(Rupc, Rcpc), 'lbs', 'Unfactored platform channel beam end reaction')


    BodyHeader('Platform Channel Beam Deflections', head_level=2) ######################################################################################
    dallow = CalcVariable('\delta_{allow}', Lpc*ft_to_in/dlim, 'in')
    delastic = CalcVariable('\delta_{elastic}', 5*wpc/k_to_lb*Lpc**4*ft_to_in**3/(384*E*Ixpc), 'in')
    CheckVariable( delastic, '<=', dallow)

    BodyHeader('Platform Channel Beam Flexural Design (ADM Chapter F)', head_level=2) ######################################################################################

    BodyHeader('Yielding and Rupture (ADM F.2)')
    Mnp = CalcVariable('M_{np}', MIN(Zpc*Fcy, 1.5*Spc*Fty, 1.5*Spc*Fcy)*(k_to_lb/ft_to_in),'lbs-ft', 'Yield limit state nominal moment capacity',code_ref='ADM F.2')
    PMnp = CalcVariable('\phi M_{np}', Pby*Mnp,'lbs-ft')
    PMnu = CalcVariable('\phi M_{nu}', Pbr*Zpc*Ftu/kt*(k_to_lb/ft_to_in), 'lbs-ft', 'Rupture limit state moment capacity', code_ref='ADM F.2-1' )

    BodyHeader('Local Buckling (ADM F.3.2)')

    Feec = CalcVariable('F_{eec}', PI**2*E/(5*BRACKETS(bpc-twpc-Rpc)/tfpc)**2, 'ksi', code_ref='ADM Table B.5.1')
    yeqc = CalcVariable('\lambda_{eqc}', PI*SQRT(E/Feec), '', code_ref='B.5-11')

    if yeqc.result() <= y1e.result():
        CheckVariablesText(yeqc, '<=', y1e)
        BodyText('Member yielding controls')
        Fbpc = CalcVariable('F_{bpc}', Mnp/Spc*(ft_to_in/k_to_lb), 'ksi', code_ref='ADM B.5.5.5')
    elif yeqc.result() < Cp.result():
        CheckVariablesText(y1e, '<', yeqc, '<', Cp)
        BodyText('Inelastic buckling controls')
        Fbpc = CalcVariable('F_{bpc}', Mnp/Spc*(ft_to_in/k_to_lb)-BRACKETS(Mnp/Spc*(ft_to_in/k_to_lb)-PI**2*E/Cp**2)*(yeqc-y1e)/(Cp-y1e) , 'ksi', code_ref='ADM B.5.5.5')
    else:
        CheckVariablesText(yeqc, '>=', Cp)
        BodyText('Post-buckling controls')
        Fbpc = CalcVariable('F_{bpc}', k2b*SQRT(Bp*E)/yeqc, 'ksi', code_ref='ADM B.5.5.5')
    PMnlb = CalcVariable('\phi M_{nlb}', Pby*Fbpc*Spc*(k_to_lb/ft_to_in), 'lbs-ft', 'Local buckling limit state moment capacity', code_ref='ADM F.3-2')


    BodyHeader('Lateral-Torsional Buckling (ADM F.4)')
    Cb = CalcVariable('C_b', 1.0, '', code_ref='ADM F.4.1(a)')
    ryepc = CalcVariable('r_{yepc}', SQRT(SQRT(Iypc)/Spc*SQRT(Cwpc+0.038*Jpc*(Lpc*ft_to_in)**2)), 'in', code_ref='ADM F.4-4')
    ybpc = CalcVariable('\lambda_{bpc}', Lpc*ft_to_in/(ryepc*SQRT(Cb)), '', code_ref='ADM F.4-3')

    if ybpc.result() < Cc.result():
        CheckVariablesText(ybpc, '<', Cc)
        BodyText('Inelastic lateral torsional buckling controls')
        PMnmb = CalcVariable('\phi M_{nmb}',Pby*(Mnp*BRACKETS(1-ybpc/Cc)+PI**2*E*ybpc*Spc/Cc**3*(k_to_lb/ft_to_in)), 'lbs-ft', 'Lateral torsional buckling moment capacity', code_ref='ADM F.4')
    else:
        CheckVariablesText(ybpc, '>=', Cc)
        BodyText('Elastic lateral torsional buckling controls')
        PMnmb = CalcVariable('\phi M_{nmb}', Pby*PI**2*E*Spc/ybpc**2*k_to_lb/ft_to_in, 'lbs-ft', 'Lateral torsional buckling moment capacity', code_ref='ADM F.4')

    BodyHeader('Controlling Strength')
    PMnpc = CalcVariable('\phi M_{npc}', MIN(PMnp, PMnu, PMnlb,  PMnmb), 'lbs-ft', 'Member moment strength')
    CheckVariable( Mupc, '<=', PMnpc, truestate="OK", falsestate="ERROR", result_check=True)

    BodyHeader('Mid-Level Platform Design and Platform Tributary Weights', head_level=2)

    BodyText('Member sizes on the mid-height platform are identical to those of the top platform. As the spans and loaded area are less than the top platform, the members can be assumed to pass all design checks.')


    Wdtp = CalcVariable('W_{d,p}', Wtp*Ltp*DL + 2*wswpr*Ltp + 2*wswpc*Wtp+ 4*wdsc*Lsc/2, 'lbs', 'Total tributary dead load associated with each platform (conservative)', result_check=True)
    Wltp = CalcVariable('W_{l,p}', Wtp*Ltp*LL + 2*LL*Wtr*Lsc/2, 'lbs', 'Total tributary live load associated with each platform (conservative)', result_check=True)
    # Wdmp = CalcVariable('W_{d,mp}', Wtp*Ltp*DL + 2*wswpr*Ltp + 2*wswpc*Wtp* 4*wdsc*Lsc/2, 'lbs', 'Total tributary dead load associated with the mid platform (conservative)')
    # Wlmp = CalcVariable('W_{l,mp}', Wtp*Ltp*LL + 2*LL*Wtr*Lsc/2, 'lbs', 'Total tributary live load associated with the mid platform (conservative)')




    calculation_sum = {'head':HeadCollection.head_instances, 'assum': AssumCollection.assum_instances, 'setup':SetupCollection.setup_instances, 'calc':CalcCollection.calc_instances, 'foot':FootCollection.foot_instances}
    return calculation_sum
