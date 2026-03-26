# ShopZon - Python Flask E-Commerce Project

ShopZon is a beginner-friendly, simple e-commerce website built using Python Flask on the backend and pure HTML/CSS/JavaScript on the frontend. It uses SQLite for learning database operations and includes sample product data.

## Requirements

- Python 3.8 or higher installed on your computer.

## Step-by-Step Setup Instructions

### 1. Open Terminal and Navigate to Project
Open your Command Prompt or PowerShell and navigate to the project folder:
```bash
cd "C:\Users\daran\Desktop\ecommerce- website"
```

### 2. Set Up a Virtual Environment 
Creating a virtual environment ensures Python packages don't interfere with your system.
```bash
python -m venv venv
```

Activate the virtual environment:
- On Windows:
```bash
venv\Scripts\activate
```
- On Mac/Linux:
```bash
source venv/bin/activate
```

### 3. Install Required Libraries
Install Flask and Werkzeug using the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### 4. Initialize the Database
Run the script to create the SQLite database and populate it with sample products:
```bash
python init_db.py
```
*You should see a message saying "Database initialized successfully with sample products."*

### 5. Start the Server
Now, start the Flask application:
```bash
python app.py
```

### 6. View the Website
Open your web browser (Chrome, Firefox, etc.) and go to:
[http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## Project Structure Explained
- `app.py`: The main Flask server code with REST API endpoints for user authentication, fetching products, and managing the cart.
- `init_db.py`: A Python script that executes SQL to create the database schema (`database.db`) and inserts sample store items.
- `templates/index.html`: The only HTML file, serving as a single-page layout.
- `static/css/style.css`: Contains vanilla CSS to give the app a modern, Amazon-like user interface.
- `static/js/main.js`: Makes `fetch()` requests to `app.py` directly, managing user sessions and cart logic without needing complex frameworks like React or Angular.

Happy coding!
