#############
# Packages #
#############

# ReportLab Packages #
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors

# Other Packages #
import io
import datetime

################
# Module Files #
################
from app import models

# Set Styles 
styles=getSampleStyleSheet()


###############################
# Create Booking Confirmation #
###############################
def createBookingConformation(customerID, fileLocation, bookingDate, bookingTime, bookingQRCode):
    
    session = models.Session()

    doc = SimpleDocTemplate(
        fileLocation,
        title='Pharmanet Booking Confirmation',
        pagesize=letter,
        rightMargin=72,leftMargin=72,
        topMargin=72,bottomMargin=18
    )

    content = []

    # 
    customer = session.query(models.Customer).filter(models.Customer.id == customerID).first() 

    
    # Add Title 
    content.append(Paragraph('Pharmanet Booking Confirmation', styles['Title']))

    # Add Pharmanet Logo
    logoImage = Image("logo.png", 3*inch, 3*inch)
    content.append(logoImage)

    # Add Today's Date and Time
    todaysDateTime = datetime.datetime.now().strftime('%A %d %B %Y %H:%M')
    content.append(Paragraph(todaysDateTime, styles['Normal']))

    # Add a spacer between DateTime and Dear
    content.append(Spacer(1, 12))

    # Dear
    dearText = f'Dear {customer.forename},'
    content.append(Paragraph(dearText, styles['Normal']))

    # Add a spacer between Dear and Body
    content.append(Spacer(1, 12))

    # Body
    body=f'This letter confirms that you have booked to visit the Pharmacy on: {bookingDate} at {bookingTime}. We look forward to seeing you soon...'
    content.append(Paragraph(body, styles['Normal']))

    # Add QRCode
    bio = io.BytesIO()
    bookingQRCode.save(bio, format='PNG')
    content.append(Image(bio, 2*inch, 2*inch))

    doc.build(content)

#############################
# Create Order Confirmation #
#############################
def createOrderConformation(customerID, fileLocation, collectionDate, collectionTime, orderQRCode, orderTable, moneyInformation):
    
    orderTable.insert(0, ['Product', 'Price', 'Quantity', 'Total'])
    session = models.Session()

    doc = SimpleDocTemplate(
        fileLocation,
        title='Pharmanet Order Confirmation',
        pagesize=letter,
        rightMargin=72,leftMargin=72,
        topMargin=72,bottomMargin=18
    )

    content = []

    # 
    customer = session.query(models.Customer).filter(models.Customer.id == customerID).first() 

    
    # Add Title 
    content.append(Paragraph('Pharmanet Order Confirmation', styles['Title']))

    # Add Pharmanet Logo
    logoImage = Image("logo.png", 3*inch, 3*inch)
    content.append(logoImage)

    # Add Today's Date and Time
    todaysDateTime = datetime.datetime.now().strftime('%A %d %B %Y %H:%M')
    content.append(Paragraph(todaysDateTime, styles['Normal']))

    # Add a spacer between DateTime and Dear
    content.append(Spacer(1, 12))

    # Dear
    dearText = f'Dear {customer.forename},'
    content.append(Paragraph(dearText, styles['Normal']))

    # Add a spacer between Dear and Body
    content.append(Spacer(1, 12))

    # Body
    body=f'This letter confirms that you have ordered the following items. You can collect them from the pharmacy on: {collectionDate} at {collectionTime}. We look forward to seeing you soon...'
    content.append(Paragraph(body, styles['Normal']))

    # Add QRCode
    bio = io.BytesIO()
    orderQRCode.save(bio, format='PNG')
    content.append(Image(bio, 2*inch, 2*inch))

    # Add Table
    tableStyle = TableStyle([
        ("FONT", (0,0), (3,0), "Helvetica-Bold"),
        ("INNERGRID", (0,0), (-1,-1), 0.25, colors.black),
        ("BOX", (0,0), (-1,-1), 0.25, colors.black)
    ])
    content.append(Table(orderTable, style=tableStyle))

    # Add a spacer between table and Money Information
    content.append(Spacer(1, 12))
    
    # Add Money Information
    money = f"Sub Total: {moneyInformation['sub_total']} \n VAT: {moneyInformation['vat']} \n Total: {moneyInformation['total']}"
    content.append(Paragraph(money, styles['Normal']))

    session.close()
    doc.build(content)

