import os

global admin_accounts, inventory_items, issue_log, student_details
global rollno, rollno_file
global fine_rate
global lock

# Lock : {False : Close, True : Open}
lock = False
# Rs 1 per extra day
fine_rate=1
# Collection of all the admin users
admin_accounts = []
# Collection of items
inventory_items = []
# Collection of issue logs
issue_log = []
# Collection of valid student details
student_details = []
# Collection of student with their access details
student_access_list = []

# Current active rollno
rollno = None

dir_path = os.path.dirname(__file__)
data_dir_path = os.path.join(dir_path, 'data')

# Get path of files
# File in which current rollno exists
rollno_file = os.path.join(data_dir_path, 'rollno.txt')

student_details_file = os.path.join(data_dir_path, 'student_details.csv')
student_access_file = os.path.join(data_dir_path, 'student_access_list.csv')
inventory_file = os.path.join(data_dir_path, 'inventory_list.csv')
issue_file = os.path.join(data_dir_path, 'issue_list.csv')
history_file = os.path.join(data_dir_path, 'history.csv')
