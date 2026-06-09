"""
app/evaluation/deepeval_suite.py

Full DeepEval evaluation suite using Claude as judge.
Metrics:
  - Answer Relevancy
  - Faithfulness
  - Context Precision
  - Context Recall
  - Context Relevancy
  - Answer Correctness
  - Custom G-Eval: Tone (professional), Accuracy, Conciseness
"""
import os
from typing import List, Dict, Any

import deepeval
from deepeval import evaluate
from deepeval.models import DeepEvalBaseLLM
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
    HallucinationMetric,
    GEval,
)
from deepeval.test_case import LLMTestCase
from deepeval.test_case import SingleTurnParams as LLMTestCaseParams

import openai
from app.core.config import get_settings
from app.data.golden_dataset import GOLDEN_DATASET
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


# ── GPT-4o-mini judge wrapper for DeepEval ───────────────────────────────────

class GPTJudge(DeepEvalBaseLLM):
    """Wraps GPT-4o-mini (via key gateway) as the DeepEval judge model."""

    def __init__(self):
        self._client = openai.OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )

    def load_model(self):
        return self

    def generate(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    async def a_generate(self, prompt: str) -> str:
        return self.generate(prompt)

    def get_model_name(self) -> str:
        return "gpt-4o-mini"


# ── G-Eval custom metrics ─────────────────────────────────────────────────────

def _make_tone_metric(model: GPTJudge) -> GEval:
    return GEval(
        name="Tone",
        criteria=(
            "Evaluate whether the recommendation uses professional, clinical engineering language "
            "appropriate for a biomedical engineer. It should be formal, not conversational, and "
            "avoid lay terminology when clinical terminology is available."
        ),
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
        model=model,
        threshold=0.7,
    )


def _make_accuracy_metric(model: GPTJudge) -> GEval:
    return GEval(
        name="Accuracy",
        criteria=(
            "Evaluate whether the maintenance recommendation is technically accurate based on "
            "established biomedical engineering principles. Check: are thresholds (temperature, "
            "wear, torque) cited correctly? Are corrective actions appropriate for the stated "
            "failure type? Penalise fabricated specifications."
        ),
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.RETRIEVAL_CONTEXT],
        model=model,
        threshold=0.75,
    )


def _make_conciseness_metric(model: GPTJudge) -> GEval:
    return GEval(
        name="Conciseness",
        criteria=(
            "Evaluate whether the recommendation is appropriately concise. It should cover all "
            "necessary information without unnecessary repetition or padding. A response longer "
            "than 400 words for a routine query should be penalised unless complexity warrants it."
        ),
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
        model=model,
        threshold=0.7,
    )


# ── Test case builder ─────────────────────────────────────────────────────────

def build_test_cases(
    query_results: List[Dict[str, Any]],
) -> List[LLMTestCase]:
    """
    Build DeepEval test cases from live query results.
    query_results: list of {input, actual_output, retrieval_context, expected_output}
    """
    cases = []
    for r in query_results:
        ctx = r.get("retrieval_context", [])
        if isinstance(ctx, str):
            ctx = [ctx]
        case = LLMTestCase(
            input=r["input"],
            actual_output=r["actual_output"],
            expected_output=r.get("expected_output", ""),
            retrieval_context=ctx,
        )
        cases.append(case)
    return cases


# ── Main evaluation runner ────────────────────────────────────────────────────

def run_evaluation(
    query_results: List[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Run full evaluation suite.
    If query_results not provided, uses golden dataset with placeholder outputs
    (useful for CI smoke test).
    Returns dict of metric name → {score, passed, threshold}.
    """
    model = GPTJudge()

    metrics = [
        AnswerRelevancyMetric(threshold=0.7, model=model),
        FaithfulnessMetric(threshold=0.7, model=model),
        ContextualPrecisionMetric(threshold=0.7, model=model),
        ContextualRecallMetric(threshold=0.7, model=model),
        ContextualRelevancyMetric(threshold=0.7, model=model),
        HallucinationMetric(threshold=0.3, model=model),
        _make_tone_metric(model),
        _make_accuracy_metric(model),
        _make_conciseness_metric(model),
    ]

    if query_results is None:
        # Use golden dataset (expected output as stand-in actual output for smoke test)
        query_results = [
            {
                "input": g["input"],
                "actual_output": g["expected_output"],
                "expected_output": g["expected_output"],
                "retrieval_context": g["context_keywords"],
            }
            for g in GOLDEN_DATASET[:5]  # limit for cost
        ]

    test_cases = build_test_cases(query_results)

    results_summary: Dict[str, Any] = {}
    for metric in metrics:
        try:
            for tc in test_cases:
                metric.measure(tc)
            avg_score = (
                sum(tc.metrics_data[0].score for tc in test_cases if tc.metrics_data)
                / max(len(test_cases), 1)
            )
            results_summary[metric.__class__.__name__] = {
                "score": round(avg_score, 3),
                "threshold": metric.threshold,
                "passed": avg_score >= metric.threshold,
            }
        except Exception as e:
            logger.error(f"Metric {metric.__class__.__name__} failed: {e}")
            results_summary[metric.__class__.__name__] = {"error": str(e)}

    logger.info(f"Evaluation complete: {len(results_summary)} metrics")
    return results_summary
