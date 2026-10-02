from pathlib import Path
from datetime import datetime
import pandas as pd

from database import get_attendance_by_date

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"


def export_attendance(date_string=None):
    date_string = date_string or datetime.now().strftime("%Y-%m-%d")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    rows = get_attendance_by_date(date_string)
    data = [dict(row) for row in rows]

    columns = [
        "student_id", "roll_number", "name",
        "date", "time", "status"
    ]
    df = pd.DataFrame(data, columns=columns)

    csv_path = REPORTS_DIR / f"attendance_{date_string}.csv"
    xlsx_path = REPORTS_DIR / f"attendance_{date_string}.xlsx"

    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False, engine="openpyxl")

    return csv_path, xlsx_path
