from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.sql import func

db = SQLAlchemy()

shortlist = db.Table(
    'shortlist',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'),
              primary_key=True),
    db.Column('program_id', db.Integer, db.ForeignKey('program.id'),
              primary_key=True),
    db.Column('date_added', db.DateTime(timezone=True),
              server_default=func.now())
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150))

    gpa = db.Column(db.Float, default=0.0)
    toefl_score = db.Column(db.Integer, default=0)
    internship_exp = db.Column(db.Integer, default=0)
    research_papers = db.Column(db.Integer, default=0)

    shortlisted_programs = db.relationship(
        'Program', secondary=shortlist, backref='interested_students'
    )


class University(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    country = db.Column(db.String(100), nullable=False)
    qs_rank = db.Column(db.Integer)
    logo_url = db.Column(db.String(300))

    programs = db.relationship('Program', backref='university', lazy=True)


class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100))
    university_id = db.Column(db.Integer, db.ForeignKey('university.id'))

    min_gpa = db.Column(db.Float, nullable=False)
    min_toefl = db.Column(db.Integer, default=0)
    tuition_fee = db.Column(db.String(100))
    deadline = db.Column(db.String(50))

    research_focus = db.Column(db.Boolean, default=False)
    industry_focus = db.Column(db.Boolean, default=False)

    source_url = db.Column(db.String(300))
    last_updated = db.Column(db.DateTime(timezone=True), default=func.now())

    def calculate_compatibility(self, user):
        """
        Logic to match User stats vs Program reqs.
        Returns: (Status_String, Bootstrap_Color_Class)
        """
        score = 0

        if user.gpa >= self.min_gpa:
            score += 2
        elif user.gpa >= (self.min_gpa - 0.2):
            score += 1

        if user.toefl_score >= self.min_toefl:
            score += 1

        if self.research_focus and user.research_papers > 0:
            score += 2
        if self.industry_focus and user.internship_exp >= 3:
            score += 1

        if score >= 4:
            return "Safe / High Chance", "success"
        elif score >= 2:
            return "Target / Medium Chance", "warning"
        else:
            return "Reach / Low Chance", "danger"
