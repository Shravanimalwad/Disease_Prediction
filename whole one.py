import os
import shutil
from datetime import datetime

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import mysql.connector

import cv2



APP_NAME = "Smart Healthcare"
APP_TITLE = "Smart Healthcare - Disease Prediction System"

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "sql@59766"
DATABASE_NAME = "disease_prediction"


LAB_REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab_reports")



COLORS = {
    "primary": "#4F46E5",
    "primary_dark": "#3730A3",
    "primary_light": "#EEF2FF",

    "success": "#16A34A",
    "success_light": "#DCFCE7",

    "danger": "#DC2626",
    "danger_light": "#FEE2E2",

    "warning": "#D97706",
    "warning_light": "#FEF3C7",

    "background": "#F5F7FB",
    "white": "#FFFFFF",

    "text": "#1F2937",
    "text_dark": "#111827",
    "text_light": "#6B7280",

    "border": "#E5E7EB",
    "sidebar": "#111827",

    "blue": "#2563EB",
    "blue_light": "#DBEAFE",

    "purple": "#7C3AED",
    "purple_light": "#EDE9FE",

    "teal": "#0F766E",
    "teal_light": "#CCFBF1",

    "orange": "#EA580C",
    "orange_light": "#FFEDD5",
}

FONT = "Segoe UI"


def get_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=DATABASE_NAME
    )


def _safe_alter(cursor, statement):

    try:
        cursor.execute(statement)
    except mysql.connector.Error:
        pass



def setup_database():
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
        cursor.close()
        connection.close()

        connection = get_connection()
        cursor = connection.cursor()

        # USERS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                full_name VARCHAR(150),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        _safe_alter(cursor, "ALTER TABLE users ADD COLUMN full_name VARCHAR(150)")

        # PATIENTS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                name VARCHAR(150) NOT NULL,
                age INT,
                gender VARCHAR(20),
                contact VARCHAR(50),
                address VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # PREDICTIONS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                patient_id INT NULL,
                category VARCHAR(20) NOT NULL DEFAULT 'Human',
                symptoms TEXT NOT NULL,
                disease VARCHAR(255) NOT NULL,
                confidence FLOAT NOT NULL,
                prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE SET NULL
            )
        """)
        _safe_alter(cursor, "ALTER TABLE predictions ADD COLUMN patient_id INT NULL")
        _safe_alter(cursor, "ALTER TABLE predictions ADD COLUMN category VARCHAR(20) NOT NULL DEFAULT 'Human'")

        # LAB REPORTS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lab_reports (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                patient_id INT NULL,
                report_name VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                notes TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE SET NULL
            )
        """)

        # REMINDERS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                medicine_name VARCHAR(255) NOT NULL,
                dosage VARCHAR(100),
                reminder_time VARCHAR(10) NOT NULL,
                frequency VARCHAR(20) NOT NULL DEFAULT 'Daily',
                is_active TINYINT(1) DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        connection.commit()
        cursor.close()
        connection.close()

        os.makedirs(LAB_REPORTS_DIR, exist_ok=True)

        return True

    except Exception as e:
        messagebox.showerror(
            "Database Connection Error",
            "Unable to connect with MySQL.\n\n"
            "Please check:\n"
            "\u2022 MySQL server is running\n"
            "\u2022 Username is correct\n"
            "\u2022 Password is correct\n\n"
            f"Error: {e}"
        )
        return False



def register_user(username, password, full_name=""):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users(username, password, full_name) VALUES(%s, %s, %s)",
            (username, password, full_name)
        )
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except mysql.connector.IntegrityError:
        return False
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return False


def login_user(username, password):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, username, full_name FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return None



def add_patient(user_id, name, age, gender, contact, address):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO patients(user_id, name, age, gender, contact, address)
            VALUES(%s, %s, %s, %s, %s, %s)
            """,
            (user_id, name, age, gender, contact, address)
        )
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return False


def get_patients(user_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT id, name, age, gender, contact, address, created_at
            FROM patients WHERE user_id=%s ORDER BY created_at DESC
            """,
            (user_id,)
        )
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return []




def save_prediction(user_id, patient_id, category, symptoms, disease, confidence):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO predictions (user_id, patient_id, category, symptoms, disease, confidence)
            VALUES(%s, %s, %s, %s, %s, %s)
            """,
            (user_id, patient_id, category, symptoms, disease, confidence)
        )
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return False


def get_prediction_history(user_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT p.id, IFNULL(pt.name, 'General'), p.category, p.symptoms,
                   p.disease, p.confidence, p.prediction_date
            FROM predictions p
            LEFT JOIN patients pt ON p.patient_id = pt.id
            WHERE p.user_id=%s
            ORDER BY p.prediction_date DESC
            """,
            (user_id,)
        )
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return []


def get_patient_case_records(user_id):
    """Returns one row per (patient, prediction) pair - used to build a
    patient-centric case view, as opposed to the flat chronological
    prediction history log."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT p.id, p.name, p.age, p.gender, p.contact,
                   pr.category, pr.symptoms, pr.disease, pr.confidence, pr.prediction_date
            FROM patients p
            LEFT JOIN predictions pr ON pr.patient_id = p.id
            WHERE p.user_id = %s
            ORDER BY p.name ASC, pr.prediction_date DESC
            """,
            (user_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        return rows
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return []


def get_user_statistics(user_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM predictions WHERE user_id=%s", (user_id,))
        total = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(confidence) FROM predictions WHERE user_id=%s", (user_id,))
        average = cursor.fetchone()[0]

        cursor.execute(
            "SELECT disease FROM predictions WHERE user_id=%s ORDER BY prediction_date DESC LIMIT 1",
            (user_id,)
        )
        latest = cursor.fetchone()
        latest_disease = latest[0] if latest else "No predictions"

        cursor.execute("SELECT COUNT(*) FROM patients WHERE user_id=%s", (user_id,))
        patient_count = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        if average is None:
            average = 0

        return total, average, latest_disease, patient_count
    except Exception:
        return 0, 0, "No predictions", 0



def save_lab_report(user_id, patient_id, report_name, file_path, notes):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO lab_reports(user_id, patient_id, report_name, file_path, notes)
            VALUES(%s, %s, %s, %s, %s)
            """,
            (user_id, patient_id, report_name, file_path, notes)
        )
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return False


def get_lab_reports(user_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT lr.id, IFNULL(pt.name, 'General'), lr.report_name,
                   lr.file_path, lr.notes, lr.uploaded_at
            FROM lab_reports lr
            LEFT JOIN patients pt ON lr.patient_id = pt.id
            WHERE lr.user_id=%s
            ORDER BY lr.uploaded_at DESC
            """,
            (user_id,)
        )
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return []




def add_reminder(user_id, medicine_name, dosage, reminder_time, frequency):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO reminders(user_id, medicine_name, dosage, reminder_time, frequency)
            VALUES(%s, %s, %s, %s, %s)
            """,
            (user_id, medicine_name, dosage, reminder_time, frequency)
        )
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return False


def get_reminders(user_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT id, medicine_name, dosage, reminder_time, frequency, is_active
            FROM reminders WHERE user_id=%s
            ORDER BY reminder_time ASC
            """,
            (user_id,)
        )
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return []


def delete_reminder(reminder_id):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM reminders WHERE id=%s", (reminder_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return False


HUMAN_SYMPTOMS = [
    "Fever", "Cough", "Headache", "Fatigue", "Nausea", "Vomiting",
    "Sore Throat", "Shortness of Breath", "Chest Pain", "Stomach Pain",
    "Diarrhea", "Body Pain", "Cold", "Dizziness", "Loss of Appetite"
]

ANIMAL_SYMPTOMS = [
    "Loss of Appetite", "Lethargy", "Vomiting", "Diarrhea", "Coughing",
    "Nasal Discharge", "Limping", "Skin Rash", "Excessive Scratching",
    "Warm Ears / Nose (Fever)", "Weight Loss", "Difficulty Breathing"
]

PLANT_SYMPTOMS = [
    "Yellowing Leaves", "Wilting", "Brown Spots on Leaves", "Leaf Curling",
    "Stunted Growth", "White Powdery Coating", "Root Rot", "Holes in Leaves",
    "Discoloration of Stem", "Fungal Growth", "Dropping Leaves",
    "Sticky Residue on Leaves"
]

CATEGORY_SYMPTOMS = {
    "Human": HUMAN_SYMPTOMS,
    "Animal": ANIMAL_SYMPTOMS,
    "Plant": PLANT_SYMPTOMS,
}


