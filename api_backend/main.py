import random
from fastapi import FastAPI, HTTPException
from schemas import Warehouse, Products, Companies, ProductsInfo
import uvicorn
import datetime
from typing import Optional
import re
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy import URL
from pydantic import BaseModel
import os

MAX_SHORT=65535
PRIME=37
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


class WarehouseCreate(BaseModel):
    warehouseName: str
    city: str
    country: str

class ProductsCreate(BaseModel):
    companyId: int
    productName: str
    description: str
    mfdDate: Optional[str]
    expDate: Optional[str]
    quantity: int
    price: float
    productImage: str

class CompaniesCreate(BaseModel):
    warehouseId: int
    companyName: str
    street: str
    city: str
    pincode: str
    country: str


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
    result=session.query(Warehouse).all()
    return result
    
# get products
@app.get("/getProducts")
def getProducts():
    result=session.query(ProductsInfo).all()
    return result

# get companies
@app.get("/getCompanies")
def getCompanies():
    result=session.query(Companies).all()
    return result

# post warehouse
@app.post("/addWarehouse", response_model=WarehouseCreate)
def addWarehouse(warehouse: WarehouseCreate):
    id=generateUniqueId("Warehouse"+warehouse.warehouseName)
    if(stringChecker(warehouse.warehouseName , warehouse.city , warehouse.country)):
        newWarehouse=Warehouse(id=id,warehouseName=warehouse.warehouseName, city=warehouse.city,country=warehouse.country)
        session.add(newWarehouse)
        #session.commit()
        return warehouse
    raise HTTPException(status_code=400, detail="Please enter valid Informaton")


@app.post("/addCompany")
def addCompany(company: CompaniesCreate):
    id=generateUniqueId("Company"+company.companyName)
    if(stringChecker(company.companyName, company.city,company.country, company.pincode,company.street)):
        result=session.query(Warehouse).filter_by(Warehouse.id==company.warehouseId)
        if(result is not None):
            newCompany=Companies(id,company.warehouseId,company.companyName,company.street,company.city,company.pincode,company.country)
            session.add(newCompany)
            #session.commit()
            return company
    raise HTTPException(status_code=400, detail="Please enter valid Informaton")

@app.post("/addProduct")
def addProduct(product:ProductsCreate):
    id=generateUniqueId("Product"+product.productName)
    if(stringChecker(product.productName) and product.price>0 and product.quantity>0):
        result=session.query(Companies).filter(Companies.id==product.companyId)
        if(result is not None):
            image=processImage(product.productImage)
            newCompany=Products(id,product.companyId,product.productName,product.description,product.mfdDate,product.expDate,product.quantity,product.price,image)
            session.add(newCompany)
            #session.commit()
            return product
    raise HTTPException(status_code=400, detail="Please enter valid Informaton")


def generateUniqueId(value: str)->int:
    value= re.sub("[-_ *&()@.,/]","",value)
    result=(abs(hash(value)) % (10 ** 6))*PRIME + random.randint(0,MAX_SHORT)
    result=result *-1 if result<0 else result
    return result

def processImage(image: str):
    with open(image, "rb") as fp:
        return fp.read()

def stringChecker(*args)->bool:
    for value in args:
        value=re.sub("\s+","",value)
        if(not(value)):
            return False
    return True


def queryDebug():
    id=generateUniqueId("Company"+"vishal")
    if(stringChecker("vishal","aachen","kasier","aachen","Germany")):
        result=session.query(Warehouse).filter(Warehouse.id==333278322)
        if(result is not None):
            newCompany=Companies(id,333278322,"vishal","aachen","kasier","aachen","Germany")
            session.add(newCompany)
            #session.commit()
            return True


if __name__=="__main__":
    #uvicorn.run(app,host="localhost",port=8089)
    queryDebug()
  