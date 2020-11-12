from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, DateField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,Regexp
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flaskDemo import db
from flaskDemo.models import User, Department, Drug, Employee, Protein, Interacts_with, Side_effect, Patient, Clinical_trial, Clinical_trial_stage, Phenotype, Demonstrates, Participates # , getDepartment, getDepartmentFactory, Project, Works_on
from wtforms.fields.html5 import DateField

#Insertion
me = Drug(drug_name = 'Zolgensma', drug_type = 'Gene therapy')
db.session.add(me)
db.session.commit()


drugs = Drug.query.with_entities(Drug.drug_name)
results=list()
for row in drugs:
    rowDict=row._asdict()
    results.append(rowDict)
DRUGS = sorted([(row['drug_name'],row['drug_name']) for row in results])

patients = Participates.query.with_entities(Participates.patient_id).distinct()
results=list()
for row in patients:
    rowDict=row._asdict()
    results.append(rowDict)
PATIENTS = sorted([(row['patient_id'],row['patient_id']) for row in results])

cs = Participates.query.with_entities(Participates.clinical_trial_id)
results=list()
for row in cs:
    rowDict=row._asdict()
    results.append(rowDict)
CS = sorted([(row['clinical_trial_id'],row['clinical_trial_id']) for row in results])

sn = Participates.query.with_entities(Participates.stage_num)
results=list()
for row in sn:
    rowDict=row._asdict()
    results.append(rowDict)
SN = sorted([(row['stage_num'],row['stage_num']) for row in results])

'''
Account forms

'''
class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        #domain = email.data.split('@')[1]
        if '@pharma.com' not in email.data:
            raise ValidationError('Please use your company email.')
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    # picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

# class PostForm(FlaskForm):
#     title = StringField('Title', validators=[DataRequired()])
#     content = TextAreaField('Content', validators=[DataRequired()])
#     submit = SubmitField('Post')



"""
Department Forms
"""

# Get employee choices for manager form
employees = Employee.query.all()
print(employees)
emp_results = list()
for row in employees:
    rowDict=row.__dict__
    emp_results.append(rowDict)
employee_choices = [(row['employee_id'], row['employee_name']) for row in emp_results]


class DeptUpdateForm(FlaskForm):
    department_id = HiddenField("")
    department_name = StringField('Department Name:', validators=[DataRequired(),Length(max=15)])
    managerID = SelectField("Manager's ID", choices=employee_choices)  # myChoices defined at top
    submit = SubmitField('Update this department')

# got rid of def validate_dnumber

    def validate_dname(self, department_name):    # apparently in the company DB, dname is specified as unique
         dept = Department.query.filter_by(department_name=department_name.data).first()
         if dept and (str(dept.department_id) != str(self.department_id.data)):
             raise ValidationError('That department name is already being used. Please choose a different name.')

    def validate_managerID(self, managerID):  # manager must work in same department
        # employees can only manage one department
        emp = Employee.query.filter_by(employee_id=managerID.data).first()
        if emp:
            departments = Department.query.all()
            for dept in departments:
                if str(emp.employee_id) == str(dept.managerID):
                    raise ValidationError('That employee is already a manager. Please choose another employee.')
    #
    # def validate_department_id(self, department_id):  # because dnumber is primary key and should be unique
    #     dept = Department.query.filter_by(department_id=department_id.data).first()
    #     if dept:
    #         raise ValidationError('That department number is taken. Please choose a different one.')


class DeptForm(DeptUpdateForm):
    department_id = IntegerField('Department Number', validators=[DataRequired()])
    department_name = StringField('Department Name:', validators=[DataRequired(),Length(max=15)])
    submit = SubmitField('Add this department')

    def validate_department_id(self, department_id):  # because dnumber is primary key and should be unique
        dept = Department.query.filter_by(department_id=department_id.data).first()
        if dept:
            raise ValidationError('That department number is taken. Please choose a different one.')

    def validate_managerID(self, managerID):  # manager must work in same department
        emp = Employee.query.filter_by(employee_id=managerID.data).first()
        if emp:
            depts = Department.query.all()
            for dept in depts:
                if str(emp.employee_id) == str(dept.managerID):
                    raise ValidationError('That employee is already a manager. Please choose another employee.')

"""
Employee Forms
"""
# Get department choices for employee form
departments = Department.query.all()
dept_results = list()
for row in departments:
    rowDict=row.__dict__
    dept_results.append(rowDict)
dept_choices = [(row['department_id'], row['department_name']) for row in dept_results]



