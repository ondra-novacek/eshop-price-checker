import matplotlib.pyplot as plt
from tinydb import TinyDB, Query

def plot(userID):
    db = TinyDB('db.json')
    users = db.table("Users")
    products = db.table('Products')
    
    p = chooseProduct(users, products, userID)
    product = products.get(doc_id=p)
    plt.plot(product["prices"])
    plt.xticks(range(len(product["prices"])), product["time"], rotation=90)
    plt.xlabel('Time')
    plt.ylabel('Price')
    imageName = str(p)+'.png'
    plt.savefig(imageName, dpi=300, bbox_inches="tight")
    print("\nThe plot is saved in current folder with name %s.\n" % imageName)

def chooseProduct(users, products, userID):
    userProducts = users.get(doc_id=userID)["products"]
    for i in userProducts:
        product = products.get(doc_id=i)
        print(i, ": ", product["link"])

    try:
        p = int(input("Choose product from the list above by entering its number: "))
        while p not in userProducts:
            p = int(input("Incorrect input. Try again: "))
        
        return p
    except:
        print("\nYou need to write a number. Try again.")
        return chooseProduct(users, products, userID)

