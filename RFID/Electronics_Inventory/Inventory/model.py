from datetime import datetime
from datetime import timedelta

# Class to keep track of who has issued what items
##########################################
# Component_ID | Rollno | IssuedQuantity #
##########################################
class Issue():
    def __init__(self, data):
        if data:
            self.id = data[0]
            self.rollno = data[1]
            self.quantity = data[2]
            self.issued_date = data[3]
            try:
                self.expected_return_date = data[4]
            except:
                self.expected_return_date = self.issued_date + timedelta(days=45)

    def get_id(self):
        return self.id
    def get_rollno(self):
        return self.rollno
    def get_issued_quantity(self):
        return self.quantity
    def get_issued_date(self):
        return self.issued_date
    def get_return_date(self):
        return self.expected_return_date


# Class to keep track of list of items available in club
#########################################################################################
# Component_ID | Name | Type | Total Quantity | Location | IssuedQuantity | Description #
#########################################################################################
class Inventory():
    def __init__(self,data):
        if data:
            self.id = data[0]
            self.name = data[1]
            self.type = data[2]
            self.description = data[3]
            self.quantity = int(data[4])
            self.location = data[5]
            self.barcode = data[6]
            if data[7]:
                self.issued_quantity = int(data[7])
            else:
                self.issued_quantity = 0

    def get_id(self):
        return self.id
    def get_name(self):
        return self.name
    def get_type(self):
        return self.type
    def get_description(self):
        return self.description
    def get_quantity(self):
        return self.quantity
    def get_location(self):
        return self.location
    def get_issued_quantity(self):
        return self.issued_quantity
    def get_barcode(self):
        return self.barcode
    def __str__(self):
        return self.name
    
# Class to keep track of student details
######################################################
# Rollno | Name | Fine | Remarks (Ex. Robotics Club) #
######################################################
class StudentDetails():
    def __init__(self, data):
        if data:
            self.rollno = data[0]
            self.name = data[1]
            self.fine = data[2]
            if data[3]:
                self.remarks = data[3]

    def get_rollno(self):
        return self.rollno
    def get_name(self):
        return self.name
    def get_fine(self):
        return self.fine
    def  get_remarks(self):
        return self.remarks
    def __str__(self):
        return self.name

# Class to keep track of student with their accessibility
#####################
# Rollno | location #
#####################
class StudentAccess():
    def __init__(self, data):
        if data:
            self.rollno = data[0]
            self.location = data[1]

    def get_rollno(self):
        return self.rollno
    def get_location(self):
        return self.location
    def __str__(self):
        return str(self.rollno) + ' ' + str(self.location)


# Class to keep track of student details
#######################
# Username | Password #
#######################
class Admin():
    def __init__(self, data):
        if data:
            self.userid = data[0]
            self.password = data[1]

    def get_Userid(self):
        return self.userid

    def get_Password(self):
        return self.password

    def __str__(self):
        return self.userid
