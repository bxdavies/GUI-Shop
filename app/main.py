#############
# Libraries #
#############
import PySimpleGUI as sg
from datetime import datetime

################
# Module Files #
################
from app import auth, booking, functions, models, staff, order


###############
# Main Window #
###############
def main():
    ''' Main Window, First window to display '''

    # Database Session
    session = models.Session()

    # Define Buttons Frame
    buttons = [
        [sg.Button('Login', key="-login-"), sg.Button('Sign Up', key="-signup-")],
        [sg.Button('Staff Login', key="-stafflogin-")]
    ]

    # Define Window Layout
    layout = [
        [sg.Text('Pharmanet', font='Any 30', justification='center', expand_x=True)],
        [sg.Text('Welcome to Pharmanet, please Login or Sign Up', justification='center', expand_x=True)],
        [sg.Frame('', buttons, expand_x=True,  relief='flat', element_justification='center')],
        [sg.HorizontalSeparator(pad=(10, 10))],
        [sg.Button('Exit', key="-exit-")]
    ]

    # Create the Window
    window = sg.Window('Pharmanet - Home', layout, icon=functions.getIcon())

    # Handle events
    while True:
        event, values = window.read()

        match event:

            # Window Closed
            case sg.WIN_CLOSED | "-exit-":
                session.close()
                quit()

            # Login Button Press
            case "-login-":
                session.close()
                window.close()
                auth.login()

            # Sign Up Button Press
            case "-signup-":
                session.close()
                window.close()
                auth.signup()

            # Staff Login Button Press
            case "-stafflogin-":
                session.close()
                window.close()
                auth.staffLogin()

    window.close()


#################
# Customer Home #
#################
def customerHome(customerID):
    ''' 
    Customer Home 

    Parameters:
        customerID: Customer ID (int)
    '''

    # Database Session
    session = models.Session()

    # Get Customer
    customer = session.query(models.Customer).filter(
        models.Customer.id == customerID).first()

    # Window Variables
    bookingsList = []
    ordersList = []

    # Get current customers bookings that are greater than today's date from the Database
    bookings = session.query(models.Booking).filter(models.Booking.customer == customer, models.Booking.used == False,
                                                    models.Booking.booking_datetime >= datetime.now(), models.Booking.approved == True).order_by(models.Booking.booking_datetime).all()

    # For each booking in the Database add the details to the bookingsList
    for cBooking in bookings:
        bookingsList.append([cBooking.id,  datetime.strftime(
            cBooking.booking_datetime, '%A %d %B %Y %H:%M')])

    # If bookingList is empty add an error
    if not bookingsList:
        bookingsList = [['No bookings Found', 'Hello']]

    #
    orders = session.query(models.Order).filter(
        models.Order.customer == customer and models.Order.completed == False).all()

    for cOrder in orders:
        ordersList.append([cOrder.id, datetime.strftime(
            cOrder.collection_datetime, '%A %d %B %Y %H:%M'), f'£{cOrder.total}'])

    if not ordersList:
        ordersList = ['.', 'No Orders Found', '.']

    # Define Col1
    col1 = [
        [sg.Text('Bookings', justification='center', expand_x=True)],
        [sg.Table(values=bookingsList, headings=['ID', 'Date Time'], enable_click_events=True, key="-bookings-")],
        [sg.Button('New Booking', key="-newbooking-")]
    ]

    # Define Col2
    col2 = [
        [sg.Text('Orders', justification='center', expand_x=True)],
        [sg.Table(values=ordersList, headings=['ID', 'Date Time', 'Total'], enable_click_events=True, key="-orders-")],
        [sg.Button('Shop', key="-shop-")]
    ]

    # Define Window Layout
    layout = [
        [sg.Text('Customer Home', font='Any 30', justification='center', expand_x=True)],
        [sg.Text(f'Hello, {customer.forename} and Welcome to Pharmanet', font='Any 20', justification='center', expand_x=True)],
        [sg.Text('From here, create, view and edit Orders or Bookings', justification='center', expand_x=True)],
        [sg.Column(col1), sg.Column(col2)],
        [sg.HorizontalSeparator(pad=(10, 10))],
        [sg.Button('Exit', key="-exit-")]
    ]

    # Create the Window
    window = sg.Window('Pharmanet - Customer Home', layout, icon=functions.getIcon())

    # Handle events
    while True:
        event, values = window.read()

        match event:

            # Window Closed
            case sg.WIN_CLOSED | "-exit-":
                window.close()
                session.close()
                quit()

            # New Booking Button Pressed
            case "-newbooking-":
                session.close()
                window.close()
                booking.new(customerID)

            # Shop Button Pressed
            case "-shop-":
                session.close()
                window.close()
                order.shop(customerID, None, None)

        # If event is a tuple match the first element
        if isinstance(event, tuple):

            match event[0]:

                # If event key is bookings then show booking
                case "-bookings-":
                    if event[2][0] in range(0, len(bookingsList)):
                        session.close()
                        window.close()
                        booking.edit(customerID, bookingsList[event[2][0]][0])

                # If event key is orders then show order
                case "-orders-":
                    if event[2][0] in range(0, len(ordersList)):
                        session.close()
                        window.close()
                        order.edit(customerID, ordersList[event[2][0]][0])

    window.close()

##############
# Staff Home #
##############


def staffHome():
    ''' Staff Home Window '''

    # Define Buttons
    buttons = [
        [sg.Button('Scan QR Code', key="-scan-")],
        [sg.Button('Show Approved Bookings', key="-showbookings-"), sg.Button('Approve Bookings', key="-approvebookings-"), sg.Button('Show Orders', key="-showorders-")],
        [sg.Button('List Products', key="-listproducts-"),
         sg.Button('List Categories', key="-listcategories-")],
        [sg.Button('Add Product', key="-addproduct-"),
         sg.Button('Add Category', key="-addcategory-")],
        [sg.Button('Data Visualization', key="-datavisualization-")]
    ]

    # Define Window Layout
    layout = [
        [sg.Text('Staff Home', font='Any 30', justification='center', expand_x=True)],
        [sg.Text('Welcome Staff Member, from here you can change and view many things', justification='center', expand_x=True)],
        [sg.Frame('', buttons, expand_x=True,  relief='flat', element_justification='center')],
        [sg.HorizontalSeparator(pad=(10, 10))],
        [sg.Button('Exit', key="-exit-")]
    ]

    # Create the Window
    window = sg.Window('Pharmanet - Staff Home', layout, icon=functions.getIcon())

    # Handle events
    while True:
        event, values = window.read()

        match event:

            # Window Closed
            case sg.WIN_CLOSED | "-exit-":
                quit()

            # Scan Button Press
            case "-scan-":
                window.close()
                staff.qrCodeScanner()

            # Show Bookings Button Press
            case "-showbookings-":
                window.close()
                staff.showApprovedBookings()

            case "-approvebookings-":
                window.close()
                staff.approveBookings()

            # Show Order Button Press
            case "-showorders-":
                window.close()
                staff.showOrders()

            # List Products Button Press
            case "-listproducts-":
                window.close()
                staff.listProducts(None)

            # List Categories Button Press
            case "-listcategories-":
                window.close()
                staff.listCategories()

            # Add Product Button Press
            case "-addproduct-":
                window.close()
                staff.addProduct()

            # Add Category Button Press
            case "-addcategory-":
                window.close()
                staff.addCategory()

            case "-datavisualization-":
                window.close()
                staff.dataVisualization()

    window.close()