def predict_human(selected):
    s = set(selected)

    if {"Fever", "Cough", "Sore Throat"}.issubset(s):
        return "Flu", 91.0
    elif {"Fever", "Cough", "Shortness of Breath"}.issubset(s):
        return "Respiratory Infection", 88.0
    elif {"Vomiting", "Diarrhea", "Stomach Pain"}.issubset(s):
        return "Gastroenteritis", 92.0
    elif {"Headache", "Fever", "Body Pain"}.issubset(s):
        return "Viral Infection", 86.0
    elif {"Cold", "Cough", "Sore Throat"}.issubset(s):
        return "Common Cold", 90.0
    elif {"Chest Pain", "Shortness of Breath"}.issubset(s):
        return "Possible Cardiac / Respiratory Condition", 75.0
    elif {"Nausea", "Vomiting"}.issubset(s):
        return "Stomach Infection", 78.0
    elif {"Headache", "Dizziness"}.issubset(s):
        return "Migraine / Dizziness", 74.0
    elif "Headache" in s:
        return "Headache / Migraine", 72.0
    elif "Fever" in s:
        return "Possible Viral Infection", 70.0
    elif "Cough" in s:
        return "Respiratory Infection", 68.0
    else:
        return "General Illness", 60.0


def predict_animal(selected):
    s = set(selected)

    if {"Coughing", "Nasal Discharge", "Warm Ears / Nose (Fever)"}.issubset(s):
        return "Kennel Cough / Respiratory Infection", 87.0
    elif {"Difficulty Breathing", "Lethargy"}.issubset(s):
        return "Possible Respiratory Distress - Seek Vet Immediately", 78.0
    elif {"Loss of Appetite", "Lethargy", "Vomiting"}.issubset(s):
        return "Possible Gastrointestinal Illness", 85.0
    elif {"Diarrhea", "Vomiting"}.issubset(s):
        return "Gastroenteritis (Animal)", 82.0
    elif {"Excessive Scratching", "Skin Rash"}.issubset(s):
        return "Skin Allergy / Parasite Infestation", 80.0
    elif {"Limping", "Weight Loss"}.issubset(s):
        return "Joint Issue / Possible Arthritis", 70.0
    elif "Loss of Appetite" in s:
        return "General Illness - Monitor Closely", 65.0
    else:
        return "No Clear Pattern - Consult Veterinarian", 55.0


def predict_plant(selected):
    s = set(selected)

    if {"Yellowing Leaves", "Wilting", "Root Rot"}.issubset(s):
        return "Root Rot Disease", 88.0
    elif "White Powdery Coating" in s:
        return "Powdery Mildew", 85.0
    elif {"Brown Spots on Leaves", "Leaf Curling"}.issubset(s):
        return "Fungal Leaf Spot Disease", 80.0
    elif {"Sticky Residue on Leaves", "Holes in Leaves"}.issubset(s):
        return "Pest Infestation (Aphids / Insects)", 78.0
    elif {"Stunted Growth", "Discoloration of Stem"}.issubset(s):
        return "Nutrient Deficiency", 70.0
    elif "Wilting" in s:
        return "Possible Underwatering / Root Stress", 60.0
    elif "Yellowing Leaves" in s:
        return "Possible Overwatering / Nutrient Issue", 58.0
    else:
        return "General Plant Stress - Monitor Conditions", 50.0


def predict_disease(category, symptoms):
    if category == "Animal":
        return predict_animal(symptoms)
    elif category == "Plant":
        return predict_plant(symptoms)
    return predict_human(symptoms)



MEDICINE_MAP = {
    # Human
    "Flu": "Paracetamol, rest and fluids. Antihistamines for congestion. See a doctor if symptoms last beyond 5 days.",
    "Respiratory Infection": "Cough syrup, steam inhalation; antibiotics only if prescribed by a doctor.",
    "Gastroenteritis": "Oral Rehydration Solution (ORS), probiotics and a light, bland diet.",
    "Viral Infection": "Paracetamol for fever, plenty of fluids and complete rest.",
    "Common Cold": "Antihistamines, decongestants, warm fluids and rest.",
    "Possible Cardiac / Respiratory Condition": "Seek emergency medical attention immediately.",
    "Stomach Infection": "ORS, antacids and a bland diet; consult a doctor if it persists.",
    "Migraine / Dizziness": "Pain relievers, hydration and rest in a dark, quiet room.",
    "Headache / Migraine": "Paracetamol or Ibuprofen and adequate rest.",
    "Possible Viral Infection": "Rest, fluids and paracetamol for fever.",
    "General Illness": "Rest, hydration and monitoring; consult a doctor if it worsens.",
    # Animal
    "Kennel Cough / Respiratory Infection": "Consult a veterinarian for antibiotics or cough suppressants.",
    "Possible Respiratory Distress - Seek Vet Immediately": "Emergency veterinary care required.",
    "Possible Gastrointestinal Illness": "Withhold food briefly, provide water, consult a vet.",
    "Gastroenteritis (Animal)": "Bland diet, hydration and veterinary consultation.",
    "Skin Allergy / Parasite Infestation": "Vet-prescribed anti-parasitic shampoo or medication.",
    "Joint Issue / Possible Arthritis": "Vet-prescribed anti-inflammatory and joint supplements.",
    "General Illness - Monitor Closely": "Monitor the animal closely and consult a vet if symptoms persist.",
    "No Clear Pattern - Consult Veterinarian": "Consult a veterinarian for a proper diagnosis.",
    # Plant
    "Root Rot Disease": "Improve drainage, reduce watering frequency, apply a fungicide.",
    "Powdery Mildew": "Apply sulfur-based or neem oil fungicide; improve air circulation.",
    "Fungal Leaf Spot Disease": "Remove affected leaves and apply a copper-based fungicide.",
    "Pest Infestation (Aphids / Insects)": "Apply neem oil or insecticidal soap.",
    "Nutrient Deficiency": "Apply a balanced fertilizer suited to the plant type.",
    "Possible Underwatering / Root Stress": "Adjust the watering schedule and check soil moisture.",
    "Possible Overwatering / Nutrient Issue": "Reduce watering frequency and check drainage.",
    "General Plant Stress - Monitor Conditions": "Monitor light, water and soil conditions closely.",
}


def get_medicine_suggestion(disease):
    return MEDICINE_MAP.get(
        disease,
        "No specific suggestion available. Please consult a qualified professional."
    )



HOSPITAL_MAP = {
    "Human": [
        ("City Care General Hospital", "General Medicine", "1800-000-111"),
        ("Sunrise Multispecialty Hospital", "Internal Medicine / Emergency", "1800-000-222"),
        ("Wellness Family Clinic", "General Physician", "1800-000-333"),
    ],
    "Animal": [
        ("Green Valley Veterinary Clinic", "General Veterinary Care", "1800-000-444"),
        ("PetCare Animal Hospital", "Emergency & Surgery", "1800-000-555"),
    ],
    "Plant": [
        ("District Agriculture Extension Office", "Crop & Plant Health Advisory", "1800-000-666"),
        ("AgroCare Plant Clinic", "Plant Disease Diagnosis", "1800-000-777"),
    ],
}


def get_hospital_suggestions(category):
    return HOSPITAL_MAP.get(category, [])



def create_button(parent, text, command, bg=None, fg="white", width=18, height=1):
    if bg is None:
        bg = COLORS["primary"]

    return tk.Button(
        parent, text=text, command=command,
        font=(FONT, 10, "bold"), bg=bg, fg=fg,
        activebackground=COLORS["primary_dark"], activeforeground="white",
        bd=0, relief="flat", cursor="hand2", width=width, height=height
    )


def styled_entry(parent, show=None):
    entry = tk.Entry(parent, font=(FONT, 11), bd=1, relief="solid", show=show)
    return entry


def field_label(parent, text):
    tk.Label(
        parent, text=text, font=(FONT, 10, "bold"),
        bg="white", fg=COLORS["text"]
    ).pack(anchor="w")


def zebra_stripe(tree, even_color="#FFFFFF", odd_color="#F3F4F6"):
    """Applies alternating row shading to a ttk.Treeview for a cleaner,
    more professional table look."""
    tree.tag_configure("evenrow", background=even_color)
    tree.tag_configure("oddrow", background=odd_color)

    for index, child in enumerate(tree.get_children()):
        existing_tags = [t for t in tree.item(child, "tags") if t not in ("evenrow", "oddrow")]
        existing_tags.append("evenrow" if index % 2 == 0 else "oddrow")
        tree.item(child, tags=tuple(existing_tags))



