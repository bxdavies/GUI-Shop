#############
# Libraries #
#############
import PySimpleGUI as sg
from datetime import datetime
from password_strength import PasswordPolicy

################
# Module Files #
################
from app import models, main, functions

###################
# Password Policy #
###################
policy = PasswordPolicy.from_names(
    length=8,  # min length: 8
    uppercase=1,  # need min. 1 uppercase letters
    numbers=2,  # need min. 2 digits
    special=1,  # need min. 1 special characters
    # need min. 2 non-letter characters (digits, specials, anything)
    nonletters=2,
)


##################
# Customer Login #
##################
def login():
    ''' Customer Login Window '''

    # Database Session #
    session = models.Session()

    # Define Window Layout
    layout = [
        [sg.Text('Login', font='Any 30', justification='center', expand_x=True)],
        [sg.Text('Please login using your email address and password...', justification='center', expand_x=True)],
        [sg.Text('Email Address:', size=(22, 1)), sg.InputText(key="-emailaddress-", size=(40, 1))],
        [sg.Text('Date of Birth (DD MM YY):', size=(22, 1)), sg.Input(key="-dob-", disabled=True, size=(30, 1)), sg.CalendarButton('Date', format='%d %m %Y', locale="en_GB.utf8'")],
        [sg.Text('Password:', size=(22, 1)), sg.InputText(key="-password-", size=(40, 1), password_char='*')],
        [sg.Text('', key="-error-", text_color='red')],
        [sg.Button('Login!', key='-login-')],
        [sg.HorizontalSeparator(pad=(10, 10))],
        [sg.Button('Welcome', key="-welcome-")]
    ]

    # Create the Window
    window = sg.Window('GUI Shop - Login', layout, icon=functions.getIcon())

    # Handle events
    while True:
        event, values = window.read()

        match event:

            # Window Closed
            case sg.WIN_CLOSED | "-welcome-":
                session.close()
                window.close()
                main.main()

            # Login Button Pressed
            case '-login-':

                # If email address is empty then show an error
                if values["-emailaddress-"] == '':
                    window["-error-"].update('Enter your email address!')

                # Of password is empty then show an error
                elif values["-password-"] == '':
                    window["-error-"].update('Enter your password!')

                # Query the Database and check if customer exists and passwords match
                else:
                    window["-error-"].update('')
                    customer = session.query(models.Customer).filter(
                        models.Customer.email_address == values["-emailaddress-"]).first()

                    # Check if customer exists
                    if customer is not None:

                        # Convert user input date to date object
                        dob = datetime.strptime(
                            values["-dob-"], '%d %m %Y').date()

                        # If passwords match then show the Customer Home window
                        if customer.checkPassword(values["-password-"]) and customer.dob == dob:
                            session.close()
                            window.close()
                            main.customerHome(customer.id)

                        # If date does not match then show an error
                        elif customer.dob != dob:
                            window["-error-"].update('Your DOB is incorrect!')

                        # If passwords don't match then show an error
                        elif customer.checkPassword(values["-password-"]) is False:
                            window["-error-"].update('Your password is incorrect!')

                    # If customer does not exist then show an error
                    else:
                        window["-error-"].update('No Account found with that Email Address!')

    session.close()
    window.close()


