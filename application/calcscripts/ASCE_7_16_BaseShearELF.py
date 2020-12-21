from application.calcscripts.process.basedefinitions import CalculationTitle, DescriptionHead, Assumption, CheckVariable, \
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

    CalculationTitle('ASCE 7-16 Seismic Base Shear Calculation')

    DescriptionHead("With structure weight, height, and seismic setting, calculate the seismic design base shear for the main lateral force resisting system.")

    ##

    Assumption("Structure is a building or building-like")
    Assumption("The revisions included in section 15.5 do not apply")
    Assumption("Equivalent lateral force procedure is permitted in accordance with Table 12.6-1")

    W = DeclareVariable('W_d', 100, 'kips', 'Effective seismic weight per section 12.7.2')
    hn = DeclareVariable('h_n', 16, 'ft', 'Structural height defined in section 11.2')
    R = DeclareVariable('R', 3, '', 'Response modification factor')
    Ie = DeclareVariable('I_e', 1, '', 'Importance factor per section 11.5.1')
    Sds = DeclareVariable('S_{DS}', 0.85, 'g', 'Design spectral response acceleration parameter in the short period range')
    Sd1 = DeclareVariable('S_{D1}', 0.45, 'g', 'Design spectral response acceleration parameter at a period of one second')
    S1 = DeclareVariable('S_1', 0.55, 'g', 'Mapped maximum considered earthquake spectral response acceleration parameter')
    TL = DeclareVariable('T_L', 12, 's', 'Long-period transition period')
    Ct = DeclareVariable('C_t', 0.02, '', 'Coefficient to find approximate fundamental period per Table 12.8-2')
    xt = DeclareVariable('x', 0.75, '', 'Coefficient to reduce height in approximate fundamental period calculation per Table 12.8-2')





    ###   DO NOT DEFINE INPUTS BELOW HERE OR EDIT THE FOLLOWING SECTION   ###

    if len(updated_input)>0:
        for input_variable in DeclareVariable.instances:
            new_value = updated_input.get(input_variable.name)
            if new_value:
                input_variable._set_value(new_value)

    ###   DEFINE CALCULATION, BODY HEADER, AND BODY TEXT   ###
    Ta = CalcVariable('T_a', Ct*hn**xt, 's', 'Approximate fundamental period', code_ref='ASCE 12.8-7')

    Csi = CalcVariable('C_{si}', Sds/(R/Ie), '', code_ref='ASCE 12.8-2')

    if Ta.result() <= TL.result():
        Csmax = CalcVariable('C_{smax}', Sd1/(Ta*R/Ie), '', code_ref='ASCE 12.8-3')
    else:
        Csmax = CalcVariable('C_{smax}', Sd1*TL/(Ta**2*R/Ie), '', code_ref='ASCE 12.8-3')

    Csmin1 = CalcVariable('C_{smin1}', 0.044*Sds*Ie, '', code_ref='ASCE 12.8-5')
    Csmin2 = CalcVariable('C_{smin2}', 0.01, '', code_ref='ASCE 12.8-5')

    if S1.result() >= 0.6:
        Csmin3 = CalcVariable('C_{smin3}', 0.5*S1/(R/Ie), '', code_ref='ASCE 12.8-6')
    else:
        Csmin3 = CalcVariable('C_{smin3}', 0, '', 'Since S1 is less than 0.6g, ASCE equation 12.8-6 does not apply')

    Cs = CalcVariable('C_{s}', MIN(Csmax, MAX(Csi, Csmin1, Csmin2, Csmin3)), '', 'Seismic response coefficient', code_ref='ASCE 12.8.1.1')

    V = CalcVariable('V', Cs*W, 'kips', 'Seismic base shear', code_ref='ASCE 12.8-1', result_check=True)
    Vv = CalcVariable('V_v', 0.2*V, 'kips', 'Seismic vertical component', code_ref='ASCE 12.4.2.2', result_check=True)






    calculation_sum = {'head':HeadCollection.head_instances, 'assum': AssumCollection.assum_instances, 'setup':SetupCollection.setup_instances, 'calc':CalcCollection.calc_instances, 'foot':FootCollection.foot_instances}
    return calculation_sum