class LoginWindow:

    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE + " - Login")
        self.root.geometry("900x600")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["background"])

        self.create_ui()
        self.root.bind("<Return>", lambda event: self.login())

    def create_ui(self):
        left = tk.Frame(self.root, bg=COLORS["primary"], width=400, height=600)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="\u271a", font=(FONT, 50, "bold"),
                 bg=COLORS["primary"], fg="white").pack(pady=(80, 5))

        tk.Label(left, text="SMART\nHEALTHCARE", font=(FONT, 26, "bold"),
                 bg=COLORS["primary"], fg="white", justify="center").pack()

        tk.Label(left, text="Disease Prediction System", font=(FONT, 12),
                 bg=COLORS["primary"], fg="#E0E7FF").pack(pady=10)

        tk.Label(
            left,
            text="A student-developed healthcare\napplication for educational\ndisease prediction.",
            font=(FONT, 10), bg=COLORS["primary"], fg="#C7D2FE", justify="center"
        ).pack(pady=30)

        tk.Label(left, text="Python  \u2022  MySQL  \u2022  Tkinter", font=(FONT, 9, "bold"),
                 bg=COLORS["primary"], fg="white").pack(side="bottom", pady=35)

        right = tk.Frame(self.root, bg=COLORS["background"], width=500, height=600)
        right.pack(side="right", fill="both", expand=True)
        right.pack_propagate(False)

        tk.Label(right, text="Welcome Back", font=(FONT, 25, "bold"),
                 bg=COLORS["background"], fg=COLORS["text_dark"]).pack(pady=(85, 5))

        tk.Label(right, text="Login to access your healthcare dashboard",
                 font=(FONT, 10), bg=COLORS["background"], fg=COLORS["text_light"]).pack(pady=(0, 30))

        form = tk.Frame(right, bg=COLORS["white"], padx=40, pady=35)
        form.pack(padx=55, fill="x")

        field_label(form, "Username")
        self.username = styled_entry(form)
        self.username.pack(fill="x", ipady=8, pady=(7, 18))

        field_label(form, "Password")
        self.password = styled_entry(form, show="\u25cf")
        self.password.pack(fill="x", ipady=8, pady=(7, 20))

        create_button(form, "LOGIN TO ACCOUNT", self.login, width=30, height=2).pack(fill="x")

        tk.Button(
            form, text="Don't have an account?  Sign Up",
            font=(FONT, 10, "bold"), bg="white", fg=COLORS["primary"],
            activebackground="white", activeforeground=COLORS["primary_dark"],
            bd=0, cursor="hand2", command=self.go_to_register
        ).pack(pady=(18, 0))

        self.username.focus_set()

    def login(self):
        username = self.username.get().strip()
        password = self.password.get()

        if not username or not password:
            messagebox.showwarning("Missing Information", "Please enter both username and password.")
            return

        result = login_user(username, password)

        if result:
            self.root.destroy()
            dashboard_root = tk.Tk()
            Dashboard(dashboard_root, result[0], result[1])
            dashboard_root.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def go_to_register(self):
        self.root.destroy()
        register_root = tk.Tk()
        RegisterWindow(register_root)
        register_root.mainloop()



class RegisterWindow:

    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE + " - Sign Up")
        self.root.geometry("900x650")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["background"])

        self.create_ui()
        self.root.bind("<Return>", lambda event: self.register())

    def create_ui(self):
        left = tk.Frame(self.root, bg=COLORS["success"], width=400, height=650)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="\u271a", font=(FONT, 50, "bold"),
                 bg=COLORS["success"], fg="white").pack(pady=(90, 5))

        tk.Label(left, text="JOIN\nSMART HEALTHCARE", font=(FONT, 22, "bold"),
                 bg=COLORS["success"], fg="white", justify="center").pack()

        tk.Label(
            left,
            text="Create an account to save patients,\nrun predictions and track your\nhealthcare history.",
            font=(FONT, 10), bg=COLORS["success"], fg="#DCFCE7", justify="center"
        ).pack(pady=30)

        tk.Label(left, text="Python  \u2022  MySQL  \u2022  Tkinter", font=(FONT, 9, "bold"),
                 bg=COLORS["success"], fg="white").pack(side="bottom", pady=35)

        right = tk.Frame(self.root, bg=COLORS["background"], width=500, height=650)
        right.pack(side="right", fill="both", expand=True)
        right.pack_propagate(False)

        tk.Label(right, text="Create Account", font=(FONT, 25, "bold"),
                 bg=COLORS["background"], fg=COLORS["text_dark"]).pack(pady=(55, 5))

        tk.Label(right, text="Sign up to get started", font=(FONT, 10),
                 bg=COLORS["background"], fg=COLORS["text_light"]).pack(pady=(0, 20))

        form = tk.Frame(right, bg=COLORS["white"], padx=40, pady=30)
        form.pack(padx=55, fill="x")

        field_label(form, "Full Name")
        self.full_name = styled_entry(form)
        self.full_name.pack(fill="x", ipady=8, pady=(7, 14))

        field_label(form, "Username")
        self.username = styled_entry(form)
        self.username.pack(fill="x", ipady=8, pady=(7, 14))

        field_label(form, "Password")
        self.password = styled_entry(form, show="\u25cf")
        self.password.pack(fill="x", ipady=8, pady=(7, 14))

        field_label(form, "Confirm Password")
        self.confirm_password = styled_entry(form, show="\u25cf")
        self.confirm_password.pack(fill="x", ipady=8, pady=(7, 20))

        create_button(
            form, "CREATE ACCOUNT", self.register,
            bg=COLORS["success"], width=30, height=2
        ).pack(fill="x")

        tk.Button(
            form, text="Already have an account?  Login",
            font=(FONT, 10, "bold"), bg="white", fg=COLORS["success"],
            activebackground="white", activeforeground=COLORS["success"],
            bd=0, cursor="hand2", command=self.go_to_login
        ).pack(pady=(18, 0))

        self.full_name.focus_set()

    def register(self):
        full_name = self.full_name.get().strip()
        username = self.username.get().strip()
        password = self.password.get()
        confirm_password = self.confirm_password.get()

        if not username or not password or not confirm_password:
            messagebox.showwarning("Missing Information", "Please fill in all required fields.")
            return

        if len(username) < 3:
            messagebox.showwarning("Invalid Username", "Username must contain at least 3 characters.")
            return

        if len(password) < 4:
            messagebox.showwarning("Weak Password", "Password must contain at least 4 characters.")
            return

        if password != confirm_password:
            messagebox.showwarning("Password Mismatch", "Password and Confirm Password do not match.")
            return

        if register_user(username, password, full_name):
            messagebox.showinfo(
                "Account Created",
                "Your account has been created successfully.\n\nYou can now login."
            )
            self.go_to_login()
        else:
            messagebox.showerror("Registration Failed", "This username already exists.")

    def go_to_login(self):
        self.root.destroy()
        login_root = tk.Tk()
        LoginWindow(login_root)
        login_root.mainloop()




