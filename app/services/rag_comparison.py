from app.services.rag_ask_question import ask_question
from app.services.llm import get_llm


def compare_question(question, doc_ids):
    print('inside compare_question')
    results = {}

    for doc_id in doc_ids:
        res = ask_question(question, doc_id)

        results[doc_id] = {
            "answer": res["answer"],
            "provider": res["provider"],
            "file_name": res["file_name"]
        }

        print(f'Result for {doc_id} is {results[doc_id]}')

    # ----------------------------
    # Build structured context
    # ----------------------------
    context = ""

    for doc_id, data in results.items():
        provider = data["provider"]
        answer = data["answer"]

        context += f"""
        ### {provider}
        {answer}
        """

    # ----------------------------
    # Structured comparison prompt
    # ----------------------------
    prompt = f"""
    You are an insurance policy comparison assistant.
    
    You MUST follow these rules:
    
    1. Use ONLY the information provided in the context
    2. Separate answers by provider (Aetna, Cigna, etc.)
    3. Do NOT mix information between providers
    4. If multiple providers are present, include a Comparison section
    5. Be concise and factual
    
    Format STRICTLY as:
    
    Aetna:
    - ...
    
    Cigna:
    - ...
    
    Comparison:
    - ...
    
    Context:
    {context}
    
    Question:
    {question}
    
    Answer:
    """

    print('invoking comparison llm')
    llm = get_llm()
    response = llm.invoke(prompt)

    sources = []
    for doc_id, data in results.items():
        sources.append({
                "file": f'http://127.0.0.1:8000/data/raw_pdfs/{data["file_name"]}',
                "page": "",
                "text": data["answer"]
            })

    return {
        "answer": response.content,
        "sources": sources
    }