class EmployeeUpdateForm(FlaskForm):
    employee_id = HiddenField("")
    employee_name = StringField('Employee Name:', validators=[DataRequired(),Length(max=60)])
    department_id = SelectField("Department ID", choices=dept_choices)  # myChoices defined at top
    submit = SubmitField('Update this employee')


# got rid of def validate_dnumber

class EmployeeForm(EmployeeUpdateForm):
    # department_id = IntegerField('Department Number', validators=[DataRequired()])
    # department_name = StringField('Department Name:', validators=[DataRequired(),Length(max=15)])
    submit = SubmitField('Add this employee')



'''
DrugForm and DrugUpdateForm
'''

class DrugUpdateForm(FlaskForm):
    drug_name = SelectField('Drug Name', choices=DRUGS) #drop down
    drug_type=StringField('Drug Type:', validators=[DataRequired(),Length(max=15)])
    submit = SubmitField('Update this assignment')


# got rid of def validate_dnumber

    def validate_dname(self, drug_type):    # apparently in the company DB, dname is specified as unique
         drug = Drug.query.filter_by(drug_type=drug_type.data).first()
         if drug and (str(drug.drug_name) != str(self.drug_name.data)):
             raise ValidationError('That drug name is already being used. Please choose a different name.')


class DrugForm(FlaskForm):
    drug_name=StringField('Drug Name', validators=[DataRequired(),Length(max=70)])
    drug_type=StringField('Drug Type:', validators=[DataRequired(),Length(max=70)])
    submit = SubmitField('Add this drug')

    def validate_assign(self, drug_name):  
        drug = Drug.query.filter_by(drug_name=drug_name.data).first()
        if drug:
            raise ValidationError('That drug name is currently assigned. Please choose a different one.')

'''
ParticipateUpdate
'''

class ParticipateUpdateForm(FlaskForm):
    patient_id = HiddenField("")
    clinical_trial_id = HiddenField("")
    stage_num = HiddenField("")

    # patient_id = SelectField('Patient ID', choices=PATIENTS) #drop down
    # clinical_trial_id= SelectField('Clinical Trial ID', choices=CS)
    # stage_num = SelectField('Stage Number', choices=SN)
    Completes_trial=SelectField('Completes trial', validators=[DataRequired()], choices=["yes", "no"])
    start_date=StringField('Start Date',validators=[DataRequired(),Length(max=30)])
    End_date=StringField('End Date', validators=[DataRequired(),Length(max=30)])
    submit = SubmitField('Update this participant')

    def validate_start_date(self, start_date):
        # TODO
        pass


    def validate_end_date(self, end_date):
        # TODO
        pass


'''
Clinical Trial

'''
clinical_trials = Clinical_trial.query.all()
print(clinical_trials)
CT_results = list()
for row in clinical_trials:
    rowDict=row.__dict__
    CT_results.append(rowDict)
CT_choices = [(row['clinical_trial_id'], row['lead_physician']) for row in CT_results]
print(CT_choices)

class TrialUpdateForm(FlaskForm):
    clinical_trial_id = SelectField('Clinical Trial ID', choices=CT_choices)
    lead_physician=StringField('Lead Physician Name:', validators=[DataRequired(),Length(max=15)])
    #lead_physician = StringField('Lead Physician Name:', validators=[DataRequired(),Length(max=70)])
    submit = SubmitField('Update clinical trial.')
    
    def validate_assign(self, lead_physician):  
        clinical_trial = Clinical_trial.query.filter_by(lead_physician = lead_physician.data).first()
        #clinical_trial = Clinical_trial.query.filter_by(clinical_trial_id=clinical_trial_id.data).first()
        if clinical_trial and (str(clinical_trial.clinical_trial_id) != str(self.lead_physician.data)):
            raise ValidationError('That clinical trial ID is currently assigned. Please choose a different one.')
         
    
    
class TrialForm(FlaskForm):
    clinical_trial_id = IntegerField('Clinical Trial ID', validators= [DataRequired()])
    lead_physician=StringField('Lead Physician Name:', validators=[DataRequired(),Length(max=15)])
    #lead_physician = StringField('Lead Physician Name:', validators=[DataRequired(),Length(max=70)])
    submit = SubmitField('Add this clinical trial')
    
    def validate_assign(self, clinical_trial_id):  
        clinical_trial = Clinical_trial.query.filter_by(clinical_trial_id=clinical_trial_id.data).first()
        if clinical_trial:
            raise ValidationError('That clinical trial ID is currently assigned. Please choose a different one.')