class Dashboard:

    def __init__(self, root, user_id, username):
        self.root = root
        self.user_id = user_id
        self.username = username

        self.root.title(APP_TITLE)
        self.root.geometry("1250x760")
        self.root.minsize(1050, 680)
        self.root.configure(bg=COLORS["background"])

        self.create_ui()

    def create_ui(self):
        sidebar = tk.Frame(self.root, bg=COLORS["sidebar"], width=240)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        logo_frame = tk.Frame(sidebar, bg=COLORS["sidebar"])
        logo_frame.pack(fill="x", pady=25)

        tk.Label(logo_frame, text="\u271a", font=(FONT, 28, "bold"),
                 bg=COLORS["sidebar"], fg="#818CF8").pack()
        tk.Label(logo_frame, text="SMART HEALTHCARE", font=(FONT, 13, "bold"),
                 bg=COLORS["sidebar"], fg="white").pack(pady=5)
        tk.Label(logo_frame, text="Disease Prediction System", font=(FONT, 8),
                 bg=COLORS["sidebar"], fg="#9CA3AF").pack()

        self.sidebar_button(sidebar, "\u2302   Dashboard", self.refresh_dashboard)
        self.sidebar_button(sidebar, "\U0001f6cf   Patient Details", self.open_patients)
        self.sidebar_button(sidebar, "\U0001fa7a   Symptom Prediction", self.open_prediction)
        self.sidebar_button(sidebar, "\U0001f4cb   Patient Case Records", self.open_case_records)
        self.sidebar_button(sidebar, "\U0001f9ea   Lab Reports", self.open_lab_reports)
        self.sidebar_button(sidebar, "\u23f0   Medicine Reminder", self.open_reminders)
        self.sidebar_button(sidebar, "\u25a3   Prediction History", self.open_history)
        self.sidebar_button(sidebar, "\u25a7   X-Ray Analysis", self.open_xray)

        user_area = tk.Frame(sidebar, bg="#1F2937")
        user_area.pack(side="bottom", fill="x")

        tk.Label(user_area, text=f"Logged in as\n{self.username}", font=(FONT, 9, "bold"),
                 bg="#1F2937", fg="white", justify="left").pack(padx=20, pady=(15, 10), anchor="w")

        tk.Button(
            user_area, text="Logout", font=(FONT, 9, "bold"),
            bg="#374151", fg="white", activebackground="#4B5563",
            activeforeground="white", bd=0, cursor="hand2", command=self.logout
        ).pack(fill="x", padx=15, pady=(0, 15), ipady=7)

        self.content = tk.Frame(self.root, bg=COLORS["background"])
        self.content.pack(side="right", fill="both", expand=True)

        self.refresh_dashboard()

    def sidebar_button(self, parent, text, command):
        button = tk.Button(
            parent, text=text, font=(FONT, 10, "bold"),
            bg=COLORS["sidebar"], fg="#D1D5DB",
            activebackground="#312E81", activeforeground="white",
            bd=0, cursor="hand2", anchor="w", padx=25, command=command
        )
        button.pack(fill="x", ipady=12)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def refresh_dashboard(self):
        self.clear_content()

        header = tk.Frame(self.content, bg=COLORS["background"])
        header.pack(fill="x", padx=45, pady=(30, 10))

        tk.Label(header, text=f"Good day, {self.username} \U0001f44b", font=(FONT, 24, "bold"),
                 bg=COLORS["background"], fg=COLORS["text_dark"]).pack(anchor="w")
        tk.Label(header, text="Monitor your prediction activity from one place.",
                 font=(FONT, 10), bg=COLORS["background"], fg=COLORS["text_light"]).pack(anchor="w", pady=4)

        total, average, latest, patient_count = get_user_statistics(self.user_id)

        stats_frame = tk.Frame(self.content, bg=COLORS["background"])
        stats_frame.pack(fill="x", padx=45, pady=20)

        self.create_stat_card(stats_frame, "TOTAL PREDICTIONS", str(total), "Records saved", COLORS["primary"], 0)
        self.create_stat_card(stats_frame, "AVG. CONFIDENCE", f"{average:.1f}%", "Prediction score", COLORS["success"], 1)
        self.create_stat_card(stats_frame, "LATEST RESULT", latest, "Most recent", COLORS["purple"], 2)
        self.create_stat_card(stats_frame, "PATIENTS ADDED", str(patient_count), "Total records", COLORS["orange"], 3)

        tk.Label(self.content, text="Healthcare Tools", font=(FONT, 16, "bold"),
                 bg=COLORS["background"], fg=COLORS["text_dark"]).pack(anchor="w", padx=45, pady=(10, 12))

        tools = tk.Frame(self.content, bg=COLORS["background"])
        tools.pack(fill="x", padx=45)

        tool_defs = [
            ("\U0001f6cf", "Patient Details", "Add and manage patient\nrecords for predictions.", self.open_patients, COLORS["orange"]),
            ("\U0001fa7a", "Symptom Prediction", "Predict conditions for\nHuman, Animal or Plant.", self.open_prediction, COLORS["primary"]),
            ("\U0001f4cb", "Patient Case Records", "Browse every patient with\ntheir symptoms and results.", self.open_case_records, COLORS["blue"]),
            ("\U0001f9ea", "Lab Reports", "Upload and review\nlab report files.", self.open_lab_reports, COLORS["teal"]),
            ("\u23f0", "Medicine Reminder", "Set reminders for\nmedicine schedules.", self.open_reminders, COLORS["blue"]),
            ("\u25a3", "Prediction History", "Review saved symptoms,\nresults and scores.", self.open_history, COLORS["success"]),
            ("\u25a7", "X-Ray Analysis", "Upload an X-Ray image\n(CNN phase pending).", self.open_xray, COLORS["purple"]),
        ]

        for index, (icon, title, desc, command, accent) in enumerate(tool_defs):
            self.create_tool_card(tools, icon, title, desc, command, accent, index // 3, index % 3)

        disclaimer = tk.Frame(self.content, bg=COLORS["warning_light"], padx=20, pady=15)
        disclaimer.pack(fill="x", padx=45, pady=25)

        tk.Label(disclaimer, text="\u26a0  Educational Use Only", font=(FONT, 10, "bold"),
                 bg=COLORS["warning_light"], fg=COLORS["warning"]).pack(anchor="w")
        tk.Label(
            disclaimer,
            text=("This student project provides educational predictions only and should not be used "
                  "as a substitute for professional medical, veterinary or agricultural advice."),
            font=(FONT, 9), bg=COLORS["warning_light"], fg="#92400E", wraplength=900, justify="left"
        ).pack(anchor="w", pady=(5, 0))

    def create_stat_card(self, parent, title, value, subtitle, accent, column):
        card = tk.Frame(parent, bg=COLORS["white"], height=110)
        card.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 10, 0))
        parent.grid_columnconfigure(column, weight=1)
        card.grid_propagate(False)

        tk.Frame(card, bg=accent, width=5).pack(side="left", fill="y")
        inner = tk.Frame(card, bg="white")
        inner.pack(fill="both", expand=True, padx=16, pady=14)

        tk.Label(inner, text=title, font=(FONT, 8, "bold"), bg="white", fg=COLORS["text_light"]).pack(anchor="w")
        tk.Label(inner, text=value, font=(FONT, 17, "bold"), bg="white", fg=COLORS["text_dark"]).pack(anchor="w", pady=3)
        tk.Label(inner, text=subtitle, font=(FONT, 8), bg="white", fg=COLORS["text_light"]).pack(anchor="w")

    def create_tool_card(self, parent, icon, title, description, command, accent, row, column):
        card = tk.Frame(parent, bg=COLORS["white"], width=270, height=175)
        card.grid(row=row, column=column, sticky="nsew", padx=(0 if column == 0 else 10, 0), pady=(0 if row == 0 else 12, 0))
        card.grid_propagate(False)
        parent.grid_columnconfigure(column, weight=1)

        icon_frame = tk.Frame(card, bg=COLORS["primary_light"], width=48, height=48)
        icon_frame.pack(anchor="w", padx=20, pady=(18, 8))
        icon_frame.pack_propagate(False)

        tk.Label(icon_frame, text=icon, font=(FONT, 18), bg=COLORS["primary_light"], fg=accent).place(
            relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text=title, font=(FONT, 12, "bold"), bg="white", fg=COLORS["text_dark"]).pack(anchor="w", padx=20)
        tk.Label(card, text=description, font=(FONT, 8), bg="white", fg=COLORS["text_light"], justify="left").pack(
            anchor="w", padx=20, pady=4)

        tk.Button(
            card, text="Open Module  \u2192", font=(FONT, 9, "bold"), bg="white", fg=accent,
            activebackground="white", activeforeground=accent, bd=0, cursor="hand2", command=command
        ).pack(anchor="w", padx=17, pady=4)

    def open_patients(self):
        PatientWindow(self.root, self.user_id)

    def open_prediction(self):
        PredictionWindow(self.root, self.user_id)

    def open_case_records(self):
        PatientRecordsWindow(self.root, self.user_id)

    def open_lab_reports(self):
        LabReportWindow(self.root, self.user_id)

    def open_reminders(self):
        ReminderWindow(self.root, self.user_id)

    def open_history(self):
        HistoryWindow(self.root, self.user_id)

    def open_xray(self):
        XRayWindow(self.root, self.user_id)

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            login_root = tk.Tk()
            LoginWindow(login_root)
            login_root.mainloop()




