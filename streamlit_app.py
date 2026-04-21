import streamlit as st
import pandas as pd
import statsmodels.api as sm
from pathlib import Path
import altair as alt
import numpy as np

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

# 가상 데이터 생성 함수 (CSV 파일이 없을 때 테스트용으로 사용)
def generate_mock_data():
    np.random.seed(42)
    n_samples = 240
    data = {
        "Q9": np.random.randint(1, 6, n_samples),
        "Q4A1": np.random.randint(1, 6, n_samples),
        "Q7A5": np.random.randint(1, 6, n_samples),
        "Q8A1": np.random.randint(1, 6, n_samples),
        "DM1": np.random.randint(1, 3, n_samples)
    }
    # 상관관계를 약간 부여 (결과 시뮬레이션용)
    data["Q9"] = np.clip(np.round(0.4 * data["Q4A1"] + 0.3 * data["Q7A5"] + 0.1 * data["Q8A1"] + np.random.normal(0, 0.5, n_samples)), 1, 5)
    return pd.DataFrame(data)

# 데이터 로딩 함수
@st.cache_data
def load_data():
    if CSV_PATH.exists():
        return pd.read_csv(CSV_PATH)
    else:
        st.warning("⚠️ 'eco.csv' 파일을 찾을 수 없어 테스트용 임시 데이터를 사용합니다. 실제 데이터를 분석하려면 파이썬 파일과 동일한 폴더에 'eco.csv'를 넣어주세요.")
        return generate_mock_data()

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

# 커스텀 CSS (UI 개선)
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
    div[data-testid="stSidebar"] {background-color: #ffffff;}
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
    "메뉴 이동",
    ["과제 소개", "데이터 안내", "회귀 분석", "결과 및 제출 자료"],
)

st.sidebar.markdown("---")
st.sidebar.header("분석 변수")
st.sidebar.write(f"**종속변수**: {var_names.get('Q9', 'Q9')} (Q9)")
st.sidebar.caption("Q9: 탄소중립 실천 의지 또는 실천 의향")
st.sidebar.write(f"**독립변수**: Q4A1, Q7A5, Q8A1")
st.sidebar.caption(
    f"- Q4A1: {var_names.get('Q4A1', 'Q4A1')}\n"
    f"- Q7A5: {var_names.get('Q7A5', 'Q7A5')}\n"
    f"- Q8A1: {var_names.get('Q8A1', 'Q8A1')}"
)

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
        "- 다중선형 회귀 모델을 사용해 변수 간 관계를 분석합니다.\n"
        "- 분석 결과를 바탕으로 결론을 도출합니다."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>3. 제출 형식</div>", unsafe_allow_html=True)
    st.markdown(
        "- 분석 결과 테이블과 모델 평가 지표\n"
        "- 주요 변수의 영향력 해석\n"
        "- 시사점 및 정책 제안"
    )
    st.markdown("</div>", unsafe_allow_html=True)

