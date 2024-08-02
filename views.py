from flask import Blueprint, Flask, redirect, render_template, request, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from .models import *
from passlib.hash import pbkdf2_sha256 as hasher
from os import path
from functools import wraps
from website.models import *
from . import db
import os

#creates blueprint to connect file to main file 'app.py'
views = Blueprint('views', __name__)

#function to check that user is logged in
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'id' in session:
            return f(*args, **kwargs)
        else:
            return redirect("/")
    return wrap

#home page for user
@views.route("/home", methods = ["GET", "POST"])
@login_required
def home(): #index parameter is the index of the book that is currently being displayed from the users books marked as 'reading'
    student = Students.query.filter_by(id=session['id']).first()
    books = (insertion_sort(Books.query.filter_by(student_id = session["id"], status="reading").all())[::-1])
    num_plan=len(Books.query.filter_by(student_id = session["id"],status="waiting").all())
    num_read=len(Books.query.filter_by(student_id = session["id"],status="skimmed").all())+ len(Books.query.filter_by(student_id = session["id"],status="finished").all())+len(Books.query.filter_by(student_id = session["id"],status="dnf").all())
    #'challenges' array stores tuples containing each challenge and whether or not the current user has completed that challenge
    challenges = []
    for challenge in Challenges.query.all():
        data = Data.query.filter_by(student_id=session["id"],challenge_id=challenge.id).first()
        tuple = (challenge, data.checked)
        challenges.append(tuple)

    #When webpage is being loaded, index is set to 0
    if request.method == 'GET':
        index = 0
        
    #check for logout button being pressed
    if request.method == 'POST' and request.form["button"] == 'logout':
        session["id"] = None
        session.pop("user_id",None)
        return redirect(url_for('auth.login'))
    #if 'Next Book' button is pressed while viewing last book in list of currently reading books, index is reset to zero
    if request.method == 'POST':
        index = request.form["button"]
        index = int(index) % len(books)
    return render_template("home.html", student=student, books=books, index=index, challenges=challenges, num_plan=num_plan, num_read=num_read)

#Insertion sort method 
def insertion_sort(obj):
    for i in range(0, len(obj)):
        key = (obj[i].name).lower()
        j = i
        while j > 0 and (obj[j - 1].name).lower() > key:
            store = obj[j]
            obj[j] = obj[j-1]
            obj[j-1] = store
            j = j - 1
    return obj

@views.route("/list", methods = ["GET", "POST"])
@login_required
def list():
    if request.method == "GET":
        student = Students.query.filter_by(id=session['id']).first()
        #create seperate sorted lists of all users books in each category
        reading = insertion_sort(Books.query.filter_by(student_id = session["id"],status="reading").all())
        finished = insertion_sort(Books.query.filter_by(student_id = session["id"],status="finished").all())
        waiting = insertion_sort(Books.query.filter_by(student_id = session["id"],status="waiting").all())
        skimmed = insertion_sort(Books.query.filter_by(student_id = session["id"],status="skimmed").all())
        dnf = insertion_sort(Books.query.filter_by(student_id = session["id"],status="dnf").all())

    
        #'more' button pressed go to detailed view page for respective book
        return render_template("list.html", student=student, reading=reading,finished=finished,waiting=waiting,skimmed=skimmed, dnf=dnf)
    if request.method=='POST' and request.form['button'][:4] == "more":
        return redirect(url_for('views.detail', book_id=request.form['button'][4:]))
    else:
        KEY = request.form['title']
        #Searching the desired book
        all_books = insertion_sort(Books.query.filter_by(student_id = session["id"]).all())
        POS = binary_search(all_books, 0, len(all_books), KEY)
        book_id1 = all_books[POS].book_id
        return redirect(url_for('views.detail', book_id=book_id1))
        

