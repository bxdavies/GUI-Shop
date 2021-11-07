#############
# Libraries #
#############
import PySimpleGUI as sg
from decimal import Decimal
from datetime import datetime, timedelta
import qrcode
import json
import io
import os
import webbrowser

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
    

########
# Shop #
########
def shop(customerID, category, cart):
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

    if cart is None:
        cart = []

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
                productsCol2.append([sg.Image(f'app/images/products/{product.image}', size=(200, 200))])
                productsCol2.append([sg.Text(product.description)])
                productsCol2.append([sg.Text(product.category.name), sg.Text(product.stock)])
                productsCol2.append([sg.Button('Add to Cart', key=f"-product{product.id}-",)])
            else:

                # Add Product Details to Product Column 1
                productsCol1.append([sg.HorizontalSeparator()])
                productsCol1.append([sg.Text(product.name)])
                productsCol1.append([sg.Image(f'app/images/products/{product.image}', size=(200, 200))])
                productsCol1.append([sg.Text(product.description)])
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
                productsCol2.append([sg.Image(f'app/images/products/{product.image}', size=(200, 200))])
                productsCol2.append([sg.Text(product.description)])
                productsCol2.append([sg.Text(product.category.name), sg.Text(product.stock)])
                productsCol2.append([sg.Button('Add to Cart', key=f"-product{product.id}-",)])
            else:

                # Add Product Details to Product Column 1
                productsCol1.append([sg.HorizontalSeparator()])
                productsCol1.append([sg.Text(product.name)])
                productsCol1.append([sg.Image(f'app/images/products/{product.image}', size=(200, 200))])
                productsCol1.append([sg.Text(product.description)])
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
        [sg.Button('', key="-cart-", image_size=(48, 48), image_data=b'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAACLklEQVRoge3YTYhNcRjH8Y+bhTCikViiLKyIlcxQM0oWbGjs7GxkzUJZ0DTZ2lDkbUGkpryUWEmTYjRWIyVlISszTJTXsXjOje64zLj//z2jzreexe3cfs/vec7T/zznUFFRUTFbmWyI71hZqqMZcvqXOCuKOFyqoxZ5hqdlm2iFk6aOVbtiIkUBOwuxYQy0MZ7gRYoCOvAZ91OIzYBrGEol9gCfMD+V4DQYwmAqsaNijHpSCU6DV+IkTMImUcCxVIJ/oSbGNlm+uRgXo9QOVoiGHUwpOii6siClaBM2igL6UooeKES3pRRtwq4i19aUomsK0f6Uok2oN2ttauGXEp7Nf6BfFNCZWvgMvoiHW04uFHlqqYX7RGe2pxZu4B5e5xDuxDexq+RkFCO5xIfxMJd4wXvcySU+IOZzUYs6S7ABe3BIrA13xehM4lKL+k3pKRLsmMZ/l4k1ZJ9YCy7jEcZM3f3H8BhXcBxdqY3XmYcPOFH8buzkxcLI+G9Mvi2uXRV3cj96sQpzchlupFO8Zk4U0WjyjdiZzuEI9orVYHG7DDajQ3S9bnoU58UL/26sw8KyzP2N1XgujF/H+nLtzIzl4uXio8TbYbu4JY7N3rKN/AubxdjkfvJm4xS+YmnZRv6VEXF2t/N7UGO0xDvlfZWrR8vUsAXdMuznuXPVcNvPbtxMJdyuXN2m3tJcS1aWXP99ATVxK+uCN+QdoSy5aqITXakEZ0muioqKihb4AbCd8/afwF4IAAAAAElFTkSuQmCC')]
    ]

    # Define Window Layout
    layout = [
        [sg.Text('Shop', font='Any 30', justification='center', expand_x=True)],
        [sg.Column(categoryCol, justification='left', expand_x=True, element_justification='left', vertical_alignment='center',), sg.Column(cartCol, justification='right', expand_y=True, expand_x=True, element_justification='right')],
        [sg.Column(productsCol1, vertical_scroll_only=True, expand_x=True, element_justification='center', vertical_alignment='top'), sg.Column(productsCol2, vertical_scroll_only=True, expand_x=True, element_justification='center', vertical_alignment='top')],
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
               main.customerHome(customerID)
            
            # Category Drop Down Changed
            case "-category-":
                session.close()
                window.close()
                shop(customerID, values["-category-"], cart)
            
            # Cart Button Pressed 
            case "-cart-":
                session.close()
                window.close()
                showCart(customerID, cart)
            
            # Add to Cart Button Pressed for a Product
            case productIDs:
                productID = event.replace('product', '')
                productID = productID.replace('-', '')
                cart.append(productID)

    window.close()


#############
# Show Cart #
#############
def showCart(customerID, cart):
    ''' 
    Show the Customers Cart

    Parameters:
        customerID: Customer ID (int)
        cart: Customers Shopping Cart (list)

    Returns:
        Continue Shopping: Returns to the shop window retaining the existing cart contents
        Chose Collection Time: Returns the Collection Date Selection Window
    '''

    # If cart is empty don't show this window
    if not cart:
        sg.popup_auto_close('The cart can not be shown at this time as its empty. \nPlease add something to the cart and try again!', 
        auto_close_duration=5, title="Cart Error")
        shop(customerID, None, None)
    
    # Database Session 
    session = models.Session()

    # Window Variables 
    products = []
    total = 0
    cartNoDuplicates = list(dict.fromkeys(cart)) # Cart without duplicates

    # Loop through the cart without duplicates
    for productID in cartNoDuplicates:

        # If productID appears multiple times in cart then calculate based on Quantity
        if cart.count(productID) > 1:
            product = session.query(models.Product).filter(models.Product.id == productID).first()
            products.append([product.name, product.price, cart.count(productID), f'£{product.price*cart.count(productID)}'])
            total = total + product.price*cart.count(productID)
        
        # Else a product only appears once in the cart
        else:
            product = session.query(models.Product).filter(models.Product.id == productID).first()
            products.append([product.name, product.price, 1, f'£{product.price}'])
            total = total + product.price

    # Calculate VAT
    vat = round(total * Decimal('0.20'), 2)

    # Define Window Layout
    layout = [
        [sg.Text('Cart', font='Any 30', justification='center', expand_x=True)],
        [sg.Text('Products currently in your cart, once your happy chose a time.', justification='center', expand_x=True)],
        [sg.Table(products, headings=['Product', 'Price', 'Quantity', 'Total'])],
        [sg.Text(f'Sub Total: £{total}')],
        [sg.Text(f'VAT: £{vat}')],
        [sg.Text(f'Total £{total+vat}')],
        [sg.Button('Chose Collection Time', key='-collection-')],
        [sg.HorizontalSeparator(pad=(10, 10))],
        [sg.Button('Continue Shopping', key="-continueshopping-")]
       
    ]

    # Create the Window
    window = sg.Window('Pharmanet - Cart', layout)

    # Handle events
    while True:
        event, values = window.read()

        match event:

            # Window Closed
            case sg.WIN_CLOSED | "-continueshopping-":
                session.close()
                window.close()
                shop(customerID, None, cart)

            # Chose Collection Time Button Pressed
            case "-collection-":
                session.close()
                window.close()
                collectionDate(customerID, cart)

    window.close()

##################
# New collection #
##################
def collectionDate(customerID, cart):
    '''
    Create a new Collection

    Parameters:
        customerID: Customer ID (int)
        cart: Customers Shopping Cart (list)

    Returns:
        listTimes(): List Times Window
        main.customerHome(): Customer Home Window
    '''

    # Database Session 
    session = models.Session()

    # Define Window Layout
    layout = [
        [sg.Text('New Collection', font='Any 30', justification='center', expand_x=True)],
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
                main.customerHome(customerID)

            # Find times button press
            case "-findtimes-":
                window.hide()
                session.close()
                listCollectionTimes(customerID, cart, window, values["-calendar-"], values["-time-"])

    window.close()

##############
# List times #
##############
def listCollectionTimes(customerID, cart, newWindow, date, time):
    '''
    List times for the specified date and AM / PM

    Parameters:
        customerID: Customer ID (int)
        cart: Customers Shopping Cart (list)
        newWindow: Previous Window object
        date: Booking Date
        time: AM / PM

    Returns:
       Main Menu: Returns Customer Home Window
       Book: Returns Booking Confirmation Window
    '''

    # Database Session 
    session = models.Session()
    
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

            #Convert Strings to DateTime objects
            collectionStart = datetime.strptime(f'{date} {hour}:{minute}', '%A %d %B %Y %H:%M')
            collectionEnd = collectionStart + timedelta(minutes = 10)

            # Convert DateTime objects to String Times
            collectionStartTime = datetime.strftime(collectionStart, '%H:%M')
            collectionEndTime = datetime.strftime(collectionEnd, '%H:%M')

            # Query time against the DB
            collection = session.query(models.Order).filter(models.Order.collection_datetime == collectionStart).first()

            # Check if time exists in Query
            if collection is None:
                eventKey = f"-time{collectionStartTime}-"
                timeSlotsEvents.append(eventKey)
                timeslots.append([sg.Text(f'{collectionStartTime} - {collectionEndTime}'), sg.Button('Book', key=eventKey)])
            else:
                timeslots.append([sg.Text(f'{collectionStartTime} - {collectionEndTime}'), sg.Text('Booked')])

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
                collectionStart = datetime.strptime(f'{date} {time}', '%A %d %B %Y %H:%M')
                collectionEnd = collectionStart + timedelta(minutes = 10)

                collectionStartEnd = datetime.strftime(collectionStart, '%A %d %B %Y %H:%M') + ' - ' + datetime.strftime(collectionEnd, '%A %d %Y %H:%M')
                
                session.close()
                window.close()
                collect(customerID, cart, collectionStart, collectionStartEnd)

    window.close()

#############################
# Confirm Collection Window #
#############################
def collect(customerID, cart, collectionStart, collectionStartEnd):
    ''' 
    Confirm Order and Collection Time 
    
     Parameters:
        customerID: Customer ID (int)
        cart: Customers Shopping Cart (list)
        collectionStart:
        collectionStartEnd:

    Returns:
        Collect: Saves order to the database and shows order confirmation
        Main Menu: Returns Customer Home Window
    '''
    
    # Database Session 
    session = models.Session()

    # Window Variables 
    products = []
    total = 0
    cartNoDuplicates = list(dict.fromkeys(cart)) # Cart without duplicates

    # Get Customer
    customer = session.query(models.Customer).filter(models.Customer.id == customerID).first()

    # Loop through the cart without duplicates
    for productID in cartNoDuplicates:

        # If productID appears multiple times in cart then calculate based on Quantity
        if cart.count(productID) > 1:
            product = session.query(models.Product).filter(models.Product.id == productID).first()
            products.append([product.name, product.price, cart.count(productID), f'£{product.price*cart.count(productID)}'])
            total = total + product.price*cart.count(productID)
        
        # Else a product only appears once in the cart
        else:
            product = session.query(models.Product).filter(models.Product.id == productID).first()
            products.append([product.name, product.price, 1, f'£{product.price}'])
            total = total + product.price

    # Calculate VAT
    vat = round(total * Decimal('0.20'), 2)

    # Define Window Layout
    layout = [
        [sg.Text('Cart', font='Any 30', justification='center', expand_x=True)],
        [sg.Text('Products currently in your cart, once your happy chose a time.', justification='center', expand_x=True)],
        [sg.Table(products, headings=['Product', 'Price', 'Quantity', 'Total'])],
        [sg.Text(f'Sub Total: £{total}')],
        [sg.Text(f'VAT: £{vat}')],
        [sg.Text(f'Total £{total+vat}')],
        [sg.Text(f'Collection Date Time {collectionStartEnd}')],
        [sg.Button('Collect', key="-collect-")],
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
                main.customerHome(customerID)

            # Collect Button Pressed
            case "-collect-":
                order = models.Order(customer=customer, collection_datetime=collectionStart, sub_total=total, total=total+vat)
                session.add(order)
                for productID in cartNoDuplicates:

                    if cart.count(productID) > 1:
                        product = session.query(models.Product).filter(models.Product.id == productID).first()
                        subOrder = models.SubOrder(order=order, product=product, product_quantity=cart.count(productID))
                    else:
                        product = session.query(models.Product).filter(models.Product.id == productID).first()
                        subOrder = models.SubOrder(order=order, product=product, product_quantity=1)
                    session.add(subOrder)

                session.commit()
                orderID = order.id
                session.close()
                window.close()
                edit(customerID, orderID)

    window.close()

######################
# Order Confirmation #
######################
def edit(customerID, orderID):
    '''
    Edit / Show Order

    Parameters:
        customerID: Customer ID (int)
        orderID: Order ID (int)
    
    Returns:
        Save Order Confirmation: Saves the booking to a PDF
        Cancel Order: Cancels the booking and returns to the Customer Home window
        Main Menu:  Returns Customer Home Window
    '''

    # Database Session 
    session = models.Session()

    # Get order object from orderID
    order = session.query(models.Order).filter(models.Order.id == orderID).first()

    # Convert Order Date Time to correctly formatted python DateTime object
    orderDateTime = datetime.strftime(order.collection_datetime, '%A %d %B %Y %H:%M')

    # Define JSON for QRCode
    orderJSON = {
        'order': order.id
    }

    subOrders = session.query(models.SubOrder).filter(models.SubOrder.order == order).all()
    orderTable = []

    for subOrder in subOrders:
        orderTable.append([subOrder.product.name, f'£{subOrder.product.price}' ,subOrder.product_quantity, f'£{subOrder.product.price*subOrder.product_quantity}'])

    vat = round(order.total * Decimal('0.20'), 2)
    vat = f'£{vat}'
    subTotal = f'£{order.sub_total}'
    total =  f'£{order.total}'

    moneyInfomation = {
        "sub_total": subTotal,
        "vat": vat,
        "total": total
    }
    # Create QRCode object from JSON
    orderQRCode = qrcode.make(json.dumps(orderJSON))

    # Define a group of Buttons
    buttons = [
        [
            sg.Input('', do_not_clear=False, visible=False, key="-save-", enable_events=True),
            sg.FileSaveAs('Save Order Confirmation', file_types=(("PDF", "*.pdf"), ), initial_folder=os.path.expanduser('~/Documents')),
            sg.Button(f'Cancel Order', key="-cancel-")
        ]
    ]

    money = [
        [sg.Text(subTotal), sg.Text(vat), sg.Text(total)]
    ]

    # Define Window Layout
    layout = [
        [sg.Text('Order', font='Any 30', justification='center', expand_x=True)],
        [sg.Text(f'{orderDateTime}', font='Any 20', justification='center', expand_x=True)],
        [sg.Text('Cancel or Save your order', justification='center', expand_x=True)],
        [sg.Image(source=convertToBytes(orderQRCode), expand_x=True)],
        [sg.Table(orderTable, headings=['Product', 'Price', 'Quantity', 'Total'], justification='center', expand_x=True)],
        [sg.Frame('', money, expand_x=True, relief='flat', element_justification='center')],
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
                session.query(models.SubOrder).filter(models.SubOrder.order == order).delete()
                session.query(models.Order).filter(models.Order.id == order.id).delete()
                session.commit()
                session.close()
                window.close()
                main.customerHome(customerID)

            # Save Button pressed
            case "-save-":
                collectionDate = datetime.strftime(order.collection_datetime, '%A %d %B %Y')
                collectionTime = datetime.strftime(order.collection_datetime, '%H:%M')
                pdf.createOrderConformation(customerID, values['-save-'], collectionDate, collectionTime, orderQRCode, orderTable, moneyInfomation)
                webbrowser.open_new(values['-save-'])

    window.close()