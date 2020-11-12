from datetime import datetime
from flaskDemo import db, login_manager
from flask_login import UserMixin
from functools import partial
from sqlalchemy import orm

db.Model.metadata.reflect(db.engine)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Protein(db.Model):
    __table__ = db.Model.metadata.tables['protein']

class Drug(db.Model):
    __table__ = db.Model.metadata.tables['drug']

class Phenotype(db.Model):
    __table__ = db.Model.metadata.tables['phenotype']

class Interacts_with(db.Model):
    __table__ = db.Model.metadata.tables['interacts_with']

class Side_effect(db.Model):
    __table__ = db.Model.metadata.tables['side_effect']

class Clinical_trial(db.Model):
    __table__ = db.Model.metadata.tables['clinical_trial']

class Clinical_trial_stage(db.Model):
    __table__ = db.Model.metadata.tables['clinical_trial_stage']

class Patient(db.Model):
    __table__ = db.Model.metadata.tables['patient']

class Demonstrates(db.Model):
    __table__ = db.Model.metadata.tables['demonstrates']

class Department(db.Model):
    __table__ = db.Model.metadata.tables['department']

class Employee(db.Model):
    __table__ = db.Model.metadata.tables['employee']

class Participates(db.Model):
    __table__ = db.Model.metadata.tables['participates']
