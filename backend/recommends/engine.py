from typing import Optional

from django.contrib.auth.models import User

from .profile_engine import profile_recommend
from .query_engine import query_recommend


def recommend(user: Optional[User] = None, query: Optional[str] = None):
    """
    오케스트레이터: query 유무로 추천 엔진을 분기.
    """
    if query:
        return query_recommend(query=query, user=user)
    return profile_recommend(user=user)