#Binary search method
def binary_search(obj, front, end, KEY):
    if end >= front:
        mid = front + (end - front)//2
        if obj[mid].name == KEY:
            return mid
        if obj[mid].name > KEY:
            return binary_search(obj, front, mid-1, KEY)
        return binary_search(obj, mid+1, end, KEY)
    return -1

@views.route("/`add`", methods = ["GET", "POST"])
@login_required
#Adding a book
def add():
    if request.method == "GET":
        return render_template("add.html")
    else:
        name = request.form["name"]
        author = request.form["author"]
        total_pages = (request.form["no_pages"])
        current_page = (request.form["current_page"])
        f = request.files['file']
        if f:
            flash("File recieved!")
            f.save(os.path.join("website/static/images", f.filename.replace(" ","_")))
        else:
            f.filename = "batman.png"
        book = Books(student_id = session["id"], name = name, author = author, pages = total_pages, bookcover = "/static/images/" + str(f.filename).replace(" ","_"), currentpage = current_page, status="reading")
        db.session.add(book)
        db.session.commit()
        flash("Book successfully added!")
        return redirect(url_for('views.list'))
    
    
@views.route("/goal", methods = ["GET", "POST"])
@login_required
#Loading Goal Page and Add Goals
def goal():
    if request.method == "GET":
        goals = Goals.query.filter_by(student_id=session["id"])
        goal_array = []
        for i in goals:
            goal_array.append(i)
        return render_template("goal.html", goals=goal_array)
    else:
        value = request.form["button"]
        goals = Goals.query.filter_by(student_id=session["id"])
    #Save
        if value == "save":
            new_goal = Goals(student_id=session["id"], goal=request.form.get("title"), checked=False)
            add = True
            for i in goals:
                if new_goal.goal.lower() == i.goal.lower():
                    add = False
            if add == True: 
                db.session.add(new_goal)
                db.session.commit()
    #Delete
        elif value[:3] == "del":
            deleted = Goals.query.filter_by(id=value[3:]).first()
            db.session.delete(deleted)
            db.session.commit()
    #Checkbox
        else:
            goal = Goals.query.get(value[5:])
            if goal:
                goal.checked = not goal.checked
                db.session.add(goal)
                db.session.commit()
            
        return redirect("/goal")

#Page of the details of the book, allow user to edit and change the details of a book
@views.route("/detail/<book_id>", methods=["GET", "POST"])
@login_required
def detail(book_id):
    if request.method=='POST': 
        book_id = request.form['button']
    book = Books.query.filter_by(book_id=book_id).first()
    if not book:
        flash("Book not found", category="error")
    elif request.method == 'POST':
        name=book.name
        author=book.author
        pages=book.pages
        current_page=book.currentpage
        file_name=book.bookcover
        status=request.form["book_status"]
        
        if request.form['name'] != "": name = request.form["name"]
        if request.form['author'] != "": author = request.form["author"]
        if request.form['no_pages'] != "": pages = (request.form["no_pages"])
        if request.form['current_page'] != "": current_page = (request.form["current_page"])
        if request.files['file']: file_name="/static/images/static" + str(request.files['file'].name)
        

        new_book = Books(student_id = session["id"], name = name, author = author, pages = pages, bookcover = file_name, currentpage = current_page, status=status)
        db.session.add(new_book)
        db.session.delete(book)
        db.session.commit()
        flash("Book successfully added!")
        
        return redirect(url_for('views.list'))
    
    return render_template("detail.html", book=book)

#Page displaying all the challenges     
@views.route("/challenges", methods=["GET", "POST"])
@login_required
def challenge():

    if (request.method == "POST"):
        id = request.form['button']
        data = Data.query.filter_by(student_id=session["id"],challenge_id=id).first()
        data.checked = not data.checked
        db.session.commit()
    
    challenges = []
    for challenge in Challenges.query.all():
        data = Data.query.filter_by(student_id=session["id"],challenge_id=challenge.id).first()
        tuple = (challenge, data.checked)
        challenges.append(tuple)

    return render_template("challenge.html", challenges=challenges)
