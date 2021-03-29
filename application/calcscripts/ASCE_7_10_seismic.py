from application.calcscripts.process.basedefinitions import CalculationTitle, DescriptionHead, Assumption, CheckVariable, \
        DeclareVariable, CalcVariable, BodyText, BodyHeader, HeadCollection, SetupCollection, CalcCollection, FootCollection, AssumCollection
from application.calcscripts.process.calcmodels import FaASCE710, AISCSectionsRectangular
from application.calcscripts.process.listoptions import site_class_options, rectangular_section_sizes, wf_section_sizes
from application.calcscripts.process.latexExp import *


def create_calculation(updated_input={}):
    HeadCollection.head_instances.clear()
    AssumCollection.assum_instances.clear()
    SetupCollection.setup_instances.clear()
    CalcCollection.calc_instances.clear()
    FootCollection.foot_instances.clear()



    ###   DEFINE TITLE, DESCRIPTION, ASSUMPTIONS, AND INPUTS   ###

    CalculationTitle('ASCE 7-10 Seismic Design')

    DescriptionHead("Seismic horizontal and vertical acceleration determination in accordance with ASCE 7-10")

    Assumption("2010 version of ASCE 7")
    Assumption("IBC and CBC do not control")

    R = DeclareVariable('R', 3.25, 'in', "Response modification factor for anchored flexible base tank", code_ref='Table 15.4-2, ASCE 7-10')
    I_e = DeclareVariable('I_e', 1.5, '', 'IBC importance factor for earthquake loading (essential facility)', code_ref='Table 1.5-2, ASCE 7-10')
    site_class = DeclareVariable('SiteClass', 'D', '', 'Site site class of soil conditions at project', input_type="select", input_options=site_class_options)
    Ss = DeclareVariable('S_s', 1.888, 'g', 'Spectral response acceleration parameter at short periods')
    S1 = DeclareVariable('S_1', 0.621, 'g', 'Spectral response acceleration parameter at 1s period')
    # section_name = DeclareVariable('Section', 'HSS12X3X5/16', '', 'AISC section size')



    ###   DO NOT DEFINE INPUTS BELOW HERE OR EDIT THE FOLLOWING SECTION   ###

    if len(updated_input)>0:
        for input_variable in DeclareVariable.instances:
            new_value = updated_input.get(input_variable.name)
            if new_value:
                input_variable._set_value(new_value)

    ###   DEFINE CALCULATION, BODY HEADER, AND BODY TEXT   ###

    fa_obj =  FaASCE710.objects(SiteClass=site_class.value).first()
    if Ss.value <= 0.25:
        fa_calc = fa_obj.ss25
    else:
        fa_calc = fa_obj.ss125
        # fa_calc = 1.1

    Fa = CalcVariable('F_a', fa_calc, '','Short period site coefficient', code_ref='Table 11.4-1, ASCE 7-10')
    Fv = CalcVariable('F_v', 1.5, '', 'Long period site coefficient', code_ref='Table 11.4-2, ASCE 7-10')

    s_ms = CalcVariable('S_{MS}', Fa*Ss, 'g', 'MCE spectral response acceleration factor at short periods', code_ref="Eq.11.4-1, ASCE 7-10")
    s_ds = CalcVariable('S_{DS}', (2/3)*s_ms, 'g', 'Design spectral response acceleration factor at short periods', code_ref='Eq.11.4-3, ASCE 7-10')

    s_m1 = CalcVariable('S_{M1}', Fa*S1, 'g', 'MCE spectral response acceleration factor at a 1 second period', code_ref="Eq.11.4-2, ASCE 7-10")
    s_d1 = CalcVariable('S_{D1}', (2/3)*s_m1, 'g', 'Design spectral response acceleration factor at a 1 second period', code_ref='Eq.11.4-4, ASCE 7-10')

    BodyHeader('Effective Seismic horizontal acceleration:')
    BodyText('(strength)')
    c_s = CalcVariable('C_s', s_ds/(DIV(R,I_e)), 'g', result_check=True)
    BodyText('(allowable)')
    c_sa = CalcVariable('C_{sa}', c_s/1.4, 'g')

    BodyHeader('Effective Seismic vertical acceleration:')
    BodyText('(strength)')
    c_v = CalcVariable('C_v', 0.2*s_ds, 'g', result_check=True)
    BodyText('(allowable)')
    c_va = CalcVariable('C_{va}', c_v/1.4, 'g')
    #
    # section = AISCSectionsRectangular.objects(AISC_name=section_name.value).first()
    # nomB = CalcVariable('b_{nom}', section.B, 'in', 'Nominal section width', result_check=True)
    # actualB = CalcVariable('b_{des}', section.b, 'in', 'Actual (design) section width', result_check=True)
    #
    # testervar = CalcVariable('Long_{sub}', SQRT(Fa + Fv**Fa - POW((0.001*c_s*c_sa/c_va),3))+s_ms*19+R/I_e*Ss*99916, 'g')
    #
    # anothervar = CalcVariable('V_{env}', POW((s_m1+s_d1)/s_ms,4)-POW(s_ds, 4),'g')
    #
    # compare = CheckVariable(s_m1, '>', s_ms, result_check=True)

    calculation_sum = {'head':HeadCollection.head_instances, 'assum': AssumCollection.assum_instances, 'setup':SetupCollection.setup_instances, 'calc':CalcCollection.calc_instances, 'foot':FootCollection.foot_instances}
    return calculation_sum
