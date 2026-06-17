from app.services.rag_ask_question import ask_question
from app.services.rag_comparison import compare_question
from app.services.llm import get_llm



# ---------------------------------
# RULE-BASED DETECTION (FAST)
# ---------------------------------
def rule_based_intent(q: str):
    print('rule_based_intent')
    q = q.lower()

    keywords = ["compare", "difference", "vs", "versus", "better", "cheaper"]

    if any(k in q for k in keywords):
        return "comparison"

    # heuristic: multiple entities
    if " and " in q:
        return "comparison"

    return "unknown"


# ---------------------------------
# LLM-BASED DETECTION (FALLBACK)
# ---------------------------------
def llm_intent(q: str):
    print('llm_intent')
    prompt = f"""
    Classify the user question into one of the following categories:
    - comparison
    - single

    Question: "{q}"

    Only return one word: comparison or single.
    """

    try:
        llm = get_llm()
        res = llm.invoke(prompt)
        intent = res.content.strip().lower()

        if "comparison" in intent:
            return "comparison"
        return "single"

    except Exception:
        return "single"  # safe fallback


# ---------------------------------
# FINAL ROUTER
# ---------------------------------
def route_question(question: str, doc_id=None, doc_ids=None):

    # Step 1: rule-based
    intent = rule_based_intent(question)

    # Step 2: fallback to LLM if unsure
    if intent == "unknown":
        intent = llm_intent(question)

    print(f"Detected intent: {intent}")
    # ---------------------------------
    # ROUTING LOGIC
    # ---------------------------------
    if intent == "comparison" or (doc_ids != None and len(doc_ids)  > 1 ):
        if not doc_ids or len(doc_ids) < 2:
            return {
                "answer": "Please select at least two documents for comparison.",
                "sources": []
            }

        return compare_question(question, doc_ids)

    # default → single QA
    return ask_question(question, doc_id)