# 🛒 EZShop – Full-Stack Retail Management System

EZShop is a full-stack software engineering project developed at Politecnico di Torino.  
The system simulates the backend logic and data management of a retail shop, including product catalog management, sales tracking, and persistent storage.

This project was developed in a 5-member team following software engineering and testing practices.

---

## 👥 Team

- Mahsa Hashemzadeh  
- Marco Oliviero
- Edwin Liby  
- Letizia Pontarolo  
- Nima Hosseini 

---

## 🧰 Tech Stack

- Python  
- FastAPI  
- SQL / SQLAlchemy  
- Pytest  
- Git / GitLab workflow  
- MVC Architecture  

---

## 🧱 Architecture

The application follows an MVC-inspired layered architecture:

- **Models** – data schema and persistence  
- **Services** – business logic  
- **API** – FastAPI endpoints  
- **Database** – SQL storage layer  

---

## ✅ Features

- Product catalog management  
- Inventory tracking  
- Sales registration  
- Customer data handling  
- Persistent database storage  
- REST API endpoints  

---

## ⚙️ Setup

Create virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
````

Initialize database:

```bash
python init_db.py
```

Run the application:

```bash
uvicorn main:app --reload
```

---

## 🧪 Testing

Run tests:

```bash
pytest ./tests
```

Run tests with coverage:

```bash
pytest --cov=app ./tests
```

---

## 📄 Documentation

API documentation is available via Swagger when running the application.

---

## 🎓 Academic Context

Software Engineering Project
Politecnico di Torino

---

## 🚀 Author

Mahsa Hashemzadeh
MSc Data Science and Engineering – Politecnico di Torino

```
