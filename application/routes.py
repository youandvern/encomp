from application import application, db
from flask import render_template, request, json, jsonify, Response, redirect, flash, url_for, session, send_file
from werkzeug.utils import secure_filename
from application.models import User, Project, CalcInput, CalcType
from application.forms import LoginForm, RegisterForm, ProjectForm, CalcForm, CalcTypeForm, ChangeProjectForm, ChangeCalcForm
from application.mongo_query import getUserProjects, getProjCalcs, removeCalculationFromDB, deleteProject
from application.calcscripts.process.compilecalc import compile_calculation
import shutil
import os




@application.route("/")
@application.route("/index")
@application.route("/home")
def index():
    return render_template('index.html', index = True)

@application.route("/myprojects", methods=['GET', 'POST'])
def landing():
    if not session.get('username'):
        return redirect(url_for('index'))
    else:
        my_projects = getUserProjects(session.get('user_id'))

        selected_project_id = request.form.get('selected_project_id')
        if selected_project_id:
            session['current_project_id'] = selected_project_id
            selected_project = Project.objects(_id=selected_project_id).first()
            session['current_p_name'] = selected_project.project_name
            session['current_p_description'] = selected_project.description

        if session.get('current_project_id'):
            select_comment = False
            project_calcs = getProjCalcs(session.get('current_project_id'))
        else:
            select_comment = True
            project_calcs = False

        ###### Import Calculation  #####
        if request.method == 'POST':
            file = request.files.get('upload_calc')
            if file and file.filename == '':
                flash("No file has been selected")
            elif file and session.get('current_project_id'):
                filename = secure_filename(file.filename)
                upload_content = file.read()
                calc_import_dict = json.loads(upload_content)
                new_calc_from_import = CalcInput(calc_name = calc_import_dict['calc_name'], description = calc_import_dict['description'],calc_type_id= calc_import_dict['calc_type_id'], project_id = session.get('current_project_id'), calc_input_dict=calc_import_dict['calc_input_dict'], left_header=calc_import_dict['left_header'], center_header=calc_import_dict['center_header'],right_header=calc_import_dict['right_header'])
                new_calc_from_import.save()
                flash(f"You have uploaded {filename} successfully as: {calc_import_dict['calc_name']}", "success")
                return redirect(url_for('landing'))

        selected_calc_id = request.form.get('selected_calc_id')
        if selected_calc_id:
            session['current_calc_id'] = selected_calc_id
            selected_calculation = CalcInput.objects(_id=selected_calc_id).first()
            session['current_c_name'] = selected_calculation.calc_name
            session['current_c_description'] = selected_calculation.description
            return redirect(url_for('design_dashboard'))

        ############------------ADD PROJECT FORM-----------##############
        pform = ProjectForm()
        if pform.validate_on_submit():
            project_name = pform.project_name.data
            description = pform.description.data

            project = Project( project_name=project_name, description=description, user_id=session.get('user_id')) # user_id=ObjectId(),
            project.save()

            flash(f"You have saved {project_name}", "success")
            return redirect(url_for('landing'))

        ############------------CHANGE PROJECT NAME FORM-----------##############
        pnameform = ChangeProjectForm()
        if pnameform.validate_on_submit():
            new_project_name = pnameform.new_project_name.data
            new_description = pnameform.new_description.data

            project = Project.objects( _id = session['current_project_id'] ).first()
            project.project_name = new_project_name
            project.description = new_description
            project.save()

            flash(f"You have updated {new_project_name}", "success")
            return redirect(url_for('landing'))

        ############------------ADD calc FORM-----------##############
        cform = CalcForm()
        if cform.validate_on_submit():
            calc_name = cform.calc_name.data
            description = cform.description.data
            calc_type_name = cform.calc_type.data
            calc_type = CalcType.objects(type_name=calc_type_name).first()

            calc_type_id = calc_type._id
            project_id = session.get('current_project_id')

            calc = CalcInput( calc_name=calc_name, description=description, calc_type_id=calc_type_id, project_id=project_id) # user_id=ObjectId(),
            calc.save()

            flash(f"You have saved {calc_name}", "success")
            return redirect(url_for('landing'))

        # Delete project
        delete_project_trigger = request.form.get('delete_current_project')
        if delete_project_trigger:
            deleteProject(session.get('current_project_id'))
            deleted_project_name = session.get('current_p_name')
            session.pop('current_project_id')
            session.pop('current_p_name')
            session.pop('current_p_description')
            if session.get('current_calc_id'):
                session.pop('current_calc_id')
                session.pop('current_c_name')
                session.pop('current_c_description')
            flash(f"You have deleted {deleted_project_name}", "success")
            return redirect(url_for('landing'))

    return render_template('landing.html', my_projects=my_projects, project_calcs=project_calcs, select_comment=select_comment, pform = pform, cform=cform, pnameform = pnameform,current_p_description =session.get('current_p_description'), current_p_name = session.get('current_p_name'),  project=True)