class PatientWindow:

    def __init__(self, parent, user_id):
        self.user_id = user_id
        self.window = tk.Toplevel(parent)
        self.window.title("Patient Details")
        self.window.geometry("950x650")
        self.window.configure(bg=COLORS["background"])
        self.create_ui()

    def create_ui(self):
        header = tk.Frame(self.window, bg=COLORS["orange"], height=100)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="Patient Details", font=(FONT, 20, "bold"),
                 bg=COLORS["orange"], fg="white").pack(pady=(20, 2))
        tk.Label(header, text="Add and review patient records", font=(FONT, 9),
                 bg=COLORS["orange"], fg=COLORS["orange_light"]).pack()

        body = tk.Frame(self.window, bg=COLORS["background"])
        body.pack(fill="both", expand=True, padx=25, pady=20)

        form = tk.Frame(body, bg="white", padx=25, pady=20)
        form.pack(fill="x")

        row1 = tk.Frame(form, bg="white")
        row1.pack(fill="x", pady=6)

        col1 = tk.Frame(row1, bg="white")
        col1.pack(side="left", fill="x", expand=True, padx=(0, 10))
        field_label(col1, "Full Name")
        self.name_entry = styled_entry(col1)
        self.name_entry.pack(fill="x", ipady=6)

        col2 = tk.Frame(row1, bg="white", width=120)
        col2.pack(side="left", padx=(0, 10))
        field_label(col2, "Age")
        self.age_entry = styled_entry(col2)
        self.age_entry.pack(fill="x", ipady=6)

        col3 = tk.Frame(row1, bg="white", width=150)
        col3.pack(side="left")
        field_label(col3, "Gender")
        self.gender_box = ttk.Combobox(col3, values=["Male", "Female", "Other"], state="readonly", font=(FONT, 10))
        self.gender_box.pack(fill="x", ipady=4)

        row2 = tk.Frame(form, bg="white")
        row2.pack(fill="x", pady=6)

        col4 = tk.Frame(row2, bg="white")
        col4.pack(side="left", fill="x", expand=True, padx=(0, 10))
        field_label(col4, "Contact Number")
        self.contact_entry = styled_entry(col4)
        self.contact_entry.pack(fill="x", ipady=6)

        col5 = tk.Frame(row2, bg="white")
        col5.pack(side="left", fill="x", expand=True)
        field_label(col5, "Address")
        self.address_entry = styled_entry(col5)
        self.address_entry.pack(fill="x", ipady=6)

        create_button(form, "ADD PATIENT", self.add_patient, bg=COLORS["orange"], width=25, height=2).pack(pady=(15, 0))

        # TABLE
        table_card = tk.Frame(body, bg="white")
        table_card.pack(fill="both", expand=True, pady=(20, 0))

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("Treeview", background="white", foreground=COLORS["text"], rowheight=32, fieldbackground="white", font=(FONT, 9))
        style.configure("Treeview.Heading", background=COLORS["orange"], foreground="white", font=(FONT, 9, "bold"), padding=8)

        columns = ("ID", "Name", "Age", "Gender", "Contact", "Address")
        self.table = ttk.Treeview(table_card, columns=columns, show="headings")

        widths = {"ID": 50, "Name": 180, "Age": 60, "Gender": 90, "Contact": 130, "Address": 260}
        for c in columns:
            self.table.heading(c, text=c.upper())
            self.table.column(c, width=widths[c], anchor="center" if c in ("ID", "Age", "Gender") else "w")

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        self.load_patients()

    def add_patient(self):
        name = self.name_entry.get().strip()
        age = self.age_entry.get().strip()
        gender = self.gender_box.get()
        contact = self.contact_entry.get().strip()
        address = self.address_entry.get().strip()

        if not name:
            messagebox.showwarning("Missing Information", "Patient name is required.")
            return

        if age and not age.isdigit():
            messagebox.showwarning("Invalid Age", "Age must be a number.")
            return

        if add_patient(self.user_id, name, int(age) if age else None, gender, contact, address):
            messagebox.showinfo("Patient Added", f"{name} has been added successfully.")
            self.name_entry.delete(0, tk.END)
            self.age_entry.delete(0, tk.END)
            self.gender_box.set("")
            self.contact_entry.delete(0, tk.END)
            self.address_entry.delete(0, tk.END)
            self.load_patients()

    def load_patients(self):
        for item in self.table.get_children():
            self.table.delete(item)

        for record in get_patients(self.user_id):
            pid, name, age, gender, contact, address, _ = record
            self.table.insert("", "end", values=(pid, name, age if age else "-", gender or "-", contact or "-", address or "-"))

        zebra_stripe(self.table)



