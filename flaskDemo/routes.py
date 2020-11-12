import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskDemo import app, db, bcrypt
from flaskDemo.forms import RegistrationForm, LoginForm, UpdateAccountForm, DeptForm, DeptUpdateForm, DrugForm, DrugUpdateForm, \
    EmployeeUpdateForm, EmployeeForm, ParticipateUpdateForm, TrialForm, TrialUpdateForm
from flaskDemo.models import User, Department, Employee, Protein, Patient, Drug, Clinical_trial, Clinical_trial_stage, Participates, Interacts_with, Phenotype, Protein # , Dependent, Dept_Locations, Employee, Project, Works_On
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html') 

#why is this drug1
@app.route("/")
@app.route("/drug1")
def drug1():   
    results1 = Drug.query.all()
    return render_template('drug_home.html', outString=results1)

@app.route("/dept")
def dept1():
    results = Department.query.all()
    return render_template('dept_home.html', outString=results)

@app.route('/participates1/')
def participates1():
    results = Participates.query.all()
    return render_template('participates_home.html', outString=results)

@app.route('/clinicaltrials')
def clinical1():
    results = Clinical_trial.query.all()
    return render_template('trial_home.html', outString=results)


#@app.route("/Clinical") #on hold until more info
#def clinical():
#    results = Clinical_trial.query.all()
#    results2 = Clinical_trial.query.join(Clinical_trial_stage,Clinical_trial_stage.stage == Works_On.essn) \
#                .add_columns(Employee.ssn, Employee.lname, Works_On.pno) \
##                .join(Project, Project.pnumber == Works_On.pno).add_columns(Project.pname)
 #    results = Employee.query.join(Works_On,Employee.ssn == Works_On.essn) \
 #              .add_columns(Employee.ssn, Employee.lname, Works_On.pno)
 #   return render_template('join.html', title='Clinical Trials', joined_1_n=results, joined_m_n=results2)

@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        # if form.picture.data:
        #     picture_file = save_picture(form.picture.data)
        #     current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    # image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', form=form)


"""
Department Routes
"""


@app.route("/dept")
@login_required
def dept_home():
    """ Show all departments """
    results = Department.query.all()
    return render_template('dept_home.html', outString=results)


@app.route("/dept/new", methods=['GET', 'POST'])
@login_required
def new_dept():
    """ CREATE New Department """
    form = DeptForm()
    if form.validate_on_submit():
        # create department
        department = Department(department_name=form.department_name.data,
                                department_id=form.department_id.data,
                                managerID=form.managerID.data)
        # change manager's department to new department
        manager = Employee.query.get(department.managerID)
        manager.department_id = department.department_id
        db.session.add(department)
        db.session.add(manager)
        db.session.commit()
        flash('You have added a new department!', 'success')
        return redirect(url_for('home'))
    return render_template('create_dept.html', title='New Department',
                           form=form, legend='New Department')


@app.route("/dept/<department_id>")
@login_required
def dept(department_id):
    """ View Department """
    dept = Department.query.get_or_404(department_id)
    manager = Employee.query.get_or_404(dept.managerID)
    # Aggregate query to get total numeber of employees in department
    sql_query = "SELECT COUNT(*) FROM employee WHERE department_id = " + str(dept.department_id) + ";"
    dept_size = db.session.execute(sql_query)
    dept_size = dept_size.first()[0]
    sql_query2 = "SELECT employee_id, employee_name FROM employee WHERE department_id = " + str(dept.department_id) + ";"
    emp_res = list(db.session.execute(sql_query2))
    return render_template('dept.html', title=dept.department_name, dept=dept, manager=manager, employees=emp_res, dept_size=dept_size, now=datetime.utcnow())


@app.route("/dept/<department_id>/update", methods=['GET', 'POST'])
@login_required
def update_dept(department_id):
    """ UPDATE Department """
    dept = Department.query.get_or_404(department_id)
    currentDept = dept.department_name

    form = DeptUpdateForm()
    if form.validate_on_submit():  # notice we are are not passing the dnumber from the form
        if currentDept != form.department_name.data:
            dept.department_name = form.department_name.data
        dept.managerID = form.managerID.data
        # change manager's department to new department
        manager = Employee.query.get(dept.managerID)
        manager.department_id = dept.department_id
        db.session.commit()
        flash('Your department has been updated!', 'success')
        return redirect(url_for('dept', department_id=department_id))
    elif request.method == 'GET':  # notice we are not passing the dnumber to the form

        form.department_id.data = dept.department_id
        form.department_name.data = dept.department_name
        form.managerID.data = dept.managerID
    return render_template('create_dept.html', title='Update Department',
                           form=form, legend='Update Department')


