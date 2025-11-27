from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional, Dict, ClassVar


class PatientServiceRow(BaseModel):
    full_name: Optional[str] = None
    birthday: Optional[date] = None
    age: Optional[int] = None
    address: Optional[str] = None
    insurance_company: Optional[str] = None
    polis_number: Optional[str] = None
    card_number: Optional[str] = None

    start_date: Optional[date] = None
    end_date: Optional[date] = None
    outcome_result: Optional[str] = None
    bed_days: Optional[int] = None

    department: Optional[str] = None
    department_profile: Optional[str] = None
    diag_code: Optional[str] = None
    diag_name: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_position: Optional[str] = None

    service_code: Optional[str] = None
    service_name: Optional[str] = None
    service_quantity: Optional[int] = None
    service_date: Optional[date] = None

    service_payment_source: Optional[str] = None

    # КАРТА СООТВЕТСТВИЯ
    _COLUMN_MAP: ClassVar[Dict[str, int]] = {
        "full_name": 1,
        "birthday": 2,
        "age": 3,
        "address": 4,
        "insurance_company": 5,
        "polis_number": 6,
        "card_number": 7,
        "start_date": 9,
        "end_date": 10,
        "outcome_result": 11,
        "bed_days": 12,
        "department": 18,
        "department_profile": 19,
        "diag_code": 20,
        "diag_name": 21,
        "doctor_name": 22,
        "doctor_position": 23,
        "service_code": 24,
        "service_name": 25,
        "service_quantity": 26,
        "service_date": 27,
    }

    @field_validator('*', mode='before')
    def clean_strings(cls, v): # noqa
        """Очищает строки и превращает пустые/пробельные в None"""
        if isinstance(v, str):
            v = v.strip()
            if v == "": return None
        return v

    @field_validator('birthday', 'service_date', 'start_date', 'end_date', mode='before')
    def parse_date(cls, v): # noqa
        """Превращает 'DD.MM.YYYY' в date object. Если уже date/datetime - оставляет как есть."""
        if isinstance(v, str):
            try:
                # Если в ячейке дата текстом
                return datetime.strptime(v, "%d.%m.%Y").date()
            except ValueError:
                return None
        # Если openpyxl сам распознал дату (вернул datetime), Pydantic сам приведет её к date
        return v

    @field_validator('age', 'bed_days', 'service_quantity', mode='before')
    def parse_int(cls, v): # noqa
        if v is None:
            return None
        try:
            return int(float(v))
        except (ValueError, TypeError):
            return None

    @classmethod
    def from_row(cls, row: tuple) -> "PatientServiceRow":
        data = {}
        for field_name, col_index in cls._COLUMN_MAP.items():
            if col_index < len(row):
                data[field_name] = row[col_index]
            else:
                data[field_name] = None
        return cls(**data)