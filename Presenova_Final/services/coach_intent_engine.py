"""
Interactive AI Coach Intent Engine (Local TF-IDF + LogisticRegression + State Machine)

Replaces external LLM API calls for Dr. Alexander Vance coaching with a local
intent classification model and a finite-state conversation engine.
"""

import logging
import sys
import os
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

# Intent Training Dataset (Expanded ~100 diverse samples across 6 intent classes)
TRAINING_DATA = [
    # greeting
    ("hello dr vance", "greeting"),
    ("hi there", "greeting"),
    ("good morning", "greeting"),
    ("good afternoon", "greeting"),
    ("good evening", "greeting"),
    ("hey coach", "greeting"),
    ("ready to start practice", "greeting"),
    ("let's begin the rehearsal", "greeting"),
    ("start session", "greeting"),
    ("hello", "greeting"),
    ("hi coach", "greeting"),
    ("hey dr vance let's practice", "greeting"),
    ("starting my defense practice now", "greeting"),
    ("can we start our rehearsal?", "greeting"),
    ("greetings professor", "greeting"),
    ("hi i am ready for evaluation", "greeting"),
    ("welcome back", "greeting"),
    ("let's do a run through", "greeting"),
    ("ready when you are", "greeting"),

    # slide_feedback
    ("how do my slides look?", "slide_feedback"),
    ("is my text density too high?", "slide_feedback"),
    ("check my slide layout", "slide_feedback"),
    ("did I follow the 6x6 rule?", "slide_feedback"),
    ("are my bullet points concise?", "slide_feedback"),
    ("review my presentation design", "slide_feedback"),
    ("slide feedback please", "slide_feedback"),
    ("are my slides readable?", "slide_feedback"),
    ("are there too many words on my slides?", "slide_feedback"),
    ("is my font too small to read?", "slide_feedback"),
    ("critique my color scheme", "slide_feedback"),
    ("is my presentation visually balanced?", "slide_feedback"),
    ("how many slides should I have?", "slide_feedback"),
    ("can you analyze my slide visual hierarchy?", "slide_feedback"),
    ("are these graphics distracting?", "slide_feedback"),
    ("evaluate my presentation visuals", "slide_feedback"),
    ("do I have too much content per slide?", "slide_feedback"),
    ("is the typography legible?", "slide_feedback"),
    ("slide aesthetics critique", "slide_feedback"),
    ("check document structure and slide clarity", "slide_feedback"),

    # pacing_question
    ("am I speaking too fast?", "pacing_question"),
    ("what is my current words per minute?", "pacing_question"),
    ("is my speech pace optimal?", "pacing_question"),
    ("how is my speaking speed?", "pacing_question"),
    ("wpm feedback", "pacing_question"),
    ("am I rushing through slides?", "pacing_question"),
    ("speech tempo check", "pacing_question"),
    ("am I talking too slowly?", "pacing_question"),
    ("how was my rhythm and cadence?", "pacing_question"),
    ("is my delivery too fast for the audience?", "pacing_question"),
    ("check my speaking rate", "pacing_question"),
    ("did I spend enough time on each slide?", "pacing_question"),
    ("am I dragging or droning on?", "pacing_question"),
    ("how is my speech cadence?", "pacing_question"),
    ("evaluate my speech timing", "pacing_question"),
    ("am I speaking at 130 to 150 words per minute?", "pacing_question"),
    ("pacing critique please", "pacing_question"),

    # viva_prep
    ("ask me a thesis defense question", "viva_prep"),
    ("prepare me for academic viva", "viva_prep"),
    ("grill me on my methodology", "viva_prep"),
    ("viva practice question", "viva_prep"),
    ("what will the panel ask me?", "viva_prep"),
    ("test my research defense", "viva_prep"),
    ("cross examine my conclusions", "viva_prep"),
    ("ask me a tough technical question", "viva_prep"),
    ("simulate viva panel questions", "viva_prep"),
    ("probe my system architecture", "viva_prep"),
    ("give me a challenging counter-argument", "viva_prep"),
    ("challenge my statistical results", "viva_prep"),
    ("test my conceptual depth on this project", "viva_prep"),
    ("what are the limitations of my study?", "viva_prep"),
    ("how would I defend against edge case failures?", "viva_prep"),
    ("pose an examiner question to me", "viva_prep"),

    # disfluency_query
    ("did I use too many filler words?", "disfluency_query"),
    ("how many ums and uhs did I say?", "disfluency_query"),
    ("check my verbal disfluencies", "disfluency_query"),
    ("am I using filler words?", "disfluency_query"),
    ("verbal fluency feedback", "disfluency_query"),
    ("did I say like or you know too much?", "disfluency_query"),
    ("how can I stop saying um?", "disfluency_query"),
    ("count my speech fillers", "disfluency_query"),
    ("am I repeating words frequently?", "disfluency_query"),
    ("evaluate my vocal fillers and pauses", "disfluency_query"),
    ("disfluency breakdown", "disfluency_query"),
    ("how clean was my verbal articulation?", "disfluency_query"),
    ("did I stammer or pause awkwardly?", "disfluency_query"),

    # general_help
    ("what should I work on next?", "general_help"),
    ("how can I improve overall?", "general_help"),
    ("give me general coaching advice", "general_help"),
    ("summarize my strengths and weaknesses", "general_help"),
    ("what is my overall score?", "general_help"),
    ("how do I score higher in 7Cs?", "general_help"),
    ("what are my top 3 areas of improvement?", "general_help"),
    ("give me an executive assessment of my presentation", "general_help"),
    ("recommend next practice steps", "general_help"),
    ("how ready am I for the final presentation?", "general_help"),
    ("overview of my performance", "general_help"),
    ("tips for confidence and stage presence", "general_help"),
]