@application.route("/about")
def about():
    return render_template('about.html', about = True)


@application.route("/login", methods=['GET', 'POST'])
def login():
    if session.get('username'):
        flash(f"You are already logged in, {session.get('username')}")
        return redirect(url_for('landing'))
    form = LoginForm()
    if form.validate_on_submit():
        email       = form.email.data  # request.form.get("email")
        password    = form.password.data

        user = User.objects(email=email).first()  # gets first occurance not as array, could also do User.objects(email=email)[0]
        if user and user.get_password(password):
            flash(f"Welcome {user.first_name}, you are successfully logged in!", "success")
            session['user_id'] = str(user._id)
            session['username'] = user.first_name
            session['current_project_id'] = ""
            return redirect(url_for('landing'))
        elif user:
            flash("Password is incorrect.", "danger")
        else:
            flash("Sorry, email not found.", "danger")
    return render_template("login.html", title="Login", login=True, form=form)

@application.route("/logout")
def logout():
    current_user_id = session.get('user_id')
    # dir_path = f"C:/Users/ayoung/encomp/application/static/jsonfiles/{current_user_id}"
    dir_path = f"/home/ubuntu/encomp/application/static/jsonfiles/{current_user_id}"
    if os.path.exists(dir_path):
        try:
            shutil.rmtree(dir_path)
        except OSError as e:
            flash("Error: %s : %s" % (dir_path, e.strerror))
    [session.pop(key) for key in list(session.keys())]
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))

@application.route("/register", methods=['GET', 'POST'])
def register():
    if session.get('username'):
        flash(f"You are already registered, {session.get('username')}")
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User( email=email, first_name=first_name, last_name=last_name) # user_id=ObjectId(),
        user.set_password(password)
        user.save()

        flash("You are successfully registered", "success")
        return redirect(url_for('index'))

    return render_template("register.html", title="New User Registration", register=True, form=form)


@application.route("/addproject", methods=['GET', 'POST'])
def addproject():
    if not session.get('username'):
        flash("You are not logged in")
        return redirect(url_for('index'))
    form = ProjectForm()
    if form.validate_on_submit():
        project_name = form.project_name.data
        description = form.description.data

        project = Project( project_name=project_name, description=description, user_id=session.get('user_id')) # user_id=ObjectId(),
        project.save()

        flash(f"You have saved {project_name}", "success")
        return redirect(url_for('landing'))

    return render_template("addproject.html", title="New Project", project=True, form=form)

@application.route("/addcalc", methods=['GET', 'POST'])
def addcalc():
    if not session.get('username'):
        flash("You are not logged in")
        return redirect(url_for('index'))
    form = CalcForm()
    if form.validate_on_submit():
        calc_name = form.calc_name.data
        description = form.description.data
        calc_type = form.calc_type.data

        calc_type_id = '5fa9c9b693dbf6a9101aae15'
        project_id = '5fa9c9b693dbf6a9101aae15'
        calc_input_dict = '{"a" : 3, "b" : 4}'

        calc = CalcInput( calc_name=calc_name, description=description, calc_type_id=calc_type_id, project_id=project_id, calc_input_dict=calc_input_dict) # user_id=ObjectId(),
        calc.save()

        flash(f"You have saved {calc_name}", "success")
        return redirect(url_for('landing'))

    return render_template("addcalc.html", title="New Calculation", project=True, form=form)

