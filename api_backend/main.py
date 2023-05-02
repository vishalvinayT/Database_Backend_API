from fastapi import FastAPI
from schemas import Warehouse
import uvicorn
from sqlalchemy import Table,Column, create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy import URL
import os

DRIVER= "mysql"
USERNAME= os.getenv("MySqlUserName", None)
PASSWORD= os.getenv("MySqlPassword", None)
HOST= os.getenv("MysqlHost", "localhost")
DATABASE="grocerydeliverysystem"

url_object = URL.create(
    DRIVER,
    username=USERNAME,
    password=PASSWORD,  
    host=HOST,
    database=DATABASE,
)


#estalish connection
app=FastAPI()
engine=create_engine(url_object, echo=True)
metadata= MetaData()
Session=sessionmaker(bind=engine)
session=Session()
conn=engine.connect()


# get warehouses
@app.get("/getWarehouses")
def getWareHouses():
    #warehouses=Table('warehouses',metadata,autoload_with=engine)
    result=session.query(Warehouse).all()
    return result
    
# get products
@app.get("/getProducts")
def getProducts():
    products=Table('products',metadata,autoload_with=engine)
    result=session.query(products)
    data=[dict(row) for row in result]
    return {"data":data}

# get companies
@app.get("/getCompanies")
def getCompanies():
    companies=Table('companies',metadata,autoload_with=engine)
    result=session.query(companies)
    return result

if __name__=="__main__":
    uvicorn.run(app,host="localhost",port=8089)
    #getWareHouses()
