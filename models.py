from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

# models is a file that has the different python classes that are used throughout the API

class Profile(Base):
    __tablename__ = "profiles"
    # profiles has attributes id, name, user_type, balance, and contract
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    user_type = Column(String) # meaning client or contractor
    balance = Column(Float, default=0)
    # relationship- a profile can be linked to multiple contracts
    contracts = relationship("Contract", back_populates="profile") 

class Contract(Base):
    # contract class has attributes id, status, profile_id (foreign key)
    __tablename__ = "contracts"
    id = Column(Integer, primary_key=True, index=True) # contract can only have one profile linked
    status = Column(String, default="new") # ex: new, in progress, or terminated
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    # relationships- contract with profile and jobs. 
    # contract can only have one profile (primary key above) and each contract can have multiple jobs
    profile = relationship("Profile", back_populates="contracts")
    jobs = relationship("Job", back_populates="contracts")

class Job(Base):
    __tablename__ = "jobs"
    # jobs class has attributes id, description, price, paid, and contract id (a foreign key)
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    price = Column(Float)
    paid = Column(Float, default=0)
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    # relationship- each job belongs to a contract
    contract = relationship("Contract", back_populates="jobs")


