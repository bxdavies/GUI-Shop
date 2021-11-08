import PySimpleGUI as sg
from app import models, main
from datetime import datetime
import cv2
import json
from decimal import Decimal
from PIL import ImageQt
import requests
from io import BytesIO
import textwrap

def wrapText(text, size=30):
    return "\n".join(textwrap.wrap(text, size))

def urlToImage(url):
    response = requests.get(url, stream=True)
    response.raw.decode_content = True
    img = ImageQt.Image.open(response.raw)
    with BytesIO() as output:
        img.save(output, format="PNG")
        data = output.getvalue()
    return data


###################
# QR Code Scanner #
###################
def qrCodeScanner():
    ''' Scan a QR Code and display the booking or order '''

    session = models.Session()

    layout = [
        [sg.Text('QR Code Scanner', font='Any 30', justification='center', expand_x=True)],
        [sg.Text('Scan a QR Code to show Order or Booking Details', justification='center', expand_x=True)],
        [sg.Image(filename='', key='image')],
        [sg.HorizontalSeparator(pad=(10, 10))],
        [sg.Button('Main Menu', key="-mainmenu-")]
    ]
    
    # Create the Window
    window = sg.Window('Pharmanet - QR Code Scanner', layout)
    
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()

    while True:
        event, values = window.read(timeout=20)

        match event:

            case sg.WIN_CLOSED | "-mainmenu-":
                cap.release()
                cv2.destroyAllWindows()
                session.close()
                window.close()
                main.staffHome()

        _, frame = cap.read()
        data, bbox, _ = detector.detectAndDecode(frame)

        if data:
            dataDict = json.loads(data)

            if 'booking' in dataDict:
                booking = session.query(models.Booking).filter(models.Booking.id == dataDict['booking']).first()
                booking.collected = True
                session.commit()
                nicstring = f"""
                Booking: {booking.id}
                Name: {booking.customer.forename} {booking.customer.surname}
                Has been marked as visted
                """
                sg.popup(nicstring)
                break
            elif 'order' in dataDict:
                print(dataDict['order'])

        imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
        window['image'].update(data=imgbytes)

    window.close()

    
#################
# Show Bookings #
#################
def showBookings():
    ''' Show a table of bookings '''

    session = models.Session()

    bookingsList = []
    bookings = session.query(models.Booking).filter(models.Booking.used == False, models.Booking.booking_datetime >= datetime.now()).order_by(models.Booking.booking_datetime).all()
    for booking in bookings:
        bookingsList.append([booking.id, f'{booking.customer.forename} {booking.customer.surname}', datetime.strftime(booking.booking_datetime, '%A %d %B %Y %H:%M')])

    if not bookingsList:
        bookingsList = [['', 'No bookings Found', '']]

    layout = [
        [sg.Text('Customer Bookings',  font='Any 30', justification='center', expand_x=True)],
        [sg.Text('All Customer Bookings greater than today.', justification='center', expand_x=True)],
        [sg.Table(values=bookingsList, headings=['ID', 'Customer Name','Date and Time'], enable_click_events=True, key="-bookings-")],
        [sg.HorizontalSeparator(pad=(10, 10))],
        [sg.Button('Main Menu', key="-mainmenu-")]
    ]
    
    window = sg.Window('Pharmanet - Staff Bookings', layout)

    while True:
        event, values = window.read()

        match event:
            case sg.WIN_CLOSED | "-mainmenu-":
                window.close()
                main.staffHome()
            case _:
                if isinstance(event, tuple):
                    if event[2][0] in range(0, len(bookingsList)):
                        booking = session.query(models.Booking).filter(models.Booking.id == bookingsList[event[2][0]][0]).first()
                        booking.collected = True
                        session.commit()
                        session.close()
                        window.close()
                        showBookings()


