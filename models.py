from . import db
import enum

#Status of a book class
class Status(enum.Enum):
    reading = 1 
    finished = 2 
    waiting = 3 
    skimmed = 4
    dnf = 5

#Student objects represent the student using the program
class Students(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), nullable=False)
    name = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)

#Book objects represent the books a student entered
class Books(db.Model): 
    __tablename__ = 'books'
    book_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    name = db.Column(db.String(), nullable=False)
    author = db.Column(db.String(), nullable = False)
    pages = db.Column(db.Integer, nullable = True)
    bookcover = db.Column(db.String(), nullable = False)
    status = db.Column(db.Enum(Status))
    currentpage = db.Column(db.Integer(), nullable = True)

#Challenges objects represent the reading challenges
class Challenges(db.Model): 
    __tablename__ = 'challenges'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=True)
    badge = db.Column(db.String(), nullable = False)

#Goal objects represent the goals a student has set
class Goals(db.Model): 
    __tablename__ = 'goals'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    goal = db.Column(db.String())
    checked = db.Column(db.Boolean)

#Data objects holds whether or not the student has completed a challenge
class Data(db.Model): 
    __tablename__ = 'datas'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    checked = db.Column(db.Boolean)

