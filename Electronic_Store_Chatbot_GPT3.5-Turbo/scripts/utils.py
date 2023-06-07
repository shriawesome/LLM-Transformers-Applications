import json
import openai
from collections import defaultdict
import sys
sys.path.append('../')

# Getting credentials
from Config import openaiConfig
openai.organization = openaiConfig.OPENAI_ORGANISATION
openai.api_key = openaiConfig.OPENAI_API_KEY

# Data File
productsFile = '../data/products.json'

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
    
    Allowed products: {productByCategory}
    
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
    
def getProductfromQuery(userMsg):
    productnCategory = getProductnCategory()
    delimiter = "####"
    sysMessage = f"""
    You will be provided with customer service queries. \
    The customer service query will be delimited with {delimiter} characters.
    Output a python list of json objects, where each object has the following format:
        'category': <one of Computers and Laptops, Smartphones and Accessories, Televisions and Home Theater Systems, \
    Gaming Consoles and Accessories, Audio Equipment, Cameras and Camcorders>,
    OR
        'products': <a list of products that must be found in the allowed products below>

    Where the categories and products must be found in the customer service query.
    If a product is mentioned, it must be associated with the correct category in the allowed products list below.
    If no products or categories are found, output an empty list.

    The allowed products are provided in JSON format.
    The keys of each item represent the category.
    The values of each item is a list of products that are within that category.
    Allowed products: {productnCategory}

    """
    
    messages =  [  
    {'role':'system', 'content': sysMessage},    
    {'role':'user', 'content': f"{delimiter}{userMsg}{delimiter}"},  
    ] 
    response = getCompletionfromMessages(messages)
    
    return response

def getMentionedProductInfo(dataList):
    productInfo = []
    if dataList is None:
        return []
    for data in dataList:
        try:
            if "products" in data:
                products = data["products"]
                for pName in products:
                    product = getProductbyName(pName)
                    if product:
                        productInfo.append(product)
                    else:
                        print(f"Product {pName} not found")
            elif "category" in data:
                cName = data['category']
                cProducts = getProductbyCategory(cName)
                for product in cProducts:
                    productInfo.append(product)
            else:
                print("Error: Invalid object format")
        except Exception as e:
            print(f"Error: {e}")
            
    return productInfo

def answerUserMsg(userMsg, productInfo):
    delimiter = "####"
    sysMessage = f"""
    You are a customer service assistant for a large electronic store. \
    Respond in a friendly and helpful tone, with concise answers. \
    Make sure to ask the user relevant follow up questions.
    """
    
    messages = [
    {'role':'system', 'content':sysMessage},
    {'role':'user', 'content':f'{delimiter}{userMsg}{delimiter}'},
    {'role':'assistant', 'content':f"Relevant product information:\n{productInfo}"}
    ]
    response = getCompletionfromMessages(messages)
    return response

