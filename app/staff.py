#############
# Libraries #
#############
import PySimpleGUI as sg
from datetime import datetime
import cv2
import json
from decimal import Decimal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


################
# Module Files #
################
from app import models, main, functions


###################
# QR Code Scanner #
###################
def qrCodeScanner():
    ''' Scan a QR Code and display the booking or order '''

    # Database Session
    session = models.Session()

    layout = [
        [sg.Text('QR Code Scanner', font='Any 30', justification='center', expand_x=True)],
        [sg.Text('Scan a QR Code to show Order or Booking Details', justification='center', expand_x=True)],
        [sg.Image(filename='', key='image')],
        [sg.HorizontalSeparator(pad=(10, 10))],
        [sg.Button('Main Menu', key="-mainmenu-")]
    ]

    # Create the Window
    window = sg.Window('GUI Shop - QR Code Scanner', layout, icon=functions.getIcon())

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
                booking = session.query(models.Booking).filter(
                    models.Booking.id == dataDict['booking']).first()
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
                session.close()
                window.close()
                orderDetails(dataDict['order'])

        imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
        window['image'].update(data=imgbytes)

    window.close()


#################
# Show Bookings #
#################
def showApprovedBookings():
    ''' Show a table of approved bookings '''

    # Database Session
    session = models.Session()

    bookingsList = []
    bookings = session.query(models.Booking).filter(
        models.Booking.booking_datetime >= datetime.now(), 
        models.Booking.used == False, models.Booking.approved == True).order_by(models.Booking.booking_datetime).all()
    
    for booking in bookings:
        bookingsList.append([booking.id, f'{booking.customer.forename} {booking.customer.surname}', datetime.strftime(
            booking.booking_datetime, '%A %d %B %Y %H:%M')])

    if not bookingsList:
        bookingsList = [['', 'No bookings Found', '']]

    layout = [
        [sg.Text('Customer Bookings',  font='Any 30', justification='center', expand_x=True)],
        [sg.Text('All Customer Bookings greater than today, that have been approved.', justification='center', expand_x=True)],
        [sg.Table(values=bookingsList, headings=['ID', 'Customer Name', 'Date and Time'], enable_click_events=True, key="-bookings-")],
        [sg.HorizontalSeparator(pad=(10, 10))],
        [sg.Button('Main Menu', key="-mainmenu-")]
    ]

    window = sg.Window('GUI Shop - Staff Bookings', layout, icon=functions.getIcon())

    while True:
        event, values = window.read()

        match event:
            case sg.WIN_CLOSED | "-mainmenu-":
                window.close()
                main.staffHome()
            case _:
                if isinstance(event, tuple):
                    if event[2][0] in range(0, len(bookingsList)):
                        booking = session.query(models.Booking).filter(
                            models.Booking.id == bookingsList[event[2][0]][0]).first()
                        booking.collected = True
                        session.commit()
                        session.close()
                        window.close()
                        showApprovedBookings()


####################
# Approve Bookings #
####################
def approveBookings():
    ''' SHow a table of bookings that needs to be approved'''
    # Database Session
    session = models.Session()

    bookingsList = []
    bookings = session.query(models.Booking).filter(
        models.Booking.booking_datetime >= datetime.now(), 
        models.Booking.used == False, models.Booking.approved == False).order_by(models.Booking.booking_datetime).all()
    
    for booking in bookings:
        bookingsList.append([booking.id, f'{booking.customer.forename} {booking.customer.surname}', datetime.strftime(
            booking.booking_datetime, '%A %d %B %Y %H:%M')])

    if not bookingsList:
        bookingsList = [['', 'No bookings Found', '']]

    layout = [
        [sg.Text('Approve Customer Bookings',  font='Any 30', justification='center', expand_x=True)],
        [sg.Text('All Customer Bookings greater than today, that are are waiting to be improved.', justification='center', expand_x=True)],
        [sg.Table(values=bookingsList, headings=['ID', 'Customer Name', 'Date and Time'], enable_click_events=True, key="-bookings-")],
        [sg.HorizontalSeparator(pad=(10, 10))],
        [sg.Button('Main Menu', key="-mainmenu-")]
    ]

    window = sg.Window('GUI Shop - Staff Bookings', layout, icon=functions.getIcon())

    while True:
        event, values = window.read()

        match event:
            case sg.WIN_CLOSED | "-mainmenu-":
                window.close()
                main.staffHome()
            case _:
                if isinstance(event, tuple):
                    if event[2][0] in range(0, len(bookingsList)):
                        booking = session.query(models.Booking).filter(
                            models.Booking.id == bookingsList[event[2][0]][0]).first()
                        booking.approved = True
                        session.commit()
                        session.close()
                        window.close()
                        showApprovedBookings()


