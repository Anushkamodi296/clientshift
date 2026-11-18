import re
from typing import List, Dict, Set, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.knowledge.catalog import RuleCatalog, MigrationRule
from app.db.models import RuleMatch

class RuleRetriever:
    def __init__(self, catalog: RuleCatalog):
        self.catalog = catalog
        self.rules = self.catalog.get_all_rules()
        self.vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b|[.\(\)\_=]")
        self._corpus = []
        self._rule_ids = []
        self._build_index()

    def _build_index(self):
        self._corpus = []
        self._rule_ids = []
        for r in self.rules:
            # Combine text representation of rule for indexing
            doc = (
                f"{r.id} {r.name} {r.category} {r.description} "
                f"{r.v1_pattern} {r.v2_pattern} {r.code_example_before} "
                f"{r.code_example_after} {r.fix_strategy} "
                f"{' '.join(str(v) for v in r.ast_match_criteria.values())}"
            )
            self._corpus.append(doc)
            self._rule_ids.append(r.id)

        if self._corpus:
            self._tfidf_matrix = self.vectorizer.fit_transform(self._corpus)
        else:
            self._tfidf_matrix = None

    def retrieve(
        self,
        code: str,
        ast_detected_rule_ids: Optional[List[str]] = None,
        top_k: int = 5,
        threshold: float = 0.05
    ) -> List[RuleMatch]:
        ast_ids_set: Set[str] = set(ast_detected_rule_ids or [])
        matches_dict: Dict[str, RuleMatch] = {}

        # 1. AST Detected rules get primary rank
        for rule_id in ast_ids_set:
            rule = self.catalog.get_rule(rule_id)
            if rule:
                matches_dict[rule_id] = RuleMatch(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    category=rule.category,
                    severity=rule.severity,
                    score=0.98,  # Grounded AST match
                    description=rule.description
                )

        # 2. Semantic TF-IDF matching on code snippet
        if self._tfidf_matrix is not None and code.strip():
            try:
                query_vec = self.vectorizer.transform([code])
                similarities = cosine_similarity(query_vec, self._tfidf_matrix).flatten()
                
                for idx, score in enumerate(similarities):
                    rule_id = self._rule_ids[idx]
                    rule = self.catalog.get_rule(rule_id)
                    if not rule:
                        continue
                    
                    if rule_id in matches_dict:
                        # Bump existing AST score slightly with TF-IDF similarity
                        existing = matches_dict[rule_id]
                        blended = min(1.0, 0.9 + (float(score) * 0.1))
                        existing.score = round(blended, 4)
                    elif score >= threshold:
                        matches_dict[rule_id] = RuleMatch(
                            rule_id=rule.id,
                            rule_name=rule.name,
                            category=rule.category,
                            severity=rule.severity,
                            score=round(float(score), 4),
                            description=rule.description
                        )
            except Exception:
                pass

        # Sort matches by score descending
        sorted_matches = sorted(matches_dict.values(), key=lambda m: m.score, reverse=True)
        return sorted_matches[:top_k]
