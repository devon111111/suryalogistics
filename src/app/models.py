from pydantic import BaseModel
from datetime import date

class ContactForm(BaseModel):
    phone: str
    pickup_location: str
    drop_location: str | None = None  # Make drop_location optional
    shifting_date: date