###############
# Show Orders #
###############
def showOrders():
    ''' Show All Customer Orders '''

    # Database Session
    session = models.Session()

    ordersList = []
    orders = session.query(models.Order).filter(
        models.Order.completed == False).all()
    for order in orders:
        ordersList.append([order.id, f'{order.customer.forename} {order.customer.surname}', datetime.strftime(
            order.collection_datetime, '%A %d %B %Y %H:%M')])

    if ordersList == []:
        ordersList = [['', 'No Orders Found', '']]

    layout = [
        [sg.Text('Customer Orders', font='Any 30', justification='center', expand_x=True)],
        [sg.Text('Show all customer orders', justification='center', expand_x=True)],
        [sg.Table(values=ordersList, headings=['ID', 'Customer Name', 'Date and Time'], enable_click_events=True, key="-bookings-")],
        [sg.HorizontalSeparator(pad=(10, 10))],
        [sg.Button('Main Menu', key="-mainmenu-")]
    ]

    window = sg.Window('GUI Shop - Staff Bookings', layout, icon=functions.getIcon())

    while True:
        event, values = window.read()

        match event:
            case sg.WIN_CLOSED | "-mainmenu-":
                window.close()
                main.staffHome()

        if isinstance(event, tuple):
            orderDetails(ordersList[event[2][0]][0])

    window.close()


#################
# Order Details #
#################
def orderDetails(orderID):
    ''' 
    Edit / Show Order

    Parameters:
        orderID: Order ID (int)

    '''

    # Database Session
    session = models.Session()

    order = session.query(models.Order).filter(
        models.Order.id == orderID).first()
    subOrders = session.query(models.SubOrder).filter(
        models.SubOrder.order == order).all()

    orderTable = []

    for subOrder in subOrders:
        orderTable.append([subOrder.product.name, f'£{subOrder.product.price}',
                          subOrder.product_quantity, f'£{subOrder.product.price*subOrder.product_quantity}'])

    vat = round(order.total * Decimal('0.20'), 2)
    vat = f'VAT: £{vat}'
    subTotal = f'SubTotal: £{order.sub_total}'
    total = f'Total: £{order.total}'

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
    window = sg.Window('GUI Shop - Collect Confirmation', layout, icon=functions.getIcon())

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


