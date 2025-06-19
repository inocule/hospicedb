# FILENAME 3: constants.py

# UI Constants
WINDOW_SIZE = "1540x800"
TITLE = "CAREBASE: PATIENT SUMMARY AND MEDICATION"

# Font and Style configurations
FONTS = {
    "title": ("CENTURY GOTHIC", 50, "bold"),
    "header": ("Calibri", 30, "bold"),
    "normal": ("CENTURY GOTHIC", 18)
}

# Button configurations with their colors
BUTTONS = {
    "Insert Masterlist Data": "#2E8B57",
    "Add Disease": "#4B0082",
    "Update": "#4169E1",
    "Delete": "#CD5C5C",
    "Clear": "#DAA520",
    "Execute SQL Query": "#228B22"
}

# Database mappings
MAPPINGS = {
    "civil_status": {
        "Single": "S", "Married": "M", "Engaged": "E",
        "Civil Union": "CU", "Widow(er)": "W",
        "Lives Alone": "LA", "Separated": "SP"
    },
    "education": {
        "None": "N", "Preschool": "P", "Grade School": "GS",
        "Junior High School": "JHS", "Senior High School": "SHS",
        "Undergraduate": "UG", "Masters": "MA", "Doctorate": "DR"
    }
}

# Database table structures
TABLE_STRUCTURES = {
    "Credential": [
        "patientNumber", "patientName", "birthDate", "civilStatus",
        "occupation", "religion", "education", "illnessCode",
        "diseaseName", "detectionDate", "medicinesTaken", "surgeryHistory",
        "surgeryDate", "contact", "emergencyPhone", "relationship"
    ],
    "Patient_Profile": [
        "patientNumber", "patientName", "birthDate", "civilStatus",
        "occupation", "religion", "education", "contact",
        "emergencyPhone", "relationship"
    ],
    "Medical_History": [
        "patientNumber", "illnessCode",
        "detectionDate", "medicinesTaken"
    ],
    "Surgery_History": [
        "surgeryID", "patientNumber", "surgeryHistory", "surgeryDate"
    ],
    "Disease_Masterlist": [
        "diseaseName", "illnessCode"
    ]
}

# Theme styles for Treeview
TREEVIEW_DARK = {
    "background": "#2a2d2e",
    "foreground": "white",
    "fieldbackground": "#2a2d2e",
    "rowheight": 25,
    "font": ("CENTURY GOTHIC", 10)
}

TREEVIEW_LIGHT = {
    "background": "white",
    "foreground": "black",
    "fieldbackground": "white",
    "rowheight": 25,
    "font": ("CENTURY GOTHIC", 10)
}

# Theme configurations
THEME_CONFIG = {
    "Dark": {
        "treeview": TREEVIEW_DARK,
        "appearance_mode": "dark"
    },
    "Light": {
        "treeview": TREEVIEW_LIGHT,
        "appearance_mode": "light"
    }
}