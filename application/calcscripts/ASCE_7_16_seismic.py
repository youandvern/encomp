from application.calcscripts.process.basedefinitions import CalculationTitle, DescriptionHead, Assumption, \
        DeclareVariable, CalcVariable, BodyText, BodyHeader, HeadCollection, SetupCollection, CalcCollection, FootCollection, AssumCollection
from application.calcscripts.process.calcmodels import FaASCE716, FvASCE716, AISCSectionsRectangular
from application.calcscripts.process.listoptions import site_class_options, rectangular_section_sizes, wf_section_sizes
from application.calcscripts.process.latexExp import *


# STATUS: Completed, Production Ready

def create_calculation(updated_input={}):
    HeadCollection.head_instances.clear()
    AssumCollection.assum_instances.clear()
    SetupCollection.setup_instances.clear()
    CalcCollection.calc_instances.clear()
    FootCollection.foot_instances.clear()




    ###   DEFINE TITLE, DESCRIPTION, ASSUMPTIONS, AND INPUTS   ###

    CalculationTitle('ASCE 7-16 Seismic Design')

    DescriptionHead("Seismic design horizontal and vertical acceleration determination in accordance with ASCE 7-16")

    Assumption("ASCE 7-16 controls seismic design")
    Assumption("The exceptions of section 11.4.8 are met for site class D, E or F")
    Assumption("Tank meets the criteria for exceptions in section 15.4.1")
    Assumption("The tank period (T) is less than the long-period transition period (TL)")

    R = DeclareVariable('R', 3.25, 'in', "Response modification factor for anchored flexible base tank", code_ref='Table 15.4-2, ASCE 7-10')
    I_e = DeclareVariable('I_e', 1.5, '', 'IBC importance factor for earthquake loading (essential facility)', code_ref='Table 1.5-2, ASCE 7-10')
    T_L = DeclareVariable('T_L', 12, 's', 'Long-period transition period')
    site_class = DeclareVariable('SiteClass', 'D', '', 'Site site class of soil conditions at project', input_type="select", input_options=site_class_options)
    Ss = DeclareVariable('S_s', 1.0, 'g', 'Spectral response acceleration parameter at short periods')
    S1 = DeclareVariable('S_1', 0.5, 'g', 'Spectral response acceleration parameter at 1s period')



    ###   DO NOT DEFINE INPUTS BELOW HERE OR EDIT THE FOLLOWING SECTION   ###

    if len(updated_input)>0:
        for input_variable in DeclareVariable.instances:
            new_value = updated_input.get(input_variable.name)
            if new_value:
                input_variable._set_value(new_value)

    ###   DEFINE CALCULATION, BODY HEADER, AND BODY TEXT   ###

# Interpolate Fa and Fv from ASCE tables
    fa_obj =  FaASCE716.objects(SiteClass=site_class.value).first()
    if Ss.value <= 0.25:
        fa_calc = fa_obj.ss25
    elif Ss.value < 0.50:
        fa_calc = fa_obj.ss25 + (Ss.value - 0.25)*(fa_obj.ss50 - fa_obj.ss25)/(0.50-0.25)
    elif Ss.value < 0.75:
        fa_calc = fa_obj.ss50 + (Ss.value - 0.50)*(fa_obj.ss75 - fa_obj.ss50)/(0.75-0.50)
    elif Ss.value < 1.0:
        fa_calc = fa_obj.ss75 + (Ss.value - 0.75)*(fa_obj.ss100 - fa_obj.ss75)/(1.0-0.75)
    elif Ss.value < 1.25:
        fa_calc = fa_obj.ss100 + (Ss.value - 1.0)*(fa_obj.ss125 - fa_obj.ss100)/(1.25-1.0)
    else:
        fa_calc = fa_obj.ss125

    fv_obj =  FvASCE716.objects(SiteClass=site_class.value).first()
    if S1.value <= 0.1:
        fv_calc = fv_obj.s11
    elif S1.value < 0.2:
        fv_calc = fv_obj.s11 + (S1.value - 0.1)*(fv_obj.s12 - fv_obj.s11)/(0.2-0.1)
    elif S1.value < 0.3:
        fv_calc = fv_obj.s12 + (S1.value - 0.2)*(fv_obj.s13 - fv_obj.s12)/(0.3-0.2)
    elif S1.value < 0.4:
        fv_calc = fv_obj.s13 + (S1.value - 0.3)*(fv_obj.s14 - fv_obj.s13 )/(0.4-0.3)
    elif S1.value < 0.5:
        fv_calc = fv_obj.s14 + (S1.value - 0.4)*(fv_obj.s15  - fv_obj.s14 )/(0.5-0.4)
    elif S1.value < 0.6:
        fv_calc = fv_obj.s15 + (S1.value - 0.5)*(fv_obj.s16 - fv_obj.s15)/(0.6-0.5)
    else:
        fv_calc = fv_obj.s16

    Fa = CalcVariable('F_a', fa_calc, '','Short period site coefficient', code_ref='Table 11.4-1, ASCE 7-16')
    Fv = CalcVariable('F_v', fv_calc, '', 'Long period site coefficient', code_ref='Table 11.4-2, ASCE 7-16')

    s_ms = CalcVariable('S_{MS}', Fa*Ss, 'g', '', code_ref="Eq.11.4-1, ASCE 7-16")
    s_ds = CalcVariable('S_{DS}', (2/3)*s_ms, 'g', 'Design spectral response acceleration factor at short periods', result_check=True, code_ref='Eq.11.4-3, ASCE 7-16')

    s_m1 = CalcVariable('S_{M1}', Fv*S1, 'g', '', code_ref="Eq.11.4-2, ASCE 7-16")
    s_d1 = CalcVariable('S_{D1}', (2/3)*s_m1, 'g', 'Design spectral response acceleration factor at a 1 second period', result_check=True, code_ref='Eq.11.4-4, ASCE 7-16')

    BodyHeader('Effective Seismic horizontal acceleration (Section 12.8.1.1):')
    c_smin0 = Variable('0.01 g',0.01,unit="g")
    c_smin1 = CalcVariable('C_{s,min1}', MAX(0.044*s_ds*I_e,c_smin0), 'g', code_ref='Eq. 15.4-3')
    if S1.value >= 0.6:
        c_smin2 = CalcVariable('C_{s,min2}', 0.5*S1/(R/I_e), 'g','Since S1 > 0.6g:', code_ref='Eq. 15.4-4')
    else:
        c_smin2 = CalcVariable('C_{s,min2}', 0, 'g','Since S1 < 0.6g:')
    c_scalc = CalcVariable('C_{s,calc}', s_ds/(DIV(R,I_e)), 'g')
    c_s = CalcVariable('C_s', MAX(c_smin1, c_smin2, c_scalc), 'g',code_ref='strength')
    c_sa = CalcVariable('C_{sa}', c_s/1.4, 'g', code_ref='allowable', result_check=True)

    BodyHeader('Effective seismic vertical acceleration (Section 12.4.2.2):')
    c_v = CalcVariable('C_v', 0.2*s_ds, 'g',code_ref='strength')
    c_va = CalcVariable('C_{va}', c_v/1.4, 'g', code_ref='allowable', result_check=True)



    calculation_sum = {'head':HeadCollection.head_instances, 'assum': AssumCollection.assum_instances, 'setup':SetupCollection.setup_instances, 'calc':CalcCollection.calc_instances, 'foot':FootCollection.foot_instances}
    return calculation_sum
