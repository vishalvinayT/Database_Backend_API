import random
from fastapi.responses import ORJSONResponse
from fastapi import FastAPI, UploadFile, File, Depends, Request, status,HTTPException
from schemas import Warehouse, Companies, ProductsInfo, Products
import uvicorn
from datetime import datetime
from typing import Optional
from logging.config import dictConfig
from logConfig import LogConfig
import logging
from copy import copy
import re
from sqlalchemy import create_engine, MetaData,exc
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
app=None
engine=None
metadata= None
Session=None
session=None
conn=None

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

logConfig=LogConfig()
dictConfig(logConfig.dict())
logger=logging.getLogger(logConfig.LOGGER_NAME)

#estalish connection
app=FastAPI()
engine=create_engine(url_object, echo=True)
metadata= MetaData()
Session=sessionmaker(bind=engine)
session=Session()  
print("Connecting...to {}@{}".format(USERNAME,HOST))
conn=engine.connect()



# get warehouses
@app.get("/getWarehouses")
def getWareHouses(request: Request):
    result=session.query(Warehouse).all()
    request_info = f" \"{request.method} {request.url.path} {request.scope['http_version']} \" "
    logging.info(request_info + str(status.HTTP_200_OK))
    return result
    
# get products
@app.get("/getProducts")
def getProducts(request: Request):
    result=session.query(ProductsInfo).all()
    request_info = f" \"{request.method} {request.url.path} {request.scope['http_version']} \" "
    logging.info(request_info + str(status.HTTP_200_OK))
    return result

# get companies
@app.get("/getCompanies")
def getCompanies(request: Request):
    result=session.query(Companies).all()
    request_info = f" \"{request.method} {request.url.path} {request.scope['http_version']} \" "
    logging.info(request_info + str(status.HTTP_200_OK))
    return result

# post warehouse
@app.post("/addWarehouse", response_model=WarehouseCreate)
def addWarehouse(request: Request,warehouse: WarehouseCreate):
    request_info = f" \"{request.method} {request.url.path} {request.scope['http_version']} \" "
    try:
        id=generateUniqueId("Warehouse"+warehouse.warehouseName)
        if(stringChecker(warehouse.warehouseName , warehouse.city , warehouse.country)):
            newWarehouse=Warehouse(id=id,warehouseName=warehouse.warehouseName, city=warehouse.city,country=warehouse.country)
            session.add(newWarehouse)
            session.commit()
            logging.info(request_info + str(status.HTTP_201_CREATED))
            return ORJSONResponse({"message":"Added data"}, status_code=201)
        logging.info(request_info + str(status.HTTP_400_BAD_REQUEST))
        return ORJSONResponse({"message":"Invalid informatation"}, status_code=400)
    except Exception:
        logging.exception(request_info + str(status.HTTP_404_NOT_FOUND))
        return ORJSONResponse({"message":"Something Went Wrong"}, status_code=404)


@app.post("/addCompany")
def addCompany(request: Request,company: CompaniesCreate):
    request_info = f" \"{request.method} {request.url.path} {request.scope['http_version']} \" "
    try:
        id=generateUniqueId("Company"+company.companyName)
        if(stringChecker(company.companyName, company.city,company.country, company.pincode,company.street)):
            result=session.query(Warehouse).filter(Warehouse.id==company.warehouseId)
            if(bool(result.first())):
                newCompany=Companies(id=id,warehouseId=company.warehouseId,companyName=company.companyName,street=company.street,city=company.city,country=company.country)
                session.add(newCompany)
                session.commit()
                logging.info(request_info +str(status.HTTP_201_CREATED))
                return ORJSONResponse({"message":"Added data"}, status_code=201)
        logging.info(request_info + str(status.HTTP_400_BAD_REQUEST))
        return ORJSONResponse({"message":"Invalid informatation"}, status_code=400)
    except Exception:
        logging.exception(request_info+str(status.HTTP_404_NOT_FOUND))
        return ORJSONResponse({"message":"Something went wrong"}, status_code=404)

@app.post("/addProduct")
async def addProduct(request: Request,product:ProductsCreate = Depends(), insertImage: UploadFile = File(...)):
    request_info = f" \"{request.method} {request.url.path} {request.scope['http_version']} \" "
    try:
        id=generateUniqueId("Product"+product.productName)
        if(stringChecker(product.productName) and product.price>0 and product.quantity>0):
            result=session.query(Companies).filter(Companies.id==product.companyId)
            if(bool(result.first())):
                image=await insertImage.read()
                print(type(image))
                newProduct=Products(id=id,companyId=product.companyId,productName=product.productName,description=product.description,mfdDate=formatDate(product.mfdDate),expDate=formatDate(product.expDate),quantity=product.quantity,price=product.price,productImage=image)
                session.add(newProduct)
                session.commit()
                logging.info(request_info+str(status.HTTP_201_CREATED))
                return ORJSONResponse({"message":"Added data"}, status_code=201)
        logging.info(request_info+str(status.HTTP_400_BAD_REQUEST))
        return ORJSONResponse({"message":"Invalid informatation"}, status_code=400)
    except Exception:
        logging.exception(request_info+str(status.HTTP_404_NOT_FOUND))
        return ORJSONResponse({"message":"Something went wrong"}, status_code=404)
    