def showOrders():

    session = models.Session()

    ordersList = []
    orders = session.query(models.Order).filter(models.Order.completed == False).all()
    for order in orders:
        ordersList.append([order.id, f'{order.customer.forename} {order.customer.surname}', datetime.strftime(order.collection_datetime, '%A %d %B %Y %H:%M')])
    
    if ordersList == []:
        ordersList= [['', 'No Orders Found', '']]
    
    layout = [
        [sg.Text('Customer Orders', font='Any 30', justification='center', expand_x=True)],
        [sg.Text('Show all customer orders',  justification='center', expand_x=True)],
        [sg.Table(values=ordersList, headings=['ID', 'Customer Name','Date and Time'], enable_click_events=True, key="-bookings-")],
        [sg.Button('Main Menu', key="-mainmenu-")]
    ]

    window = sg.Window('Pharmanet - Staff Bookings', layout)

    while True:
        event, values = window.read()

        match event:
            case sg.WIN_CLOSED | "-mainmenu-":
                window.close()
                main.staffHome()
            
        if isinstance(event, tuple):
            orderDetails(ordersList[event[2][0]][0])

    window.close()

def orderDetails(orderID):

    session = models.Session()

    order = session.query(models.Order).filter(models.Order.id == orderID).first()
    subOrders = session.query(models.SubOrder).filter(models.SubOrder.order == order).all()

    orderTable = []

    for subOrder in subOrders:
        orderTable.append([subOrder.product.name, f'£{subOrder.product.price}' ,subOrder.product_quantity, f'£{subOrder.product.price*subOrder.product_quantity}'])

    vat = round(order.total * Decimal('0.20'), 2)
    vat = f'VAT: £{vat}'
    subTotal = f'SubTotal: £{order.sub_total}'
    total =  f'Total: £{order.total}'

    money = [
        [sg.Text(subTotal), sg.Text(vat), sg.Text(total)]
    ]

    layout = [
        [sg.Text('Order Details', font='Any 30', justification='center', expand_x=True)],
        [sg.Text(f'Order {orderID}, details', justification='center', expand_x=True)],
        [sg.Text(f'Customer Name: {order.customer.forename} {order.customer.surname}')],
        [sg.Table(orderTable, headings=['Product', 'Price', 'Quantity', 'Total'], justification='center', expand_x=True)],
        [sg.Frame('', money, expand_x=True, relief='flat', element_justification='center')],
        [sg.HorizontalSeparator(pad=(10, 10))],
        [sg.Button('Main Menu', key="-mainmenu-")]
    ]

    # Create the Window
    window = sg.Window('Pharmanet - Collect Confirmation', layout)
      # Handle events
    while True:

        event, values = window.read()

        match event:

            # Window Closed or Main Menu Button Pressed
            case sg.WIN_CLOSED | "-mainmenu-":
                session.close()
                window.close()
                main.staffHome()
            
    window.close()


    

