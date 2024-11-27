# Python Backend Exercise- API

In this project, I created a FastAPI that serves as a REST API to manage profiles, jobs, payments, and payments. 

## How to Launch the Application

### 1. Clone the Repository
```
git clone <repository-url>
cd <repository-directory>
```

### 2. Install Dependencies
Install all required packages form the requirements.txt file
```
pip install -r requirements.txt
```

### 3. Set Up the Database
Initialize the database using SQLAlchemy models from the models.py file:
```
python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### 4. Seed the Database (Optional)
If you'd like to populate the database with sample data, run the seed.py file:
```
python seed.py
```

### 5. Run the Application
use uvicorn to start the FastAPI app from main.py:
```
uvicorn main:app --reload
```

### 6. Access the API
Open your browser to:
```
Base URL: http://127.0.0.1:8000/
Interactive Documentation: http://127.0.0.1:8000/docs
```

With the interactive documentation, you can test the API endpoints directly. 



## API Reference

### Welcome Message

```http
GET /
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `none` | `-` | Displays a welcome message with instructions to access '/ docs'.|

### PROFILES

#### Create Profile

```http
POST /create-profile
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `name`      | `string` | **Required**. Name of the user. |
| `user_type`      | `string` | **Required**. User_type (either client or contractor) |


#### Get All Profiles
```http
GET /profiles
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `None`      | `-` | Returns a list of all profiles. |

### CONTRACTS

#### Create Contract

```http
POST /create-contract
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `profile_id`      | `int` | **Required**. Profile ID of 'onwer' of contract. |

#### Get Contract Details

```http
GET /contracts/{contract_id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `contract_id`      | `int` | **Required**. ID of the contract. |

#### Get Current Contracts for the Current User

```http
GET /contracts
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `current_profile_id`      | `int` | **Required**. User's Profile ID (Query Parameter) |


### JOBS

#### Add Job to Contract
```http
POST /add-job
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `contract_id`      | `int` | **Required**. Contract ID |
| `description`      | `string` | **Required**. Job description |
| `price`      | `float` | **Required**. Job price |

#### Get Unpaid Jobs
```http
GET /jobs/unpaid
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `current_profile_id`      | `int` | **Required**. User's profile ID (Query Parameter) |

#### Pay for a Job
```http
POST /jobs/{job_id}/pay
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `job_id`      | `int` | **Required**. ID of the job.|

### BALANCES

#### Deposit Balance
```http
POST /balances/deposit/{user_id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `user_id`      | `int` | **Required**. ID of the user. |
| `amount`      | `float` | **Required**. Amount to deposit. (Query Parameter) |

### ADMIN

#### Get Best Profession
```http
GET /admin/best-profession
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `start_date`      | `datetime` | **Required**. Start date of the range. |
| `end_date`      | `datetime` | **Required**. End date of the range. |

#### Get Best Clients
```http
GET /admin/best-clients
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `start_date`      | `datetime` | **Required**. Start date of the range. |
| `end_date`      | `datetime` | **Required**. End date of the range. |
| `limit`      | `int` | Limit on the number of clients returned (default: 2) |
