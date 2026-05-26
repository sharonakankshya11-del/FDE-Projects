"""
evaluation/evaluator.py
Step 8 — Evaluation Framework

Integrates DeepEval for standardised LLM output evaluation.
Falls back to a lightweight custom evaluator if DeepEval is unavailable.

Metrics:
  • Faithfulness
  • Answer Relevancy
  • Hallucination (via ContextualRelevancy)
  • Custom confidence score
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DeepEval integration (optional — graceful fallback if not installed)
# ---------------------------------------------------------------------------

def run_deepeval(
    query: str,
    response: str,
    context: str,
) -> Dict[str, float]:
    """
    Run DeepEval metrics on a single response.
    Returns a dict of metric_name → score (0.0–1.0).
    """
    try:
        from deepeval import evaluate
        from deepeval.test_case import LLMTestCase
        from deepeval.metrics import (
            FaithfulnessMetric,
            AnswerRelevancyMetric,
            ContextualRelevancyMetric,
        )

        test_case = LLMTestCase(
            input=query,
            actual_output=response,
            retrieval_context=[context],
        )

        metrics = [
            FaithfulnessMetric(threshold=0.7, model="gpt-4o-mini"),
            AnswerRelevancyMetric(threshold=0.7, model="gpt-4o-mini"),
            ContextualRelevancyMetric(threshold=0.7, model="gpt-4o-mini"),
        ]

        results = evaluate([test_case], metrics)

        scores = {}
        for metric in metrics:
            name = metric.__class__.__name__.replace("Metric", "").lower()
            scores[name] = getattr(metric, "score", 0.0)

        logger.info("DeepEval scores: %s", scores)
        return scores

    except ImportError:
        logger.warning("DeepEval not installed — using fallback evaluator")
        return _fallback_evaluator(query, response, context)
    except Exception as exc:
        logger.error("DeepEval error: %s — using fallback", exc)
        return _fallback_evaluator(query, response, context)


# ---------------------------------------------------------------------------
# Lightweight fallback evaluator (no extra API calls)
# ---------------------------------------------------------------------------

def _fallback_evaluator(
    query: str, response: str, context: str
) -> Dict[str, float]:
    """
    Simple heuristic-based evaluation when DeepEval is unavailable.
    """
    scores = {}

    # Relevancy: does response contain query keywords?
    query_words = set(query.lower().split())
    response_words = set(response.lower().split())
    overlap = len(query_words & response_words)
    scores["answerrelevancy"] = min(overlap / max(len(query_words), 1), 1.0)

    # Faithfulness: fraction of response words in context
    context_words = set(context.lower().split())
    common = len(response_words & context_words)
    scores["faithfulness"] = min(common / max(len(response_words), 1), 1.0)

    # Contextual relevancy: fraction of context keywords in response
    if context_words:
        ctx_in_resp = len(context_words & response_words)
        scores["contextualrelevancy"] = min(ctx_in_resp / max(len(context_words), 1), 1.0)
    else:
        scores["contextualrelevancy"] = 0.5   # neutral when no context

    return scores


# ---------------------------------------------------------------------------
# Pass/Fail decision
# ---------------------------------------------------------------------------

THRESHOLDS = {
    "faithfulness": 0.6,
    "answerrelevancy": 0.6,
    "contextualrelevancy": 0.5,
}


def evaluate_response(
    query: str,
    response: str,
    context: str,
) -> Dict:
    """
    Run evaluation and return a structured result dict.
    """
    scores = run_deepeval(query, response, context)

    pass_fail = {
        name: score >= THRESHOLDS.get(name, 0.6)
        for name, score in scores.items()
    }

    overall_pass = all(pass_fail.values())
    avg_score = sum(scores.values()) / len(scores) if scores else 0.0

    result = {
        "scores": scores,
        "pass_fail": pass_fail,
        "overall_pass": overall_pass,
        "average_score": round(avg_score, 3),
    }

    logger.info(
        "Evaluation complete | Overall=%s | Avg=%.3f",
        "PASS" if overall_pass else "FAIL",
        avg_score,
    )
    return result