_CLASSIFIER_PIPELINE = None


def _get_intent_classifier():
    global _CLASSIFIER_PIPELINE
    if _CLASSIFIER_PIPELINE is None:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.linear_model import LogisticRegression
            from sklearn.pipeline import make_pipeline

            texts, labels = zip(*TRAINING_DATA)
            pipeline = make_pipeline(
                TfidfVectorizer(ngram_range=(1, 2)),
                LogisticRegression(max_iter=1000)
            )
            pipeline.fit(texts, labels)
            _CLASSIFIER_PIPELINE = pipeline
            logger.info("[coach_intent_engine] Trained LogisticRegression intent classifier.")
        except Exception as exc:
            logger.warning("[coach_intent_engine] Could not train intent classifier: %s", exc)
            _CLASSIFIER_PIPELINE = False

    return _CLASSIFIER_PIPELINE if _CLASSIFIER_PIPELINE is not False else None


def predict_intent(user_message: str) -> str:
    """Classify user intent using TF-IDF + LogisticRegression model."""
    msg = user_message.lower().strip()
    classifier = _get_intent_classifier()
    if classifier:
        try:
            intent = classifier.predict([msg])[0]
            return str(intent)
        except Exception as exc:
            logger.warning("[coach_intent_engine] Intent prediction error: %s", exc)

    # Heuristic fallback
    if any(k in msg for k in ["hello", "hi", "hey", "start", "begin"]):
        return "greeting"
    elif any(k in msg for k in ["slide", "density", "bullet", "layout", "6x6"]):
        return "slide_feedback"
    elif any(k in msg for k in ["wpm", "speed", "pace", "pacing", "fast", "slow"]):
        return "pacing_question"
    elif any(k in msg for k in ["viva", "defense", "panel", "question", "grill"]):
        return "viva_prep"
    elif any(k in msg for k in ["um", "uh", "filler", "disfluency", "repeat"]):
        return "disfluency_query"
    else:
        return "general_help"


COACH_RESPONSES = {
    "greeting": (
        "Hello! I am Dr. Alexander Vance, your AI Presentation Coach. "
        "I am ready to help you refine your slide design, vocal delivery, WPM pacing, and academic viva defense readiness. "
        "What specific aspect of your presentation would you like to rehearse first?"
    ),
    "slide_feedback": (
        "Based on our deterministic 7Cs analysis, effective slides require scannable bullet points (max 15 words per line) "
        "and strict adherence to the 6x6 rule. Ensure your titles clearly state key takeaways rather than generic topics."
    ),
    "pacing_question": (
        "Target an optimal speaking pace of 130–150 words per minute (WPM). Speaking faster than 160 WPM causes listener fatigue, "
        "while dropping below 120 WPM can reduce audience engagement."
    ),
    "viva_prep": (
        "Here is a key viva defense question for your research: "
        "'What are the primary methodological assumptions of your study, and how did you validate your empirical baseline?' "
        "Take a moment to formulate a structured 3-part response: Problem, Methodology, and Validation Data."
    ),
    "disfluency_query": (
        "To minimize verbal disfluencies ('um', 'uh', 'like', 'you know'), embrace deliberate pauses. "
        "A 2-second silent pause sounds confident to an evaluation panel, whereas a filler word breaks authority."
    ),
    "general_help": (
        "Focus on three core pillars: (1) Slide Scannability, (2) Controlled Vocal Delivery (130-150 WPM), and "
        "(3) Defensible Empirical Evidence. Which area would you like to practice now?"
    )
}


def process_coach_chat(
    user_message: str,
    current_state: str = "INIT",
    session_context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Process coach user message using intent classification & state transitions.
    """
    from services.coach_state_machine import transition_state

    intent = predict_intent(user_message)
    response_text, next_state = transition_state(current_state, intent)

    return {
        "response": response_text,
        "intent": intent,
        "current_state": current_state,
        "next_state": next_state,
        "persona": "Dr. Alexander Vance",
        "recommendations": [
            "Maintain controlled WPM between 130-150.",
            "Use silent pauses instead of filler words.",
            "Align slide bullet points with 6x6 design rules."
        ]
    }
