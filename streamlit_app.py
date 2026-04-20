import streamlit as st
import pandas as pd
import statsmodels.api as sm
from pathlib import Path
import matplotlib.pyplot as plt

# --- 그래프 한글 폰트 깨짐 방지 설정 ---
# Windows 환경을 기본으로 설정합니다. Mac인 경우 'Malgun Gothic'을 'AppleGothic'으로 변경하세요.
plt.rcParams['font.family'] = 'Malgun Gothic' 
plt.rcParams['axes.unicode_minus'] = False

# 페이지 설정
st.set_page_config(
    page_title="과제형 탄소중립 분석",
    page_icon="📘",
    layout="wide",
)

# 파일 경로 설정
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "eco.csv"
EXCEL_PATH = BASE_DIR / "eco.xlsx"
PDF_PATH = BASE_DIR / "eco.pdf"

# 데이터 로딩 함수 (예외 처리 추가)
@st.cache_data
def load_data():
    try:
        return pd.read_csv(CSV_PATH)
    except FileNotFoundError:
        st.error("⚠️ 'eco.csv' 파일을 찾을 수 없습니다. 파이썬 파일과 동일한 폴더에 파일이 있는지 확인해주세요.")
        st.stop() # 에러 발생 시 앱 실행 중지

@st.cache_data
def load_excel():
    try:
        return pd.read_excel(EXCEL_PATH)
    except Exception:
        return None

# 데이터 불러오기
raw_df = load_data()
all_vars = [col for col in raw_df.columns if col.startswith("Q")]

# 변수명 매핑
var_names = {
    "Q9": "탄소중립 실천 의지",
    "Q4A1": "기후변화 관심도",
    "Q7A5": "생활습관 죄책감",
    "Q8A1": "학교 교육 충분성"
}

# 커스텀 CSS (보이지 않는 특수 공백 완전 제거)
st.markdown(
    """
    <style>
    .card {background: #f8f9fa; border: 1px solid #e2e3e5; border-radius: 16px; padding: 22px; margin-bottom: 18px; box-shadow: 0 6px 18px rgba(0,0,0,0.04);}
    .card h3 {margin-top: 0;}
    .section-title {font-size: 1.2rem; font-weight: 600; margin-bottom: 10px;}
    .metric-card {background: #ffffff; border: 1px solid #e2e3e5; border-radius: 16px; padding: 18px 16px; margin-bottom: 12px; text-align: center;}
    .metric-title {font-size: 0.95rem; color: #6c757d; margin-bottom: 8px;}
    .metric-value {font-size: 1.9rem; font-weight: 700; color: #111827;}
    .note-box {background: #fff6e5; border: 1px solid #f2d388; border-radius: 14px; padding: 18px 20px; color: #5a4634; margin-top: 12px;}
    .small-note {color: #6c757d;}
    div[data-testid="stSidebar"] {
        background-color: #ffffff;
    }
    .stSidebar .sidebar-content {padding-top: 24px;}
    </style>
    """,
    unsafe_allow_html=True,
)

with st.container():
    st.title("📘 과제형 탄소중립 실천 요인 분석")
    st.write("① 데이터 구조 파악 ➔ ② 고정 변수 기반 다중회귀분석 ➔ ③ 핵심 인사이트 및 결론 도출")

# 사이드바 설정
section = st.sidebar.radio(
    "과제 창",
    ["과제 소개", "데이터 안내", "회귀 분석", "결과 및 제출 자료"],
)

st.sidebar.markdown("---")
st.sidebar.header("분석 변수")
st.sidebar.write(f"종속변수: {var_names['Q9']} (Q9)")
st.sidebar.caption("Q9: 탄소중립 실천 의지 또는 실천 의향")
st.sidebar.write(f"독립변수: {var_names['Q4A1']} (Q4A1), {var_names['Q7A5']} (Q7A5), {var_names['Q8A1']} (Q8A1)")
st.sidebar.caption(f"Q4A1: {var_names['Q4A1']}\n Q7A5: {var_names['Q7A5']}\n Q8A1: {var_names['Q8A1']}")

dependent_var = "Q9"
independent_vars = ["Q4A1", "Q7A5", "Q8A1"]