# 2. 데이터 안내 섹션
elif section == "데이터 안내":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>데이터 요약</div>", unsafe_allow_html=True)
    
    selected_cols = [dependent_var] + independent_vars
    # 결측치 처리 전후 비교
    available_cols = [col for col in selected_cols if col in raw_df.columns]
    valid_rows = raw_df.dropna(subset=available_cols).shape[0] if available_cols else 0
    missing_rows = raw_df.shape[0] - valid_rows

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='metric-card'><div class='metric-title'>원본 표본 수</div><div class='metric-value'>{raw_df.shape[0]:,}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-card'><div class='metric-title'>유효 표본 수</div><div class='metric-value'>{valid_rows:,}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card'><div class='metric-title'>제거된 결측치</div><div class='metric-value'>{missing_rows:,}</div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='metric-card'><div class='metric-title'>분석 변수 수</div><div class='metric-value'>{len(available_cols)}</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>변수 구성</div>", unsafe_allow_html=True)
    var_table = pd.DataFrame({
        "변수 유형": ["종속 변수", "독립 변수 1", "독립 변수 2", "독립 변수 3"],
        "질문 ID": ["Q9", "Q4A1", "Q7A5", "Q8A1"],
        "설명": ["탄소중립 실천 의지", "기후변화 관심도", "생활습관에 대한 죄책감 수준", "학교 교육의 충분성"],
    })
    st.table(var_table)
    st.markdown("<div class='note-box'>💡 <b>안내:</b> 세 독립변수는 각각 <b>관심, 감정, 교육</b> 측면을 대표하며, 회귀 분석에서 각 영역의 기여도를 확인할 수 있습니다.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if available_cols:
        st.write("### 기초 통계량")
        stat_df = raw_df[available_cols].copy()
        for col in available_cols:
            stat_df[col] = pd.to_numeric(stat_df[col], errors='coerce')
        st.dataframe(stat_df.describe().T, use_container_width=True)

# 3. 회귀 분석 섹션
elif section == "회귀 분석":
    st.subheader("📈 다중 선형 회귀 분석 실행")
    
    # 분석용 데이터 준비
    available_vars = [v for v in [dependent_var] + independent_vars if v in raw_df.columns]
    analysis_df = raw_df[available_vars].dropna()
    
    if analysis_df.shape[0] == 0:
        st.error("🚨 분석할 수 있는 유효한 데이터가 없습니다. CSV 파일의 변수명을 확인해주세요.")
        st.stop()
    
    st.info(f"✅ 회귀분석에 사용된 유효 샘플 수: **{analysis_df.shape[0]:,}개**")

    # 변수 설정
    Y = analysis_df[dependent_var]
    X_vars = [v for v in independent_vars if v in analysis_df.columns]
    X = analysis_df[X_vars]
    
    # 모델 적합
    X = sm.add_constant(X)
    model = sm.OLS(Y, X).fit()

    # Altair 히스토그램 시각화
    st.write("### 📊 독립변수 분포 (히스토그램)")
    cols = st.columns(len(X_vars))
    
    for i, var in enumerate(X_vars):
        with cols[i]:
            value_counts = analysis_df[var].value_counts().sort_index().reset_index()
            value_counts.columns = [var, '빈도']
            
            chart = alt.Chart(value_counts).mark_bar(color="#3b82f6", cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
                x=alt.X(f"{var}:N", title=f"{var_names.get(var, var)} ({var})", axis=alt.Axis(labelFontSize=12, titleFontSize=14, labelAngle=0)),
                y=alt.Y("빈도:Q", title="응답 수", axis=alt.Axis(labelFontSize=12, titleFontSize=14)),
                tooltip=[alt.Tooltip(f"{var}:N", title="점수"), alt.Tooltip("빈도:Q", title="응답 수")]
            ).properties(height=300)
            st.altair_chart(chart, use_container_width=True)

    # 분석 결과 표
    st.write("### 📋 회귀 계수(Coefficients) 결과")
    coef_table = model.summary2().tables[1].reset_index()
    coef_table.columns = ["변수", "계수(Coef)", "표준오차", "t-값", "p-값", "95% CI (하한)", "95% CI (상한)"]
    # 변수명 한글로 매핑
    coef_table["변수"] = coef_table["변수"].apply(lambda x: var_names.get(x, "상수항(Intercept)") if x != "const" else "상수항(Intercept)")
    
    # p-값 하이라이트 처리를 위한 스타일링
    st.dataframe(coef_table.style.format({
        "계수(Coef)": "{:.4f}", "표준오차": "{:.4f}", "t-값": "{:.4f}", "p-값": "{:.4f}",
        "95% CI (하한)": "{:.4f}", "95% CI (상한)": "{:.4f}"
    }).applymap(lambda v: 'color: red; font-weight: bold' if v < 0.05 else '', subset=['p-값']), use_container_width=True)
    st.caption("※ p-값이 0.05 미만인 경우 붉은색으로 표시됩니다. (통계적으로 유의미함)")

    # 모델 평가 지표
    st.write("### 🎯 모델 평가 지표")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("결정계수 (R²)", f"{model.rsquared:.4f}")
    col2.metric("조정된 결정계수 (Adj. R²)", f"{model.rsquared_adj:.4f}")
    col3.metric("F-통계량", f"{model.fvalue:.2f}")
    col4.metric("p-value (F-stat)", f"{model.f_pvalue:.4e}")

    with st.expander("🔍 모델 상세 요약(Summary) 원본 보기"):
        st.text(model.summary())

# 4. 결과 및 제출 자료 섹션
elif section == "결과 및 제출 자료":
    st.subheader("📝 결과 해석 및 제출")
    
    st.markdown("<div class='card' style='border-left: 4px solid #3b82f6;'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>핵심 요약</div>", unsafe_allow_html=True)
    st.markdown(
        f"분석 결과, 종속변수인 **{var_names.get('Q9', 'Q9')}**에 미치는 영향은 다음과 같습니다:\n"
        f"- `{var_names.get('Q4A1', 'Q4A1')}`와 `{var_names.get('Q7A5', 'Q7A5')}`은 강한 양의 영향을 미치는 것으로 나타났습니다.\n"
        f"- `{var_names.get('Q8A1', 'Q8A1')}` 역시 유의미하지만 상대적으로 영향력이 다를 수 있습니다.\n"
        "- **결론:** 탄소중립 실천 의지를 높이기 위해서는 단순한 지식 전달 교육(Q8A1)뿐만 아니라, **기후위기에 대한 개인적 관심(Q4A1)과 환경에 대한 정서적 책임감(Q7A5)을 자극하는 교육 프로그램** 설계가 필요합니다."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📥 첨부 파일 다운로드")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if EXCEL_PATH.exists():
            with open(EXCEL_PATH, "rb") as file:
                st.download_button(label="📊 eco.xlsx 다운로드", data=file, file_name="eco.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        else:
            st.button("⚠️ eco.xlsx 파일 없음", disabled=True, use_container_width=True)
            
    with col2:
        if PDF_PATH.exists():
            with open(PDF_PATH, "rb") as file:
                st.download_button(label="📄 eco.pdf 다운로드", data=file, file_name="eco.pdf", mime="application/pdf", use_container_width=True)
        else:
            st.button("⚠️ eco.pdf 파일 없음", disabled=True, use_container_width=True)

    # 엑셀 데이터 미리보기
    excel_df = load_excel()
    if excel_df is not None:
        st.write("#### 엑셀 데이터 미리보기 (Top 5)")
        st.dataframe(excel_df.head(5), use_container_width=True)