class PredictionWindow:

    def __init__(self, parent, user_id):
        self.user_id = user_id
        self.category = tk.StringVar(value="Human")
        self.checkbox_vars = {}
        self.last_result = None

        self.window = tk.Toplevel(parent)
        self.window.title("Symptom Prediction")
        self.window.geometry("950x780")
        self.window.configure(bg=COLORS["background"])

        self.create_ui()

    def create_ui(self):
        header = tk.Frame(self.window, bg=COLORS["primary"], height=100)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="Symptom Based Prediction", font=(FONT, 20, "bold"),
                 bg=COLORS["primary"], fg="white").pack(pady=(18, 2))
        tk.Label(header, text="Choose a category, select a patient, then select symptoms",
                 font=(FONT, 9), bg=COLORS["primary"], fg="#E0E7FF").pack()

        main = tk.Frame(self.window, bg=COLORS["white"])
        main.pack(fill="both", expand=True, padx=30, pady=20)

        top_row = tk.Frame(main, bg="white")
        top_row.pack(fill="x", padx=25, pady=(20, 5))

        cat_frame = tk.Frame(top_row, bg="white")
        cat_frame.pack(side="left")

        tk.Label(cat_frame, text="Category:", font=(FONT, 10, "bold"), bg="white", fg=COLORS["text"]).pack(side="left", padx=(0, 10))

        for value, label in [("Human", "\U0001f9d1 Human"), ("Animal", "\U0001f43e Animal"), ("Plant", "\U0001f331 Plant")]:
            tk.Radiobutton(
                cat_frame, text=label, variable=self.category, value=value,
                font=(FONT, 10), bg="white", activebackground="white",
                selectcolor=COLORS["primary_light"], command=self.build_symptom_grid
            ).pack(side="left", padx=8)

        patient_frame = tk.Frame(top_row, bg="white")
        patient_frame.pack(side="right")

        tk.Label(patient_frame, text="Patient / Subject:", font=(FONT, 10, "bold"), bg="white", fg=COLORS["text"]).pack(side="left", padx=(0, 8))
        self.patient_box = ttk.Combobox(patient_frame, state="readonly", width=28, font=(FONT, 9))
        self.patient_box.pack(side="left")
        self.load_patient_options()

        tk.Label(main, text="Select all symptoms that apply.", font=(FONT, 9),
                 bg="white", fg=COLORS["text_light"]).pack(anchor="w", padx=25, pady=(10, 0))

        self.symptom_frame = tk.Frame(main, bg="white")
        self.symptom_frame.pack(fill="x", padx=25, pady=15)

        self.build_symptom_grid()

        self.live_frame = tk.Frame(
            main, bg=COLORS["background"],
            highlightbackground=COLORS["border"], highlightthickness=1,
            padx=20, pady=12
        )
        self.live_frame.pack(fill="x", padx=25, pady=(0, 15))

        tk.Label(
            self.live_frame, text="\u26a1 Live Assessment  \u2022  updates automatically as you select symptoms",
            font=(FONT, 8, "bold"), bg=COLORS["background"], fg=COLORS["text_light"]
        ).pack(anchor="w")

        self.live_result_label = tk.Label(
            self.live_frame, text="Select symptoms to see a live prediction preview.",
            font=(FONT, 12, "bold"), bg=COLORS["background"], fg=COLORS["text_dark"]
        )
        self.live_result_label.pack(anchor="w", pady=(4, 0))

        create_button(main, "CONFIRM & SAVE PREDICTION", self.predict, width=28, height=2).pack(pady=(0, 15))

        self.result_frame = tk.Frame(main, bg=COLORS["primary_light"], padx=25, pady=18)
        self.result_frame.pack(fill="x", padx=25, pady=(0, 10))

        tk.Label(self.result_frame, text="\u2713 Confirmed & Saved Result", font=(FONT, 10, "bold"),
                 bg=COLORS["primary_light"], fg=COLORS["primary"]).pack(anchor="w")

        self.result_label = tk.Label(self.result_frame, text="No prediction yet", font=(FONT, 15, "bold"),
                                      bg=COLORS["primary_light"], fg=COLORS["text_dark"], justify="left")
        self.result_label.pack(anchor="w", pady=5)

        self.warning_label = tk.Label(self.result_frame, text="", font=(FONT, 8),
                                       bg=COLORS["primary_light"], fg=COLORS["text_light"], wraplength=850, justify="left")
        self.warning_label.pack(anchor="w")

        # Suggested Medicine + Suggest Hospital
        bottom_row = tk.Frame(main, bg="white")
        bottom_row.pack(fill="x", padx=25, pady=(5, 20))

        med_card = tk.Frame(bottom_row, bg=COLORS["success_light"], padx=18, pady=14)
        med_card.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(med_card, text="\U0001f48a  Suggested Medicine", font=(FONT, 10, "bold"),
                 bg=COLORS["success_light"], fg=COLORS["success"]).pack(anchor="w")
        self.medicine_label = tk.Label(med_card, text="-", font=(FONT, 9), bg=COLORS["success_light"],
                                        fg=COLORS["text"], wraplength=380, justify="left")
        self.medicine_label.pack(anchor="w", pady=(6, 0))

        hosp_card = tk.Frame(bottom_row, bg=COLORS["teal_light"], padx=18, pady=14)
        hosp_card.pack(side="left", fill="both", expand=True, padx=(8, 0))

        tk.Label(hosp_card, text="\U0001f3e5  Suggested Hospital / Facility", font=(FONT, 10, "bold"),
                 bg=COLORS["teal_light"], fg=COLORS["teal"]).pack(anchor="w")
        self.hospital_label = tk.Label(hosp_card, text="-", font=(FONT, 9), bg=COLORS["teal_light"],
                                        fg=COLORS["text"], wraplength=380, justify="left")
        self.hospital_label.pack(anchor="w", pady=(6, 0))

    def load_patient_options(self):
        patients = get_patients(self.user_id)
        self.patient_lookup = {"General / Quick Check (no patient)": None}
        for pid, name, *_rest in patients:
            self.patient_lookup[f"{name}  (ID {pid})"] = pid

        values = list(self.patient_lookup.keys())
        self.patient_box["values"] = values
        self.patient_box.set(values[0])

    def build_symptom_grid(self):
        for widget in self.symptom_frame.winfo_children():
            widget.destroy()

        self.checkbox_vars = {}
        symptoms = CATEGORY_SYMPTOMS[self.category.get()]

        for index, symptom in enumerate(symptoms):
            variable = tk.BooleanVar()
            self.checkbox_vars[symptom] = variable
            variable.trace_add("write", lambda *args: self.update_live_preview())

            tk.Checkbutton(
                self.symptom_frame, text=symptom, variable=variable, font=(FONT, 9),
                bg="white", activebackground="white", selectcolor=COLORS["primary_light"],
                anchor="w", cursor="hand2"
            ).grid(row=index // 3, column=index % 3, padx=15, pady=6, sticky="w")

        if hasattr(self, "live_result_label"):
            self.live_result_label.config(
                text="Select symptoms to see a live prediction preview.",
                fg=COLORS["text_dark"]
            )

    def update_live_preview(self):
        selected = [s for s, v in self.checkbox_vars.items() if v.get()]

        if not selected:
            self.live_result_label.config(
                text="Select symptoms to see a live prediction preview.",
                fg=COLORS["text_dark"]
            )
            return

        disease, confidence = predict_disease(self.category.get(), selected)

        if confidence >= 85:
            color = COLORS["success"]
        elif confidence >= 70:
            color = COLORS["warning"]
        else:
            color = COLORS["danger"]

        self.live_result_label.config(
            text=f"{disease}  \u2022  {confidence:.0f}% confidence (live preview, not yet saved)",
            fg=color
        )

    def predict(self):
        selected = [s for s, v in self.checkbox_vars.items() if v.get()]

        if not selected:
            messagebox.showwarning("No Symptoms Selected", "Please select at least one symptom.")
            return

        category = self.category.get()
        disease, confidence = predict_disease(category, selected)

        self.result_label.config(text=f"Category: {category}   |   Possible Condition: {disease}\nPrediction Confidence: {confidence:.1f}%")

        self.warning_label.config(
            text=("Educational prediction only. The result is generated using the project's rule-based "
                  "engine and is not a professional diagnosis. Please consult a qualified professional.")
        )

        self.medicine_label.config(text=get_medicine_suggestion(disease))

        hospitals = get_hospital_suggestions(category)
        if hospitals:
            hosp_text = "\n".join(f"\u2022 {name} - {specialty} ({contact})" for name, specialty, contact in hospitals)
        else:
            hosp_text = "No facility data available for this category."
        self.hospital_label.config(text=hosp_text)

        patient_id = self.patient_lookup.get(self.patient_box.get())

        saved = save_prediction(self.user_id, patient_id, category, ", ".join(selected), disease, confidence)

        if saved:
            messagebox.showinfo("Prediction Saved", "Prediction completed successfully.\n\nThe result has been saved to your history.")



class LabReportWindow:

    def __init__(self, parent, user_id):
        self.user_id = user_id
        self.selected_file = None

        self.window = tk.Toplevel(parent)
        self.window.title("Lab Reports")
        self.window.geometry("980x680")
        self.window.configure(bg=COLORS["background"])

        self.create_ui()

    def create_ui(self):
        header = tk.Frame(self.window, bg=COLORS["teal"], height=100)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="Lab Report Upload", font=(FONT, 20, "bold"),
                 bg=COLORS["teal"], fg="white").pack(pady=(18, 2))
        tk.Label(header, text="Attach a lab report to a patient record", font=(FONT, 9),
                 bg=COLORS["teal"], fg=COLORS["teal_light"]).pack()

        body = tk.Frame(self.window, bg=COLORS["background"])
        body.pack(fill="both", expand=True, padx=25, pady=20)

        form = tk.Frame(body, bg="white", padx=25, pady=20)
        form.pack(fill="x")

        row = tk.Frame(form, bg="white")
        row.pack(fill="x", pady=6)

        col1 = tk.Frame(row, bg="white")
        col1.pack(side="left", fill="x", expand=True, padx=(0, 10))
        field_label(col1, "Patient / Subject")
        self.patient_box = ttk.Combobox(col1, state="readonly", font=(FONT, 9))
        self.patient_box.pack(fill="x", ipady=4)
        self.load_patient_options()

        col2 = tk.Frame(row, bg="white")
        col2.pack(side="left", fill="x", expand=True)
        field_label(col2, "Report Name")
        self.report_name_entry = styled_entry(col2)
        self.report_name_entry.pack(fill="x", ipady=6)

        field_label(form, "Notes")
        self.notes_entry = styled_entry(form)
        self.notes_entry.pack(fill="x", ipady=6, pady=(6, 10))

        upload_row = tk.Frame(form, bg="white")
        upload_row.pack(fill="x", pady=(5, 0))

        self.file_label = tk.Label(upload_row, text="No file selected", font=(FONT, 9), bg="white", fg=COLORS["text_light"])
        self.file_label.pack(side="left", padx=(0, 15))

        create_button(upload_row, "BROWSE FILE", self.select_file, bg=COLORS["teal"], width=16).pack(side="left")
        create_button(upload_row, "UPLOAD REPORT", self.upload_report, bg=COLORS["success"], width=18).pack(side="left", padx=10)

        # TABLE
        table_card = tk.Frame(body, bg="white")
        table_card.pack(fill="both", expand=True, pady=(20, 0))

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("Treeview", background="white", foreground=COLORS["text"], rowheight=32, fieldbackground="white", font=(FONT, 9))
        style.configure("Treeview.Heading", background=COLORS["teal"], foreground="white", font=(FONT, 9, "bold"), padding=8)

        columns = ("ID", "Patient", "Report Name", "Notes", "Uploaded")
        self.table = ttk.Treeview(table_card, columns=columns, show="headings")

        widths = {"ID": 50, "Patient": 150, "Report Name": 180, "Notes": 250, "Uploaded": 150}
        for c in columns:
            self.table.heading(c, text=c.upper())
            self.table.column(c, width=widths[c], anchor="center" if c == "ID" else "w")

        self.table.bind("<Double-1>", self.open_selected_report)

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        self.records = []
        self.load_reports()

    def load_patient_options(self):
        patients = get_patients(self.user_id)
        self.patient_lookup = {"General (no patient)": None}
        for pid, name, *_rest in patients:
            self.patient_lookup[f"{name}  (ID {pid})"] = pid

        values = list(self.patient_lookup.keys())
        self.patient_box["values"] = values
        self.patient_box.set(values[0])

    def select_file(self):
        path = filedialog.askopenfilename(
            title="Select Lab Report",
            filetypes=[("Documents", "*.pdf *.jpg *.jpeg *.png"), ("All Files", "*.*")]
        )
        if path:
            self.selected_file = path
            self.file_label.config(text=os.path.basename(path), fg=COLORS["teal"])

    def upload_report(self):
        report_name = self.report_name_entry.get().strip()
        notes = self.notes_entry.get().strip()
        patient_id = self.patient_lookup.get(self.patient_box.get())

        if not report_name:
            messagebox.showwarning("Missing Information", "Please enter a report name.")
            return

        if not self.selected_file:
            messagebox.showwarning("No File", "Please select a report file to upload.")
            return

        try:
            os.makedirs(LAB_REPORTS_DIR, exist_ok=True)
            filename = f"{self.user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.path.basename(self.selected_file)}"
            destination = os.path.join(LAB_REPORTS_DIR, filename)
            shutil.copy(self.selected_file, destination)
        except Exception as e:
            messagebox.showerror("File Error", f"Could not save the file: {e}")
            return

        if save_lab_report(self.user_id, patient_id, report_name, destination, notes):
            messagebox.showinfo("Report Uploaded", "Lab report saved successfully.")
            self.report_name_entry.delete(0, tk.END)
            self.notes_entry.delete(0, tk.END)
            self.selected_file = None
            self.file_label.config(text="No file selected", fg=COLORS["text_light"])
            self.load_reports()

    def load_reports(self):
        for item in self.table.get_children():
            self.table.delete(item)

        self.records = get_lab_reports(self.user_id)

        for record in self.records:
            rid, patient_name, report_name, file_path, notes, uploaded_at = record
            date_text = uploaded_at.strftime("%d-%m-%Y %I:%M %p") if hasattr(uploaded_at, "strftime") else uploaded_at
            self.table.insert("", "end", iid=str(rid), values=(rid, patient_name, report_name, notes or "-", date_text))

        zebra_stripe(self.table)

    def open_selected_report(self, event):
        selection = self.table.selection()
        if not selection:
            return

        rid = int(selection[0])
        for record in self.records:
            if record[0] == rid:
                file_path = record[3]
                if os.path.exists(file_path):
                    try:
                        os.startfile(file_path)
                    except AttributeError:
                        messagebox.showinfo("File Location", f"Report saved at:\n{file_path}")
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not open file: {e}")
                else:
                    messagebox.showwarning("File Missing", "The report file could not be found on disk.")
                break



