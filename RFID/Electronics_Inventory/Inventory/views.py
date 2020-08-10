# TODO
# If student details not exists while issuing - ask user to enter details
# Updating file can be improvised
# Fine Calculation
# Limiting renew chances

# Use sql database if possible

# Only registered are allowed to open the index.html
# After Issue -> Open the lock option -> Check if allowed to open the cupboard (if yes -> issue button(disabled) )



from flask import Flask, render_template, redirect, url_for, session, request
# from model import Admin, StudentDetails, Issue, Inventory
from . import model
from . import settings
from .scrapping import scrap_rollno

import os
import csv
import time
from datetime import datetime, timedelta

def createApp():
    # create app
    app = Flask(__name__)
    # Set the secret key to some random bytes. Keep this really secret!
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

    return app

def home():
    if validate_user():
        return redirect(url_for('dashboard'))

    if scrap_rollno() != "" and scrap_rollno() != " ":
        settings.rollno = scrap_rollno()
        return redirect(url_for('login'))

    return render_template("home.html")

def reset_user():
    return redirect(url_for('logout'))

def login():
    if validate_user():
        print(settings.rollno)
        return redirect(url_for('dashboard'))
        
    session['username'] = settings.rollno
    return redirect(url_for('dashboard'))


def logout():
    # remove the username from the session if it is there
    try:
        session.pop('username', None)
    except:
        pass
    settings.rollno = None
    settings.lock = False
    return redirect(url_for('home'))

def dashboard():
    if not validate_user():
        return redirect(url_for('home'))

    # Find student details with rollno
    cur_student = model.StudentDetails(None)

    for stud in settings.student_details:
        if str(stud.get_rollno()) == str(settings.rollno):
            cur_student = stud
            break

    access = accessAllowed()
    return render_template("index.html", posts={'student':cur_student, 'access':access})

def update_file(filename, id, quantity, table, header):
    try:
        os.remove(filename)
    except FileNotFoundError:
        print("File doesn't exists")
    else:
        dump(filename, header)
        for row in table:
            data = list(row.__dict__.values())
            dump(filename, data)

def validateStudent(RollNo):
    for stud in settings.student_details:
        if stud.get_rollno() == RollNo:
            return True
    return False

def dump(filename, data):
    try:
        with open(filename, "a+") as f:
            for item in data:
                f.write('"' + str(item) + '"' +",")
            f.write("\n")
    except FileNotFoundError or ValueError:
        print("Error occurs while writing to file", filename)

def renew():
    if not validate_user():
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        requested_items = request.form.to_dict()
        print(requested_items)
        date = datetime.now()

        for issued_item in settings.issue_log:
            if issued_item.get_id() == requested_items['renew']:
                break
        
        # Calculate fine for renewed item
        fine = calc_fine_item(issued_item)
        if fine > 0:
            # Update student details with fine
            for student in settings.student_details:
                if str(student.get_rollno()) == str(settings.rollno):
                    student.fine = float(student.get_fine()) + fine
                    header = ["rollno", "name", "fine", "remarks"]
                    update_file(settings.student_details_file, settings.rollno, None, settings.student_details, header)

        issued_item.issued_date = date
        issued_item.expected_return_date = date + timedelta(days=45)
        # Update issue file
        header = ["ID","Rollno","Quantity","Issued Date","Expected Return Date"]
        update_file(settings.issue_file, requested_items['renew'], None, settings.issue_log, header)

        # Add to history
        # ["Component ID","Component name","Task","Quantity","Date","Rollno","Student Name",]
        history = []

    
    return redirect(url_for('account'))

