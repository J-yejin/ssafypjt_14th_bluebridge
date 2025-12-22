import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import json

# ==========================================================
# 기본 설정
# ==========================================================
API_KEY = "d5984d49-751d-47c4-8607-75737cf1ce54"
BASE_URL = "https://www.youthcenter.go.kr/go/ythip/getPlcy"

PAGE_SIZE = 10
MAX_WORKERS = 40
RETRY = 3
TIMEOUT = 7

# ==========================================================
# 한글 컬럼 매핑 (공식 스펙 기준)
# ==========================================================
FIELD_MAP = {
    "plcyNo": "정책번호",
    "bscPlanCycl": "기본계획차수",
    "bscPlanPlcyWayNo": "기본계획정책방향번호",
    "bscPlanFcsAsmtNo": "기본계획중점과제번호",
    "bscPlanAsmtNo": "기본계획과제번호",
    "pvsnInstGroupCd": "제공기관그룹코드",
    "plcyPvsnMthdCd": "정책제공방법코드",
    "plcyAprvSttsCd": "정책승인상태코드",
    "plcyNm": "정책명",
    "plcyKywdNm": "정책키워드명",
    "plcyExplnCn": "정책설명내용",
    "lclsfNm": "정책대분류명",
    "mclsfNm": "정책중분류명",
    "plcySprtCn": "정책지원내용",
    "sprvsnInstCd": "주관기관코드",
    "sprvsnInstCdNm": "주관기관코드명",
    "sprvsnInstPicNm": "주관기관담당자명",
    "operInstCd": "운영기관코드",
    "operInstCdNm": "운영기관코드명",
    "operInstPicNm": "운영기관담당자명",
    "sprtSclLmtYn": "지원규모제한여부",
    "aplyPrdSeCd": "신청기간구분코드",
    "bizPrdSeCd": "사업기간구분코드",
    "bizPrdBgngYmd": "사업기간시작일자",
    "bizPrdEndYmd": "사업기간종료일자",
    "bizPrdEtcCn": "사업기간기타내용",
    "plcyAplyMthdCn": "정책신청방법내용",
    "srngMthdCn": "심사방법내용",
    "aplyUrlAddr": "신청URL주소",
    "sbmsnDcmntCn": "제출서류내용",
    "etcMttrCn": "기타사항내용",
    "refUrlAddr1": "참고URL주소1",
    "refUrlAddr2": "참고URL주소2",
    "sprtSclCnt": "지원규모수",
    "sprtArvlSeqYn": "지원도착순서여부",
    "sprtTrgtMinAge": "지원대상최소연령",
    "sprtTrgtMaxAge": "지원대상최대연령",
    "sprtTrgtAgeLmtYn": "지원대상연령제한여부",
    "mrgSttsCd": "결혼상태코드",
    "earnCndSeCd": "소득조건구분코드",
    "earnMinAmt": "소득최소금액",
    "earnMaxAmt": "소득최대금액",
    "earnEtcCn": "소득기타내용",
    "addAplyQlfcCndCn": "추가신청자격조건내용",
    "ptcpPrpTrgtCn": "참여제외대상내용",
    "inqCnt": "조회수",
    "rgtrInstCd": "등록자기관코드",
    "rgtrInstCdNm": "등록자기관코드명",
    "rgtrUpInstCd": "등록자상위기관코드",
    "rgtrUpInstCdNm": "등록자상위기관코드명",
    "rgtrHghrkInstCd": "등록자최상위기관코드",
    "rgtrHghrkInstCdNm": "등록자최상위기관코드명",
    "zipCd": "정책거주지역코드",
    "plcyMajorCd": "정책전공요건코드",
    "jobCd": "정책취업요건코드",
    "schoolCd": "정책학력요건코드",
    "aplyYmd": "신청기간",
    "frstRegDt": "최초등록일시",
    "lastMdfcnDt": "최종수정일시",
    "sbizCd": "정책특화요건코드",
}

# ==========================================================
# STEP 1. 전체 페이지 수 확인
# ==========================================================
print("전체 정책 수 조회 중...")

first_res = requests.get(
    BASE_URL,
    params={
        "apiKeyNm": API_KEY,
        "pageNum": 1,
        "pageSize": PAGE_SIZE,
        "rtnType": "json",
    },
    timeout=TIMEOUT,
).json()

total = first_res["result"]["pagging"]["totCount"]
page_size = first_res["result"]["pagging"]["pageSize"]
total_pages = (total + page_size - 1) // page_size

print(f"총 정책 수: {total}")
print(f"총 페이지 수: {total_pages}")

# ==========================================================
# STEP 2. 페이지 단위 수집 함수
# ==========================================================
def fetch_page(page: int):
    params = {
        "apiKeyNm": API_KEY,
        "pageNum": page,
        "pageSize": PAGE_SIZE,
        "rtnType": "json",
    }

    for attempt in range(RETRY):
        try:
            res = requests.get(BASE_URL, params=params, timeout=TIMEOUT)
            res.raise_for_status()
            return res.json()["result"]["youthPolicyList"]
        except Exception:
            print(f"[페이지 {page}] 실패 → 재시도 {attempt + 1}/{RETRY}")
            time.sleep(1)

    print(f"[페이지 {page}] 최종 실패 (스킵)")
    return []

# ==========================================================
# STEP 3. 병렬 수집
# ==========================================================
print("\n정책 병렬 수집 시작...")

all_raw = []

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(fetch_page, p) for p in range(1, total_pages + 1)]
    for future in as_completed(futures):
        all_raw.extend(future.result())

print(f"수집된 정책 수: {len(all_raw)}")

# ==========================================================
# STEP 4. 중복 제거 (정책번호 기준)
# ==========================================================
unique = {}
for p in all_raw:
    unique[p["plcyNo"]] = p

all_raw = list(unique.values())
print(f"중복 제거 후 정책 수: {len(all_raw)}")

# ==========================================================
# STEP 5. RAW + KOR 구조 생성
# ==========================================================
final_data = []

for policy in all_raw:
    kor = {kor_name: policy.get(eng_key) for eng_key, kor_name in FIELD_MAP.items()}
    final_data.append(kor)

# ==========================================================
# STEP 6. JSON 저장
# ==========================================================
with open("all_policies_full.json", "w", encoding="utf-8") as f:
    json.dump(final_data, f, ensure_ascii=False, indent=2)

print("\n✅ 전국 청년정책 FULL JSON 생성 완료")
print("파일명: all_policies_full.json")
