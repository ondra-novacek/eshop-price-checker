import requests #manual import needed - pip install requests
from bs4 import BeautifulSoup #manual import needed - pip install bs4
import smtplib
import time
from urllib.parse import urlparse
import logging
import re
from datetime import datetime
from tinydb import TinyDB, Query, where #manual import needed - pip install tinydb
import plotting as plt

# default vars
checkEvery = 1000 # 1000s, later it will be probably set to every 24hours
db = TinyDB('db.json')
users = db.table("Users")
products = db.table('Products')
shops = db.table('Shops')

# set email logger
emaillogger = logging.getLogger('emailClient')
emaillogger.setLevel(logging.INFO)
# set error logger
errlogger = logging.getLogger(__name__)
errlogger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')

email_file_handler = logging.FileHandler('emaillog.txt')
email_file_handler.setFormatter(formatter)

error_file_handler = logging.FileHandler('errlog.txt')
error_file_handler.setFormatter(formatter)

emaillogger.addHandler(email_file_handler)
errlogger.addHandler(error_file_handler)

def urlValidation(link):
    try:
        result = urlparse(link)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False

def addProduct():
    link = input('Enter the link for the product: ').strip()
    lfprice = float(input('Enter at what price you want to be notified (in eshop currency): '))
    if urlValidation(link):
        return [True, link, lfprice]
    else:
        print('URL is incorrect. Try again.')
        return [False, None, None]


def setEshop(supportedEshops):
    print('Enter a number at what eshop would you like to check prices:')
    for i, supp in enumerate(supportedEshops):
        print(f'{i+1} : {supp}')
    try:
        eshop = int(input('Desired number: '))
        while not(eshop > 0 and eshop <= len(supportedEshops)):
            eshop = int(input('Wrong number. Try again writing the desired number: '))
        return eshop
    except:
        print('Wrong input. Application will close now.')
        exit()

def extractValue(value, eshop):
    for v in eshop:
        value = value.find(attrs=v)
    return value.get_text().encode('ascii', 'ignore').decode('ascii').strip()

def check_price(URL, headers, lfprice, eshop, user, regularCheck = False):
    try:
        # get the page
        page = requests.get(URL, headers=headers)

        # parse the page
        page = BeautifulSoup(page.content, 'html.parser')

        eshop = shops.get(doc_id=eshop)
        title = price = page
        # extract price tag
        price = extractValue(price, eshop["priceIndex"])
        # extract product title
        title = extractValue(title, eshop["titleIndex"])
    except Exception as e:
        errlogger.error(f'Error msg: {e}')
    else:
        # get only numbers from price var and convert to float
        price = float(''.join(filter(str.isdigit, price)))

        # calculate the difference
        diff = price - lfprice

        # send mail notification if the price is same or lower than we want
        if (diff <= 0):
            send_mail(user["email"], title, URL, diff)

        # updating database
        updateDb(link, price, title, lfprice, regularCheck)

        print("Success.")

def send_mail(sendTo, productTitle, URL, diff):
    email_pass = "add_yours" #email pass only for this app, not for login
    email_sender = "youremail@gmail.com" 
    email_receiver = sendTo
    # two sets verification needs to be enabled at gmail
    server = smtplib.SMTP('smtp.gmail.com', 587)
    try:
        # establish connection
        server.ehlo()
        # encrypt connection
        server.starttls()
        # log to account with credentials
        server.login(email_sender, email_pass)

        subject = f"{productTitle} price drop!"
        body = f"Price is {diff} below your required one!\n\nCheck the link with the product: \n{URL}"

        msg = f"Subject: {subject}\n\n{body}"

        server.sendmail(
            # from
            email_sender,
            # to
            email_receiver,
            # msg
            msg
        )

        # log sent email
        emaillogger.info(f'Email has been sent to {email_receiver} for product: {productTitle}.')
        # close the connection
        server.quit()
    except Exception as e:
        # error log
        errlogger.error(f'Error mail msg: {e}')

def checkUser(email):
    query = users.get(where('email') == email)
    if query is None:
        users.insert({"email": email, "products": [],"priceToInform": []})
        return len(users)
    else:
        return query.doc_id

def checkEmail(email):
    exp = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if (re.search(exp, email)):
        return True
    else:
        return False

def updateDb(link, price, title, lfprice, regularCheck):
    doc = products.get(where('link') == link)
    if doc is None:
        products.insert({"link": link, "time": [str(datetime.now())[:-7]], "prices": [price]})
        productID = len(products)
    else:
        doc['time'].append(str(datetime.now())[:-7])
        doc['prices'].append(price)
        productID = doc.doc_id
        products.update(doc, doc_ids=[productID])

    if not regularCheck:
        for i in range(len(user["products"])):
            if productID == user["products"][i]:
                print(title)
                change = input("This product is already in you subscription list. Do you want to change the desired price? [y/n] ")
                if change == "y":
                    user["priceToInform"][i] = lfprice

    if productID not in user["products"]:
        user["products"].append(productID)
        user["priceToInform"].append(lfprice)
    users.update(user, doc_ids=[userID])

# so it is executed only if it is not imported
if __name__ == "__main__":
    # set user agent 
    headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"}
    # supported eshops for file load
    supportedEshops = [x['name'] for x in shops]
    # store user email
    sendTo = input('Hello! Enter your email: ').strip()
    #handle wrong input
    while not checkEmail(sendTo):
        print("Something's wrong with your address!")
        sendTo = input('Enter your email once again: ')

    userID = checkUser(sendTo)
    user = users.get(doc_id=userID)
    if len(user["products"]) > 0:
        unsub = input("Do you want to unsubscribe? [y/n] ")
        if unsub == "y":
            users.remove(doc_ids=[userID])
            print("You were removed from the database.")
            exit()
        else:
            plot = input("Do you want to show the price changes of your product(s) over time? [y/n] ")
            if plot == "y":
                plt.plot(userID)

    toCheck = [] # [[link, lfprice],...]
    add = input('Do you want to add a product? [y/n] ')
    if add == 'y':
        eshop = setEshop(supportedEshops)
        while True:
            valid, link, price = addProduct()
            if valid:
                toCheck.append([eshop, link, price])
            else:
                print('Wrong inputs.')
            another = input('Do you want to set another product? [y/n] ')
            if another == 'n':
                break

    while(True):
        if len(toCheck) != 0:
            for product in toCheck:
                eshop, link, lfprice = product
                check_price(link, headers, lfprice, eshop, user)

        for i in range(len(user["products"])):
            product_id = user["products"][i]
            lfprice = user["priceToInform"][i]
            link = products.get(doc_id=product_id)["link"]
            if "alza.cz" in link:
                eshop = 1
            elif "answear.cz" in link:
                eshop = 2
            else:
                eshop = 3

            check_price(link,headers,lfprice,eshop,user,True)
        # pauses for number of seconds
        time.sleep(checkEvery)
        #break # break for testing purposes, we dont want to to keep it running indefinitely yet