def listProducts(category):
    ''' 
    Shop Window Displaying Products

    Parameters:
        customerID: Customer ID (int)
        category: Category Name (string)
        cart: Customers Shopping Cart (list)

    Returns:
        Category: Reloads this window passing the category
        Cart: Shows the Cart window
        Main Menu: Returns Customer Home Window
    '''

    # Database Session 
    session = models.Session()

    # Window Variables 
    productsCol1 = []
    productsCol2 = []
    productIDs = []


    # Get a list of categories 
    categories = ['All']
    for acategory in session.query(models.Category).all():
        categories.append(acategory.name)

    # Category is None or all so show all products
    if category is None or category == 'All':
        
        # Query Database for all Products
        products = session.query(models.Product).all()

        # Loop through products and add to columns 
        for product in products:
            productIDs.append(product.id)

            # If product ID is an even number then add to Column 2 if its not add to Column 1
            if (product.id % 2) == 0:

                # Add Product Details to Product Column 2
                productsCol2.append([sg.HorizontalSeparator()])
                productsCol2.append([sg.Text(product.name)])
                productsCol2.append([sg.Image(urlToImage(product.image), size=(200, 200))])
                productsCol2.append([sg.Text(wrapText(product.description, 60))])
                productsCol2.append([sg.Text(product.category.name), sg.Text(product.stock)])
                productsCol2.append([sg.Button('Add to Cart', key=f"-product{product.id}-",)])
            else:

                # Add Product Details to Product Column 1
                productsCol1.append([sg.HorizontalSeparator()])
                productsCol1.append([sg.Text(product.name)])
                productsCol1.append([sg.Image(urlToImage(product.image), size=(200, 200))])
                productsCol1.append([sg.Text(wrapText(product.description, 60))])
                productsCol1.append([sg.Text(product.category.name), sg.Text(product.stock)])
                productsCol1.append([sg.Button('Add to Cart', key=f"-product{product.id}-",)])
                
    # Show products based on Category provided 
    else:

        # Query Database for Category and Product
        category = session.query(models.Category).filter(models.Category.name == category).first()
        products = session.query(models.Product).filter(models.Product.category == category).all()
        
        # Loop through products and add to columns 
        for product in products:

            # If product ID is an even number then add to Column 2 if its not add to Column 1
            productIDs.append(product.id)
            if (product.id % 2) == 0:

                # Add Product Details to Product Column 2
                productsCol2.append([sg.HorizontalSeparator()])
                productsCol2.append([sg.Text(product.name)])
                productsCol2.append([sg.Image(urlToImage(product.image), size=(200, 200))])
                productsCol2.append([sg.Text(wrapText(product.description, 60))])
                productsCol2.append([sg.Text(product.category.name), sg.Text(product.stock)])
                productsCol2.append([sg.Button('Add to Cart', key=f"-product{product.id}-",)])
            else:

                # Add Product Details to Product Column 1
                productsCol1.append([sg.HorizontalSeparator()])
                productsCol1.append([sg.Text(product.name)])
                productsCol1.append([sg.Image(urlToImage(product.image), size=(200, 200))])
                productsCol1.append([sg.Text(wrapText(product.description, 60))])
                productsCol1.append([sg.Text(product.category.name), sg.Text(product.stock)])
                productsCol1.append([sg.Button('Add to Cart', key=f"-product{product.id}-",)])

    # Set Category Display Name and Description if Category is included
    if category is None or category == 'All':
        categoryToShow = 'All'
        categoryDescriptionToShow = 'All Products'
    else:
        categoryToShow = category.name
        categoryDescriptionToShow = category.description

    # Define Category Column Layout
    categoryCol = [
        [sg.Text('Select Category'), sg.Combo(categories, key='-category-', enable_events=True, default_value=categoryToShow)],
        [sg.Text(categoryDescriptionToShow)]
    ]

    # Define Cart Column Layout
    cartCol =  [
        
    ]

    productsCol = [
        [sg.Column(productsCol1, key="-productsCol1-",vertical_scroll_only=True ,expand_x=True, element_justification='center', vertical_alignment='top'), sg.Column(productsCol2, vertical_scroll_only=True, expand_x=True, element_justification='center', vertical_alignment='top')],
    ]

    # Define Window Layout
    layout = [
        [sg.Text('Shop', font='Any 30', justification='center', expand_x=True)],
        [sg.Column(categoryCol, justification='left', expand_x=True, element_justification='left', vertical_alignment='center',), sg.Column(cartCol, justification='right', expand_y=True, expand_x=True, element_justification='right')],
        [sg.Column(productsCol, size=(800, 800), scrollable=True, vertical_scroll_only=True, expand_x=True, element_justification='center', vertical_alignment='top')],
        [sg.HorizontalSeparator(pad=(10, 10))],
        [sg.Button('Main Menu', key="-mainmenu-")]
    ]

    # Create the Window
    window = sg.Window('Pharmanet - Shop', layout)

    # Handle events
    while True:
        event, values = window.read()

        match event:

            # Window Closed
            case sg.WIN_CLOSED | "-mainmenu-":
                session.close()
                window.close()
                main.staffHome()
            
            # Category Drop Down Changed
            case "-category-":
                session.close()
                window.close()
                listProducts(values["-category-"])
            
            # Add to Cart Button Pressed for a Product
            case productIDs:
                productID = event.replace('product', '')
                productID = productID.replace('-', '')
                session.execute('SET FOREIGN_KEY_CHECKS = 0')
                session.query(models.Product).filter(models.Product.id == productID).delete()
                session.execute('SET FOREIGN_KEY_CHECKS = 1')
                session.commit()
                session.close()
                window.close()
                listProducts(None)

    window.close()

