# 🏥 AI Disease Prediction System

An AI-based Disease Prediction System developed using Python, Tkinter, MySQL, and Machine Learning concepts. The application provides a simple graphical interface where users can enter symptoms, view predicted health conditions, and maintain a history of their predictions.

## 📌 Project Overview

The AI Disease Prediction System is a student project designed to demonstrate how Python, database management, and AI/ML concepts can be combined to build a desktop application.

The system includes user registration and login, symptom-based disease prediction, prediction history, and an X-ray analysis interface.

## ✨ Features

- **User Authentication** — Register and log in to access the application.
- **Symptom-Based Prediction** — Select symptoms and view a predicted health condition.
- **Prediction Confidence** — Display a confidence percentage with the prediction.
- **Prediction History** — View previously saved predictions.
- **X-Ray Analysis Interface** — Access the X-ray analysis section.
- **MySQL Database** — Store user information and prediction records.
- **Graphical User Interface** — Simple desktop interface built with Tkinter.
- **User-Friendly Dashboard** — Navigate between the application's main features.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Tkinter | Graphical user interface |
| MySQL | Database management |
| `mysql-connector-python` | Python–MySQL connectivity |
| Pickle | Load or save serialized objects, if used by the implementation |
| Machine Learning concepts | Support the prediction functionality |

## 📂 Project Structure

```text
Disease-Prediction-System/
│
├── disease_prediction_system.py
├── README.md
├── requirements.txt
└── models/
    └── model.pkl
```

*Note: This is a suggested structure. Keep only the files and folders that actually exist in your project. Include `model.pkl` only if your application uses a saved model.*

## ⚙️ Installation and Setup

### 1. Install Python

Download and install Python from [python.org](https://www.python.org/downloads/).

Verify the installation:

```bash
python --version
```

### 2. Install MySQL

Install and start MySQL Server. Make sure your MySQL username and password are configured correctly.

### 3. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
```

Navigate into the project directory:

```bash
cd YOUR-REPOSITORY
```

### 4. Install Dependencies

Install the required Python package:

```bash
pip install mysql-connector-python
```

Tkinter is included with many standard Python installations. On some Linux systems, it may need to be installed separately.

### 5. Configure the Database

Open your Python file and update the MySQL connection settings to match your local environment.

Example:

```python
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "YOUR_MYSQL_PASSWORD"
DATABASE_NAME = "disease_prediction"
```

Ensure the database and required tables are created by your application or database setup script.

### 6. Run the Application

```bash
python disease_prediction_system.py
```

Replace the filename with your actual Python file name.

## 🗄️ Database

The application can use a MySQL database named `disease_prediction` to manage its data.

Suggested tables:

- **users** — Stores user account details.
- **predictions** — Stores symptoms, predicted conditions, confidence values, and prediction timestamps.

The exact schema depends on your implementation.

## 🔄 Application Workflow

1. Launch the desktop application.
2. Register a new account or log in.
3. Open the dashboard.
4. Select the symptoms relevant to the prediction.
5. View the predicted condition and displayed confidence.
6. Review previous predictions in the history section.
7. Access other available features from the dashboard.

## 🎯 Project Objectives

- Develop a desktop application using Python.
- Integrate a graphical interface with a MySQL database.
- Demonstrate symptom-based prediction functionality.
- Practice database connectivity and CRUD operations.
- Understand how AI/ML concepts can be incorporated into a software project.

## 🔮 Future Enhancements

- Train and integrate a validated machine learning model using a reliable medical dataset.
- Improve prediction performance through model evaluation.
- Add secure password hashing and stronger authentication.
- Implement actual medical-image analysis using a validated image classification model.
- Add downloadable prediction reports.
- Improve accessibility and interface design.
- Add more comprehensive testing and error handling.

## ⚠️ Medical Disclaimer

This application is intended **for educational and demonstration purposes only**. Its predictions are not medically validated and must not be used to diagnose diseases, recommend treatment, or replace professional medical advice.

Any displayed confidence percentage should not be interpreted as the probability that a person has a disease unless the model has been properly trained, calibrated, and clinically validated.

