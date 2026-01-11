from enum import StrEnum


class VitalType(StrEnum):
    HR = "HR"  # Heart Rate
    RR = "RR"  # Respiratory Rate
    SBP = "SBP"  # Systolic Blood Pressure
    DBP = "DBP"  # Diastolic Blood Pressure
    SPO2 = "SpO2"  # Oxygen Saturation
    BT = "BT"  # Body Temperature
