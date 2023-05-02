from sqlalchemy import Column, INTEGER, VARCHAR, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


base=declarative_base()
class Warehouse(base):
    __tablename__="warehouses"
    id=Column("id",INTEGER,primary_key=True)
    warehouseName=Column("warehouseName", VARCHAR)
    city=Column("city",VARCHAR)
    country=Column("country",VARCHAR)

    