@app.route("/dept/<department_id>/delete", methods=['POST'])
@login_required
def delete_dept(department_id):
    """ DELETE Department"""
    dept = Department.query.get_or_404(department_id)
    db.session.delete(dept)
    db.session.commit()
    flash('The department has been deleted!', 'success')
    return redirect(url_for('home'))


"""
Employee
"""
@app.route("/employee/new", methods=['GET', 'POST'])
@login_required
def new_emp():
    """ CREATE New Employee """
    employees = Employee.query.all()
    # find largest employee id
    max_id = 0
    for emp in employees:
        if emp.employee_id > max_id:
            max_id = emp.employee_id

    new_id = max_id + 1  # new id is next int
    form = EmployeeForm()
    if form.validate_on_submit():
        # create employee
        employee = Employee(employee_name=form.employee_name.data,
                                department_id=form.department_id.data,
                                employee_id=new_id)

        db.session.add(employee)
        db.session.commit()
        flash('You have added a new employee!', 'success')
        return redirect(url_for('home'))
    return render_template('create_emp.html', title='New Employee',
                           form=form, legend='New Employee')


@app.route("/employee/<employee_id>/update", methods=['GET', 'POST'])
@login_required
def update_emp(employee_id):
    """ UPDATE Department """
    emp = Employee.query.get_or_404(employee_id)
    dept = Department.query.get_or_404(emp.department_id)
    form = EmployeeUpdateForm()
    if form.validate_on_submit():
        emp.employee_name = form.employee_name.data
        emp.department_id = form.department_id.data
        db.session.commit()
        flash('Employee has been updated!', 'success')
        return redirect(url_for('dept', department_id=emp.department_id))
    elif request.method == 'GET':  # notice we are not passing the dnumber to the form
        form.department_id.data = emp.department_id  # since form displays department name
        form.employee_name.data = emp.employee_name
        form.employee_id.data = emp.employee_id
    return render_template('create_emp.html', title='Update Employee',
                           form=form, legend='Update Employee')


@app.route("/employee/<employee_id>/delete", methods=['POST'])
@login_required
def delete_emp(employee_id):
    """ DELETE Employee"""
    emp = Employee.query.get_or_404(employee_id)
    flash('You cannot delete a manager. Reassign manager for department before deleting.', 'danger')
    return redirect(url_for('update_dept', department_id=emp.department_id))
    ##TODO check if employee is manager
    db.session.delete(emp)
    db.session.commit()
    flash('The employee has been deleted!', 'success')
    return redirect(url_for('home'))



"""
Drugs
"""

@app.route("/drug/<drug_name>")
@login_required
def drug(drug_name):
    drug = Drug.query.get_or_404(drug_name)
    drug = drug.query.join(Interacts_with, Drug.drug_name == Interacts_with.drug_name) \
        .add_columns(Drug.drug_name, Interacts_with.phenotype_id, Interacts_with.protein_id, Drug.drug_type) \
        .join(Protein, Protein.protein_id == Interacts_with.protein_id).add_columns(Protein.protein_name, Protein.subunit_num) \
        .filter(Drug.drug_name == drug_name)
    return render_template('interactions.html',  outString=drug, Name=drug_name)

@app.route("/drug/new", methods=['GET', 'POST'])
@login_required
def new_drug():
    """ CREATE New Drug """
    form = DrugForm()
    if form.validate_on_submit():
        drug = Drug(drug_name=form.drug_name.data, drug_type=form.drug_type.data)
        db.session.add(drug)
        db.session.commit()
        flash('You have added a new drug!', 'success')
        return redirect(url_for('home'))
    return render_template('create_drug.html', title='New Drug',
                           form=form, legend='New Drug')

@app.route("/drug/<drug_name>/update", methods=['GET','POST'])
@login_required
def update_drug(drug_name):
    drug = Drug.query.get_or_404(drug_name)
    #currentAssign = (assign.essn, assign pno)
    currentName = drug.drug_name
    currentType = drug.drug_type
    form = DrugUpdateForm()
    if form.validate_on_submit():          # notice we are are not passing the dnumber from the form
        if currentName !=form.drug_name.data:
            drug.drug_name=form.drug_name.data
        if currentType != form.drug_type.data:
            drug.drug_type=form.drug_type.data
        db.session.commit()
        flash('Your drug has been updated!', 'success')
        return redirect(url_for('drug', drug_name=drug_name))
    elif request.method == 'GET':              # notice we are not passing the dnumber to the form
        form.drug_type.data=drug.drug_type
        form.drug_name.data = drug.drug_name
    return render_template('create_drug.html', title='Update Drug',
                           form=form, legend='Update Drug')



