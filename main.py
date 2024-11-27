from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime
import models
import database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# function to verify that the  id of the current user is the id used in the function
# to ensure that the user 'has permission' to do the task
# need to add profile_id query parameter
def get_current_profile_id(
    profile_id: int = Query(..., description="ID of the current user's profile")
):
    return profile_id

@app.get("/")
# an extra function to show users how to get to /docs to see and experiment with other endpoints when they don't type any endpoints
def read_root():
    return {"message": "Welcome to the API! Use /docs to see available endpoints."}

@app.post("/create-profile")
# function that creates a profile
def create_profile(name:str, user_type:str, db:Session = Depends(database.get_db)):
    profile = models.Profile(name=name, user_type=user_type, balance=0)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return {"message": "Profile created", "profile_id": profile.id}


@app.post("/create-contract")
# function to create contract
def create_contract(profile_id: int, db: Session = Depends(database.get_db)):
    
    contract = models.Contract(profile_id=profile_id, status="new")
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return{"message": "Contract created", "contract_id": contract.id}

@app.post("/add-job")
# function to add a job
def add_job(contract_id: int, description: str, price: float, db:Session = Depends(database.get_db)):
    job = models.Job(contract_id=contract_id, description=description, price=price)
    db.add(job)
    db.commit()
    db.refresh(job)
    return{"message": "Job added", "job_id": job.id}


@app.get("/profiles")
# function to get a list of all profiles
def get_profiles(db: Session = Depends(database.get_db)):
    profiles = db.query(models.Profile).all()
    return[{"id": p.id, "name": p.name, "type": p.user_type, "balance": p.balance} for p in profiles]


@app.get("/contracts/{profile_id}")
# function to get all of the contracts for a specific profile
def get_contracts(profile_id: int, db: Session = Depends(database.get_db)):
    contracts = db.query(models.Contract).filter(models.Contract.profile_id == profile_id).all()
    return [{"id": c.id, "status": c.status} for c in contracts]


@app.get("/contracts/{contract_id}")
# function to get the contract  for a specific contract_id, only if the contract belongs to the user
def get_contract_details(
    contract_id: int,
    current_profile_id: int = Depends(get_current_profile_id), # calls function above
    db: Session = Depends(database.get_db)
    ):
    contract = db.query(models.Contract).filter(
        models.Contract.id == contract_id, 
        models.Contract.profile_id == current_profile_id
    ).first()
    if not contract:
        # deals with authentication/authorization
        raise HTTPException(status_code=404, detail="Contract not found or Unauthorized for this User")
    return {
        "id": contract.id, 
        "status": contract.status, 
        "jobs": [{"id": job.id, "description": job.description, "price": job.price} for job in contract.jobs]
    }

@app.get("/contracts")
# function that gets all non-terminated contracts belonging to a user (either client or contractor)
def get_user_contracts(
    current_profile_id: int = Depends(get_current_profile_id), 
    db: Session = Depends(database.get_db)
):
    contracts = db.query(models.Contract).filter(
        models.Contract.profile_id == current_profile_id,
        models.Contract.status != "terminated" # makes sure it's not terminated
    ).all()
    return [
        {
            "id": contract.id, 
            "status": contract.status,
            "jobs": [{"id": job.id, "description": job.description, "price": job.price} for job in contract.jobs]
        } for contract in contracts
    ]