def return_item():
    if not validate_user():
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        requested_items = request.form.to_dict()
        print(requested_items)
        # Remove item from issue list
        for item in settings.issue_log:
            if item.get_id() == requested_items['return']:
                return_amount = item.get_issued_quantity()
                issued_item = item
                settings.issue_log.remove(item)
                break
        # Calculate fine for the item i.e. returned
        fine = calc_fine_item(issued_item)
        if fine > 0:
            # Update student details with fine
            for student in settings.student_details:
                if str(student.get_rollno()) == str(settings.rollno):
                    student.fine = float(student.get_fine()) + fine
                    header = ["rollno", "name", "fine", "remarks"]
                    update_file(settings.student_details_file, settings.rollno, None, settings.student_details, header)

        # Decrease issued quantity of item by return_amount in inventory list
        for row in settings.inventory_items:
            if row.get_id() == requested_items['return']:
                row.issued_quantity = int(row.issued_quantity) - int(return_amount)
                break
        # Update issue file
        header = ["ID","Rollno","Quantity","Issued Date","Expected Return Date"]
        update_file(settings.issue_file, requested_items['return'], None, settings.issue_log, header)
        # Update inventory file
        header = ["ID","Name","Type","Description","Amount(in num)","location","Issued Quantity","Barcode"]
        update_file(settings.inventory_file, requested_items['return'], None, settings.inventory_items, header)
        
    return redirect(url_for('account'))
    
def account():
    if not validate_user():
        return redirect(url_for('home'))
    
    for stud in settings.student_details:
        if int(stud.get_rollno()) == int(settings.rollno):
            break
    
    issued_items = []   # List of objects of Issue class
    # list_of_component
    # get all the id of items issued by rollno
    issued_id = []  # [id, quantity_issued, issued date, return date]
    for log in settings.issue_log:
        if str(log.get_rollno()) == str(settings.rollno):
            issued_id.append([log.get_id(), log.get_issued_quantity(), log.get_issued_date(), log.get_return_date()])
            issued_items.append(log)

    # Get the items details having ID = id
    # Store the issued item list in issued_item
    issued_item_details = []   # [Items, quantity_issued, issued_date]
    for item in settings.inventory_items:
        for log in issued_id:
            if str(item.get_id()) == str(log[0]):
                issued_item_details.append([item, log[1], log[2], log[3]])

    fine = calc_fine(settings.rollno, issued_items)
    print('Fine = ', fine)
    return render_template("account.html", posts={
        'fine':fine,
        'student':stud,
        'items':issued_item_details,
    })

# Calculate fine of a student with given rollno
# Input : Rollno, List of items issued by student
# Output: Total Fine
def calc_fine(student_rollno, issued_items):
    # get previous fine from student_details list
    # get all the issued item list
    # Calculate fine for all the items
    previous_fine = 0.0
    for student in settings.student_details:
        if str(student.get_rollno()) == str(settings.rollno):
            previous_fine = float(student.get_fine())
    
    fine = previous_fine

    for item in issued_items:
        fine = fine + calc_fine_item(item)

    return fine

def calc_fine_item(item):
    issue_date = item.get_issued_date()
    try:
        issue_date_obj = datetime.strptime(issue_date, '%Y-%m-%d %H:%M:%S.%f')
    except TypeError:
        issue_date_obj = issue_date

    fine = 0.0
    current_date = datetime.now()
    print('&&&&&&&&', type(issue_date_obj))
    print(type(current_date))
    if (current_date - issue_date_obj).days > 45:
        fine = fine + float(settings.fine_rate*(abs((current_date - issue_date_obj).days) - 45))
    return float(fine)

def show_list():
    if not validate_user():
        return redirect(url_for('home'))
        
    return render_template("list_of_components.html", items=settings.inventory_items)

def admin():
    if not validate_user():
        return redirect(url_for('home'))
        
    return render_template("admin_login.html")

def validate_user():
    # Check session and rollno
    if 'username' in session and settings.rollno is not None and str(settings.rollno) != "" and str(settings.rollno) != ' ':
        print("%^&", (settings.rollno))
        if str(settings.rollno) == ' ':
            print("It's a space")
        print("2")
        return True
    else:
        return False

def accessAllowed():
    # Check if user have access to the electronics club items
    accessAllowed = False
    for stud in settings.student_details:
        if str(stud.get_rollno()) == str(settings.rollno):
            accessAllowed = True
            break
    if accessAllowed:
        return True
    else:
        return False

# To load data from filename
def load(filename, classname, collection):

    print(filename)
    with open(filename, "r") as csvFile:
        data = csv.reader(csvFile)

        for row in list(data)[1:]:
            # print(row)
            obj = classname(row)
            collection.append(obj)

