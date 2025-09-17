# Automation-of-Laundry-and-Ironing-Services-Using-Web-Based-System
Copy code
# Automation-of-Laundry-and-Ironing-Services-Using-Web-Based-System 

This project is a **web-based system** for automating laundry and ironing services.  
It provides an online platform where:  
- Customers can **register**  
- Place **laundry/ironing requests**  
- **Track order status**  
- Manage **online payments**  

The system is built with a **Python backend**, **MySQL database**, and a **responsive frontend** using HTML, CSS, Bootstrap, and JavaScript.  

---

##  Features  

Customer Registration & Login  
Place Laundry / Ironing Requests  
Track Order Status (Pending, In Progress, Completed, Delivered)  
Payment Management  
Admin Dashboard (Manage Customers, Orders, Payments)  
Responsive Frontend (Mobile & Desktop Friendly)  

---

## Tech Stack  

- **Backend**: Python (Flask / Django)  
- **Database**: MySQL  
- **Frontend**: HTML, CSS, Bootstrap, JavaScript  
- **IDE**: Visual Studio Code (VS Code)  

---

## Installation & Setup (Visual Studio Code)  

Follow these steps to run the project on your local system:  

### Step 1: Install Prerequisites  

- Install [Python (>=3.8)](https://www.python.org/downloads/)  
- Install [MySQL Community Server](https://dev.mysql.com/downloads/mysql/)  
- Install [Visual Studio Code](https://code.visualstudio.com/download)  
- Install Git (optional, for cloning repositories)  

Check versions in CMD/Terminal:  
```bash
python --version
mysql --version
Step 2: Clone the Repository
bash
Copy code
git clone https://github.com/rushikeshhadawale/Automation-of-Laundry-and-Ironing-Services-Using-Web-Based-System.git
cd laundry-automation-system
Or download the ZIP and extract it.

Step 3: Create & Activate Virtual Environment
bash
Copy code
python -m venv venv
Activate it:

Windows

bash
Copy code
venv\Scripts\activate
Mac/Linux

bash
Copy code
source venv/bin/activate
Step 4: Install Dependencies
Install required libraries from requirements.txt:

bash
Copy code
pip install -r requirements.txt

bash
Copy code
pip install flask mysql-connector-python flask-mysqldb
Step 5: Configure MySQL Database
Open MySQL command line or use phpMyAdmin.

Create a database:

sql
Copy code
CREATE DATABASE laundry_db;

sql
Copy code
USE laundry_db;
SOURCE database/laundry_db.sql;
Update database credentials in config.py (or settings file):

python
Copy code
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "yourpassword"
MYSQL_DB = "laundry_db"

Step 6: Run the Application
bash
Copy code
python app.py
If using Flask, by default the app will run on:
 http://127.0.0.1:5000/

Step 7: Open in Browser
Open http://127.0.0.1:5000/ in your browser.

Register as a new customer and start using the system.

Project Structure
graphql
Copy code
├── app.py                  # Main application file (Flask/Django)
├── config.py               # Database configuration
├── static/                 # CSS, JS, Images
│   ├── css/
│   ├── js/
│   └── images/
├── templates/              # HTML templates (Bootstrap UI)
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
├── database/
│   └── laundry_db.sql      # SQL script for MySQL
├── requirements.txt        # Python dependencies
└── README.md               # Documentation

Future Enhancements
Add email/SMS notifications for order updates

Author
Developed by Rushikesh Hadawale

Contact: rushikeshhadawale10@gmail.com
GitHub: rushikeshhadawale