def listCategories():

    session = models.Session()

    categoriesList = []

    categories = session.query(models.Category).all()
    for category in categories:
        categoriesList.append([category.id, category.name, category.description ])

    if categoriesList == []:
        categoriesList = [ ['.', '', 'No categories found']]
    
    layout = [
        [sg.Table(values=categoriesList, headings=['ID', 'Name', 'Description'], enable_click_events=True, key="-bookings-")],
        [sg.Button('Main Menu', key="-mainmenu-")]
    ]

    window = sg.Window('Pharmanet - Categories', layout)

    while True:
        event, values = window.read()

        match event:
            case sg.WIN_CLOSED | "-mainmenu-":
                window.close()
                main.staffHome()

        if isinstance(event, tuple):
            if event[2][0] in range(0, len(categoriesList)):
                print(categoriesList[event[2][0]][0])
                session.query(models.Category).filter(models.Category.id ==  categoriesList[event[2][0]][0]).delete()
                session.commit()
                session.close()
                window.close()
                listCategories()

    window.close()

def addProduct():

    session = models.Session()

    categories = []

    for acategory in session.query(models.Category).all():
        categories.append(acategory.name)

    layout = [
        [sg.Text('Add Product', font='Any 30', justification='center', expand_x=True)],
        [sg.Text('Fill out the form and click Add!', justification='center', expand_x=True)],
        [sg.Text('Name'), sg.Input(key="-name-")],
        [sg.Text('Description'), sg.Multiline(key="-description-")],
        [sg.Text('Image CDN URL'), sg.Input(key="-image-")],
        [sg.Text('Price'), sg.Input(key="-price-")],
        [sg.Text('Category'), sg.Combo(categories, key='-category-')],
        [sg.Text('Stock'), sg.Input(key="-stock-")],
        [sg.Button('Add', key="-add-")],
        [sg.HorizontalSeparator(pad=(10, 10))],
        [sg.Button('Main Menu', key="-mainmenu-")],
    ]

    window = sg.Window('Pharmanet - Add Product', layout)

    while True:
        event, values = window.read()

        match event:
            case sg.WIN_CLOSED | "-mainmenu-":
                window.close()
                main.staffHome()
            case "-add-":
                category = session.query(models.Category).filter(models.Category.name == values["-category-"]).first()
                product = models.Product(name=values["-name-"], description=values["-description-"], image=values["-image-"], price=values["-price-"], category=category, stock=values["-stock-"])
                session.add(product)
                session.commit()
                window.close()
                listProducts(None)
    window.close()

     

def addCategory():
    session = models.Session()
    
    layout = [
        [sg.Text('Add Category', font='Any 30', justification='center', expand_x=True)],
        [sg.Text('Fill out the form and click Add!', justification='center', expand_x=True)],
        [sg.Text('Category Name'), sg.Input(key="-name-")],
        [sg.Text('Category Description'), sg.Multiline(key="-description-")],
        [sg.Button('Add', key="-add-")],
        [sg.HorizontalSeparator(pad=(10, 10))],
        [sg.Button('Main Menu', key="-mainmenu-")]
    ]

    window = sg.Window('Pharmanet - Add Category', layout)

    while True:
        event, values = window.read()

        match event:
            case sg.WIN_CLOSED | "-mainmenu-":
                window.close()
                main.staffHome()
            case "-add-":
                category = models.Category(name=values["-name-"], description=values["-description-"])
                session.add(category)
                session.commit()
                window.close()
                listCategories()
    window.close()