class ReminderWindow:

    def __init__(self, parent, user_id):
        self.user_id = user_id
        self.fired_today = set()

        self.window = tk.Toplevel(parent)
        self.window.title("Medicine Reminder")
        self.window.geometry("900x650")
        self.window.configure(bg=COLORS["background"])

        self.create_ui()
        self.check_reminders()

    def create_ui(self):
        header = tk.Frame(self.window, bg=COLORS["blue"], height=100)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="Medicine Reminder", font=(FONT, 20, "bold"),
                 bg=COLORS["blue"], fg="white").pack(pady=(18, 2))
        tk.Label(header, text="Schedule reminders so medicines are never missed", font=(FONT, 9),
                 bg=COLORS["blue"], fg=COLORS["blue_light"]).pack()

        body = tk.Frame(self.window, bg=COLORS["background"])
        body.pack(fill="both", expand=True, padx=25, pady=20)

        form = tk.Frame(body, bg="white", padx=25, pady=20)
        form.pack(fill="x")

        row = tk.Frame(form, bg="white")
        row.pack(fill="x", pady=6)

        col1 = tk.Frame(row, bg="white")
        col1.pack(side="left", fill="x", expand=True, padx=(0, 10))
        field_label(col1, "Medicine Name")
        self.medicine_entry = styled_entry(col1)
        self.medicine_entry.pack(fill="x", ipady=6)

        col2 = tk.Frame(row, bg="white")
        col2.pack(side="left", fill="x", expand=True, padx=(0, 10))
        field_label(col2, "Dosage")
        self.dosage_entry = styled_entry(col2)
        self.dosage_entry.pack(fill="x", ipady=6)

        col3 = tk.Frame(row, bg="white", width=110)
        col3.pack(side="left", padx=(0, 10))
        field_label(col3, "Time (HH:MM)")
        self.time_entry = styled_entry(col3)
        self.time_entry.pack(fill="x", ipady=6)

        col4 = tk.Frame(row, bg="white", width=120)
        col4.pack(side="left")
        field_label(col4, "Frequency")
        self.frequency_box = ttk.Combobox(col4, values=["Daily", "Once"], state="readonly", font=(FONT, 9))
        self.frequency_box.set("Daily")
        self.frequency_box.pack(fill="x", ipady=4)

        create_button(form, "ADD REMINDER", self.add_new_reminder, bg=COLORS["blue"], width=25, height=2).pack(pady=(15, 0))

        tk.Label(
            body,
            text="Note: reminders trigger only while this window stays open (checked every 30 seconds), "
                 "since this is a desktop demo without background/OS notifications.",
            font=(FONT, 8), bg=COLORS["background"], fg=COLORS["text_light"], wraplength=880, justify="left"
        ).pack(anchor="w", pady=(10, 0))

        table_card = tk.Frame(body, bg="white")
        table_card.pack(fill="both", expand=True, pady=(15, 0))

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("Treeview", background="white", foreground=COLORS["text"], rowheight=32, fieldbackground="white", font=(FONT, 9))
        style.configure("Treeview.Heading", background=COLORS["blue"], foreground="white", font=(FONT, 9, "bold"), padding=8)

        columns = ("ID", "Medicine", "Dosage", "Time", "Frequency")
        self.table = ttk.Treeview(table_card, columns=columns, show="headings")

        widths = {"ID": 50, "Medicine": 220, "Dosage": 150, "Time": 100, "Frequency": 120}
        for c in columns:
            self.table.heading(c, text=c.upper())
            self.table.column(c, width=widths[c], anchor="center" if c in ("ID", "Time", "Frequency") else "w")

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        create_button(body, "DELETE SELECTED", self.delete_selected, bg=COLORS["danger"], width=20).pack(pady=(10, 0), anchor="e")

        self.load_reminders()

    def add_new_reminder(self):
        medicine_name = self.medicine_entry.get().strip()
        dosage = self.dosage_entry.get().strip()
        reminder_time = self.time_entry.get().strip()
        frequency = self.frequency_box.get()

        if not medicine_name or not reminder_time:
            messagebox.showwarning("Missing Information", "Medicine name and time are required.")
            return

        try:
            datetime.strptime(reminder_time, "%H:%M")
        except ValueError:
            messagebox.showwarning("Invalid Time", "Please enter time in 24-hour HH:MM format, e.g. 09:30.")
            return

        if add_reminder(self.user_id, medicine_name, dosage, reminder_time, frequency):
            messagebox.showinfo("Reminder Added", "Medicine reminder has been scheduled.")
            self.medicine_entry.delete(0, tk.END)
            self.dosage_entry.delete(0, tk.END)
            self.time_entry.delete(0, tk.END)
            self.load_reminders()

    def load_reminders(self):
        for item in self.table.get_children():
            self.table.delete(item)

        for record in get_reminders(self.user_id):
            rid, medicine_name, dosage, reminder_time, frequency, _is_active = record
            self.table.insert("", "end", iid=str(rid), values=(rid, medicine_name, dosage or "-", reminder_time, frequency))

        zebra_stripe(self.table)

    def delete_selected(self):
        selection = self.table.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a reminder to delete.")
            return

        if messagebox.askyesno("Delete Reminder", "Remove this reminder?"):
            delete_reminder(int(selection[0]))
            self.load_reminders()

    def check_reminders(self):
        current_time = datetime.now().strftime("%H:%M")

        for record in get_reminders(self.user_id):
            rid, medicine_name, dosage, reminder_time, frequency, is_active = record
            key = (rid, current_time)

            if reminder_time == current_time and key not in self.fired_today:
                self.fired_today.add(key)
                messagebox.showinfo(
                    "\u23f0 Medicine Reminder",
                    f"It's time to take:\n\n{medicine_name} ({dosage or 'as prescribed'})"
                )

        if self.window.winfo_exists():
            self.window.after(30000, self.check_reminders)


class HistoryWindow:

    def __init__(self, parent, user_id):
        self.user_id = user_id
        self.window = tk.Toplevel(parent)
        self.window.title("Prediction History")
        self.window.geometry("1050x600")
        self.window.configure(bg=COLORS["background"])
        self.create_ui()

    def create_ui(self):
        header = tk.Frame(self.window, bg=COLORS["background"])
        header.pack(fill="x", padx=40, pady=(30, 10))

        tk.Label(header, text="Prediction History", font=(FONT, 23, "bold"),
                 bg=COLORS["background"], fg=COLORS["text_dark"]).pack(anchor="w")
        tk.Label(header, text="Previously saved symptom prediction records", font=(FONT, 9),
                 bg=COLORS["background"], fg=COLORS["text_light"]).pack(anchor="w", pady=4)

        card = tk.Frame(self.window, bg="white")
        card.pack(fill="both", expand=True, padx=40, pady=20)

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("Treeview", background="white", foreground=COLORS["text"], rowheight=36, fieldbackground="white", font=(FONT, 9))
        style.configure("Treeview.Heading", background=COLORS["primary"], foreground="white", font=(FONT, 9, "bold"), padding=10)
        style.map("Treeview", background=[("selected", COLORS["primary_light"])], foreground=[("selected", COLORS["primary"])])

        columns = ("ID", "Patient", "Category", "Symptoms", "Disease", "Confidence", "Date")
        self.table = ttk.Treeview(card, columns=columns, show="headings")

        widths = {"ID": 45, "Patient": 130, "Category": 80, "Symptoms": 280, "Disease": 200, "Confidence": 90, "Date": 150}
        for c in columns:
            self.table.heading(c, text=c.upper())
            self.table.column(c, width=widths[c], anchor="center" if c in ("ID", "Category", "Confidence") else "w")

        scrollbar = ttk.Scrollbar(card, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=15)
        scrollbar.pack(side="right", fill="y", padx=(0, 15), pady=15)

        self.load_records()

    def load_records(self):
        for item in self.table.get_children():
            self.table.delete(item)

        for record in get_prediction_history(self.user_id):
            pred_id, patient_name, category, symptoms, disease, confidence, date = record
            date_text = date.strftime("%d-%m-%Y %I:%M %p") if hasattr(date, "strftime") else date
            self.table.insert("", "end", values=(pred_id, patient_name, category, symptoms, disease, f"{confidence:.1f}%", date_text))

        zebra_stripe(self.table)



