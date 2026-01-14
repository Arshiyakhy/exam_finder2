# exam_finder/backend.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Allow your React dev server to call FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Schemas (API contract)
# ----------------------------


class ExamLookupRequest(BaseModel):
    courses: List[str]  # e.g. ["MATA31", "CSCA08"]


class ExamResult(BaseModel):
    course_code: str
    date: Optional[str] = None      # None if not found
    time: Optional[str] = None      # None if not found
    location: Optional[str] = None  # None if not found
    status: str                     # "FOUND" or "NOT_FOUND"


# (Optional) If you want to keep "create exam" functionality later:
class ExamCreate(BaseModel):
    course_code: str
    date: str
    time: str
    location: str


class Exam(ExamCreate):
    id: int


# ----------------------------
# Mock data (replace later)
# ----------------------------
MOCK_EXAMS = {
    "MATA31": {"date": "2026-04-22", "time": "09:00", "location": "UTSC - HL 001"},
    "PHY101": {"date": "2026-04-24", "time": "14:00", "location": "UTSC - BV 473"},
    "CHEM101": {"date": "2026-04-26", "time": "19:00", "location": "UTSC - IC 130"},
}


# ----------------------------
# Endpoints
# ----------------------------
@app.get("/")
def read_root():
    return {"message": "Welcome to the Exam Finder API"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/exams/lookup", response_model=List[ExamResult])
def lookup_exams(req: ExamLookupRequest):
    results: List[ExamResult] = []

    for raw in req.courses:
        code = raw.strip().upper()
        if not code:
            continue

        if code in MOCK_EXAMS:
            info = MOCK_EXAMS[code]
            results.append(
                ExamResult(
                    course_code=code,
                    date=info["date"],
                    time=info["time"],
                    location=info["location"],
                    status="FOUND",
                )
            )
        else:
            results.append(
                ExamResult(
                    course_code=code,
                    status="NOT_FOUND",
                )
            )

    return results


# ----------------------------
# Optional CRUD (keep/remove)
# ----------------------------
FAKE_DB: List[Exam] = [
    Exam(id=1, course_code="MATA31", date="2026-04-22",
         time="09:00", location="UTSC - HL 001"),
    Exam(id=2, course_code="PHY101", date="2026-04-24",
         time="14:00", location="UTSC - BV 473"),
]


@app.get("/exams", response_model=List[Exam])
def get_exams():
    return FAKE_DB


@app.post("/exams", response_model=Exam)
def create_exam(exam: ExamCreate):
    new_id = (FAKE_DB[-1].id + 1) if FAKE_DB else 1
    created = Exam(id=new_id, **exam.model_dump())
    FAKE_DB.append(created)
    return created
