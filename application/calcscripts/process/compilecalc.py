from pydoc import locate

def compile_calculation(compile_calc_path, compile_update_vals=False, compile_updated_items=[]):
    calc_errors = ''
    html_strings = {'head':[], 'assum': [], 'setup':[], 'calc':[], 'foot':[]}

    updated_input = {}
    if compile_update_vals:
        for item in compile_updated_items:
            updated_input[item.name] = item.value

    create_calculation = locate(compile_calc_path)
    totallist = create_calculation( updated_input=updated_input)



    headlist = totallist['head']
    assumlist = totallist['assum']
    setuplist = totallist['setup']
    calclist = totallist['calc']

    if headlist:
        for item in headlist:
            html_strings['head'].append([item.__class__.__name__, str(item)])
    if assumlist:
        for item in assumlist:
            html_strings['assum'].append([item.__class__.__name__, str(item)])
    if setuplist:
        for item in setuplist:
            if item.__class__.__name__ == 'DeclareVariable' and item.input_type != "number":
                declare_string = fr"\mathrm{{{item.name}}} = \mathrm{{{item.value}}} \ {item.unit}"
            elif item.__class__.__name__ =='DeclareTable':
                declare_string = item.value
            else:
                declare_string = str(item)
            html_strings['setup'].append([item.__class__.__name__, item.description, declare_string])
    if calclist:
        length_guess = None
        calc_type = 'Long'
        name_only = None
        symbolic_string = None
        substituted_string = None
        result_unit = None
        for item in calclist:
            description_text = item.description
            code_ref = item.code_ref
            if code_ref:
                code_ref = f"[{code_ref}]"
            if item.__class__.__name__ =='BodyHeader':
                calc_type = str(int(float(item.head_level)+1))
            elif item.__class__.__name__ =='CalcVariable':
                length_guess = item.get_operation_length()
                name_only = item.name
                symbolic_string = fr"= {item.operation.strSymbolic()}"
                substituted_string = fr"= {item.operation.strSubstituted()}"
                try:
                    result_unit = fr"= {item.strResultWithUnit()}"
                    if item.unformat_operation_sym().strip() == item.unformat_operation_sub().strip(): # use unformat_operation_sym() and unformat_operation_sub() instead
                        calc_type = 'Float'
                    elif length_guess <= 50:
                        calc_type = 'Short'
                    else:
                        calc_type = 'Long'
                except ValueError:
                    result_unit = r"= 0"
                    item.operation = 0
                    calc_errors += fr"Variable \( {name_only} \) could not be calculated. There has been a math domain error. Please review and change input variables to an acceptable domain."
            elif item.__class__.__name__ =='CalcTable':
                calc_type = 'Table'
                name_only = item.name
                symbolic_string = item.value[0] # headings
                substituted_string = item.value[:]
                result_unit = ''
            elif item.__class__.__name__ =='CheckVariable':
                name_only = "Check  "
                symbolic_string = item.strSymbolic()
                substituted_string = item.strSubstituted()
                result_unit = item.result()
            elif item.__class__.__name__ =='CheckVariablesText':
                symbolic_string = item.strSymbolic()

            html_strings['calc'].append([item.__class__.__name__, description_text, code_ref, calc_type, name_only, symbolic_string, substituted_string, result_unit])

    return {"html_strings": html_strings, 'all_items':totallist}, calc_errors
