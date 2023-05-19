import random
from fastapi.responses import ORJSONResponse
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from schemas import Warehouse, Companies, ProductsInfo, Products
import uvicorn
from datetime import datetime
from typing import Optional
from copy import deepcopy, copy
import re
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy import URL
from pydantic import BaseModel
import os

"""todo: implement crud operations
        create  logging 
        return Orjsonreponses
        deploy in a container """
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
    companyId: Optional[int]
    productName: Optional[str]
    description: Optional[str] = None
    mfdDate: Optional[str]
    expDate: Optional[str] = None
    quantity: Optional[int]
    price: Optional[float]

class Test(BaseModel):
    value: int
    model: str
    
class CompaniesCreate(BaseModel):
    warehouseId: int
    companyName: str
    street: str = None
    city: str = None
    pincode: str= None
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
    try:
        id=generateUniqueId("Warehouse"+warehouse.warehouseName)
        if(stringChecker(warehouse.warehouseName , warehouse.city , warehouse.country)):
            newWarehouse=Warehouse(id=id,warehouseName=warehouse.warehouseName, city=warehouse.city,country=warehouse.country)
            session.add(newWarehouse)
            session.commit()
            return ORJSONResponse({"message":"Added data"}, status_code=201)
        return ORJSONResponse({"message":"Invalid informatation"}, status_code=400)
    except Exception:
        return ORJSONResponse({"message":"Something Went Wrong"}, status_code=404)


@app.post("/addCompany")
def addCompany(company: CompaniesCreate):
    try:
        id=generateUniqueId("Company"+company.companyName)
        if(stringChecker(company.companyName, company.city,company.country, company.pincode,company.street)):
            result=session.query(Warehouse).filter(Warehouse.id==company.warehouseId)
            if(bool(result.one())):
                newCompany=Companies(id=id,warehouseId=333278322,companyName="vishal",street="kaiser",city="aachen",country="Germany")
                session.add(newCompany)
                session.commit()
                return ORJSONResponse({"message":"Added data"}, status_code=201)
        return ORJSONResponse({"message":"Invalid informatation"}, status_code=400)
    except Exception:
        return ORJSONResponse({"message":"Something went wrong"}, status_code=404)

@app.post("/addProduct")
async def addProduct(product:ProductsCreate = Depends(), insertImage: UploadFile = File(...)):
    try:
        id=generateUniqueId("Product"+product.productName)
        if(stringChecker(product.productName) and product.price>0 and product.quantity>0):
            result=session.query(Companies).filter(Companies.id==product.companyId)
            if(bool(result.one())):
                image=await insertImage.read()
                print(type(image))
                newProduct=Products(id=id,companyId=product.companyId,productName=product.productName,description=product.description,mfdDate=formatDate(product.mfdDate),expDate=formatDate(product.expDate),quantity=product.quantity,price=product.price,productImage=image)
                session.add(newProduct)
                session.commit()
                return ORJSONResponse({"message":"Added data"}, status_code=201)
        return ORJSONResponse({"message":"Invalid informatation"}, status_code=400)
    except Exception:
        return ORJSONResponse({"message":"Something went wrong"}, status_code=404)
    
@app.put("/putProduct/{productName}")
async def putProdutInfo(productName: str,description: str, image: UploadFile= File(...)):
    image=await image.read()
    session.query(Products).filter(Products.productName==productName).update(dict(description=description,productImage=image))
    session.commit()
    return {"message":"ok"}

@app.put("/putCompany/{companyName}")
def putCompanyInfo(companyName: str, company: CompaniesCreate):
    session.query(Companies).filter(Companies.companyName==companyName).update(dict(street=company.street,city=company.city,pincode=company.pincode))
    session.commit()
    return {"message":"ok"}


@app.get("/searchByCompanies")
def findCompany(companyName: str):
    res=session.query(Companies).filter(Companies.companyName==companyName)
    if(bool(res.all())):
        return res
    return ORJSONResponse({"message":"Bad Request"}, status_code=400)


@app.get("/searchByProducts")
def findProduct(productName: str):
    res=session.query(Products).filter(Products.productName==productName)
    if(bool(res.all())):
        return res
    return ORJSONResponse({"message":"Bad Request"}, status_code=400)

@app.delete("/deleteCompany/{companyName}")
def deleteCompany(companyName: str):
    session.query(Companies).filter(Companies.companyName==companyName).delete(synchronize_session=False)
    session.commit()
    return {"message":"ok"}

@app.delete("/deleteProduct/{productName}")
def deleteCompany(productName: str):
    session.query(Products).filter(Products.productName==productName).delete(synchronize_session=False)
    session.commit()
    return {"message":"ok"}

@app.delete("/deleteWarehouse/{warehouseName}")
def deleteCompany(warehouseName: str):
    session.query(Warehouse).filter(Warehouse.warehouseName==warehouseName).delete(synchronize_session=False)
    session.commit()
    return {"message":"ok"}


## Validators ##
def generateUniqueId(value: str)->int:
    value= re.sub("[-_ *&()@.,/]","",value)
    result=(abs(hash(value)) % (10 ** 6))*PRIME + random.randint(0,MAX_SHORT)
    result=result *-1 if result<0 else result
    return result

def formatDate(strDate:str):
    print(strDate)
    return datetime.strptime(strDate,'%d-%m-%y')

def stringChecker(*args)->bool:
    for value in args:
        value=re.sub("\s+","",value)
        if(not(value)):
            return False
    return True


def queryDebug():
    from copy import copy
    ## test function to debug ##
    res=session.query(Companies).filter(Companies.companyName=="ahdkjdbh")
    copyRes=copy(res)
    if(bool(copyRes.one())):
        print("result: ",bool(res))
        return copyRes.all()


if __name__=="__main__":
    uvicorn.run(app,host="localhost",port=8089)
    #queryDebug()
  