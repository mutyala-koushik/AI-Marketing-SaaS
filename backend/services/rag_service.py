import math
import re
from typing import List, Dict, Any

class LightweightRAG:
    """
    A lightweight, embedded semantic retrieval engine using Cosine Similarity.
    Zero external C++ binary dependencies required.
    """
    def __init__(self):
        self.documents = [
            {
                "id": "pol_month_to_month_contract",
                "friction": "Contract",
                "text": (
                    "Authorized Policy for Month-to-Month Contract friction: To stabilize short-term "
                    "contract churn risk, authorize an immediate migration to a 1-year agreement with a "
                    "locked-in $15/month account credit, waived transition fees, and 6 months of complimentary "
                    "dedicated priority technical support."
                )
            },
            {
                "id": "pol_high_monthly_charges",
                "friction": "MonthlyCharges",
                "text": (
                    "Authorized Policy for High Monthly Charges friction: For accounts flagged with bill "
                    "sensitivity exceeding baseline rates, authorize a recurring loyalty discount of $15/month "
                    "tied to paperless autopay enrollment, plus an immediate $20 one-time billing statement credit."
                )
            },
            {
                "id": "pol_low_tenure_early_churn",
                "friction": "tenure",
                "text": (
                    "Authorized Policy for Low Tenure / Early Drop-off friction: For customers with tenure under "
                    "6 months, authorize a complimentary 1-on-1 customer onboarding audit, priority account "
                    "management, and an introductory 15% discount on the next billing cycle."
                )
            },
            {
                "id": "pol_tech_support_deficit",
                "friction": "TechSupport",
                "text": (
                    "Authorized Policy for Tech Support Deficit: When lack of technical assistance is a churn driver, "
                    "authorize an instant 12-month zero-cost upgrade to 24/7 Dedicated Priority Technical Support "
                    "with direct VIP helpline escalation."
                )
            }
        ]

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\w+', text.lower())

    def _vectorize(self, tokens: List[str], vocabulary: List[str]) -> List[int]:
        return [tokens.count(word) for word in vocabulary]

    def _cosine_similarity(self, vec_a: List[int], vec_b: List[int]) -> float:
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        mag_a = math.sqrt(sum(a * a for a in vec_a))
        mag_b = math.sqrt(sum(b * b for b in vec_b))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot_product / (mag_a * mag_b)

    def retrieve_policy(self, query: str, top_k: int = 1) -> str:
        query_tokens = self._tokenize(query)
        scored_docs = []

        for doc in self.documents:
            doc_tokens = self._tokenize(doc["text"] + " " + doc["friction"])
            vocab = list(set(query_tokens + doc_tokens))
            
            vec_q = self._vectorize(query_tokens, vocab)
            vec_d = self._vectorize(doc_tokens, vocab)
            
            sim = self._cosine_similarity(vec_q, vec_d)
            scored_docs.append((sim, doc["text"]))

        # Sort descending by similarity
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        top_matches = [doc_text for _, doc_text in scored_docs[:top_k]]
        return "\n\n".join(top_matches)

# Singleton instance
rag_engine = LightweightRAG()

def retrieve_policy_context(query: str) -> str:
    return rag_engine.retrieve_policy(query)