# Load data
def load_data():
    # Get path of files
    # load from each file
    load(settings.student_details_file, model.StudentDetails, settings.student_details)
    load(settings.student_access_file, model.StudentAccess, settings.student_access_list)
    load(settings.inventory_file, model.Inventory, settings.inventory_items)
    load(settings.issue_file, model.Issue, settings.issue_log)

# Check if student have access to open the cupboard
def accessCupboard():
    global requested_items
    if not validate_user():
        return redirect(url_for('home'))

    flag = False
    if request.method == 'POST':
        # Get the dict of items id requested along with quantity
        requested_items = request.form.to_dict()
        # Remove items for which 0 items are requested
        temp = {}
        for item in requested_items.items():
            if item[1] != '':
                if int(item[1]) != 0:
                    temp[item[0]] = item[1]
        requested_items = temp
        
        # Go through list and check access and requested amount < available amount
        # If requested amount is invalid : Display requested amount is not valid
        # If access granted : send signal to open the lock
        # If access denied : Show access denied message
            
        access_list = []
        valid_request = []
        for item in requested_items:
            # get item id
            item_id = item
            # quantity required
            req_quantity = int(requested_items[item])

            if req_quantity <= 0:
                valid_request.append(False)
                access_list.append(False)
                continue
            else:
                # if required quantity is available then request is valid
                was_valid_request = False
                for row in settings.inventory_items:
                    if row.get_id() == item_id:
                        if int(row.get_quantity()) - int(row.get_issued_quantity()) >= req_quantity:
                            valid_request.append(True)
                            was_valid_request = True
                        else:
                            valid_request.append(False)
                            access_list.append(False)
                        break
                if not was_valid_request:
                    continue
                else:
                    # Check for access
                    # Loop over student_access_list and check if location of row is accesible to settings.rollno
                    access_flag = False
                    for stud in settings.student_access_list:
                        # print(str(row.get_location())[:2] == str(stud.get_location()))
                        # print(stud.get_rollno())
                        # print(settings.rollno)
                        if str(stud.get_rollno()) == str(settings.rollno) and str(stud.get_location()) == str(row.get_location())[:2]:
                            # Access Granted
                            access_list.append(True)
                            access_flag = True
                            # Open the lock
                            settings.lock = True
                            flag = True
                            break
                    
                    if not access_flag:
                        access_list.append(False)

        if flag:
            time.sleep(10)
            settings.lock = False

        return render_template('issue_page.html', posts={
            'flag':flag,
            'access_list':access_list,
            'valid_request':valid_request,
            'requested_items':requested_items,
        })  
    return redirect(url_for('home'))  


def issue():
    if not validate_user():
        return redirect(url_for('home'))

    if request.method == 'POST':
        # requested_items = request.form.to_dict()
        print("**********", request.form.to_dict())
        # Get current date
        date = datetime.now()
        return_date = datetime.now() + timedelta(days=45)
        
        # print(requested_items)
        for item in requested_items:
            
            # get item id
            item_id = item
            # quantity required
            req_quantity = int(requested_items[item])

            if req_quantity <= 0:
                continue

            # if required quantity is available then issue
            for avail_item in settings.inventory_items:
                if avail_item.get_id() == item_id:
                    break
            
            if int(avail_item.get_quantity()) - int(avail_item.get_issued_quantity()) >= req_quantity:
                # Increased the issued quantity record
                avail_item.issued_quantity = avail_item.issued_quantity + req_quantity
                new_obj = model.Issue([item_id, settings.rollno, req_quantity, date])
                # Issue item to the user
                settings.issue_log.append(new_obj)
                # Update the issue file
                dump(settings.issue_file, [item_id, settings.rollno, req_quantity, date, return_date])
                # Update Inventory file
                # Set header for inventory file
                header = ["ID","Name","Type","Description","Amount(in num)","location","Issued Quantity","Barcode"]
                update_file(settings.inventory_file, item_id, req_quantity, settings.inventory_items, header)

    return redirect(url_for('account'))

# Display lock details to give response to lock
def lock_details():
    if settings.lock:
        return "1"
    else:
        return "0"

def add_to_history(data):
    dump(settings.history_file, data)