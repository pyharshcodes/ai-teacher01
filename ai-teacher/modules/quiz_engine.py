"""
quiz_engine.py
---------------
Small helper around the "final_assessment" block produced by llm_engine, plus
simple MCQ grading (LLM is used only for the harder short-answer grading via
llm_engine.evaluate_answer).
"""


def grade_mcq(question, student_choice):
    correct = question.get("correct_answer", "").strip().lower()
    given = (student_choice or "").strip().lower()
    return correct != "" and correct == given
