from application.models import User, Project, CalcInput, CalcType, DeletedProject, DeletedCalc
from bson.objectid import ObjectId


def getUserProjects(user_id):
    projects = list(User.objects.aggregate(*[
    {
        '$lookup': {
            'from': 'project',
            'localField': '_id',
            'foreignField': 'user_id',
            'as': 'r1'
        }
    }, {
        '$unwind': {
            'path': '$r1',
            'includeArrayIndex': 'r1_id',
            'preserveNullAndEmptyArrays': False
        }
    }, {
        '$match': {
            '_id': ObjectId(user_id)
        }
    }
    ]))
    return projects

def getProjCalcs(project_id):
    calcs = list(Project.objects.aggregate(*[
    {
        '$lookup': {
            'from': 'calc_input',
            'localField': '_id',
            'foreignField': 'project_id',
            'as': 'rcalc'
        }
    }, {
        '$unwind': {
            'path': '$rcalc',
            'includeArrayIndex': 'rcalc_id',
            'preserveNullAndEmptyArrays': False
        }
    }, {
        '$match': {
            '_id': ObjectId(project_id)
        }
    }
]))
    return calcs

def removeCalculationFromDB(calc_id, new_project_id = False):
    calculation = CalcInput.objects(_id = calc_id).first()
    if calculation:
        if new_project_id:
            project_id = new_project_id
        else:
            project_id = calculation.project_id
        deleted_calculation = DeletedCalc(calc_name=calculation.calc_name, description=calculation.description, calc_type_id=calculation.calc_type_id, project_id=project_id, calc_input_dict=calculation.calc_input_dict)
        deleted_calculation.save()
        CalcInput.objects(_id = calc_id).delete()


def deleteProject(project_id):
    project = Project.objects(_id = project_id).first()
    if project:
        deleted_project = DeletedProject(previous_id=project_id, project_name=project.project_name, description=project.description, user_id=project.user_id)
        deleted_project.save()
        new_project_id = deleted_project._id
        deleted_calcs = CalcInput.objects(project_id = project_id)
        for calc in deleted_calcs:
            deleteCalculation(calc._id, new_project_id=new_project_id)
        Project.objects(_id = project_id).delete()
