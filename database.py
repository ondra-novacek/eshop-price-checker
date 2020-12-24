from tinydb import TinyDB, Query
db = TinyDB('db.json')
db.drop_tables()

table = db.table('Shops')
table.insert({"name":'alza.cz - sometimes bot policy problems',"titleIndex":[{"itemprop":"name"}],"priceIndex":[{"class":"price_withVat"}]})
table.insert({"name":'answear.cz',"titleIndex":[{"id":"productPanel"},{"class":"productPanelTop"},{"class":"title"}],"priceIndex":[{"id":"productPanel"},{"class":"productPanelTop"},{"itemprop":"price"}]})
table.insert({"name":'planetaher.cz',"titleIndex":[{"class":"last"}],"priceIndex":[{"id":"snippet--snPrice"}]})

table2 = db.table('Products')
table2.insert({"link": "https://answear.cz/2109948-tommy-hilfiger-boty.html", "time": ["2020-05-11 14:57:44.739347","2020-05-11 14:58:19.634006"], "prices": [1899,2201]})

table3 = db.table('Users')
table3.insert({"email": "vavasyukova@edu.hse.ru", "products": [1], "priceToInform": [2000]})

db.close()

