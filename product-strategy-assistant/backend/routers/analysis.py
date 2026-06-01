from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import io
import csv
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from agents.orchestrator import run_full_analysis

router = APIRouter()


@router.post("/upload")
async def upload_and_analyze(
    data_file: UploadFile = File(...),
    reviews_file: UploadFile = File(None),
):
    """Accept uploaded files and run the full multi-agent analysis pipeline."""
    try:
        raw_data = (await data_file.read()).decode("utf-8", errors="ignore")
        raw_reviews = ""
        if reviews_file:
            raw_reviews = (await reviews_file.read()).decode("utf-8", errors="ignore")

        # Extract reviews column from CSV if no separate reviews file
        if not raw_reviews and data_file.filename.endswith(".csv"):
            reader = csv.DictReader(io.StringIO(raw_data))
            reviews = []
            for row in reader:
                for key in row:
                    if "review" in key.lower() or "feedback" in key.lower() or "comment" in key.lower():
                        if row[key].strip():
                            reviews.append(row[key].strip())
            raw_reviews = "\n".join(reviews[:200])

        results = run_full_analysis(raw_data, raw_reviews)
        return JSONResponse(content=results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text")
async def analyze_text(payload: dict):
    """Analyze raw text data directly."""
    raw_data = payload.get("data", "")
    raw_reviews = payload.get("reviews", "")
    if not raw_data:
        raise HTTPException(status_code=400, detail="No data provided")
    results = run_full_analysis(raw_data, raw_reviews)
    return JSONResponse(content=results)