"""
Participates
"""

@app.route("/participates/<patient_id>/<stage_num>/<clinical_trial_id>/")
@login_required
def participates(patient_id, stage_num, clinical_trial_id):
    participates = Participates.query.filter_by(patient_id=patient_id, stage_num=stage_num, clinical_trial_id=clinical_trial_id).first()
    return render_template('participates.html', title=str(participates.patient_id), participates=participates, now=datetime.utcnow())


@app.route("/participates/<patient_id>/<clinical_trial_id>/<stage_num>/update", methods=['GET','POST'])
@login_required
def update_participates(patient_id, stage_num, clinical_trial_id):
    participant = Participates.query.filter_by(patient_id=patient_id, stage_num=stage_num, clinical_trial_id=clinical_trial_id).first()
    # #currentAssign = (assign.essn, assign pno)
    currentID = participant.patient_id
    currentStatus = participant.Completes_trial
    form = ParticipateUpdateForm()
    if form.validate_on_submit():
        # if currentID !=form.patient_id.data:
        #     participant.patient_id=form.patient_id.data
        if currentStatus !=form.Completes_trial.data:
            participant.Completes_trial=form.Completes_trial.data
        participant.start_date = form.start_date.data
        participant.End_date = form.End_date.data
        db.session.commit()
        flash('Your participant has been updated!', 'success')
        return redirect(url_for('participates', patient_id=patient_id, stage_num=stage_num, clinical_trial_id=clinical_trial_id))
    elif request.method == 'GET':
        # TODO these are not setting the value for the dropdowns
        form.patient_id.data = participant.patient_id
        form.clinical_trial_id.data = participant.clinical_trial_id
        form.stage_num.data = participant.stage_num
        form.Completes_trial.data = participant.Completes_trial
        form.start_date.data = participant.start_date
        form.End_date.data = participant.End_date
    return render_template('create_participate.html', title='Update Participant', form=form,participant=participant, legend='Update Participant')


'''
clinical trials
'''
#maybe we try to link this to participates
@app.route('/clinicaltrials/<clinical_trial_id>')
@login_required
def clinical_trial(clinical_trial_id):
    clinical_trial = Clinical_trial.query.get_or_404(clinical_trial_id)
    return render_template('clinical_trial.html', title='Clinical Trials', OutString=clinical_trial, now=datetime.utcnow())


    #this works
@app.route("/clinicaltrials/new", methods=['GET', 'POST'])
@login_required
def new_trial():
    """ CREATE New Trial """
    form = TrialForm()
    if form.validate_on_submit():
        clinical_trial = Clinical_trial(clinical_trial_id=form.clinical_trial_id.data, lead_physician=form.lead_physician.data)
        db.session.add(clinical_trial)
        db.session.commit()
        flash('You have added a new clinical trial!', 'success')
        return redirect(url_for('clinical1'))
    return render_template('create_trial.html', title='New Clinical Trial',
                            form=form, legend='New Clinical Trial')  

@app.route("/clinicaltrials/<clinical_trial_id>/update", methods=['GET','POST'])
@login_required
def update_trials(clinical_trial_id):
    clinical_trial = Clinical_trial.query.get_or_404(clinical_trial_id)
    currentID = clinical_trial.clinical_trial_id
    currentPhysician = clinical_trial.lead_physician
    form = TrialUpdateForm()
    if form.validate_on_submit():         
        if currentID !=form.clinical_trial_id.data:
            clinical_trial.clinical_trial_id=form.clinical_trial_id.data
        if currentPhysician !=form.lead_physician.data:
            clinical_trial.lead_physician=form.lead_physician.data
        db.session.commit()
        flash('This clinical trial has been updated!', 'success')
        return redirect(url_for('clinical1'))
    elif request.method == 'GET':              
        form.clinical_trial_id.data = clinical_trial.clinical_trial_id
        form.lead_physician = clinical_trial.lead_physician
    return render_template('create_trial.html', title='Update Clinical Trial',
                            form=form, legend='Update Clinical Trial')





