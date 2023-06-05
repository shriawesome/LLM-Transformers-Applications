import json
import openai
from collections import defaultdict

# Getting credentials
from Config import openaiConfig
openai.organization = openaiConfig.OPENAI_ORGANISATION
openai.api_key = openaiConfig.OPENAI_API_KEY

# Data File
productsFile = 'data/products.json'

def getCompletionfromMessages(messages, 
                              model="gpt-3.5-turbo",
                              temperature=0,
                              max_tokens=500):
    response = openai.ChatCompletion.create(model=model,
                                            messages = messages,
                                            temperature = temperature,
                                            max_tokens = max_tokens)
    return response.choices[0].message["content"]

def getProducts():
    with open(productsFile,'r') as file:
        products = json.load(file)
    return products

def getProductnCategory():
    products = getProducts()
    productByCategory = defaultdict(list)
    for productName, productInfo in products.items():
        category = productInfo.get('category')
        if category:
            productByCategory[category].append(productInfo.get('name'))
    
    return dict(productByCategory)

def findCategoryProductsOnly(userInput, productsByCategory):
    delimiter = "####"
    systemMessage = f"""
    You will be provided with customer service queries. \
    The customer service query will be delimited with {delimiter} characters. \
    Output a python list of objects, where each object has the following format:
    'category': <one of Computers and Laptops, Smartphones and Accessories, Television and Home Theater Systems, \
    Gaming Consoles and Accessories, Audio Equipment, Cameras and Camcorders>,
    OR
    'products': <a list of products that must be found in the allowed products below>
    
    Where categories and products must be found in the customer service query.
    If a product is mentioned, it must be associated with the correct category in the allowed products list below.
    If no products or categories are found, output an empty list.
    
    Allowed products:
    Computers and Laptops:
    TechPro Ultrabook
    BlueWave Gaming Laptop
    PowerLite Convertible
    TechPro Desktop
    BlueWave Chromebook

    Smartphones and Accessories category:
    SmartX ProPhone
    MobiTech PowerCase
    SmartX MiniPhone
    MobiTech Wireless Charger
    SmartX EarBuds

    Televisions and Home Theater Systems category:
    CineView 4K TV
    SoundMax Home Theater
    CineView 8K TV
    SoundMax Soundbar
    CineView OLED TV

    Gaming Consoles and Accessories category:
    GameSphere X
    ProGamer Controller
    GameSphere Y
    ProGamer Racing Wheel
    GameSphere VR Headset

    Audio Equipment category:
    AudioPhonic Noise-Canceling Headphones
    WaveSound Bluetooth Speaker
    AudioPhonic True Wireless Earbuds
    WaveSound Soundbar
    AudioPhonic Turntable

    Cameras and Camcorders category:
    FotoSnap DSLR Camera
    ActionCam 4K
    FotoSnap Mirrorless Camera
    ZoomMaster Camcorder
    FotoSnap Instant Camera

    Only output the list of objects, nothing else.
    """
    
    messages = [
        {'role':'system', 'content':systemMessage},
        {'role':'user','content':f"{delimiter}{userInput}{delimiter}"},
         ]
    return getCompletionfromMessages(messages)

def getProductbyName(name):
    products = getProducts()
    return products.get(name, None)

def getProductbyCategory(name):
    products = getProducts()
    return [product for product in products.values() if product["category"]==name]

def generateOutputString(dataList):
    output = ""
    if dataList is None:
        return output
    for data in dataList:
        try:
            if 'products' in data:
                productsList = data['products']
                for productName in productsList:
                    product = getProductbyName(productName)
                    if product:
                        output += json.dumps(product, indent=4)+'\n'
                    else:
                        print(f"Error: Product '{productName}' not found")
            elif 'category' in data:
                categoryName = data['category']
                categoryProducts = getProductbyCategory(categoryName)
                for product in categoryProducts:
                    output += json.dumps(product, indent=4)+'\n'
            else:
                print('Error: Invalid object format')
        except Exception as e:
            print(f'Error: {e}')
            
    return output

def readString2List(inputString):
    if inputString is None:
        return None
    try:
        # Replace single quotes with double quotes valid for JSON
        inputString = inputString.replace("'","\"")
        data = json.loads(inputString)
        return data
    except json.JSONDecodeError:
        print('Error: Invalid JSON string')
        return None