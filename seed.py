from sqlalchemy.orm import Session
from database import engine, Base, session_local
from models import Profile, Contract, Job

# Create all tables in the database
Base.metadata.create_all(bind=engine)

def seed_data():
    # Create a new session
    db: Session = session_local()

    try:
        # Clear existing data
        db.query(Job).delete()
        db.query(Contract).delete()
        db.query(Profile).delete()
        db.commit()

        # Create Profiles
        client = Profile(name="John", user_type="client", balance=1000)
        contractor = Profile(name="Joe", user_type="contractor", balance=500)

        # Add Profiles to DB
        db.add(client)
        db.add(contractor)
        db.commit()

        # Refresh Profiles to get their IDs
        db.refresh(client)
        db.refresh(contractor)

        # Create Contracts
        contract1 = Contract(profile_id=client.id, status="in_progress")
        contract2 = Contract(profile_id=client.id, status="new")

        # Add Contracts to DB
        db.add(contract1)
        db.add(contract2)
        db.commit()

        # Refresh Contracts to get their IDs
        db.refresh(contract1)
        db.refresh(contract2)

        # Create Jobs
        job1 = Job(description="Design logo", price=200, paid=0, contract_id=contract1.id)
        job2 = Job(description="Develop website", price=500, paid=0, contract_id=contract1.id)
        job3 = Job(description="Write blog post", price=100, paid=0, contract_id=contract2.id)

        # Add Jobs to DB
        db.add_all([job1, job2, job3])
        db.commit()

        print("Database seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error occurred while seeding data: {e}")

    finally:
        # Close the session
        db.close()


if __name__ == "__main__":
    seed_data()