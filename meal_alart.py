import re
from datetime import date

import streamlit as st

from ai_helper import ask_ai
from meal_api import fetch_meals, search_schools

ALLERGY_NAMES = {
    "1": "난류(계란)", "2": "우유", "3": "메밀", "4": "땅콩", "5": "대두",
    "6": "밀", "7": "고등어", "8": "게", "9": "새우", "10": "돼지고기",
    "11": "복숭아", "12": "토마토", "13": "아황산류", "14": "호두", "15": "닭고기",
    "16": "쇠고기", "17": "오징어", "18": "조개류", "19": "잣",
}


def explain_allergy(menu_lines):
    code_table = ", ".join(f"{k}={v}" for k, v in ALLERGY_NAMES.items())
    prompt = (
        "아래는 학교 급식 메뉴입니다. 괄호 안 숫자는 알레르기 유발 식품 번호이며, "
        f"번호 의미는 다음과 같습니다: {code_table}\n\n"
        + "\n".join(menu_lines)
        + "\n\n위 메뉴는 모두 알레르기 번호가 있는 메뉴입니다. 각 메뉴에 들어 있는 알레르기 유발 식품을 "
        "메뉴별로 짧게 설명해 주세요. 알레르기 번호가 없는 메뉴나 일반적인 주의 사항은 언급하지 마세요. 한국어로 답하세요."
    )
    return ask_ai(prompt)


def format_menu(ddish):
    lines = []
    for raw in re.split(r"<br\s*/?>|\\n|\n", ddish):
        match = re.match(r"\s*(.*?)\s*(\(.*\))?\s*$", raw)
        name = re.sub(r"^n(?=[가-힣])", "", match.group(1).strip(" ."))
        codes = match.group(2) or ""
        if name:
            lines.append(f"{name} {codes}".strip())
    return lines

st.set_page_config(page_title="학교 급식 알리미", page_icon="🍱")
st.title("🍱 학교 급식 알리미")

with st.form("school_search"):
    school_name = st.text_input("학교명", placeholder="예: 흥진초등학교")
    searched = st.form_submit_button("학교 검색")

if searched:
    if not school_name.strip():
        st.warning("학교명을 입력해주세요.")
    else:
        try:
            with st.spinner("학교를 검색하는 중..."):
                st.session_state["schools"] = search_schools(school_name.strip())
        except Exception as e:
            st.error(f"API 호출 실패: {e}")
            st.stop()

schools = st.session_state.get("schools", [])
if searched and school_name.strip() and not schools:
    st.info("검색 결과가 없습니다.")

if schools:
    school = st.selectbox(
        "학교 선택",
        schools,
        format_func=lambda s: f"{s['SCHUL_NM']} ({s['SCHUL_KND_SC_NM']}, {s['JU_ORG_NM']})",
    )
    meal_date = st.date_input("날짜", value=date.today())

    if st.button("급식 조회"):
        try:
            with st.spinner("급식 정보를 불러오는 중..."):
                meals = fetch_meals(
                    school["ATPT_OFCDC_SC_CODE"],
                    school["SD_SCHUL_CODE"],
                    meal_date.strftime("%Y%m%d"),
                )
        except Exception as e:
            st.error(f"API 호출 실패: {e}")
            st.stop()

        if not meals:
            st.info("해당 날짜의 급식 정보가 없습니다.")
        for meal in meals:
            st.subheader(f"{meal['MMEAL_SC_NM']} · {meal['CAL_INFO']}")
            menu_lines = format_menu(meal["DDISH_NM"])
            st.markdown("  \n".join(menu_lines))
            allergy_lines = [line for line in menu_lines if re.search(r"\([\d.]+\)", line)]
            if allergy_lines:
                with st.spinner("알레르기 정보를 설명하는 중..."):
                    try:
                        st.subheader("알레르기 정보 설명")
                        st.write(explain_allergy(allergy_lines))
                    except Exception as e:
                        st.error(f"AI 호출 실패: {e}")