@app.get("/jobs/unpaid")
# function that returns a list of unpaid jobs from a client or contractor in active contracts
def get_unpaid_jobs(
    current_profile_id: int = Depends(get_current_profile_id), 
    db: Session = Depends(database.get_db)
):
    # gets contracts where user is client of contractor- if not, raise exception
    profile = db.query(models.Profile).filter(models.Profile.id == current_profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    # gets unpaid jobs only from active contracts
    unpaid_jobs = db.query(models.Job).join(models.Contract).filter(
        or_(
            models.Contract.profile_id == current_profile_id, 
        ),
        models.Contract.status != "terminated",  
        models.Job.paid == 0 
    ).all()
    return [
        {
            "id": job.id, 
            "description": job.description, 
            "price": job.price, 
            "contract_id": job.contract_id
        } for job in unpaid_jobs
    ]

@app.post("/jobs/{job_id}/pay")
# function that pays for a job, moving money from client to contractor
# only if the client has enough money to pay
def pay_job(
    job_id: int, 
    current_profile_id: int = Depends(get_current_profile_id), 
    db: Session = Depends(database.get_db)
):
    # finds jobs and contract and catches exceptions
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    contract = db.query(models.Contract).filter(models.Contract.id == job.contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    if contract.profile_id != current_profile_id: # makes sure current user is client of this specific contract
        raise HTTPException(status_code=403, detail="Unauthorized to pay for this job")
    
    client = db.query(models.Profile).filter(models.Profile.id == contract.profile_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client profile not found")
    if client.balance < job.price: # makes sure client has enough money to pay
        raise HTTPException(status_code=400, detail="Insufficient balance")
    # finds contractor and transfers money from client to contractor
    client.balance -= job.price
    contractor_profile = db.query(models.Profile).filter(
        models.Profile.id != client.id,
        models.Profile.user_type == "contractor"
    ).first()
    if not contractor_profile:
        raise HTTPException(status_code=404, detail="Contractor profile not found")
    contractor_profile.balance += job.price
    job.paid = job.price #marks job as paid
    db.commit()
    return {"message": "Job paid successfully"}


@app.post("/balances/deposit/{user_id}")
# function that deposits money into client's balance
# restriction- client can't deposit more than 25% of total jobs to pay
def deposit_balance(
    user_id: int, 
    amount: float, 
    current_profile_id: int = Depends(get_current_profile_id),
    db: Session = Depends(database.get_db)
):
    # finds client and makes sure it's the current client
    if user_id != current_profile_id:
        raise HTTPException(status_code=403, detail="Unauthorized to deposit to this account")
    client = db.query(models.Profile).filter(
        models.Profile.id == user_id, 
        models.Profile.user_type == "client"
    ).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client profile not found")
    # calculates total jobs to pay to calculate max deposit amount
    total_jobs_to_pay = db.query(func.sum(models.Job.price)).join(models.Contract).filter(
        models.Contract.profile_id == user_id,
        models.Job.paid == 0
    ).scalar() or 0
    max_deposit = total_jobs_to_pay * 0.25
    if amount > max_deposit:
        raise HTTPException(status_code=400, detail=f"Cannot deposit more than {max_deposit}")
    client.balance += amount # adds balance
    db.commit()
    return {"message": "Deposit successful", "new_balance": client.balance}

@app.get("/admin/best-profession")
# function with parameters of start and end dates that finds the profession that earned the most money in that time
def get_best_profession(start_date: datetime, end_date: datetime, db: Session = Depends(database.get_db)):
    best_profession = db.query(
        models.Profile.user_type, 
        func.sum(models.Job.price).label('total_earned')
    ).join(models.Contract).join(models.Job).filter(
        models.Job.paid > 0,
        models.Job.contract_id == models.Contract.id,
        models.Contract.profile_id == models.Profile.id
    ).group_by(models.Profile.user_type).order_by(
        func.sum(models.Job.price).desc()
    ).first()
    if not best_profession:
        raise HTTPException(status_code=404, detail="No data found in the specified date range")
    return {"profession": best_profession[0], "total_earned": best_profession[1]}

@app.get("/admin/best-clients")
# function that takes parameters of start and end dates with a limit of how many in the list (defaulted at 2)
# and returns the clients who paid the most for jobs in that time period
def get_best_clients(start_date: datetime, end_date: datetime, limit: int = 2, db: Session = Depends(database.get_db)):
    best_clients = db.query(
        models.Profile.id, 
        models.Profile.name, 
        func.sum(models.Job.price).label('total_paid')
    ).join(models.Contract).join(models.Job).filter(
        models.Job.paid > 0,
        models.Job.contract_id == models.Contract.id,
        models.Contract.profile_id == models.Profile.id,
        models.Profile.user_type == "client"
    ).group_by(models.Profile.id, models.Profile.name).order_by(
        func.sum(models.Job.price).desc()
    ).limit(limit).all()
    return [
        {
            "id": client.id, 
            "full_name": client.name, 
            "paid": client.total_paid
        } for client in best_clients
    ]