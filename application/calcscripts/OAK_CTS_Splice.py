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
    Assumption("All concrete is normal-weight")
    
        

    Tu = DeclareVariable('T_u', 23000, 'lbs', 'Design ultimate tensile demand per cable group (Appendix B Page 46)', code_ref='Appendix B Page 46', input_type="number", min_value=0)
    Vu = DeclareVariable('V_u', 3500, 'lbs', 'Design ultimate shear demand per cable group (Appendix B Page 46)',  code_ref='Appendix B Page 46', input_type="number", min_value=0)

    Fcn = DeclareVariable("f'_cn", 4000, 'psi', 'New concrete strength', input_type='number', min_value=0)
    Fce = DeclareVariable("f'_ce", 3100, 'psi', 'Existing concrete strength (See appendix A)', 'ACI 214.4R-10 Eq. 9-9', input_type='number', min_value=0)
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

    Sa = DeclareVariable('S_a', 8, 'in', 'Transverse center-to-center spacing of splice bars', input_type='number', min_value=0)
    
    Sbpe = DeclareVariable("S_{b,p,e}", 2, "in", 'Closest spacing between post-installed bar and existing bar', input_type='number', min_value=0)
    cbp = DeclareVariable("c_{b,p}", 2, "in", 'Minimum center-to-edge distance of post-installed bars', input_type='number', min_value=0)
    cbe = DeclareVariable("c_{b,e}", 2, "in", 'Minimum center-to-edge distance of existing bars', input_type='number', min_value=0)

    ce = DeclareVariable("c_{1,e}", 2, "in", 'Maximum distance from end of existing bar to surface of concrete', input_type='number', min_value=0)
    Le = DeclareVariable('L_e', 5, 'in', 'Total embedment depth of post-installed bar', input_type='number', min_value=0)

    Hh = DeclareVariable('l_{dh}', 12, 'in', 'Hooked development length of post-installed bar in wall cap')

    Nh = DeclareVariable("N_h", 6, "", 'Number of horizontal bars in wall cap', input_type='number', min_value=0)
    Dh = DeclareVariable('D_h', reinforcement_bar_sizes[1], '', 'Horizontal bar size (eighth of an inch diameter)')

    Muj = DeclareVariable(r"\mu_j", 1.0, '', 'Coefficient of friction between new wall cap and existing wall (ACI 318-14 Table 22.9.4.2)')

    Hcap = DeclareVariable('H_{cap}', 16, 'in', 'Height of new wall cap', input_type='number')
    Hunr = DeclareVariable('H_{unreinforced}', 12, 'in', 'Height of existing unreinforced zone above prestressing', input_type='number')

    Es = DeclareVariable('E_s', 29000000, 'psi', 'Modulus of elasticity of reinforcement steel')
    Yep = DeclareVariable(r'\psi_{e,p}', 1.0, '', 'Modification factor for epoxy coated post-installed bars (ACI 318-14 Table 25.4.2.4)')
    Yee = DeclareVariable(r'\psi_{e,e}', 1.0, '', 'Modification factor for epoxy coated existing bars (ACI 318-14 Table 25.4.2.4)')
    Yt = DeclareVariable(r'\psi_{t}', 1.0, '', 'Modification factor for splice casting position (ACI 318-14 Table 25.4.2.4)')
    Ktr = DeclareVariable("K_{tr}", 0, "", 'Confining reinforcement factor', input_type='number', min_value=0)



    ###   DO NOT DEFINE INPUTS BELOW HERE OR EDIT THE FOLLOWING SECTION   ###

    if len(updated_input) > 0:
        for input_variable in DeclareVariable.instances:
            new_value = updated_input.get(input_variable.name)
            if new_value:
                input_variable._set_value(new_value)

    ###   DEFINE CALCULATION, BODY HEADER, AND BODY TEXT   ###

    k_to_lb = Variable('1000 \ \mathrm{lbs/kip}', 1000, 'lbs/kip')
    ft_to_in = Variable('12 \ \mathrm{in/ft}', 12, 'in/ft')
    twelve_inches = Variable('12 \ \mathrm{in}', 12, 'in')

    BodyHeader('Tension Design', head_level=1)

    db = CalcVariable('d_b', Da/8, 'in', 'Post-installed bar diameter')
    aa = CalcVariable('A_a', PI*(db/2)**2, 'in^2', 'Post-installed bar area')
    atot = CalcVariable('A_{stot}', aa*Na, 'in^2', 'Total steel area of post-installed bars')

    dbe = CalcVariable('d_be', Dae/8, 'in', 'Existing bar diameter')
    aae = CalcVariable('A_{ae}', PI*(dbe/2)**2, 'in^2', 'Existing bar area')
    atote = CalcVariable('A_{stote}', aae*Na, 'in^2', 'Total steel area of existing bars')

    Lspe = CalcVariable('L_{s,pe}', Le - ce, 'in', 'Provided lap splice length between post-installed and existing bars')

    # Ldmin = CalcVariable('L_{d,min}', 12, 'in', 'Minimum allowable development length in tension', code_ref='ACI 318-14 25.4.2.1(b)')

    
    BodyHeader('Post-installed reinforcement tension splice', head_level=2)
    
    if Da.value <= 6:
        CheckVariablesText(Da.value, '<=', Variable('6', 6, ''))
        ccmin = CalcVariable('c_{c,min}', 1.1875, 'in', 'Minimum concrete cover', code_ref='ESR-3814 4.2.3')
    else:
        CheckVariablesText(Da.value, '>', Variable('6', 6, ''))
        ccmin = CalcVariable('c_{c,min}', 1.5625, 'in', 'Minimum concrete cover', code_ref='ESR-3814 4.2.3')
    
    cbmin = CalcVariable('c_{b,min}', db/2+ccmin, 'in', 'Required minimum edge distance for post-installed reinforcing bars', code_ref='ESR-3814 4.2.3')
    CheckVariable( cbmin, '<=', cbp, truestate="OK", falsestate="ERROR", result_check=True)

    sbmin = CalcVariable('S_{b,min}', db+ccmin, 'in', 'Required minimum center-to-center spacing between post-installed reinforcing bars', code_ref='ESR-3814 4.2.3')
    CheckVariable( sbmin, '<=', Sa, truestate="OK", falsestate="ERROR", result_check=True)

    sbpemin = CalcVariable('S_{bpe,min}', dbe/2 + db/2 + ccmin, 'in', 'Required minimum center-to-center distance between existing and post-installed reinforcing bars', code_ref='ESR-3814 4.2.3')
    CheckVariable( sbpemin, '<=', Sbpe, truestate="OK", falsestate="ERROR", result_check=True)

    if Da.value >= 7:
        CheckVariablesText(Da, '>=', Variable('7', 7, ''))
        Ysp = CalcVariable(r'\psi_{s,p}', 1.0, '', 'Modification factor for post-installed bar size', code_ref='ACI 318-14 Table 25.4.2.4')
    else:
        CheckVariablesText(Da, '<=', Variable('6', 6, ''))
        Ysp = CalcVariable(r'\psi_{s,p}', 0.8, '', 'Modification factor for post-installed bar size', code_ref='ACI 318-14 Table 25.4.2.4')

    cbpm = CalcVariable('c_{bp,min}', MIN(cbp, Sa/2), 'in', code_ref='ACI 318-14 R25.4.2.3')
    cbdp = CalcVariable('C_{conf,p}', MAX(2.5, (cbpm + Ktr)/db), '', 'Confinement term for development length', code_ref='ACI 318-14 25.4.2.3')


    Ldpc = CalcVariable('L_{dpc}', BRACKETS(3*Fsy*Yt*Yep*Ysp / (40*SQRT(Fce)*cbdp) )*db, 'in', 'Calculated required development length for post-installed bar', code_ref='ACI 318-14 Eq. 25.4.2.3a')
    # Ldp = CalcVariable('L_{dp}', MAX(Ldmin, Ldpc), 'in', 'Required development length for post-installed bar', code_ref='ACI 318-14 25.4.2.1')

    Lstp = CalcVariable('L_{st,p}', MAX(1.3*Ldpc, twelve_inches), 'in', 'Required tension lap splice length for post-installed reinforcing', code_ref='ACI 318-14 Table 25.5.2.1')
    CheckVariable( Lspe, '>=', Lstp, truestate="OK", falsestate="ERROR", result_check=True)

    BodyHeader('Existing reinforcement tension splice', head_level=2)
    
    if Dae.value <= 6:
        CheckVariablesText(Dae.value, '<=', Variable('6', 6, ''))
        ccmine = CalcVariable('c_{c,min,e}', 1.1875, 'in', 'Minimum concrete cover', code_ref='ESR-3814 4.2.3')
    else:
        CheckVariablesText(Dae.value, '>', Variable('6', 6, ''))
        ccmine = CalcVariable('c_{c,min,e}', 1.5625, 'in', 'Minimum concrete cover', code_ref='ESR-3814 4.2.3')
    
    cbmine = CalcVariable('c_{b,min,e}', dbe/2+ccmine, 'in', 'Required minimum edge distance for existing reinforcing bars', code_ref='ESR-3814 4.2.3')
    CheckVariable( cbmine, '<=', cbe, truestate="OK", falsestate="ERROR", result_check=True)

    sbmine = CalcVariable('S_{b,min,e}', dbe+ccmine, 'in', 'Required minimum center-to-center spacing between existing reinforcing bars', code_ref='ESR-3814 4.2.3')
    CheckVariable( sbmine, '<=', Sa, truestate="OK", falsestate="ERROR", result_check=True)

    if Dae.value >= 7:
        CheckVariablesText(Dae, '>=', Variable('7', 7, ''))
        Yse = CalcVariable(r'\psi_{s,e}', 1.0, '', 'Modification factor for existing bar size', code_ref='ACI 318-14 Table 25.4.2.4')
    else:
        CheckVariablesText(Dae, '<=', Variable('6', 6, ''))
        Yse = CalcVariable(r'\psi_{s,e}', 0.8, '', 'Modification factor for existing bar size', code_ref='ACI 318-14 Table 25.4.2.4')

    cbem = CalcVariable('c_{be,min}', MIN(cbe, Sa/2), 'in', code_ref='ACI 318-14 R25.4.2.3')
    cbde = CalcVariable('C_{conf,e}', MAX(2.5, (cbem + Ktr)/dbe), '', 'Confinement term for development length', code_ref='ACI 318-14 25.4.2.3')


    Ldec = CalcVariable('L_{dec}', BRACKETS(3*Fsye*Yt*Yee*Yse / (40*SQRT(Fce)*cbde) )*dbe, 'in', 'Calculated required development length for existing bar', code_ref='ACI 318-14 Eq. 25.4.2.3a')
    # Ldp = CalcVariable('L_{dp}', MAX(Ldmin, Ldpc), 'in', 'Required development length for post-installed bar', code_ref='ACI 318-14 25.4.2.1')

    Lste = CalcVariable('L_{st,e}', MAX(1.3*Ldec, twelve_inches), 'in', 'Required tension lap splice length for post-installed reinforcing', code_ref='ACI 318-14 Table 25.5.2.1')
    CheckVariable( Lspe, '>=', Lste, truestate="OK", falsestate="ERROR", result_check=True)


    BodyHeader('Reinforcement tensile strength', head_level=2)
    Pntmax = CalcVariable('P_{nt,max}', MIN(Fsy*atot, Fsye*atote), 'lbs', 'Limiting nominal steel tensile strength', code_ref='ACI 318-14 Eq. 22.4.3.1')
    BodyText('Reinforcement is fully developed for both post-installed and existing bars, therefore the weaker bars will fully yield before failure.')
    Phit = CalcVariable(r'\phi_{tens}', 0.9, description='Strength reduction factor for tension controlled section capacity', code_ref='ACI 318-14 Table 21.2.2')
    Pnt = CalcVariable(r'\phi P_{nt}', Phit*Pntmax, 'lbs', 'Design steel tensile strength', code_ref='ESR-3814 4.2.1')
    CheckVariable(Tu, '<=', Pnt )


    BodyHeader('Shear Design', head_level=1)

    BodyHeader('Wall Cap Hoop Tension', head_level=2)
    BodyText('The new wall cap horizontal steel will be designed to take the entire hoop tension of the new dome structure created by outward shear force at the anchors.')
    Thu = CalcVariable('T_{uh}', Vu / Ww * Rt*ft_to_in, 'lbs', 'Hoop tension in wall cap')
    ah = CalcVariable('A_h', PI*(Dh/8/2)**2, 'in^2', 'Area of horizontal bars')
    ahtot = CalcVariable('A_{htot}', ah*Nh, 'in^2', 'Total steel area of horizontal bars')
    Pnmax = CalcVariable('P_{nt,max}', Fsy*ahtot, 'lbs', 'Nominal axial tension capacity of new wall cap', 'ACI 318-14 Eq. 22.4.3.1')
    PPnmax = CalcVariable(r'\phi P_{nt,max}', Phit*Pnmax, description='Design axial tension capacity of new wall cap')
    cpnmax = CheckVariable(Thu, '<=', PPnmax)

    BodyText('As a conservative design check, the joint and existing wall strength will be analyzed as if the shear force from the new dome anchors is transferred through the new connection rather than taken as a hoop force in the new wall cap. This shear would induce an out-of-plane moment on the previously unreinforced portion of the wall until the loads are disributed into the existing prestressing layer.')
    
    BodyHeader('Shear Friction at Wall Cap Joint', head_level=2)
    Vnfl = CalcVariable('V_{nf,l}', Muj*Pntmax, 'lbs', 'Limiting nominal shear friction capacity at joint', code_ref='ACI 318-14 Eq. 22.9.4.2')
    Ac = CalcVariable('A_c', Tw*Ww, 'in^2', 'Area of concrete section resisting shear transfer')
    Fcmin = CalcVariable("f'_{c,min}", MIN(Fce, Fcn), 'psi', 'Minimum concrete strength at joint', code_ref='ACI 318-14 22.9.4.4')

    if Muj > 0.9:
        Vnma = CalcVariable('V_{nm,a}', 0.2*Fcmin*Ac, 'lbs', code_ref='ACI 318-14 Table 22.9.4.4(a)')
        Vnmb = CalcVariable('V_{nm,b}', BRACKETS(480+0.08*Fcmin)*Ac, 'lbs', code_ref='ACI 318-14 Table 22.9.4.4(b)')
        Vnmc = CalcVariable('V_{nm,c}', 1600*Ac, 'lbs', code_ref='ACI 318-14 Table 22.9.4.4(c)')
        Vnmax = CalcVariable('V_{nmax}', MIN(Vnma, Vnmb, Vnmc), 'lbs', code_ref='ACI 318-14 Table 22.9.4.4')
    else:
        Vnmd = CalcVariable('V_{nm,d}', 0.2*Fcmin*Ac, 'lbs', code_ref='ACI 318-14 Table 22.9.4.4(d)')
        Vnme = CalcVariable('V_{nm,e}', 800*Ac, 'lbs', code_ref='ACI 318-14 Table 22.9.4.4(e)')
        Vnmax = CalcVariable('V_{nmax}', MIN(Vnmd, Vnme), 'lbs', code_ref='ACI 318-14 Table 22.9.4.4')
    
    Vnf = CalcVariable('V_{nf}', MIN(Vnfl, Vnmax), 'lbs', 'Nominal shear friction capacity at joint', code_ref='ACI 318-14 22.9.4.4')
    Phiv = CalcVariable(r'\phi_{v}', 0.75, description='Strength reduction factor for shear strength', code_ref='ACI 318-14 Table 21.2.1')
    PVnf = CalcVariable(r'\phi V_{nf}', Phiv*Vnf, 'lbs', 'Design shear friction strength')
    CheckVariable(Vu, '<=', PVnf, code_ref='ACI 318-14 Eq. 22.9.3.1' )



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