# 1. 과제 소개 섹션
if section == "과제 소개":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>1. 과제 목표</div>", unsafe_allow_html=True)
    st.write("청소년의 탄소중립 실천 의지에 영향을 주는 요인을 분석하고, 결과를 기반으로 학교 교육 방향을 제시합니다.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>2. 수행 과제</div>", unsafe_allow_html=True)
    st.markdown(
        "- 데이터셋을 이해하고 주요 변수를 확인합니다.\n"
        "- `Q9`를 종속변수로, `Q4A1`, `Q7A5`, `Q8A1`을 독립변수로 설정합니다.\n"
        "- `Q9`: 탄소중립 실천 의지 또는 실천 의향\n"
        "- `Q4A1`: 기후변화 관심도, `Q7A5`: 생활습관 죄책감, `Q8A1`: 학교 교육 충분성\n"
        "- 다중선형 회귀 모델을 사용해 변수 간 관계를 분석합니다.\n"
        "- 분석 결과를 바탕으로 결론을 도출합니다."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>3. 제출 형식</div>", unsafe_allow_html=True)
    st.markdown(
        "- 분석 결과 테이블과 모델 평가 지표\n"
        "- 주요 변수의 영향력 해석\n"
        "- 시사점 및 정책 제안\n"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 과제 진행 순서")
    st.write(
        "1. 고정 변수로 설정된 분석을 확인하고,\n"
        "2. 데이터 미리보기로 변수 상태를 확인한 뒤,\n"
        "3. 회귀 분석 결과를 통해 해석을 완성합니다."
    )

# 2. 데이터 안내 섹션
elif section == "데이터 안내":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>데이터 소개</div>", unsafe_allow_html=True)
    st.write(
        "본 페이지는 데이터 분석 과제 제출을 위해 제작된 Streamlit 애플리케이션입니다. 데이터 탐색(EDA)부터 지정된 변수 기반의 회귀분석 실행, 그리고 최종 결론 도출까지의 분석 과정을 순차적으로 제공합니다."
    )

    selected_cols = [dependent_var] + independent_vars
    valid_rows = raw_df.dropna(subset=selected_cols).shape[0]
    missing_rows = raw_df.shape[0] - valid_rows

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(
        "<div class='metric-card'><div class='metric-title'>원본 총 표본 수</div>"
        f"<div class='metric-value'>{raw_df.shape[0]:,}</div>"
        "</div>", unsafe_allow_html=True)
    c2.markdown(
        "<div class='metric-card'><div class='metric-title'>결측 제거 후 유효 표본</div>"
        f"<div class='metric-value'>{valid_rows:,}</div>"
        "</div>", unsafe_allow_html=True)
    c3.markdown(
        "<div class='metric-card'><div class='metric-title'>제거된 결측 행</div>"
        f"<div class='metric-value'>{missing_rows:,}</div>"
        "</div>", unsafe_allow_html=True)
    c4.markdown(
        "<div class='metric-card'><div class='metric-title'>측정 변수 문항 수</div>"
        f"<div class='metric-value'>{len(all_vars)}</div>"
        "</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>변수 구성</div>", unsafe_allow_html=True)
    var_table = pd.DataFrame(
        {
            "변수 유형": ["종속 변수", "독립 변수 1", "독립 변수 2", "독립 변수 3", "통제 변수"],
            "변수명": [var_names["Q9"], var_names["Q4A1"], var_names["Q7A5"], var_names["Q8A1"], "성별, 학교급, 학년, 권역, 남여공학"],
            "질문 ID": ["Q9", "Q4A1", "Q7A5", "Q8A1", "DM1, DM2, DM3, DM4, DM9"],
            "설명": ["탄소중립 실천 의지 또는 실천 의향", "기후변화 관심도", "생활습관에 대한 죄책감 수준", "학교 교육의 충분성", "사회경제적 배경을 통제하는 변인들"],
        }
    )
    st.table(var_table)
    st.markdown("<div class='note-box'>세 독립변수는 각각 관심, 감정, 교육 측면을 대표하며, 다중회귀 분석에서 각 영역의 기여를 비교할 수 있도록 구성되었습니다.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("### 선택 변수 기술 통계")
    # --- [안전코드] 각 열별로 명확하게 숫자 변환 보장 ---
    stat_df = raw_df[selected_cols].copy()
    for col in selected_cols:
        stat_df[col] = pd.to_numeric(stat_df[col], errors='coerce')
    st.table(stat_df.describe().T)

# 3. 회귀 분석 섹션
elif section == "회귀 분석":
    st.subheader("회귀 분석 실행")
    
    # --- [안전코드] 결측치 제거 전에 숫자형으로 강제 변환 ---
    analysis_df = raw_df[[dependent_var] + independent_vars].copy()
    
    for col in analysis_df.columns:
        analysis_df[col] = pd.to_numeric(analysis_df[col], errors='coerce')
        
    analysis_df = analysis_df.dropna()
    
    # 🚨 유효 데이터 0개 에러 방지
    if analysis_df.shape[0] == 0:
        st.error("🚨 분석할 수 있는 유효한 숫자 데이터가 0개입니다! CSV 파일의 Q9, Q4A1, Q7A5, Q8A1 열에 한글이 섞여 있거나 빈칸인지 확인해 주세요.")
        st.stop()
    
    st.write(f"- 사용된 샘플 수: {analysis_df.shape[0]}개")

    Y = analysis_df[dependent_var]
    X = analysis_df[independent_vars]
    X = sm.add_constant(X)
    model = sm.OLS(Y, X).fit()

    st.write("### 독립변수 히스토그램")
    cols = st.columns(len(independent_vars))
    for i, var in enumerate(independent_vars):
        with cols[i]:
            fig, ax = plt.subplots()
            ax.hist(analysis_df[var], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            ax.set_title(f"{var_names[var]} ({var})")
            ax.set_xlabel("값")
            ax.set_ylabel("빈도")
            st.pyplot(fig)

    st.write("### 회귀 계수 결과")
    coef_table = model.summary2().tables[1].reset_index()
    coef_table.columns = ["변수", "계수", "표준오차", "t값", "p값", "[0.025", "0.975]"]
    coef_table["변수"] = coef_table["변수"].map(lambda x: var_names.get(x, x))
    st.dataframe(coef_table, use_container_width=True)

    st.write("### 모델 평가 지표")
    metrics = {
        "R-squared": round(model.rsquared, 4),
        "Adj. R-squared": round(model.rsquared_adj, 4),
        "F-statistic": round(model.fvalue, 4),
        "Prob (F-statistic)": round(model.f_pvalue, 4),
        "표본 수": int(model.nobs),
    }
    st.write(metrics)

    with st.expander("모델 상세 요약 보기", expanded=False):
        st.text(model.summary())

# 4. 결과 및 제출 자료 섹션
elif section == "결과 및 제출 자료":
    st.subheader("결과 해석 및 제출 자료")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>핵심 해석</div>", unsafe_allow_html=True)
    st.write(
        f"- `{var_names['Q4A1']}`(Q4A1), `{var_names['Q7A5']}`(Q7A5)은 `{var_names['Q9']}`에 강한 영향을 미치며,\n"
        f"- `{var_names['Q8A1']}`(Q8A1)는 영향력이 있으나 상대적으로 낮습니다.\n"
        "- 즉, 실천 의지를 높이려면 단순 교육 외에도 관심 증대와 정서적 책임감 강화가 필요합니다."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 제출 자료")
    st.write(
        "- 분석 결과 요약 보고서\n"
        "- 회귀 계수 표와 평가 지표\n"
        "- 데이터 설명 및 제안 사항"
    )

    st.markdown("---")
    st.subheader("파일 자료 다운로드")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if EXCEL_PATH.exists():
            with open(EXCEL_PATH, "rb") as file:
                st.download_button(
                    label="📥 eco.xlsx 다운로드",
                    data=file,
                    file_name="eco.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.warning("⚠️ eco.xlsx 파일을 찾을 수 없습니다.")
            
    with col2:
        if PDF_PATH.exists():
            with open(PDF_PATH, "rb") as file:
                st.download_button(
                    label="📥 eco.pdf 다운로드",
                    data=file,
                    file_name="eco.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("⚠️ eco.pdf 파일을 찾을 수 없습니다.")

    excel_df = load_excel()
    if excel_df is not None:
        st.write("### 엑셀 데이터 안내")
        st.dataframe(excel_df.head(5), use_container_width=True)
    else:
        st.write("`eco.xlsx` 파일을 불러올 수 없습니다.")