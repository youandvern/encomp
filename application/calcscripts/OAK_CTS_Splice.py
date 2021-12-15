from application.calcscripts.process.basedefinitions import CalculationTitle, DescriptionHead, Assumption, CheckVariable, CheckVariablesText, \
    DeclareVariable, CalcVariable, BodyText, BodyHeader, HeadCollection, SetupCollection, CalcCollection, FootCollection, AssumCollection
from application.calcscripts.process.calcmodels import AlumShapesL, AlumShapesChannel, AlumShapesCircular, AlumShapesRectangular, AlumShapesWF
from application.calcscripts.process.listoptions import alum_channel_sizes, alum_rectangular_sizes, reinforcement_bar_sizes
from application.calcscripts.process.latexExp import *

# STATUS: Completed, Production Ready


def create_calculation(updated_input={}):
    HeadCollection.head_instances.clear()
    AssumCollection.assum_instances.clear()
    SetupCollection.setup_instances.clear()
    CalcCollection.calc_instances.clear()
    FootCollection.foot_instances.clear()

    ###   DEFINE TITLE, DESCRIPTION, ASSUMPTIONS, AND INPUTS   ###

    CalculationTitle('EBMUD Oakland Digester 3 and 4 Wall Cap Reinforcing')

    DescriptionHead(
        "Structural design capacity calculations for a new installed wall cap, placed just below bottom of the dual membrane system anchors of Digester 3 and 4, designed to transfer membrane system anchor forces connected to the existing vertical reinforcing through lap splice.")

    Assumption("ACI 318-14 controls member design")
    Assumption(
        "Design loads are taken from provided WesTech DuoSphere calculation report Revision F dated 10/5/2021")
    Assumption(
        "Existing concrete strength is calculated per ACI 214.4R-10 chapter 9 from the provided core strengths by Testing Engineers Inc dated 11/1/21 (appendix C) and by Atlas dated 6/4/21 (appendix D)")
    Assumption("The wall cap will have enough stiffness to evenly distribute loads among the post-installed vertical reinforcing")
    Assumption("Post-installed reinforcement will be installed with Hilti HIT-RE 500 adhesive in accordance with ICC ESR-3814")
    Assumption("Post-installed bars shall conform to ASTM A615 specifications")
    Assumption("Tension splice type is Class B")
        

    Tu = DeclareVariable('T_u', 23000, 'lbs', 'Design ultimate tensile demand per cable group (Appendix B Page 46)', code_ref='Appendix B Page 46', input_type="number", min_value=0)
    Vu = DeclareVariable('V_u', 3500, 'lbs', 'Design ultimate shear demand per cable group (Appendix B Page 46)',  code_ref='Appendix B Page 46', input_type="number", min_value=0)

    Fce = DeclareVariable("f'_c", 3100, 'psi', 'Existing concrete strength (See appendix A)', 'ACI 214.4R-10 Eq. 9-9', input_type='number', min_value=0)
    Fsy = DeclareVariable('f_y', 60000, 'psi', 'Post-installed reinforcement yield strength', input_type='number', min_value=0)
    Fsye = DeclareVariable('f_{ye}', 40000, 'psi', 'Existing reinforcement yield strength', input_type='number', min_value=0)

    Tw = DeclareVariable('t_w', 11, 'in', 'Wall thickness', input_type='number', min_value=0)
    Ww = DeclareVariable('w_w', 75, 'in', 'Length of wall section per cable group', input_type='number', min_value=0)
    Rt = DeclareVariable('R_t', 48, 'ft', 'Radius of tank wall center line', input_type='number', min_value=1)

    Na = DeclareVariable("N_a", 8, "", 'Number of post-installed bars per cable group', input_type='number', min_value=1)

    

    Da = DeclareVariable('D_a', reinforcement_bar_sizes[1], '', 'Post-installed bar size (eighth of an inch diameter)',
                         input_type='select', input_options=reinforcement_bar_sizes)
                        
    Dae = DeclareVariable('D_{ae}', reinforcement_bar_sizes[1], '', 'Existing bar size (eighth of an inch diameter)',
                         input_type='select', input_options=reinforcement_bar_sizes)

    Sa = DeclareVariable(
        'S_a', 8, 'in', 'Spacing of splice bars', input_type='number')
    
    Sbpe = DeclareVariable("S_{b,p,e}", 2, "in", 'Transverse center-to-center spacing of splice bars', input_type='number', min_value=0)
    cbp = DeclareVariable("c_{b,p}", 2, "in", 'Center-to-edge distance of post-installed bars', input_type='number', min_value=0)
    cbpe = DeclareVariable("c_{b,e}", 2, "in", 'Center-to-edge distance of existing bars', input_type='number', min_value=0)

    ce = DeclareVariable("c_{1,e}", 2, "in", 'Maximum distance from end of existing bar to surface of concrete', input_type='number', min_value=0)

    Ktr = DeclareVariable("K_{tr}", 0, "", 'Confining reinforcement factor', input_type='number', min_value=0)
    
    Le = DeclareVariable('L_e', 5, 'in', 'Total embedment depth of post-installed bar', input_type='number', min_value=0)

    Hh = DeclareVariable('l_{dh}', 12, 'in', 'Hooked development length of post-installed bar in wall cap')

    Nh = DeclareVariable("N_h", 6, "", 'Number of horizontal bars in wall cap', input_type='number', min_value=0)
    Dh = DeclareVariable('D_h', reinforcement_bar_sizes[1], '', 'Horizontal bar size (eighth of an inch diameter)')

    Hcap = DeclareVariable('H_{cap}', 16, 'in', 'Height of new wall cap', input_type='number')
    Hunr = DeclareVariable('H_{unreinforced}', 12, 'in', 'Height of existing unreinforced zone above prestressing', input_type='number')

    Es = DeclareVariable('E_s', 29000000, 'psi', 'Modulus of elasticity of reinforcement steel')



    ###   DO NOT DEFINE INPUTS BELOW HERE OR EDIT THE FOLLOWING SECTION   ###

    if len(updated_input) > 0:
        for input_variable in DeclareVariable.instances:
            new_value = updated_input.get(input_variable.name)
            if new_value:
                input_variable._set_value(new_value)

    ###   DEFINE CALCULATION, BODY HEADER, AND BODY TEXT   ###

    k_to_lb = Variable('1000 \ \mathrm{lbs/kip}', 1000, 'lbs/kip')
    ft_to_in = Variable('12 \ \mathrm{in/ft}', 12, 'in/ft')



    BodyHeader('Tension Design (ACI 318-14 17.4)', head_level=1)

    db = CalcVariable('d_b', Da/8, 'in', 'Anchor bar diameter')
    aa = CalcVariable('A_a', PI*(db/2)**2, 'in^2', 'Area of steel anchor')
    atot = CalcVariable('A_{stot}', aa*Na, 'in^2', 'Total steel area of anchors')

    
    BodyHeader('Steel Anchor', head_level=2)
    futa = CalcVariable('f_{uta}', MIN(1.9*Fsy, 90000), 'psi', code_ref='ACI 318-14 17.4.1.2, ESR-3814')
    Nsa = CalcVariable('N_{sa}', atot*futa, 'lbs', 'Nominal strength of anchor in tension')
    Phis = CalcVariable(r'\phi_{steel}', 0.65, description='Strength reduction factor for steel tension', code_ref='ACI 318-14 17.3.3')
    PNsa = CalcVariable(r'\phi N_{sa}', Phis*Nsa, 'lbs')
    cpnsa = CheckVariable(Tu, '<=', PNsa, code_ref='ACI 318-14 Table 17.3.1.1' )

    Freduce = CalcVariable('R_{reduction}',  Tu / PNsa, '', 'Development length reduction factor', 'ACI 318-14 25.4.10.1' )
    Ldha = CalcVariable('L_{dha}', Freduce*Fsy*0.7*db/(50*SQRT(Fce)), 'in', 'Calculated hooked development length of dowel (assuming side cover > 2.5")', 'ACI 318-14 25.4.3.1a')
    BodyText("Minimum required hooked development length for anchor:")
    Ldhb = CalcVariable('L_{dhb}', 8*db, 'in', code_ref= 'ACI 318-14 25.4.3.1b')
    Ldhc = CalcVariable('L_{dhc}', Fsy*0.7*db/(50*SQRT(Fce)), 'in', code_ref='ACI 318-14 25.4.3.1c')

    Ldh = CalcVariable('L_{dh}', MAX(Ldha, Ldhb, Ldhc), 'in', 'Hooked development length of anchor bar' ,code_ref= 'ACI 318-14 25.4.3.1b')
    cldh = CheckVariable( Hh, '>=', Ldh, truestate="OK", falsestate="ERROR", result_check=True)

    
    BodyHeader('Bond Strength', head_level=2)

    bonduncr = CalcVariable(r'\tau_{uncr}', bonduncrc*(Fce/2500)**0.15, 'psi', 'Adjusted anchor bond strength', code_ref="ESR-3814")
    bondcr = CalcVariable(r'\tau_{cr}', bondcrc*(Fce/2500)**0.15, 'psi', 'Adjusted anchor bond strength - cracked', code_ref="ESR-3814")
    

    Yecna = CalcVariable(r'\psi_{ec,Na}', 1.0, '', 'Modification factor for eccentricity', code_ref='ACI 318-14 17.4.5.3')
    camin = CalcVariable('c_{a,min}', Tw / 2, 'in', 'Minimum edge distance of anchor bar')
    camax = CalcVariable('c_{a,max}', Tw / 2, 'in', 'Maximum edge distance of anchor bar')
    cna = CalcVariable('c_{Na}', 10*db*SQRT(bonduncr/1100), 'in', 'Projected maximum edge distance', 'ACI 318-14 Eq. 17.4.5.1d')
    

    if camin.result() >= cna.result():
        CheckVariablesText(camin, '>=', cna)
        Yedna = CalcVariable(r'\psi_{ed,Na}', 1.0, '', 'Modification factor for edge effects', code_ref='ACI 318-14 17.4.5.4a')
    else:
        CheckVariablesText(camin, '<', cna)
        Yedna = CalcVariable(r'\psi_{ed,Na}', 0.7+0.3*camin/cna, '', 'Modification factor for edge effects', code_ref='ACI 318-14 17.4.5.4b')

    cac = CalcVariable('c_{ac}', 2*Ha, 'in', 'Critical edge distance', 'ACI 318-14 17.7.6')

    if camin.result() >= cac.result():
        CheckVariablesText(camin, '>=', cac)
        Ycpna = CalcVariable(r'\psi_{cp,Na}', 1.0, '', 'Modification factor to control splitting', code_ref='ACI 318-14 17.4.5.5a')
    elif camin.result()/cac.result() >= cna.result()/cac.result():
        CheckVariablesText(camin, '<', cac)
        Ycpna = CalcVariable(r'\psi_{cp,Na}', camin/cac, '', 'Modification factor to control splitting', code_ref='ACI 318-14 17.4.5.5b')
    else:
        CheckVariablesText(camin, '<', cac)
        Ycpna = CalcVariable(r'\psi_{cp,Na}', 1.0, '', 'Modification factor to control splitting', code_ref='ACI 318-14 17.4.5.5b note')

    Nba = CalcVariable('N_{ba}', bondcr*PI*db*Ha, 'lbs', 'Basic bond strength of single adhesive anchor in tension in cracked concrete')
    Anao = CalcVariable('A_{Nao}', 4*cna**2, 'in^2', 'Projected influence area of a single adhesive anchor', code_ref='ACI 318-14 17.4.5.1c')
    Ana = CalcVariable('A_{Na}', BRACKETS(camin + camax)*BRACKETS(Sa*Na), 'in^2', 'Projected influence area of the group of adhesive anchors', code_ref='ACI 318-14 17.4.5.1c')
    
    Nag = CalcVariable('N_{ag}', Yecna*Yedna*Ycpna*Nba*Ana/Anao, 'lbs', 'Nominal bond strength of the anchor group', 'ACI 318-14 Eq. 17.4.5.1b')
    Phib = CalcVariable(r'\phi_{bond}', 0.65, description='Strength reduction factor for bond failure', code_ref='ACI 318-14 17.3.3')
    PNag = CalcVariable(r'\phi N_{ag}', Phib*Nag, 'lbs')
    cpnag = CheckVariable(Tu, '<=', PNag, code_ref='ACI 318-14 Table 17.3.1.1' )

    BodyHeader('Concrete Breakout Strength', head_level=2)

    heflim = CalcVariable('h_{ef,lim}', Ha, 'in', 'Limit to effective embedment length for concrete breakout strength in tension', 'ACI 318-14 17.4.2.3' )
    hef = CalcVariable('h_{ef}', MIN(Ha, heflim), 'in', 'Effective embedment length for concrete breakout strength in tension')

    Yecn = CalcVariable(r'\psi_{ec,N}', 1.0, '', 'Modification factor for eccentricity', code_ref='ACI 318-14 17.4.2.4')

    hef15 = CalcVariable('1.5h_{ef}', 1.5*hef, 'in')
    if camin.result() >= hef15.result():
        CheckVariablesText(camin, '>=', hef15)
        Yedn = CalcVariable(r'\psi_{ed,N}', 1.0, '', 'Modification factor for edge effects', code_ref='ACI 318-14 17.4.2.5a')
    else:
        CheckVariablesText(camin, '<', hef15)
        Yedn = CalcVariable(r'\psi_{ed,N}', 0.7+0.3*camin/hef15, '', 'Modification factor for edge effects', code_ref='ACI 318-14 17.4.2.5b')
    
    Ycn = CalcVariable(r'\psi_{c,N}', 1.0, '', 'Modification factor for uncracked sections', code_ref='ACI 318-14 17.4.2.6')

    if camin.result() >= cac.result():
        CheckVariablesText(camin, '>=', cac)
        Ycpn = CalcVariable(r'\psi_{cp,N}', 1.0, '', 'Modification factor to control splitting', code_ref='ACI 318-14 17.4.2.7a')
    elif camin.result()/cac.result() >= cna.result()/cac.result():
        CheckVariablesText(camin, '<', cac)
        Ycpn = CalcVariable(r'\psi_{cp,N}', camin/cac, '', 'Modification factor to control splitting', code_ref='ACI 318-14 17.4.2.7b')
    else:
        CheckVariablesText(camin, '<', cac)
        Ycpn = CalcVariable(r'\psi_{cp,N}', 1.0, '', 'Modification factor to control splitting', code_ref='ACI 318-14 17.4.2.7b note')
    
    kc = CalcVariable('k_c', 17, '', 'Post-installed anchor breakout factor', 'ACI 318-14 17.4.2.2')
    Nb = CalcVariable('N_{b}', kc*SQRT(Fce)*hef**1.5, 'lbs', 'Basic concrete breakout strength of single adhesive anchor in tension in cracked concrete', 'ACI 318-14 17.4.2.2a')
    Anco = CalcVariable('A_{Nco}', 9*hef**2, 'in^2', 'Projected concrete failure area of a single adhesive anchor', code_ref='ACI 318-14 17.4.2.1c')
    ca1 = CalcVariable('c_{ar}', MIN(1.5*hef, camin), 'in', 'Maximum radial projected length of concrete failure for each anchor')
    ca2 = CalcVariable('c_{aa}', MIN(1.5*hef, Sa/2), 'in', 'Maximum angular projected length of concrete failure for each anchor')
    Anc = CalcVariable('A_{Nc}', Na* BRACKETS(2*ca1*2*ca2), 'in^2', 'Projected influence area of the group of adhesive anchors')

    Ncbg = CalcVariable('N_{cbg}', Yecn*Yedn*Ycn*Ycpn*Nb*Anc/Anco, 'lbs', 'Nominal concrete breakout strength of the anchor group', 'ACI 318-14 Eq. 17.4.2.1b')
    Phic = CalcVariable(r'\phi_{conc}', 0.75, description='Strength reduction factor for breakout failure with tension reinforcing across failure plane', code_ref='ACI 318-14 17.3.3')
    PNcbg = CalcVariable(r'\phi N_{cbg}', Phic*Ncbg, 'lbs')
    cpncbg = CheckVariable(Tu, '<=', PNcbg, code_ref='ACI 318-14 Table 17.3.1.1' )


    BodyHeader('Shear Design (ACI 318-14 17.5)', head_level=1)

    BodyHeader('Steel Anchor', head_level=2)
    Vsa = CalcVariable('V_{sa}', 0.6*aa*futa, 'lbs', 'Nominal shear strength of anchors in shear')
    Phisv = CalcVariable(r'\phi_{steelV}', 0.60, description='Strength reduction factor for steel shear', code_ref='ACI 318-14 17.3.3')
    PVsa = CalcVariable(r'\phi V_{sa}', Phisv*Vsa, 'lbs')
    cpvsa = CheckVariable(Vu, '<=', PVsa, code_ref='ACI 318-14 Table 17.3.1.1' )

    BodyHeader('Pryout Strength', head_level=2)
    Ncpg = CalcVariable('N_{cpg}', MIN(Nag, Ncbg), 'lbs', 'Nominal unadjusted pryout strength for the anchor group', 'ACI 318-14 17.5.3.1')
    
    kpclim = Variable('2.5', 2.5)
    if hef.result() >= 2.5:
        CheckVariablesText(hef, '>=', kpclim)
        kcp = CalcVariable('k_{cp}', 2.0, '', 'Modification factor for concrete pryout', code_ref='ACI 318-14 17.5.3.1')
    else:
        CheckVariablesText(hef, '<', kpclim)
        kcp = CalcVariable('k_{cp}', 1.0, '', 'Modification factor for concrete pryout', code_ref='ACI 318-14 17.5.3.1')
    
    Vcp = CalcVariable('V_{cp}', kcp*Ncpg, 'lbs', 'Nominal adjusted pryout strength for the anchor group', 'ACI 318-14 Eq. 17.5.3.1b')
    Phicv = CalcVariable(r'\phi_{concV}', 0.70, description='Strength reduction factor for shear failure in concrete', code_ref='ACI 318-14 17.3.3')
    PVcp = CalcVariable(r'\phi V_{cp}', Phicv*Vcp, 'lbs')
    cpvcp = CheckVariable(Vu, '<=', PVcp, code_ref='ACI 318-14 Table 17.3.1.1' )


    BodyHeader('Edge Failure', head_level=2)
    Yecv = CalcVariable(r'\psi_{ec,V}', 1.0, '', 'Modification factor for eccentricity', code_ref='ACI 318-14 17.5.2.5')

    BodyText('Since the wall is continuous perpendicular to the breakout direction (ca2 > 1.5 ca1):')
    Yedv = CalcVariable(r'\psi_{ed,V}', 1.0, '', 'Modification factor for edge effect', code_ref='ACI 318-14 17.5.2.6')

    BodyText('Since the wall is assumed to be cracked and no edge reinforcement exists:')
    Ycv = CalcVariable(r'\psi_{c,V}', 1.0, '', 'Modification factor for edge reinforcement', code_ref='ACI 318-14 17.5.2.7')

    BodyText('Since the wall is continuous below the dowel anchors:')
    Yhv = CalcVariable(r'\psi_{h,V}', 1.0, '', 'Modification factor for member thickness', code_ref='ACI 318-14 17.5.2.8')

    le = CalcVariable('l_e', MIN(Ha, 8*db), 'in', 'Load bearing length of the anchor for shear', 'ACI 318-14 17.5.2.2')
    Vb1 = CalcVariable('V_{b1}', 7*(le/db)**0.2*SQRT(db)*SQRT(Fce)*camin**1.5, 'lbs', code_ref='ACI 318-14 Eq. 17.5.2.2a')
    Vb2 = CalcVariable('V_{b2}', 9*SQRT(Fce)* camin**1.5 , 'lbs', code_ref='ACI 318-14 Eq. 17.5.2.2b')
    


    Vb = CalcVariable('V_b', MIN(Vb1, Vb2), 'lbs', 'Basic concrete breakout strength in shear of single anchor', 'ACI 318-14 17.5.2.2')
    wv = CalcVariable('w_V', MIN(2*1.5*camin, Sa), 'in', 'Width of projected single anchor failure at edge of concrete')
    hv = CalcVariable('h_V', MIN(Ha, 1.5*camin), 'in', 'Height of projected single anchor failure at face of concrete')

    AVc = CalcVariable('A_{Vc}', Na*wv*hv, 'in^2', 'Projected concrete failure area of the adhesive anchor group', code_ref='ACI 318-14 17.5.2.1')
    AVco = CalcVariable('A_{Vco}', 4.5*camin**2, 'in^2', 'Projected concrete failure area of a single anchor in a deep member', code_ref='ACI 318-14 17.5.2.1')

    Vcbg = CalcVariable('V_{cbg}', Yecv*Yedv*Ycv*Yhv*Vb*AVc/AVco, 'lbs', 'Nominal concrete breakout strength of the anchor group in shear', 'ACI 318-14 Eq. 17.5.2.1b')
    PVcbg = CalcVariable(r'\phi V_{cbg}', Phicv*Vcbg, 'lbs')
    cpncbg = CheckVariable(Vu, '<=', PVcbg, code_ref='ACI 318-14 Table 17.3.1.1' )

    BodyHeader('Tension and Shear Combined', head_level=1)
    PNn = CalcVariable(r'\phi N_{n}', MIN(PNsa, PNag, PNcbg), 'lbs', 'Controlling tension strength')
    Nratio = CalcVariable(r'Tu / \phi N_{n}', Tu / PNn, '', 'Demand ratio for tension loading')
    PVn = CalcVariable(r'\phi V_{n}', MIN(PVsa, PVcp, PVcbg), 'lbs', 'Controlling shear strength')
    Vratio = CalcVariable(r'Vu / \phi V_{n}', Vu / PVn, '', 'Demand ratio for shear loading')

    ratiolim = Variable('0.2', 0.2)
    if Vratio.result() <= 0.2:
        CheckVariablesText(Vratio, '<=', ratiolim)
        BodyText('Full strength in tension is permitted, combined effects not applicable', 'ACI318-14 17.6.1')
    elif Nratio.result() <= 0.2:
        CheckVariablesText(Nratio, '<=', ratiolim)
        BodyText('Full strength in shear is permitted, combined effects not applicable', 'ACI318-14 17.6.2')
    else:
        CheckVariablesText(Vratio, '>', ratiolim)
        CheckVariablesText(Nratio, '>', ratiolim)
        Combratio = CalcVariable('R_{combined}', Nratio + Vratio, '', 'Combined demand ratio')
        Limratio = CalcVariable('R_{comb,lim}', 1.2, '', 'Maximum allowed combined demand ratio')
        ccomb = CheckVariable(Combratio, '<=', Limratio, code_ref='ACI 318-14 Eq. 17.6.3' )

    
    BodyHeader('Wall Cap Hoop Tension', head_level=1)
    BodyText('The new wall cap horizontal steel will be designed to take the entire hoop tension of the new dome structure created by outward shear force at the anchors.')
    Thu = CalcVariable('T_{uh}', Vu / Ww * Rt*ft_to_in, 'lbs', 'Hoop tension in wall cap')
    ah = CalcVariable('A_h', PI*(Dh/8/2)**2, 'in^2', 'Area of steel anchor')
    ahtot = CalcVariable('A_{htot}', ah*Nh, 'in^2', 'Total steel area of anchors')
    Pnmax = CalcVariable('P_{nt,max}', Fsy*ahtot, 'lbs', 'Nominal axial tension capacity of new wall cap', 'ACI 318-14 Eq. 22.4.3.1')
    Phit = CalcVariable(r'\phi_{tens}', 0.90, description='Strength reduction factor for tension controlled section capacity', code_ref='ACI 318-14 Table 21.2.2')
    PPnmax = CalcVariable(r'\phi P_{nt,max}', Phit*Pnmax, description='Design axial tension capacity of new wall cap')
    cpnmax = CheckVariable(Thu, '<=', PPnmax)





    BodyHeader('Existing Wall Flexural Strength', head_level=1)
    BodyText('As a conservative design check, the existing wall strength will be analyzed as if the shear force from the new dome anchors is transferred through the new connection rather than taken as a hoop force in the new wall cap. This shear would induce an out-of-plane moment on the previously unreinforced portion of the wall until the loads are disributed into the existing prestressing layer.')
    Muv = CalcVariable('M_{uV}', Vu * BRACKETS(Hcap+Hunr), 'lb-in', 'Maximum moment demand considered in existing wall')

    ey = CalcVariable(r'\varepsilon _y', Fsy/Es, '', 'Yield strain of reinforcement steel' )
    ec_var = CalcVariable(r'\varepsilon _c', 0.003, '', 'Crushing strain of concrete')
    B1 = CalcVariable(r'\beta _1', 0.85, '', 'Equivalent rectangular compressive stress block depth ratio', code_ref='ACI 318-14 Table 22.2.2.4.3') 

    c_assume = 0.001
    c_change = 2
    c_last_change = 0

    ec = ec_var.result()
    Es_val = Es.value
    fc_val = Fce.value
    b_val = Ww.value
    B1_val = B1.result()
    tolerance = 0.001
    c_solved = False

    n = 0
    while not c_solved:
        n+=1
        if n>100:
            c_assume = 0.00100
            break

        Ptot = - 0.85 * fc_val * b_val * B1_val * c_assume
        esi = ec * (camax.result() - c_assume) / c_assume
        Ptot += atot.result() * Es_val * esi
        
        if Ptot > tolerance:
            if c_last_change == 1: # last change was an decrease
                c_change = c_change/1.5
                c_last_change = 0
            c_assume += c_change
        elif Ptot < -1 * tolerance:
            if c_last_change == 0: # last change was a increase
                c_change = c_change/1.5
                c_last_change = 1
            c_assume -= c_change
        else:
            c_solved = True

    c = CalcVariable('c', c_assume, 'in', 'Neutral axis depth required for section equilibrium')    

    et_max = CalcVariable(r'\varepsilon _{t}', ABS( ec_var * BRACKETS(camax - c) / c), '', 'Maximimum tensile strain in reinforcement steel')

    bar_moment = CalcVariable('M_{ns}', atot * Es * et_max * camax, 'lb-in', 'Net moment contribution from reinforcement steel')

    Mn = CalcVariable('M_n', BRACKETS(bar_moment) - 0.85*(Fce)*Ww*B1*c*BRACKETS(B1*c/2), 'lb-in', 'Nominal moment capacity of wall section', result_check=False)

    phi = CalcVariable(r'\phi', MAX(0.65, MIN(0.65, 0.65 + 0.25*BRACKETS((et_max-ey)/(0.005 - ey)))), '', 'Strength reduction factor', code_ref='ACI 318-14 Table 21.2.2')

    phi_mn = CalcVariable(r'\phi M_n', phi*Mn, 'lb-in', 'Design moment capacity of wall section' )
    cpmn = CheckVariable(Muv, '<=', phi_mn)
























    




    calculation_sum = {'head': HeadCollection.head_instances, 'assum': AssumCollection.assum_instances,
                       'setup': SetupCollection.setup_instances, 'calc': CalcCollection.calc_instances, 'foot': FootCollection.foot_instances}
    return calculation_sum