@application.route("/addtype", methods=['GET', 'POST'])
def addtype():
    if not session.get('username'):
        flash("You are not logged in")
        return redirect(url_for('index'))
    form = CalcTypeForm()
    if form.validate_on_submit():
        type_name = form.type_name.data
        description = form.description.data

        calctype = CalcType( type_name=type_name, description=description)
        calctype.save()

        flash(f"You have saved {type_name}", "success")
        return redirect(url_for('landing'))

    return render_template("addtype.html", title="New Calculation Type", project=True, form=form)

@application.route("/design_dashboard", methods=['GET', 'POST'])
def design_dashboard():

    if not session.get('current_calc_id'):
        return redirect(url_for('index'))

    ############------------GET CURRENT CALCULATION INFO AND DB OBJECTS-----------##############
    current_calc = CalcInput.objects( _id = session['current_calc_id'] ).first()
    current_calc_type = CalcType.objects( _id = current_calc.calc_type_id ).first()
    calc_file_name = current_calc_type.file_name
    if not current_calc:
        return render_template("design.html", calculation_name= "No calc found for id:",calculation_description=session['current_calc_id'])

    ############------------GET CALCULATION INPUT OBJECTS BY RUNNING CALC -----------##############
    calculation_path = f'application.calcscripts.{calc_file_name}.create_calculation'
    calc_items_and_strings, calc_errors = compile_calculation(compile_calc_path=calculation_path)
    calc_items = calc_items_and_strings['all_items']
    setup_items = calc_items['setup']
    calc_inputs = []
    for item in setup_items:
        if item.__class__.__name__ == 'DeclareVariable':
            calc_inputs.append(item)


    ############------------POPULATE CHANGE CALC NAME FORM DATA -----------##############
    calcnameform = ChangeCalcForm()
    left_header=current_calc.left_header
    center_header=current_calc.center_header
    right_header=current_calc.right_header
    # if request.method == 'GET':
    calcnameform.new_description.data = current_calc.description
    calcnameform.new_left_header.data = left_header
    calcnameform.new_center_header.data = center_header
    calcnameform.new_right_header.data = right_header


    ############------------CHANGE CALCULATION NAME FORM-----------##############
    def change_calculation_name(posted_dict):
        if calcnameform.validate_on_submit():
            new_calc_name = posted_dict.get('new_calc_name')
            new_description = posted_dict.get('new_description')
            new_left_header = posted_dict.get('new_left_header')
            new_center_header = posted_dict.get('new_center_header')
            new_right_header = posted_dict.get('new_right_header')

            current_calc.calc_name = new_calc_name
            current_calc.description = new_description
            current_calc.left_header = new_left_header
            current_calc.center_header = new_center_header
            current_calc.right_header = new_right_header
            current_calc.save()

            flash(f"You have updated {new_calc_name}", "success")
            return redirect(url_for('design_dashboard'))
        else:
            flash("Error in text submitted")
            return None

    ############------------DELETE CALCULATION FORM-----------##############
    def delete_current_calculation():
        removeCalculationFromDB(session['current_calc_id'])
        deleted_calc_name = session.get('current_c_name')
        session.pop('current_calc_id')
        session.pop('current_c_name')
        session.pop('current_c_description')
        flash(f"You have deleted {deleted_calc_name}", "success")
        return redirect(url_for('landing'))


    ############------------WHEN FORM IS SUBMITTED-----------##############
    if request.method == 'POST':
        form_submit_dict = request.form
        # flash(f"posted:  {form_submit_dict}")
        # submitted_form = form_submit_dict.get('submit')
        # flash(f"submitted form: {submitted_form}")
        update_results     = 'update_results_submitted' in form_submit_dict
        show_report        = 'show_calc_report' in form_submit_dict
        print_report       = 'print_calc_report' in form_submit_dict
        change_calc_name   = 'change_calc_name' in form_submit_dict
        delete_calc        = 'delete_current_calc' in form_submit_dict
        export_calc        = 'export_calc' in form_submit_dict

        if update_results:
            current_calc.calc_input_dict = form_submit_dict
            current_calc.save()
        elif show_report:
            return redirect(url_for('calcreport', print_report="view"))
        elif print_report:
            return redirect(url_for('calcreport', print_report="print"))
        elif change_calc_name:
            return change_calculation_name(form_submit_dict)
        elif delete_calc:
            return delete_current_calculation()
        elif export_calc:
            return export_calculation()


    ############------------RENDER INPUT AND OUTPUT VALUES-----------##############
    # update input variables
    calc_saved_input = current_calc.calc_input_dict
    if isinstance(calc_saved_input, dict):
        for item in calc_inputs:
            var_name = item.name
            saved_input = calc_saved_input.get(var_name)
            if saved_input:
                item._set_value(saved_input)

            else:
                calc_saved_input[var_name] = item.value
        current_calc.calc_input_dict = calc_saved_input
        current_calc.save()

    else:
        current_calc.calc_input_dict = {'a': 3, 'b': 4}
        current_calc.save()

    #  get calculation output objects
    calc_items_and_strings, calc_errors = compile_calculation(compile_calc_path=calculation_path, compile_update_vals=True, compile_updated_items=calc_inputs)
    if calc_errors:
        flash(calc_errors)
    calc_items = calc_items_and_strings['all_items']
    result_items = calc_items['calc']
    calc_results = []
    for item in result_items:
        if item.__class__.__name__ == 'CalcVariable' or item.__class__.__name__ == 'CheckVariable':
            if item.result_check:
                calc_results.append(item)

    # SAVE HTML STRINGS FOR CALC REPORT
    stringsdict = calc_items_and_strings['html_strings']
    session['stringsdict'] = stringsdict

    return render_template("design.html", calculation_name= current_calc.calc_name,calculation_description=current_calc.description, calc_inputs=calc_inputs, calc_results=calc_results, calcnameform=calcnameform,  design=True)