#################
# List Products #
#################
def listProducts(category):
    ''' 
    Shop Window Displaying Products

    Parameters:
        customerID: Customer ID (int)
        category: Category Name (string)
        cart: Customers Shopping Cart (list)
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

            # Check if product has category!
            if product.category == None:
                sg.PopupError(f'{product.name} does not have category so will not be displayed!')
                continue

            productIDs.append(product.id)

            # If product ID is an even number then add to Column 2 if its not add to Column 1
            if (product.id % 2) == 0:

                # Add Product Details to Product Column 2
                productsCol2.append([sg.HorizontalSeparator()])
                productsCol2.append([sg.Text(product.name)])
                productsCol2.append(
                    [sg.Image(functions.urlToImage(product.image), size=(200, 200))]
                )
                productsCol2.append(
                    [sg.Text(functions.wrapText(product.description, 60))]
                )
                productsCol2.append(
                    [sg.Text(product.category.name), sg.Text(product.stock)]
                )
                productsCol2.append(
                    [sg.Button('Delete Product', key=f"-product{product.id}-",)]
                )
            else:

                # Add Product Details to Product Column 1
                productsCol1.append([sg.HorizontalSeparator()])
                productsCol1.append([sg.Text(product.name)])
                productsCol1.append(
                    [sg.Image(functions.urlToImage(product.image), size=(200, 200))]
                )
                productsCol1.append(
                    [sg.Text(functions.wrapText(product.description, 60))]
                )
                productsCol1.append(
                    [sg.Text(product.category.name), sg.Text(product.stock)]
                )
                productsCol1.append(
                    [sg.Button('Delete Product', key=f"-product{product.id}-",)]
                )

    # Show products based on Category provided
    else:

        # Query Database for Category and Product
        category = session.query(models.Category).filter(
            models.Category.name == category).first()
        products = session.query(models.Product).filter(
            models.Product.category == category).all()

        # Loop through products and add to columns
        for product in products:

            # If product ID is an even number then add to Column 2 if its not add to Column 1
            productIDs.append(product.id)
            if (product.id % 2) == 0:

                # Add Product Details to Product Column 2
                productsCol2.append([sg.HorizontalSeparator()])
                productsCol2.append([sg.Text(product.name)])
                productsCol2.append(
                    [sg.Image(functions.urlToImage(product.image), size=(200, 200))]
                )
                productsCol2.append(
                    [sg.Text(functions.wrapText(product.description, 60))]
                )
                productsCol2.append(
                    [sg.Text(product.category.name), sg.Text(product.stock)]
                )
                productsCol2.append(
                    [sg.Button('Delete Product', key=f"-product{product.id}-",)]
                )
            else:

                # Add Product Details to Product Column 1
                productsCol1.append([sg.HorizontalSeparator()])
                productsCol1.append([sg.Text(product.name)])
                productsCol1.append(
                    [sg.Image(functions.urlToImage(product.image), size=(200, 200))]
                )
                productsCol1.append(
                    [sg.Text(functions.wrapText(product.description, 60))]
                )
                productsCol1.append(
                    [sg.Text(product.category.name), sg.Text(product.stock)]
                )
                productsCol1.append(
                    [sg.Button('Delete Product', key=f"-product{product.id}-",)]
                )

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
    cartCol = [

    ]

    productsCol = [
        [sg.Column(productsCol1, key="-productsCol1-", vertical_scroll_only=True, expand_x=True, element_justification='center', vertical_alignment='top'),
         sg.Column(productsCol2, vertical_scroll_only=True, expand_x=True, element_justification='center', vertical_alignment='top')],
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
    window = sg.Window('GUI Shop - Shop', layout, icon=functions.getIcon())

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
                session.query(models.Product).filter(
                    models.Product.id == productID).delete()
                session.execute('SET FOREIGN_KEY_CHECKS = 1')
                session.commit()
                session.close()
                window.close()
                listProducts(None)

    window.close()


###################
# List Categories #
###################
def listCategories():
    ''' List all categories '''

    session = models.Session()

    categoriesList = []

    categories = session.query(models.Category).all()
    for category in categories:
        categoriesList.append(
            [category.id, category.name, category.description]
        )

    if categoriesList == []:
        categoriesList = [['.', '', 'No categories found']]

    layout = [
        [sg.Text('Shop', font='Any 30', justification='center', expand_x=True)],
        [sg.Text('Click on a category to delete', font='Any 20', justification='center', expand_x=True)],
        [sg.Table(values=categoriesList, headings=['ID', 'Name','Description'], enable_click_events=True, key="-bookings-")],
        [sg.Button('Main Menu', key="-mainmenu-")]
    ]

    window = sg.Window('GUI Shop - Categories', layout, icon=functions.getIcon())

    while True:
        event, values = window.read()

        match event:
            case sg.WIN_CLOSED | "-mainmenu-":
                window.close()
                main.staffHome()

        if isinstance(event, tuple):
            if event[2][0] in range(0, len(categoriesList)):
                session.execute('SET FOREIGN_KEY_CHECKS = 0')
                session.query(models.Category).filter(
                    models.Category.id == categoriesList[event[2][0]][0]).delete()
                session.execute('SET FOREIGN_KEY_CHECKS = 1')
                session.commit()
                session.close()
                window.close()
                listCategories()

    window.close()


###############
# Add Product #
###############
def addProduct():
    ''' Add Product '''

    # Database Session
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

    window = sg.Window('GUI Shop - Add Product', layout, icon=functions.getIcon())

    while True:
        event, values = window.read()

        match event:
            case sg.WIN_CLOSED | "-mainmenu-":
                window.close()
                main.staffHome()
            case "-add-":
                category = session.query(models.Category).filter(
                    models.Category.name == values["-category-"]).first()
                product = models.Product(
                    name=values["-name-"], 
                    description=values["-description-"],
                    image=values["-image-"], 
                    price=values["-price-"], 
                    category=category, 
                    stock=values["-stock-"]
                )
                session.add(product)
                session.commit()
                window.close()
                listProducts(None)
    window.close()


################
# Add Category #
################
def addCategory():
    ''' Add a category '''

    # Database Session
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

    window = sg.Window('GUI Shop - Add Category', layout, icon=functions.getIcon())

    while True:
        event, values = window.read()

        match event:
            case sg.WIN_CLOSED | "-mainmenu-":
                window.close()
                main.staffHome()
            case "-add-":
                category = models.Category(
                    name=values["-name-"], description=values["-description-"])
                session.add(category)
                session.commit()
                window.close()
                listCategories()
    window.close()


######################
# Data Visualization #
######################
def dataVisualization(report=None):

    # Database Session
    session = models.Session()

    plt.cla()
    reports = ['Products By Category', 'Most Ordered Products']

    if report not in reports:
        report = 'Products By Category'

    match report:
        case 'Most Ordered Products':
            subOrders = session.query(models.SubOrder).all()

            productsCount = []
            for subOrder in subOrders:
                if subOrder.product_quantity > 1:
                    for i in range(subOrder.product_quantity):
                        productsCount.append(subOrder.product.name)
                else:
                    productsCount.append(subOrder.product.name)

            my_dict = {i: productsCount.count(i) for i in productsCount}
            
            keysList = list(my_dict.keys())
            keys = functions.wrapText(keysList, 15)

            values = my_dict.values()

            x_pos = []
            for i in range(len(keysList)):
                x_pos.append(i * 4)

            plt.bar(x_pos, values, align='center')

            plt.xticks(x_pos, keys)

        case 'Products By Category':
            products = session.query(models.Product).all()

            productsList = []
            for product in products:
                productsList.append(product.category.name)

            my_dict = {i: productsList.count(i) for i in productsList}

            keys = functions.wrapText(list(my_dict.keys()), 10)

            values = my_dict.values()

            plt.pie(values, labels=keys)

    fig = plt.gcf()
    fig.set_size_inches(12.5, 8.5)

    def drawFigure(canvas, figure):
        figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
        return figure_canvas_agg

    layout = [
        [sg.Text(report)],
        [sg.Text('Below is the Generated Report')],
        [sg.Combo(reports, key='-report-', enable_events=True, default_value=report)],
        [sg.Canvas(key="-canvas-")],
        [sg.Button('Main Menu', key="-mainmenu-")]
    ]

    # create the form and show it without the plot
    window = sg.Window('GUI Shop - Staff Data Visualisation',
                       layout, finalize=True, element_justification='center', icon=functions.getIcon())

    # add the plot to the window
    drawFigure(window["-canvas-"].TKCanvas, fig)

    # Handle events
    while True:
        event, values = window.read()

        match event:

            # Window Closed
            case sg.WIN_CLOSED | "-mainmenu-":
                session.close()
                window.close()
                main.staffHome()

            case "-report-":
                session.close()
                window.close()
                dataVisualization(values["-report-"])

    window.close()
