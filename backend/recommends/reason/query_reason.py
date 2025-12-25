def build_query_reason(policy, query: str) -> str:
    # policy dict 또는 객체 모두 지원
    summary = ""
    title = ""
    if isinstance(policy, dict):
        summary = policy.get("summary") or policy.get("search_summary") or ""
        title = policy.get("title") or ""
    else:
        summary = getattr(policy, "summary", "") or getattr(policy, "search_summary", "") or ""
        title = getattr(policy, "title", "") or ""
    preview = summary[:80] + ("..." if len(summary) > 80 else "")
    region = ""
    if isinstance(policy, dict):
        region = policy.get("region_sido") or policy.get("region_scope") or ""
    else:
        region = getattr(policy, "region_sido", "") or getattr(policy, "region_scope", "")
    region_txt = f" ({region})" if region else ""
    return f"'{query}'와 관련된 정책입니다: {title}{region_txt}. {preview}"
