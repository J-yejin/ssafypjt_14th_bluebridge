from datetime import datetime

def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y%m%d").date()
    except:
        return None

def to_list(*values):
    return [v for v in values if v]

# 복지로 API
def parse_welfare_policy(item):
    return {
        "source": "welfare",
        "source_id": item.get("servId"),
        "title": item.get("servNm"),
        "summary": item.get("servDgst"),
        "detail_link": item.get("servDtlLink"),
        "region_sido": item.get("ctpvNm"),
        "region_sigungu": item.get("sggNm"),
        "special_target": to_list(item.get("trgterIndvdlNmArray")),
        "provider": item.get("bizChrDeptNm"),
        "apply_method": item.get("aplyMtdNm"),
        "start_date": parse_date(item.get("enfcBgngYmd")),
        "end_date": parse_date(item.get("enfcEndYmd")),
        "status": "ACTIVE",
        "raw": item,
    }
