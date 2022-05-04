from app.models import Base
from sqlalchemy import Column, Integer, String


class SmartContract(Base):
    __tablename__ = "smart_contract"
    id = Column(Integer, index=True, primary_key=True)
    origin_name = Column(String(128), index=True, unique=True)
    code_file_name = Column(String(512))


class OriginFunction(Base):
    __tablename__ = "origin_function"
    id = Column(Integer, index=True, primary_key=True)
    origin_name = Column(String(128), index=True, unique=True)
    bpmn_file_name = Column(String(512))
    code_file_name = Column(String(512))