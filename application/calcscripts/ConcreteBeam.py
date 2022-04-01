from application.calcscripts.process.basedefinitions import CalculationTitle, DescriptionHead, Assumption, CheckVariable, CheckVariablesText, \
        DeclareVariable, DeclareTable, CalcTable, CalcVariable, BodyText, BodyHeader, HeadCollection, SetupCollection, CalcCollection, FootCollection, AssumCollection
from application.calcscripts.process.listoptions import reinforcement_bar_sizes
from application.calcscripts.process.latexExp import *

# STATUS: Completed, Production Ready
def create_calculation(updated_input={}):
    HeadCollection.head_instances.clear()
    AssumCollection.assum_instances.clear()
    SetupCollection.setup_instances.clear()
    CalcCollection.calc_instances.clear()
    FootCollection.foot_instances.clear()


    ###   DEFINE TITLE, DESCRIPTION, ASSUMPTIONS, AND INPUTS   ###

    CalculationTitle('Concrete Beam Design')

    DescriptionHead("Concrete beam section capacity designed in accordance with ACI 318-14.")

    Assumption("ACI 318-14 controls member design per sections referenced below")
    Assumption("Beam is subject to flexural and/or shear load demands only")



    fc = DeclareVariable("f'_c", 4000, 'psi', 'Specified compressive strength of concrete')
    fy = DeclareVariable('f_y', 60, 'ksi', 'Yield strength of reinforcement steel')
    Es = DeclareVariable('E_s', 29000, 'ksi', 'Modulus of elasticity of reinforcement steel')

    b = DeclareVariable('b', 12, 'in', 'Beam section width')
    h = DeclareVariable('h', 24, 'in', 'Beam height')

    # columns to be: [bar_id, As, db, x, y ]
    # units to be:   ['', in^2, in, in, in ]
    default_bars_table = [['bar_id', 'As', 'db', 'x', 'y' ], ["bar1", .2, .5, 3, 22 ], ["bar2", .2, .5, 6, 19 ], ["bar3", .2, .5, 9, 22 ]]
    bars_table = DeclareTable("Reinforcement", default_bars_table, [], 'Beam Reinforcement Properties')


    ###   DO NOT DEFINE INPUTS BELOW HERE OR EDIT THE FOLLOWING SECTION   ###

    if len(updated_input)>0:
        for input_variable in DeclareVariable.instances + DeclareTable.instances:
            if new_value := updated_input.get(input_variable.name):
                input_variable._set_value(new_value)

    ###   DEFINE CALCULATION, BODY HEADER, AND BODY TEXT   ###



    k_to_lb = Variable('1000 \ \mathrm{lbs/kip}', 1000, 'lbs/kip')
    ft_to_in = Variable('12 \ \mathrm{in/ft}', 12, 'in/ft')

    # handle error more gracefully
    if len(bars_table.value) <=1 or len(bars_table.value[0]) <= 4:
        bars_table.value = default_bars_table

    BodyHeader('Flexural Capacity', head_level=1) ######################################################################################
    ey = CalcVariable('\varepsilon _y', fy/Es, '', 'Yield strain of reinforcement steel' )
    ec_var = CalcVariable('\varepsilon _c', 0.003, '', 'Crushing strain of concrete')
    B1 = CalcVariable('\beta _1', 0.85, '', 'Equivalent rectangular compressive stress block depth ratio', code_ref='Table 22.2.2.4.3') ## UPDATE $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    bars_val = bars_table.value # columns to be: [bar_id, As, db, x, y ]

    c_assume = 0.001
    c_change = 2
    c_last_change = 0

    ec = ec_var.result()
    Es_val = Es.value
    fy_val = fy.value
    fc_val = fc.value
    b_val = b.value
    B1_val = B1.result()
    tolerance = 0.001
    c_solved = False

    n = 0
    while not c_solved:
        n+=1
        if n>100:
            c_assume = 0.00100
            break

        Ptot = - 0.85 * fc_val/1000 * b_val * B1_val * c_assume
        i = 0
        for bar in bars_val:
            i+=1
            if i == 1:
                continue # skip headers
            esi = ec * (bar[4] - c_assume) / c_assume
            fsi = Es_val * esi
            if abs(fsi) > fy_val:
                fsi = fy_val * ( esi / abs(esi) )

            Ptot += bar[1] * fsi
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

    c = CalcVariable('c', c_assume, 'in', 'Neutral axis depth required for section equilibrium', result_check=True)
    bars_output = [
        [
            'Bar #',
            'A <sub>s</sub> (in<sup>2</sup>)',
            '&epsilon;<sub>s</sub>',
            'f<sub>s</sub> (ksi)',
            'y (in)',
        ]
    ]

    et_max_val = 0
    bars_sum = 0
    i = 0
    for bar in bars_val:
        i+=1
        if i == 1:
            continue # skip headers
        esi = ec * (bar[4] - c_assume) / c_assume
        if esi > et_max_val:
            et_max_val = esi
        fsi = Es_val * esi
        if abs(fsi) > fy_val:
            fsi = fy_val * ( esi / abs(esi) )

        bars_output.append([bar[0], round(bar[1], 2), round(esi, 5), round(fsi,1), round(bar[4], 2)])
        bars_sum += bar[1]*fsi*bar[4]

    et_max = CalcVariable('\varepsilon _{t,max}', abs(et_max_val), '', 'Maximimum tensile strain in reinforcement steel')
    bars_out = CalcTable('ReinforcementResults', bars_output, result_check=True)

    bar_moment = CalcVariable('\Sigma A_{si} f_{si} y_{si}', bars_sum, 'k-in', 'Net moment contribution from reinforcement steel')

    Mn = CalcVariable('M_n', bar_moment - 0.85*(fc/1000)*b*B1*c*(B1*c)/2, 'k-in', 'Nominal moment capacity of beam section', result_check=False)

    phi = CalcVariable('\phi', MAX(0.65, MIN(0.65, 0.65 + 0.25*BRACKETS((et_max-ey)/(0.005 - ey)))), '', 'Strength reduction factor', code_ref='Table 21.2.2')

    phi_mn = CalcVariable('\phi M_n', phi*Mn/ft_to_in, 'k-ft', 'Design moment capacity of beam section', result_check=True )


    return {
        'head': HeadCollection.head_instances,
        'assum': AssumCollection.assum_instances,
        'setup': SetupCollection.setup_instances,
        'calc': CalcCollection.calc_instances,
        'foot': FootCollection.foot_instances,
    }
