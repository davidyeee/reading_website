from distutils.log import error
from nis import cat
from flask import Blueprint, render_template, request, flash, redirect, session, url_for
from .models import Students, Challenges, Data
from . import db
from passlib.hash import pbkdf2_sha256 as hasher # type: ignore
from functools import wraps


auth = Blueprint('auth', __name__)
#Function that ensure user is logged in
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'id' in session:
            return f(*args, **kwargs)
        else:
            return redirect("/")
    return wrap
	
#Login Page
@auth.route('/', methods=['GET','POST'])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        student = Students.query.filter_by(email = email).first()
        if student:
            if hasher.verify(password, student.password):
                session["id"] = student.id
                return redirect(url_for('views.home', index=0))
            else:
                flash("Your password is incorrect!", category='error')
        else:
            flash("User not found, try creating an account first!", category='error')
    return render_template("login.html")
    
#Signup page
@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        password2 = request.form["password2"]
        if password != password2:
            flash("The passwords don't match!", category='error')
            return render_template("signup.html")
        # only person from the school with this email address can access the website
        elif "school.com" not in email:
            flash("Your email doesn't belong to this organization!", category='error')
            return render_template("signup.html")
        elif name == None or email == None or password == None or password2 == None:
            flash("Please fill out all fields!", category='error')
            return render_template("signup.html")
        else:
            hash = hasher.hash(password)
            student = Students(email=email, name=name, password=hash)
            
            db.session.add(student)
            db.session.commit()

            #a 'Data' object is made for the new Student for each Challenge to store whether they have completed that challenge or not
            # #data objects will be #students * #challenges
            for challenge in Challenges.query.all():
                data = Data(student_id=student.id, challenge_id=challenge.id, checked=False)
                db.session.add(data)
            db.session.commit()
            session["id"] = student.id
            flash("Account successfully created")
            return redirect(url_for('views.home', index=0))
    return render_template("signup.html")


@auth.route('/make_challenges', methods=['GET','POST'])
def make_challenges():
    for i in range(10):
        challenge = Challenges(name=("Challenge"+str(i)), badge="/static/images/challenge" + str(i) +".png")
        db.session.add(challenge)
    db.session.commit()
    return "<p>Challenges Successfully made!</p>"
