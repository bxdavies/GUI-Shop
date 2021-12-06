#############
# Libraries #
#############
import PySimpleGUI as sg
import qrcode
from datetime import datetime, timedelta
import io
import os
import webbrowser
import json

################
# Module Files #
################
from app import models, main, pdf


##########################
# Convert Image to Bytes #
##########################
def convertToBytes(img):
    '''
    Convert Image to Bytes

    Parameters:
        img: Image to convert to Bytes

    Returns:
        bio.getvalue(): Bytes Value
    '''

    # Internalize a Bytes Object
    bio = io.BytesIO()

    # Save the image as a PNG
    img.save(bio, format="PNG")

    # Delete the image
    del img

    # Return the image Bytes Value
    return bio.getvalue()


###############
# New Booking #
###############
def new(customerID):
    '''
    Create a new Booking

    Parameters:
        customerID: Customer ID (int)
    '''
    # Database Session
    session = models.Session()

    # Get Customer
    customer = session.query(models.Customer).filter(
        models.Customer.id == customerID).first()

    # Define Window Layout
    layout = [
        [sg.Text('New Booking', font='Any 30',justification='center', expand_x=True)],
        [sg.Text('Chose a Date and AM or PM and click Find Times!', justification='center', expand_x=True)],
        [sg.Input(key='-calendar-'), sg.CalendarButton('Date', key="-calendar-", format='%A %d %B %Y', locale="en_GB.utf8'"), sg.Spin(('AM', 'PM'), key="-time-")],
        [sg.Button('Find Times', key="-findtimes-")],
        [sg.HorizontalSeparator(pad=(10, 10))],
        [sg.Button('Main Menu', key="-mainmenu-")]
    ]

    # Create the Window
    window = sg.Window('Pharmanet - New Booking', layout)

    # Handle events
    while True:
        event, values = window.read()

        match event:

            # Window Closed
            case sg.WIN_CLOSED | "-mainmenu-":
                session.close()
                main.customerHome()

            # Find times button press
            case "-findtimes-":
                window.hide()
                session.close()
                listTimes(customerID, window,
                          values["-calendar-"], values["-time-"])

    window.close()


##############
# List times #
##############
def listTimes(customerID, newWindow, date, time):
    '''
    List times for the specified date and AM / PM

    Parameters:
        customerID: Customer ID (int)
        newWindow: Previous Window object
        date: Booking Date
        time: AM / PM
    '''

    # Database Session
    session = models.Session()

    # Get Customer
    customer = session.query(models.Customer).filter(
        models.Customer.id == customerID).first()

    # Define variables
    timeslots = []
    timeSlotsEvents = []

    # Set time range based on AM or PM opening times
    match time:
        case 'AM':
            timerange = range(9, 12)
        case 'PM':
            timerange = range(12, 18)

    # Loop through time range
    for hour in timerange:

        # Loop through minutes in the hour in 10 minute intervals
        for minute in range(0, 60, 10):

            # Convert Strings to DateTime objects
            bookingStart = datetime.strptime(
                f'{date} {hour}:{minute}', '%A %d %B %Y %H:%M')
            bookingEnd = bookingStart + timedelta(minutes=10)

            # Convert DateTime objects to String Times
            bookingStartTime = datetime.strftime(bookingStart, '%H:%M')
            bookingEndTime = datetime.strftime(bookingEnd, '%H:%M')

            # Query time against the DB
            booking = session.query(models.Booking).filter(
                models.Booking.booking_datetime == bookingStart).first()

            # Check if time exists in Query
            if booking is None:
                eventKey = f"-time{bookingStartTime}-"
                timeSlotsEvents.append(eventKey)
                timeslots.append(
                    [sg.Text(f'{bookingStartTime} - {bookingEndTime}'), sg.Button('Book', key=eventKey)]
                )
                
            else:
                timeslots.append(
                    [sg.Text(f'{bookingStartTime} - {bookingEndTime}'), sg.Text('Booked')]
                )

    # Define Window Layout
    layout = [
        [sg.Text('Timeslots', font='Any 30', justification='center', expand_x=True)],
        [sg.Text('Chose a timeslot by clicking the Book button!', justification='center', expand_x=True)],
        [sg.Column(timeslots, scrollable=True, vertical_scroll_only=True, justification='center')],
        [sg.HorizontalSeparator(pad=(10, 10))],
        [sg.Button('Main Menu', key="-mainmenu-")]
    ]

    # Create the Window
    window = sg.Window('Pharmanet - Booking Times', layout)

    # Handle events
    while True:
        event, values = window.read()

        match event:

            # Window Closed
            case sg.WIN_CLOSED:
                newWindow.un_hide()
                break

            case "-mainmenu-":
                newWindow.close()
                session.close()
                window.close()
                main.customerHome(customerID)

            # Book button press
            case timeSlotsEvents:

                # Remove time and hyphens from event key
                time = event.replace('time', '')
                time = time.replace('-', '')

                # Convert to DateTime object
                bookingStart = datetime.strptime(
                    f'{date} {time}', '%A %d %B %Y %H:%M')

                # Add to the Database
                booking = models.Booking(
                    customer_id=customer.id, booking_datetime=bookingStart)
                session.add(booking)
                session.commit()

                # Close the window and open edit booking Window
                bookingID = booking.id
                session.close()
                window.close()
                edit(customerID, bookingID)

    window.close()


