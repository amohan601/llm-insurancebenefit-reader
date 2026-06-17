from app.services.vectorstore import load_vectorstore,get_retriever
from app.services.llm import get_llm
from app.core.config import Config
from collections import defaultdict



def rerank(docs, question):
    print('inside rerank')
    q_words = set(question.lower().split())

    scored = []
    for d in docs:
        score = len(q_words & set(d.page_content.lower().split()))
        scored.append((d, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [d[0] for d in scored[:4]]


# def format_docs(docs):
#     print('inside format_docs')
#     return "\n\n".join([
#         f"[PAGE {d.metadata.get('page')} | {d.metadata.get('file_name')}]\n{d.page_content}"
#         for d in docs
#     ])


def format_docs(docs):
    grouped = defaultdict(list)
    for doc in docs:
        provider = doc.metadata.get("provider", "Unknown")
        grouped[provider].append(doc)
    context = ""
    for provider, items in grouped.items():
        context += f"\n\n### {provider} Policy\n"
        for d in items:
            context += f"""
            [Page {d.metadata.get('page')}]
            {d.page_content}
            """
    print(f'context {context}')
    return context

def ask_question(question: str, doc_id: str | None = None):

    print(f'inside ask_question {question}, doc_id {doc_id}')
    vs = load_vectorstore()
    print(f'calling get_retriever')
    retriever = get_retriever(vs,Config.TOP_K)
    print(f'calling retriever.invoke')
    docs = retriever.invoke(question)
    print(f'docs {len(docs)}')

    if not docs:
        print(f'answer not found for {doc_id}')
        return {"answer": "Not found", "sources": []}

    #alternative to filter out based on document
    #Chroma-based filtered retrieval (production-grade) tbd
    if doc_id:
        docs = [
            d for d in docs
            if d.metadata.get("doc_id") == doc_id
        ]

    print(f'calling rerank')
    docs = rerank(docs, question)
    print(f'docs after rerank {len(docs)}')

    # ----------------------------
    # Extract provider
    # ----------------------------
    provider = "Unknown"

    if docs:
        providers = set(
            d.metadata.get("provider", "Unknown")
            for d in docs
        )

        if len(providers) == 1:
            provider = list(providers)[0]
        else:
            provider = "Multiple"

    print(f'calling format_docs')
    context = format_docs(docs)

    prompt = """
    You are an insurance policy assistant.

    Answer ONLY using the provided context.
    If the answer is not in the context, say "This information is not clearly specified in the provided document."
    Be precise and structured.
    Always cite the section if available using section name and page number.
    Context:
    {context}

    Question:
    {question}

    Answer:
    """

    print('create prompts')
    formatted_prompt = prompt.format(
        context=context,
        question=question
    )

    print('invoke llm with question and context')

    llm = get_llm()
    response = llm.invoke(formatted_prompt)
    print(f'answer: {response.content}, provider : {provider}')
    return {
        "answer": response.content,
        "provider": provider,
        "file_name": docs[0].metadata.get("file_name"),
        "sources": [
            {
                "file": "http://127.0.0.1:8000/data/raw_pdfs/"+d.metadata.get("file_name"),
                "page": d.metadata.get("page"),
                "text": d.page_content[:250]
            }
            for d in docs
        ]
    }

