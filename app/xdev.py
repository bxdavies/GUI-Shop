from app import models

def createStaffAccount():
    session = models.Session()
    staff = models.Staff(forename='Ben', surname='Davies')
    staff.setPassword('1234')
    session.add(staff)
    session.commit()