@application.route("/calcreport<print_report>", methods=['GET', 'POST'])
def calcreport(print_report):
    current_calc = CalcInput.objects( _id = session['current_calc_id'] ).first()
    current_calc_type = CalcType.objects( _id = current_calc.calc_type_id ).first()
    calc_name = current_calc_type.type_name

    left_header = current_calc.left_header
    center_header = current_calc.center_header
    right_header = current_calc.right_header

    stringsdict = session.get('stringsdict')


    headstrings = stringsdict['head']
    assumstrings = stringsdict['assum']
    assum_length = len(assumstrings)
    setupstrings = stringsdict['setup']
    calcstrings = stringsdict['calc']

    return render_template("calculations/view_calc_report.html", print_report=print_report, calc_title = calc_name, headstrings = headstrings, assumstrings = assumstrings, assum_length=assum_length, setupstrings=setupstrings, calcstrings=calcstrings, left_header=left_header, center_header=center_header, right_header=right_header )


@application.route("/exportcalculation")
def export_calculation():
    if session.get('user_id') and session.get('current_calc_id'):
        current_user_id = session.get('user_id')
        current_calc = CalcInput.objects( _id = session['current_calc_id'] ).first()
        if current_calc:
            calc_file_name =  current_calc.calc_name.replace(" ", "_")
            calc_export_dict = {'calc_name': current_calc.calc_name, 'description': current_calc.description, 'calc_type_id': str(current_calc.calc_type_id), 'calc_input_dict': current_calc.calc_input_dict, 'left_header': current_calc.left_header, 'center_header': current_calc.center_header, 'right_header': current_calc.right_header}
            # file_path = f"C:/Users/ayoung/encomp/application/static/jsonfiles/{current_user_id}/{calc_file_name}.json"
            file_path = f"/home/ubuntu/encomp/application/static/jsonfiles/{current_user_id}/{calc_file_name}.json"
            # dir_path = f"C:/Users/ayoung/encomp/application/static/jsonfiles/{current_user_id}"
            dir_path = f"/home/ubuntu/encomp/application/static/jsonfiles/{current_user_id}"
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            with open(file_path,"w") as file:
                json.dump(calc_export_dict,file)
            return send_file(file_path, as_attachment=True, attachment_filename=f"{calc_file_name}_export.json")
        else:
            flash("Current calculation not found.", "danger")
    else:
        return redirect(url_for('index'))
