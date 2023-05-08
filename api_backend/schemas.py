from sqlalchemy import Column, INTEGER, VARCHAR, DATETIME, DOUBLE, LargeBinary
from sqlalchemy.ext.declarative import declarative_base


base=declarative_base()
class Warehouse(base):
    __tablename__="warehouses"
    id=Column("id",INTEGER,primary_key=True)
    warehouseName=Column("warehouseName", VARCHAR)
    city=Column("city",VARCHAR)
    country=Column("country",VARCHAR)


class Companies(base):
    __tablename__="companies"
    id=Column("id",INTEGER, primary_key=True)
    warehouseId=Column("warehouse_id", INTEGER)
    companyName=Column("companyName",VARCHAR)
    street= Column("street", VARCHAR)
    city=Column("city",VARCHAR)
    pincode= Column("pincode", VARCHAR)
    country=Column("country",VARCHAR)
 
class ProductsInfo(base):
    __tablename__="products"
    id=Column("id",INTEGER, primary_key=True)
    companyId=Column("company_id",INTEGER)
    productName=Column("productName",VARCHAR)
    description=Column("description", VARCHAR)
    mfdDate=Column("mfd_date", DATETIME)
    expDate=Column("exp_date",DATETIME)
    quantity=Column("quantity", INTEGER)
    price=Column("price",DOUBLE)


class Products(base):
    __tablename__=ProductsInfo.__table__
    id=Column("id",INTEGER, primary_key=True)
    companyId=Column("company_id",INTEGER)
    productName=Column("productName",VARCHAR)
    description=Column("description", VARCHAR)
    mfdDate=Column("mfd_date", DATETIME)
    expDate=Column("exp_date",DATETIME)
    quantity=Column("quantity", INTEGER)
    price=Column("price",DOUBLE)
    productImage=Column("productImage",LargeBinary)