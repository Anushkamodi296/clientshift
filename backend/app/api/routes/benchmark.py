from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.evaluation.benchmark import BenchmarkRunner
from app.db.models import ExperimentSummary, BenchmarkCaseResult
from app.db.repository import Repository

router = APIRouter()
runner = BenchmarkRunner()
repo = Repository()

class RunBenchmarkRequest(BaseModel):
    experiment_id: str = "all"  # "all", "exp_a", "exp_b", "exp_c"
    limit: Optional[int] = None
    category: Optional[str] = None

@router.get("/summary", response_model=List[ExperimentSummary])
def get_benchmark_summaries():
    existing = repo.get_all_experiment_summaries()
    if existing:
        return existing
    # If no benchmark runs yet, run a fast sample of 12 cases per experiment to seed initial dataset!
    summaries = runner.run_all_experiments(limit=15)
    return summaries

@router.get("/cases")
def get_benchmark_cases(
    category: Optional[str] = None,
    limit: Optional[int] = Query(None, ge=1, le=100)
):
    cases = runner.load_cases(limit=limit, category=category)
    return cases

@router.post("/run", response_model=List[ExperimentSummary])
def trigger_benchmark(req: RunBenchmarkRequest):
    if req.experiment_id == "all":
        summaries = runner.run_all_experiments(limit=req.limit)
        return summaries
    else:
        summary = runner.run_experiment(
            experiment_id=req.experiment_id,
            limit=req.limit,
            category=req.category
        )
        return [summary]