################
# Edit Booking #
################
def edit(customerID, bookingID):
    '''
    Edit / Show a booking

    Parameters:
        customerID: Customer ID (int)
        bookingID: Booking ID
    '''

    # Database Session
    session = models.Session()

    # Get booking object from bookingID
    booking = session.query(models.Booking).filter(
        models.Booking.id == bookingID).first()

    # Convert Booking Date Time to correctly formatted python DateTime object
    bookingDateTime = datetime.strftime(
        booking.booking_datetime, '%A %d %B %Y %H:%M')

    # Define JSON for QRCode
    bookingJSON = {
        'booking': booking.id
    }

    # Create QRCode object from JSON
    bookingQRCode = qrcode.make(json.dumps(bookingJSON))

    # Define a group of Buttons
    buttons = [
        [
            sg.Input('', do_not_clear=False, visible=False, key="-save-", enable_events=True),
            sg.FileSaveAs('Save Booking Confirmation', file_types=(("PDF", "*.pdf"), ), initial_folder=os.path.expanduser('~/Documents')),
            sg.Button(f'Cancel Booking', key="-cancel-")
        ]
    ]

    # Define Window Layout
    layout = [
        [sg.Text('Booking', font='Any 30', justification='center', expand_x=True)],
        [sg.Text(f'{bookingDateTime}', font='Any 20', justification='center', expand_x=True)],
        [sg.Text('Cancel or Save your booking', justification='center', expand_x=True)],
        [sg.Image(source=convertToBytes(bookingQRCode), expand_x=True)],
        [sg.Frame('', buttons, expand_x=True, relief='flat', element_justification='center')],
        [sg.HorizontalSeparator(pad=(10, 10))],
        [sg.Button('Main Menu', key="-mainmenu-")]
    ]

    # Create the Window
    window = sg.Window('Pharmanet - Booking', layout)

    # Handle events
    while True:
        event, values = window.read()

        match event:

            # Window Closed or Main Menu button pressed
            case sg.WIN_CLOSED | "-mainmenu-":
                session.close()
                window.close()
                main.customerHome(customerID)

            # Cancel Button pressed
            case "-cancel-":
                session.query(models.Booking).filter(
                    models.Booking.id == bookingID).delete()
                session.commit()
                session.close()
                window.close()
                main.customerHome(customerID)

            # Save Button pressed
            case "-save-":
                bookingDate = datetime.strftime(booking.booking_datetime, '%A %d %B %Y')
                bookingTime = datetime.strftime(booking.booking_datetime, '%H:%M')
                pdf.createBookingConformation(
                    customerID, 
                    values['-save-'], 
                    bookingDate, 
                    bookingTime, 
                    bookingQRCode
                )
                webbrowser.open_new(values['-save-'])

    window.close()
