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

    CalculationTitle('EBMUD Oakland Digester 3 Wall Cap')

    DescriptionHead(
        "Structural design capacity calculations for a new installed wall cap connected to the top of an existing corewall.")

    Assumption("ACI 318-14 controls member design")
    Assumption(
        "Design loads are taken from provided Westech DuoSphere calculation report Revision E dated 7/27/2021")
    Assumption(
        "Existing concrete strength is calculated per ACI 214.4R-10 from the provided core strengths by Testing Engineers Inc dated 11/1/21")
    Assumption("The wall cap will have enough stiffness to evenly distribute loads among the new anchors")
        

    Tu = DeclareVariable('T_u', 23000, 'lbs', 'Design ultimate tensile demand per cable group', 'Westech Calcs Pg. 45', input_type="number", min_value=0)
    Vu = DeclareVariable('V_u', 3500, 'lbs', 'Design ultimate shear demand per cable group', 'Westech Calcs Pg. 45', input_type="number", min_value=0)

    Fce = DeclareVariable("f'_c", 3100, 'psi', 'Existing concrete strength', 'ACI 214.4R-10 Eq. 9-9', input_type='number', min_value=0)
    Fsy = DeclareVariable('f_y', 60000, 'psi', 'Steel yeild strength', input_type='number', min_value=0)

    Tw = DeclareVariable('t_w', 11, 'in', 'Wall thickness', input_type='number', min_value=0)
    Ww = DeclareVariable('w_w', 75, 'in', 'Length of wall section per cable group', input_type='number', min_value=0)

    Na = DeclareVariable("N_a", 8, "", 'Number of anchors per cable group', input_type='number', max_value=20, min_value=1)

    Sa = DeclareVariable(
        'S_a', 8, 'in', 'spacing of anchors', input_type='number')

    Da = DeclareVariable('D_a', reinforcement_bar_sizes[1], '', 'Anchor bar size (eighth of an inch diameter)',
                         input_type='select', input_options=reinforcement_bar_sizes)

    Ha = DeclareVariable('h_{eff,a}', 5, 'in', 'Embedment depth of anchor', input_type='number', min_value=0)

    Hh = DeclareVariable('l_{dh}', 12, 'in', 'Hooked development length of anchor in wall cap')



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
    futa = CalcVariable('f_{uta}', MIN(1.9*Fsy, 125000), 'psi', code_ref='ACI 318-14 17.4.1.2')
    Nsa = CalcVariable('N_{sa}', atot*futa, 'lbs', 'Nominal strength of anchor in tension')
    Phis = CalcVariable(r'\phi_{steel}', 0.65, description='Strength reduction factor for steel tension', code_ref='ACI 318-14 17.3.3')
    PNsa = CalcVariable(r'\phi N_{sa}', Phis*Nsa, 'lbs')
    cpnsa = CheckVariable(Tu, '<=', PNsa, code_ref='ACI 318-14 Table 17.3.1.1' )

    Freduce = CalcVariable('R_{reduction}', PNsa / Tu, '', 'Development length reduction factor', 'ACI 318-14 25.4.10.1' )
    Ldha = CalcVariable('L_{dha}', Freduce*Fsy*0.7*db/(50*SQRT(Fce)), 'in', 'Calculated hooked development length of dowel (assuming side cover > 2.5")', 'ACI 318-14 25.4.3.1a')
    BodyText("Minimum required hooked development length for anchor:")
    Ldhb = CalcVariable('L_{dhb}', 8*db, 'in', code_ref= 'ACI 318-14 25.4.3.1b')
    Ldhc = CalcVariable('L_{dhc}', Fsy*0.7*db/(50*SQRT(Fce)), 'in', code_ref='ACI 318-14 25.4.3.1c')

    Ldh = CalcVariable('L_{dh}', MAX(Ldha, Ldhb, Ldhc), 'in', 'Hooked development length of anchor bar' ,code_ref= 'ACI 318-14 25.4.3.1b')
    cldh = CheckVariable( Hh, '>=', Ldh, truestate="OK", falsestate="ERROR", result_check=True)

    
    BodyHeader('Bond Strength', head_level=2)
    bonduncr = CalcVariable(r'\tau_{uncr}', 1560, 'psi', 'Adhesive anchor bond strength', code_ref='ESR-3187 Revised May 2021')

    if Da.value < 7:
        bondcr = CalcVariable(r'\tau_{cr}', 1080, 'psi', 'Adhesive anchor bond strength (cracked)', code_ref='ESR-3187 Revised May 2021')
    else:
        bondcr = CalcVariable(r'\tau_{cr}', 853, 'psi', 'Adhesive anchor bond strength (cracked)', code_ref='ESR-3187 Revised May 2021')

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
    cpnsa = CheckVariable(Tu, '<=', PNag, code_ref='ACI 318-14 Table 17.3.1.1' )

    BodyHeader('Concrete Breakout Strength', head_level=2)

    heflim = CalcVariable('h_{ef,lim}', MAX(camax/1.5, Sa/3), 'in', 'Limit to effective embedment length for concrete breakout strength in tension', 'ACI 318-14 17.4.2.3' )
    hef = CalcVariable('h_{ef}', MIN(Ha, heflim), 'in', 'Effective embedment length for concrete breakout strength in tension')
    cacb = CalcVariable('c_{acb}', 2*hef, 'in', 'Critical edge distance, tension breakout', 'ACI 318-14 17.7.6')

    Yecn = CalcVariable(r'\psi_{ec,N}', 1.0, '', 'Modification factor for eccentricity', code_ref='ACI 318-14 17.4.2.4')

    hef15 = CalcVariable('1.5h_{ef}', 1.5*hef, 'in')
    if camin.result() >= hef15.result():
        CheckVariablesText(camin, '>=', hef15)
        Yedn = CalcVariable(r'\psi_{ed,N}', 1.0, '', 'Modification factor for edge effects', code_ref='ACI 318-14 17.4.2.5a')
    else:
        CheckVariablesText(camin, '<', hef15)
        Yedn = CalcVariable(r'\psi_{ed,N}', 0.7+0.3*camin/hef15, '', 'Modification factor for edge effects', code_ref='ACI 318-14 17.4.2.5b')
    
    Ycn = CalcVariable(r'\psi_{c,N}', 1.0, '', 'Modification factor for uncracked sections', code_ref='ACI 318-14 17.4.2.6')

    if camin.result() >= cacb.result():
        CheckVariablesText(camin, '>=', cacb)
        Ycpn = CalcVariable(r'\psi_{cp,N}', 1.0, '', 'Modification factor to control splitting', code_ref='ACI 318-14 17.4.2.7a')
    elif camin.result()/cacb.result() >= hef15.result()/cacb.result():
        CheckVariablesText(camin, '<', cacb)
        Ycpn = CalcVariable(r'\psi_{cp,N}', camin/cacb, '', 'Modification factor to control splitting', code_ref='ACI 318-14 17.4.2.7b')
    else:
        CheckVariablesText(camin, '<', cacb)
        Ycpn = CalcVariable(r'\psi_{cp,N}', 1.0, '', 'Modification factor to control splitting', code_ref='ACI 318-14 17.4.2.7b note')
    
    kc = CalcVariable('k_c', 17, '', 'Post-installed anchor breakout factor', 'ACI 318-14 17.4.2.2')
    Nb = CalcVariable('N_{b}', kc*SQRT(Fce)*hef**1.5, 'lbs', 'Basic concrete breakout strength of single adhesive anchor in tension in cracked concrete', 'ACI 318-14 17.4.2.2a')
    Anco = CalcVariable('A_{Nco}', 9*hef**2, 'in^2', 'Projected concrete failure area of a single adhesive anchor', code_ref='ACI 318-14 17.4.2.1c')
    ca1 = CalcVariable('c_{ar}', MIN(1.5*hef, camin), 'in', 'Maximum radial projected length of concrete failure for each anchor')
    ca2 = CalcVariable('c_{aa}', MIN(1.5*hef, Sa/2), 'in', 'Maximum angular projected length of concrete failure for each anchor')
    Anc = CalcVariable('A_{Nc}', 2*ca1*2*ca2, 'in^2', 'Projected influence area of the group of adhesive anchors')

    Ncbg = CalcVariable('N_{cbg}', Yecn*Yedn*Ycn*Ycpn*Nb*Anc/Anco, 'lbs', 'Nominal concrete breakout strength of the anchor group', 'ACI 318-14 Eq. 17.4.2.1b')
    Phic = CalcVariable(r'\phi_{conc}', 0.75, description='Strength reduction factor for breakout failure with tension reinforcing across failure plane', code_ref='ACI 318-14 17.3.3')
    PNcbg = CalcVariable(r'\phi N_{cbg}', Phic*Ncbg, 'lbs')
    cpnsa = CheckVariable(Tu, '<=', PNcbg, code_ref='ACI 318-14 Table 17.3.1.1' )

    










    




    calculation_sum = {'head': HeadCollection.head_instances, 'assum': AssumCollection.assum_instances,
                       'setup': SetupCollection.setup_instances, 'calc': CalcCollection.calc_instances, 'foot': FootCollection.foot_instances}
    return calculation_sum