@app.put("/putProduct/{productName}")
async def putProdutInfo(request: Request,productName: str,description: str, image: UploadFile= File(...)):
    request_info = f" \"{request.method} {request.url.path} {request.scope['http_version']} \" "
    image=await image.read()
    result=session.query(Products).filter(Products.productName==productName)
    if(bool(result.first())):
        result.update(dict(description=description,productImage=image))
        session.commit()
        logging.info(request_info+str(status.HTTP_202_ACCEPTED))
        return ORJSONResponse({"message":"Added data"}, status_code=201)
    logging.info(request_info+str(status.HTTP_400_BAD_REQUEST))
    return ORJSONResponse({"message":"Invalid informatation"}, status_code=400)

@app.put("/putCompany/{companyName}")
def putCompanyInfo(request: Request,companyName: str, company: CompaniesCreate):
    request_info = f" \"{request.method} {request.url.path} {request.scope['http_version']} \" "
    result=session.query(Companies).filter(Companies.companyName==companyName)
    if(bool(result.first())):
        result.update(dict(street=company.street,city=company.city,pincode=company.pincode))
        session.commit()
        logging.info(request_info + str(status.HTTP_202_ACCEPTED))
        return ORJSONResponse({"message":"Added data"}, status_code=201)
    logging.info(request_info + str(status.HTTP_400_BAD_REQUEST))
    return ORJSONResponse({"message":"Invalid informatation"}, status_code=400)


@app.get("/searchByCompanies")
def findCompany(request: Request,companyName: str):
    request_info = f" \"{request.method} {request.url.path} {request.scope['http_version']} \" "
    res=session.query(Companies).filter(Companies.companyName==companyName)
    if(bool(res.all())):
        logging.info(request_info+str(status.HTTP_200_OK))
        return res.all()
    logging.info(request_info + str(status.HTTP_400_BAD_REQUEST))
    return ORJSONResponse({"message":"Bad Request"}, status_code=400)


@app.get("/searchByProducts")
def findProduct(request: Request,productName: str):
    request_info = f" \"{request.method} {request.url.path} {request.scope['http_version']} \" "
    res=session.query(ProductsInfo).filter(ProductsInfo.productName==productName)
    if(bool(res.all())):
        logging.info(request_info + str(status.HTTP_200_OK))
        return res.all()
    logging.info(request_info + str(status.HTTP_400_BAD_REQUEST))
    return ORJSONResponse({"message":"Bad Request"}, status_code=400)


@app.delete("/deleteCompany/{companyName}")
def deleteCompany(request: Request,companyName: str):
    request_info = f" \"{request.method} {request.url.path} {request.scope['http_version']} \" "
    result=session.query(Companies).filter(Companies.companyName==companyName)
    if(bool(result.first())):
        result.delete(synchronize_session=False)
        session.commit()
        logging.info(request_info + str(status.HTTP_200_OK))
        return ORJSONResponse({"message":"deleted data"}, status_code=202)
    logging.info(request_info+str(status.HTTP_400_BAD_REQUEST))
    return ORJSONResponse({"message":"Invalid informatation"}, status_code=400)

@app.delete("/deleteProduct/{productName}")
def deleteProduct(request: Request,productName: str):
    request_info = f" \"{request.method} {request.url.path} {request.scope['http_version']} \" "
    result=session.query(Products).filter(Products.productName==productName)
    if(bool(result.first())):
        result.delete(synchronize_session=False)
        session.commit()
        logging.info(request_info+str(status.HTTP_200_OK))
        return ORJSONResponse({"message":"deleted data"}, status_code=202)
    logging.info(request_info +str( status.HTTP_400_BAD_REQUEST))
    return ORJSONResponse({"message":"Invalid informatation"}, status_code=400)

@app.delete("/deleteWarehouse/{warehouseName}")
def deleteCompany(request: Request,warehouseName: str):
    request_info = f" \"{request.method} {request.url.path} {request.scope['http_version']} \" "
    result=session.query(Warehouse).filter(Warehouse.warehouseName==warehouseName)
    if(bool(result.first())):
        result.delete(synchronize_session=False)
        session.commit()
        logging.info(request_info+str(status.HTTP_200_OK))
        return ORJSONResponse({"message":"deleted data"}, status_code=202)
    logging.info(request_info+str(status.HTTP_400_BAD_REQUEST))
    return ORJSONResponse({"message":"Invalid informatation"}, status_code=400)


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
    ## test function to debug ##
    res=session.query(Companies).filter(Companies.companyName=="ahdkjdbh")
    copyRes=copy(res)
    if(bool(copyRes.one())):
        print("result: ",bool(res))
        return copyRes.all()


if __name__=="__main__":
    uvicorn.run(app,host="0.0.0.0",port=8093)
    #queryDebug()
  