class PatientRecordsWindow:

    def __init__(self, parent, user_id):
        self.user_id = user_id
        self.window = tk.Toplevel(parent)
        self.window.title("Patient Case Records")
        self.window.geometry("1100x680")
        self.window.configure(bg=COLORS["background"])
        self.create_ui()

    def create_ui(self):
        header = tk.Frame(self.window, bg=COLORS["sidebar"], height=100)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="Patient Case Records", font=(FONT, 20, "bold"),
                 bg=COLORS["sidebar"], fg="white").pack(pady=(18, 2))
        tk.Label(
            header,
            text="A consolidated view of every patient with their symptoms and predictions grouped together",
            font=(FONT, 9), bg=COLORS["sidebar"], fg="#9CA3AF"
        ).pack()

        body = tk.Frame(self.window, bg=COLORS["background"])
        body.pack(fill="both", expand=True, padx=25, pady=20)

        toolbar = tk.Frame(body, bg="white", padx=15, pady=12)
        toolbar.pack(fill="x")

        tk.Label(toolbar, text="\U0001f50d  Search Patient:", font=(FONT, 10, "bold"),
                 bg="white", fg=COLORS["text"]).pack(side="left", padx=(0, 10))

        self.search_entry = styled_entry(toolbar)
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_records())

        create_button(toolbar, "REFRESH", self.load_records, bg=COLORS["sidebar"], width=12).pack(side="left", padx=(10, 0))

        legend = tk.Frame(body, bg=COLORS["background"])
        legend.pack(fill="x", pady=(12, 5))

        for label, color in [
            ("High confidence (\u226585%)", COLORS["success"]),
            ("Moderate (70-84%)", COLORS["warning"]),
            ("Low (<70%)", COLORS["danger"]),
        ]:
            tk.Label(legend, text="\u25cf", font=(FONT, 10), bg=COLORS["background"], fg=color).pack(side="left", padx=(0, 4))
            tk.Label(legend, text=label, font=(FONT, 8), bg=COLORS["background"], fg=COLORS["text_light"]).pack(side="left", padx=(0, 18))

        table_card = tk.Frame(body, bg="white")
        table_card.pack(fill="both", expand=True, pady=(5, 0))

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("Records.Treeview", background="white", foreground=COLORS["text"],
                         rowheight=34, fieldbackground="white", font=(FONT, 9))
        style.configure("Records.Treeview.Heading", background=COLORS["sidebar"],
                         foreground="white", font=(FONT, 9, "bold"), padding=8)

        columns = ("Category", "Symptoms", "Prediction", "Confidence", "Date")
        self.table = ttk.Treeview(table_card, columns=columns, show="tree headings", style="Records.Treeview")

        self.table.heading("#0", text="PATIENT")
        self.table.column("#0", width=230, anchor="w")

        widths = {"Category": 90, "Symptoms": 250, "Prediction": 190, "Confidence": 100, "Date": 150}
        for c in columns:
            self.table.heading(c, text=c.upper())
            self.table.column(c, width=widths[c], anchor="w" if c in ("Symptoms", "Prediction") else "center")

        self.table.tag_configure("high", background=COLORS["success_light"])
        self.table.tag_configure("moderate", background=COLORS["warning_light"])
        self.table.tag_configure("low", background=COLORS["danger_light"])
        self.table.tag_configure("empty", background="white", foreground=COLORS["text_light"])
        self.table.tag_configure("patient_row", background=COLORS["primary_light"])

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        self.load_records()

    def load_records(self):
        for item in self.table.get_children():
            self.table.delete(item)

        search_term = self.search_entry.get().strip().lower()
        rows = get_patient_case_records(self.user_id)

        grouped = {}
        order = []

        for row in rows:
            pid, name, age, gender, contact, category, symptoms, disease, confidence, date = row

            if pid not in grouped:
                grouped[pid] = {"info": (name, age, gender, contact), "entries": []}
                order.append(pid)

            if disease is not None:
                grouped[pid]["entries"].append((category, symptoms, disease, confidence, date))

        for pid in order:
            name, age, gender, contact = grouped[pid]["info"]

            if search_term and search_term not in name.lower():
                continue

            detail_bits = []
            if age:
                detail_bits.append(f"{age} yrs")
            if gender:
                detail_bits.append(gender)
            if contact:
                detail_bits.append(contact)
            subtitle = "  \u2022  ".join(detail_bits) if detail_bits else "No contact details on file"

            parent = self.table.insert(
                "", "end", text=f"\U0001f9cd  {name}",
                values=("", subtitle, "", "", ""),
                tags=("patient_row",), open=True
            )

            entries = grouped[pid]["entries"]

            if not entries:
                self.table.insert(
                    parent, "end", text="",
                    values=("-", "No predictions recorded yet", "-", "-", "-"),
                    tags=("empty",)
                )
                continue

            for category, symptoms, disease, confidence, date in entries:
                if confidence >= 85:
                    tag = "high"
                elif confidence >= 70:
                    tag = "moderate"
                else:
                    tag = "low"

                date_text = date.strftime("%d-%m-%Y %I:%M %p") if hasattr(date, "strftime") else date

                self.table.insert(
                    parent, "end", text="",
                    values=(category, symptoms, disease, f"{confidence:.1f}%", date_text),
                    tags=(tag,)
                )




class XRayWindow:

    def __init__(self, parent, user_id):
        self.user_id = user_id
        self.image_path = None

        self.window = tk.Toplevel(parent)
        self.window.title("X-Ray Analysis")
        self.window.geometry("850x600")
        self.window.resizable(False, False)
        self.window.configure(bg=COLORS["background"])

        self.create_ui()

    def create_ui(self):
        header = tk.Frame(self.window, bg=COLORS["purple"], height=110)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="X-Ray Analysis", font=(FONT, 22, "bold"),
                 bg=COLORS["purple"], fg="white").pack(pady=(22, 3))
        tk.Label(header, text="Medical image analysis module", font=(FONT, 9),
                 bg=COLORS["purple"], fg="#EDE9FE").pack()

        main = tk.Frame(self.window, bg="white")
        main.pack(fill="both", expand=True, padx=45, pady=30)

        tk.Label(main, text="Upload X-Ray Image", font=(FONT, 16, "bold"),
                 bg="white", fg=COLORS["text_dark"]).pack(pady=(30, 5))
        tk.Label(main, text="Select a JPG, JPEG or PNG X-Ray image from your computer.",
                 font=(FONT, 9), bg="white", fg=COLORS["text_light"]).pack()

        upload_area = tk.Frame(main, bg=COLORS["purple_light"], height=130)
        upload_area.pack(fill="x", padx=60, pady=25)
        upload_area.pack_propagate(False)

        tk.Label(upload_area, text="\u25a7", font=(FONT, 30), bg=COLORS["purple_light"], fg=COLORS["purple"]).pack(pady=(15, 2))

        self.file_label = tk.Label(upload_area, text="No image selected", font=(FONT, 9, "bold"),
                                    bg=COLORS["purple_light"], fg=COLORS["text_light"])
        self.file_label.pack()

        buttons = tk.Frame(main, bg="white")
        buttons.pack()

        create_button(buttons, "SELECT X-RAY", self.select_image, bg=COLORS["purple"], width=18, height=2).grid(row=0, column=0, padx=10)
        create_button(buttons, "ANALYZE IMAGE", self.analyze, bg=COLORS["success"], width=18, height=2).grid(row=0, column=1, padx=10)

        self.result = tk.Label(main, text="", font=(FONT, 11, "bold"), bg="white", fg=COLORS["text"], wraplength=650, justify="center")
        self.result.pack(pady=25)

        tk.Label(
            main,
            text=("Note: The current student version provides the X-Ray upload interface only. "
                  "A trained CNN model can be connected to this module in a future phase. "
                  "No medical diagnosis is generated here."),
            font=(FONT, 8), bg="white", fg=COLORS["text_light"], wraplength=680, justify="center"
        ).pack(pady=5)

    def select_image(self):
        path = filedialog.askopenfilename(
            title="Select X-Ray Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png"), ("All Files", "*.*")]
        )
        if path:
            self.image_path = path
            self.file_label.config(text=os.path.basename(path), fg=COLORS["purple"])
            self.result.config(text="")

    def analyze(self):
        if not self.image_path:
            messagebox.showwarning("No Image", "Please select an X-Ray image first.")
            return

        
        image_array = cv2.imread(self.image_path)

        if image_array is None:
            messagebox.showerror("Image Error", "Could not read the selected image file.")
            return

        image_resized = cv2.resize(image_array, (224, 224))

        self.result.config(
            text=("\u2713 X-Ray image uploaded and preprocessed successfully.\n\n"
                  "Image is ready for AI model processing.\n\n"
                  "CNN model integration can be added as the next development phase."),
            fg=COLORS["success"]
        )


if __name__ == "__main__":
    root = tk.Tk()
    database_ready = setup_database()

    if database_ready:
        LoginWindow(root)
        root.mainloop()