#############
# Libraries #
#############
import io
import requests
from PIL import ImageQt
import textwrap

#############
# Wrap Text #
##############
def wrapText(text, size=30):
    '''
    Function to convert long strings to warped text

    Parameters:
        text: The text to convert to warped text (str)
        size: The max width of a line of text (int)
    Returns:
        A string with newlines in (str)
    '''
    if type(text) is list:
        newText = []
        for i in text:
            newText.append("\n".join(textwrap.wrap(i, size)))
        return newText
    else:
        return "\n".join(textwrap.wrap(text, size))


################
# URL To Image #
################
def urlToImage(url):
    '''
    Converts a URL to a PNG Image that PySimpleGUI can understand

    Parameters:
        url: The url of the image to convert

    Returns:
        Image Data
    '''
    response = requests.get(url, stream=True)
    response.raw.decode_content = True
    img = ImageQt.Image.open(response.raw)
    with io.BytesIO() as output:
        img.save(output, format="PNG")
        data = output.getvalue()
    return data


############
# Get Icon #
############
def getIcon():
    response = requests.get('https://raw.githubusercontent.com/bxdavies/pharmanet/main/logo.jpeg', stream=True)
    response.raw.decode_content = True
    img = ImageQt.Image.open(response.raw)
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    return bio.getvalue()

################
# Get PDF Logo #
################
def getPDFLogo():
    response = requests.get('https://raw.githubusercontent.com/bxdavies/pharmanet/main/logo.png', stream=True)
    response.raw.decode_content = True
    img = ImageQt.Image.open(response.raw)
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    return bio

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

def convertImage(image):
    bio = io.BytesIO()
    image.save(bio, format='PNG')
    return bio