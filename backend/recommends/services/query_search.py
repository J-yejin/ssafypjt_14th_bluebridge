from django.db.models import Q

from policies.models import Policy


def search_candidates_from_db(query: str, terms=None, limit: int = 50):
    """
    텍스트 검색 기반 후보 확보 (여러 terms를 OR 매칭).
    """
    search_terms = [query] if query else []
    if terms:
        for t in terms:
            if t:
                search_terms.append(t)

    if not search_terms:
        return Policy.objects.filter(status="ACTIVE")[:limit]

    base_q = Q()
    for t in search_terms:
        base_q |= Q(search_summary__icontains=t) | Q(title__icontains=t) | Q(category__icontains=t)

    return Policy.objects.filter(base_q, status="ACTIVE")[:limit]