####################
# Customer Sign Up #
####################
def signup():
    ''' Customer Sign Up Window '''

    # Database Session #
    session = models.Session()

    errors = []
    # Define Window Layout
    layout = [
        [sg.Text('Sign up', font='Any 30', justification='center', expand_x=True)],
        [sg.Text('Please fill in the form to create a new account', justification='center', expand_x=True)],
        [sg.Text('Forename:', size=(22, 1)), sg.InputText(key="-forename-", size=(15, 1)), sg.Text('Surname:', size=(8, 1)), sg.InputText(key="-surname-", size=(15, 1))],
        [sg.Text('Email Address:', size=(22, 1)), sg.InputText(key="-emailaddress-", size=(42, 1))],
        [sg.Text('Date of Birth (DD MM YY):', size=(22, 1)), sg.Input(key="-dob-", size=(30, 1), disabled=True), sg.CalendarButton('Date', format='%d %m %Y', locale="en_GB.utf8'")],
        [sg.Text('Password:', size=(22, 1)), sg.InputText(key="-password-", size=(42, 1), password_char='*')],
        [sg.Text('Confirm Password:', size=(22, 1)), sg.InputText(key="-confirmpassword-", size=(42, 1), password_char='*')],
        [sg.Text('', key="-error-", text_color='red')],
        [sg.Button('Sign Up!', key="-signup-")],
        [sg.HorizontalSeparator(pad=(10, 10))],
        [sg.Button('Welcome', key="-welcome-")]
    ]

    # Create the Window
    window = sg.Window('GUI Shop - Sign Up', layout, icon=functions.getIcon())

    # Handle events
    while True:
        event, values = window.read()

        match event:

            # Window Closed
            case sg.WIN_CLOSED | "-welcome-":
                session.close()
                window.close()
                main.main()

            # Sign Up Button Press
            case "-signup-":
                for value in values:

                    # If value is Date then do nothing
                    if value == 'Date':
                        continue

                    # If value equals nothing then show an error
                    if values[value] == '':
                        valueName = value.replace('-', '')
                        if f'Enter your {valueName.capitalize()}!' not in errors:
                            errors.append(f'Enter your {valueName.capitalize()}!')
                            window["-error-"].update("\n".join(errors))

                    # If value does not equal nothing then if error is in error list then remove error from error list
                    if values[value] != '':
                        valueName = value.replace('-', '')
                        if f'Enter your {valueName.capitalize()}!' in errors:
                            errors.remove(f'Enter your {valueName.capitalize()}!')
                            window["-error-"].update("\n".join(errors))

                    # Check password strength
                    passwordStrength = policy.test(values["-password-"])

                    # If password strength is empty then remove error from error list
                    if not passwordStrength:
                        if 'Password must be at least 8 characters long and contain 1 uppercase letters, 2 numbers and 1 special character  ' in errors:
                            errors.remove('Password must be at least 8 characters long and contain 1 uppercase letters, 2 numbers and 1 special character  ')
                            window["-error-"].update("\n".join(errors))

                    # If list is not empty then show an error
                    else:
                        if 'Password must be at least 8 characters long and contain 1 uppercase letters, 2 numbers and 1 special character  ' not in errors:
                            errors.append('Password must be at least 8 characters long and contain 1 uppercase letters, 2 numbers and 1 special character  ')
                            window["-error-"].update("\n".join(errors))

                    # If passwords do not match show an error
                    if values["-password-"] != values["-confirmpassword-"]:
                        if 'Passwords do not match!' not in errors:
                            errors.append('Passwords do not match!')
                            window["-error-"].update("\n".join(errors))

                    # If passwords do not match then remove error from error list if in error list then
                    if values["-password-"] == values["-confirmpassword-"]:
                        if 'Passwords do not match!' in errors:
                            errors.remove('Passwords do not match!')
                            window["-error-"].update("\n".join(errors))

                # If there are no errors then add Customer to the Database
                if not errors:
                    customer = models.Customer(
                        forename=values["-forename-"], 
                        surname=values["-surname-"],
                        email_address=values["-emailaddress-"], 
                        dob=datetime.strptime(values["-dob-"], '%d %m %Y')
                    )
                    customer.setPassword(values["-password-"])
                    session.add(customer)
                    session.commit()
                    session.close()
                    window.close()
                    sg.PopupOK('Account Created!')
                    main.main()
    session.close()
    window.close()


###############
# Staff Login #
###############
def staffLogin():
    ''' Staff Login Window '''

    # Database Session #
    session = models.Session()

    # Define Window Layout
    layout = [
        [sg.Text('Login', font='Any 30', justification='center', expand_x=True)],
        [sg.Text('Please Login using your Staff ID and password!', justification='center', expand_x=True)],
        [sg.Text('ID:'), sg.InputText(key="-id-")],
        [sg.Text('Password:'), sg.InputText(key="-password-", password_char='*')],
        [sg.Text('', key="-error-", text_color='red')],
        [sg.Button('Login!', key='-login-')],
        [sg.HorizontalSeparator(pad=(10, 10))],
        [sg.Button('Welcome', key="-welcome-")]
    ]

    # Create the Window
    window = sg.Window('GUI Shop - Login', layout, modal=True, icon=functions.getIcon())

    # Handle events
    while True:
        event, values = window.read()

        match event:

            # Window Closed
            case sg.WIN_CLOSED | "-welcome-":
                session.close()
                window.close()
                main.main()

            # Login Button Pressed
            case '-login-':

                # Check if ID is empty
                if values["-id-"] == '':
                    window["-error-"].update('Enter your Staff ID !')

                # Check if password is empty
                elif values["-password-"] == '':
                    window["-error-"].update('Enter your password!')

                # Query the Database and check if Staff Member exists and passwords match
                else:
                    window["-error-"].update('')
                    staff = session.query(models.Staff).filter(
                        models.Staff.id == values["-id-"]).first()

                    # Check if staff Member exists
                    if staff is not None:

                        # If passwords match then show Staff Home Window
                        if staff.checkPassword(values["-password-"]):
                            session.close()
                            window.close()
                            main.staffHome()

                        # If passwords don't match then show an error
                        else:
                            window["-error-"].update(
                                'Your password is incorrect!')

                    # If staff Member does not exist show an error
                    else:
                        window["-error-"].update(
                            'No Account found with that Email Address!')

    session.close()
    window.close()
