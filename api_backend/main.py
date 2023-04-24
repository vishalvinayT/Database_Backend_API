from fastapi import FastAPI
import uvicorn
import sqlalchemy

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

engine=sqlalchemy.create_engine(url_object)
conn=engine.connect()
metadata= sqlalchemy.MetaData()
Users=sqlalchemy.Table("users",metadata,autoload_with=engine)
smt=Users.select()
op=conn.execute(smt)



