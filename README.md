# juanito-bikes-service
A small Python-based CRUD system designed to help manage the repair workflow of a fictional bike shop called Juanito Bikes.
This was built as a personal learning project to practice object-oriented programming, database management, and building a CLI-based admin system with role handling and core CRUD operations.

Features
User login with role-based access (Admin / Reception / Technician)
Full client management: create, edit, delete, view
Work order creation with issue tracking and repair dates
Technicians can view and update the status of their assigned orders

Database
The system is connected to a MySQL database hosted on Azure, so no local database setup is required. 
All interactions are done through the live cloud instance.

Technologies Used
Python 3
MySQL (hosted on Azure)
pymysql for database connection
tabulate for CLI formatting

## Requirements

- Python 3 installed on your machine
- Python libraries:
  - `pymysql`
  - `tabulate`
To install them:
```bash
pip install pymysql tabulate



