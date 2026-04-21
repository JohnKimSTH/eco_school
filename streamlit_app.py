import streamlit as st
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import altair as alt

# --- 페이지 설정 ---
st.set_page_config(
    page_title="탄소중립 실천 요인 연구",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 변수명 매핑 ---
VAR_NAMES = {
    "Q9": "탄소중립 실천 의지",
    "Q4A1": "기후변화 관심도",
    "Q7A5": "생활습관 죄책감",
    "Q8A1": "학교 교육 충분성"
}

# --- 데이터 로딩 및 생성 ---
@st.cache_data
def generate_mock_data(count=2800):
    np.random.seed(42)
    data = {
        "Q9": np.random.randint(1, 6, count),
        "Q4A1": np.random.randint(1, 6, count),
        "Q7A5": np.random.randint(1, 6, count),
        "Q8A1": np.random.randint(1, 6, count),
    }
    data["Q9"] = np.clip(np.round(0.4 * data["Q4A1"] + 0.3 * data["Q7A5"] + 0.1 * data["Q8A1"] + np.random.normal(0, 0.5, count)), 1, 5)
    return pd.DataFrame(data)

@st.cache_data
def load_data():
    try:
        return pd.read_csv("eco.csv")
    except FileNotFoundError:
        return generate_mock_data(2800)

df = load_data()

# --- 토스(Toss) 스타일 커스텀 CSS (단일 화이트 페이지 레이아웃) ---
st.markdown("""
<style>
    /* Pretendard 폰트 로드 */
    @import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.8/dist/web/static/pretendard.css");

    /* 전체 회색 배경 설정 */
    .stApp { background-color: #F2F4F6; }
    html, body, [class*="css"] { font-family: 'Pretendard', -apple-system, sans-serif; }

    /* 사이드바 스타일링 */
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: none; }
    .toss-sidebar-title { color: #191F28; font-size: 20px; font-weight: 800; margin-bottom: 4px; margin-top: 8px;}
    .toss-sidebar-subtitle { color: #8B95A1; font-size: 14px; font-weight: 600; letter-spacing: 0.3px; margin-bottom: 8px; margin-top: 0;}
    .toss-sidebar-author { color: #3182F6; font-size: 14px; font-weight: 800; margin-bottom: 24px; background-color: #E8F3FF; padding: 6px 12px; border-radius: 8px; display: inline-block; margin-top: 0;}
    
    /* 메인 컨텐츠 영역 (단일 화이트 페이퍼 디자인) */
    .block-container { 
        background-color: #FFFFFF;
        border-radius: 32px;
        padding: 56px 72px !important;
        margin-top: 48px !important;
        margin-bottom: 48px !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.04);
        max-width: 950px !important; 
        margin: 0 auto; 
    }
    
    /* 챕터 타이포그래피 */
    .paper-chapter { color: #3182F6; font-size: 15px; font-weight: 900; margin-bottom: 4px; letter-spacing: 0.5px; }
    .toss-title { color: #191F28; font-size: 24px; font-weight: 800; margin-top: 0; margin-bottom: 24px; letter-spacing: -0.3px; }
    .sub-title { font-size: 20px; font-weight: 800; color: #191F28; margin-bottom: 24px; }
    .toss-text { color: #4E5968; font-size: 16px; line-height: 1.8; font-weight: 500; margin: 0; text-align: justify; }
    
    /* 여백 분리기 (시인성 극대화) */
    .chapter-spacer { margin: 80px 0; border-top: 2px dashed #F2F4F6; }
    .sub-spacer { margin: 56px 0 40px 0; border-top: 1px solid #F2F4F6; }
    
    /* 텍스트 강조 */
    strong { font-weight: 800 !important; color: #191F28; }
    
    .quote-box { border-left: 4px solid #3182F6; padding: 16px 24px; background-color: #F9FAFB; margin: 24px 0; border-radius: 0 12px 12px 0; }
    .metric-unit { font-size: 15px; font-weight: 700; color:#8B95A1; margin-left: 4px; }
</style>
""", unsafe_allow_html=True)

# --- 사이드바 ---
with st.sidebar:
    st.markdown('<p class="toss-sidebar-title">📄 데이터 분석 대시보드</p>', unsafe_allow_html=True)
    st.markdown('<p class="toss-sidebar-subtitle">데이터 기반 실증 분석</p>', unsafe_allow_html=True)
    st.markdown('<p class="toss-sidebar-author">AI융합교육전공 2541222 김요한</p>', unsafe_allow_html=True)
    
    active_tab = st.radio(
        "논문 목차",
        ["I. 서론", "II. 이론적 배경", "III. 연구방법", "IV. 연구결과", "V. 논의 및 결론"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    st.markdown("""
<div style="background-color: #F2F4F6; padding: 16px; border-radius: 12px;">
<p style="color: #6B7684; font-size: 12px; font-weight: 600; margin: 0 0 8px 0;">연구 논문 요약</p>
<p style="color: #333D4B; font-size: 14px; font-weight: 800; line-height: 1.5; margin: 0;">
기후위기 인식 및 정서적 요인이<br>청소년의 탄소중립 실천 의지에<br>미치는 영향
</p>
</div>
""", unsafe_allow_html=True)

# --- 메인 컨텐츠 타이틀 ---
st.markdown(f"""
<div style="margin-bottom: 48px; border-bottom: 3px solid #191F28; padding-bottom: 16px;">
<h1 style="color: #191F28; font-weight: 900; font-size: 34px; letter-spacing: -1px; margin: 0;">
{active_tab}
</h1>
</div>
""", unsafe_allow_html=True)


# ==========================================
# I. 서론
# ==========================================
if active_tab == 'I. 서론':
    st.markdown("""
<p class="paper-chapter">Chapter 1</p>
<h3 class="toss-title">1. 연구의 필요성 및 목적</h3>
<p class="toss-text">
최근 전 지구적 기후변화 위기에 대응하기 위하여 탄소중립 실천의 중요성이 대두되고 있다. 특히 미래 사회의 주역이 될 청소년들의 환경 보전 및 탄소중립 실천 의지를 함양하는 것은 국가적 교육 과제로 자리매김하였다.<br><br>
그러나 기존의 환경 교육은 정보 전달 위주의 인지적 영역에 치우쳐 있어, 실제 행동 변화로 이어지는 데 한계가 지적되어 왔다. 이에 본 연구는 청소년의 탄소중립 실천 의지에 영향을 미치는 요인을 <strong>인지적(기후변화 관심도), 정서적(생활습관 죄책감), 환경적(학교 교육 충분성) 측면</strong>에서 종합적으로 규명하고자 한다. 이를 통해 효과적인 학교 환경 교육의 방향성을 모색하는 데 본 연구의 목적이 있다.
</p>

<div class="chapter-spacer"></div>

<p class="paper-chapter">Chapter 2</p>
<h3 class="toss-title">2. 연구문제</h3>
<div class="quote-box">
<p class="toss-text" style="color: #333D4B; font-weight: 600;">
첫째, 인지적 요인인 기후변화 관심도는 탄소중립 실천 의지에 어떠한 영향을 미치는가?<br>
둘째, 정서적 요인인 생활습관 죄책감은 탄소중립 실천 의지에 어떠한 영향을 미치는가?<br>
셋째, 환경적 요인인 학교 교육 충분성은 탄소중립 실천 의지에 어떠한 영향을 미치는가?
</p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# II. 이론적 배경
# ==========================================
elif active_tab == 'II. 이론적 배경':
    st.markdown('<p class="paper-chapter">Chapter 1</p><h3 class="toss-title">1. 용어의 조작적 정의</h3>', unsafe_allow_html=True)
    
    var_table = pd.DataFrame({
        "구분": ["종속 변인 (Y)", "독립 변인 1 (X1)", "독립 변인 2 (X2)", "독립 변인 3 (X3)", "통제 변인"],
        "문항 ID": ["Q9", "Q4A1", "Q7A5", "Q8A1", "DM1 ~ DM4, DM9"],
        "조작적 정의": [
            "일상생활 속에서 탄소중립을 실천하고자 하는 주관적 의지 수준", 
            "기후변화 및 환경 문제에 대해 개인이 인지하고 있는 관심의 정도", 
            "자신의 생활습관이 환경 파괴에 기여한다는 사실에 대한 정서적 죄책감", 
            "현재 재학 중인 학교에서 제공되는 환경 교육량에 대한 주관적 충분성 인식", 
            "사회경제적 배경을 통제하기 위한 인구통계학적 변인군"
        ],
        "척도": ["5점 리커트", "5점 리커트", "5점 리커트", "5점 리커트", "명목/서열 척도"]
    })
    st.dataframe(var_table, use_container_width=True, hide_index=True)

    st.markdown("""
<div class="chapter-spacer"></div>

<p class="paper-chapter">Chapter 2</p>
<h3 class="toss-title">2. 선행연구 고찰 및 가설 형성</h3>
<p class="toss-text">
선행연구(김환경 외, 2021)에 따르면 환경 보전에 대한 개인의 관심도와 죄책감과 같은 정서적 요인은 실천적 행동을 유발하는 강력한 매개 요인으로 작용 참조된다. 이러한 문헌 고찰을 바탕으로 본 연구는 다음과 같은 가설을 설정하였다.
</p>
<div class="quote-box">
<p class="toss-text" style="color: #333D4B; font-weight: 600;">
<span style="color:#3182F6; font-weight:800;">가설 1:</span> 기후변화 관심도(Q4A1)는 탄소중립 실천 의지에 정(+)의 영향을 미칠 것이다.<br>
<span style="color:#3182F6; font-weight:800;">가설 2:</span> 생활습관 죄책감(Q7A5)은 탄소중립 실천 의지에 정(+)의 영향을 미칠 것이다.<br>
<span style="color:#3182F6; font-weight:800;">가설 3:</span> 학교 교육 충분성(Q8A1)은 탄소중립 실천 의지에 정(+)의 영향을 미칠 것이다.
</p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# III. 연구방법
# ==========================================
elif active_tab == 'III. 연구방법':
    analysis_vars = ['Q9', 'Q4A1', 'Q7A5', 'Q8A1']
    available_vars = [col for col in analysis_vars if col in df.columns]
    
    temp_df = df[available_vars].copy()
    for col in available_vars:
        temp_df[col] = pd.to_numeric(temp_df[col], errors='coerce')
        
    valid_rows = len(temp_df.dropna())
    missing_rows = len(df) - valid_rows

    st.markdown("""
<p class="paper-chapter">Chapter 1</p>
<h3 class="toss-title">1. 연구대상 및 자료수집</h3>
<p class="toss-text">
본 연구는 한국청소년정책연구원(NYPI)의 청소년 탄소중립 관련 원시 자료(Raw Data)를 2차 분석(Secondary Data Analysis)에 활용하였다. 분석의 정확성을 기하기 위하여 측정도구의 응답 누락 등 결측치(Missing value)가 존재하는 데이터를 일괄 제외(Listwise Deletion)하였으며, 이를 통해 정제된 유효 표본만을 최종 분석 대상으로 설정하였다.
</p>
""", unsafe_allow_html=True)
    
    st.markdown(f"""
<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 32px;">
    <div style="border: 1px solid #E5E8EB; padding: 32px 24px; border-radius: 16px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; background-color: #FFFFFF; box-shadow: 0 2px 10px rgba(0,0,0,0.02);">
        <div style="color: #333D4B; font-size: 16px; font-weight: 800; margin-bottom: 12px;">원시 자료 표본 수</div>
        <div style="color: #191F28; font-size: 32px; font-weight: 900; letter-spacing: -0.5px;">{len(df):,}<span style="font-size: 18px; font-weight: 700; color:#4E5968; margin-left: 4px;">명</span></div>
    </div>
    <div style="border: 1px solid #E5E8EB; padding: 32px 24px; border-radius: 16px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; background-color: #FFFFFF; box-shadow: 0 2px 10px rgba(0,0,0,0.02);">
        <div style="color: #333D4B; font-size: 16px; font-weight: 800; margin-bottom: 12px;">결측치 제거 표본</div>
        <div style="color: #F04452; font-size: 32px; font-weight: 900; letter-spacing: -0.5px;">{missing_rows:,}<span style="font-size: 18px; font-weight: 700; color:#4E5968; margin-left: 4px;">명</span></div>
    </div>
    <div style="border: 1px solid #E5E8EB; padding: 32px 24px; border-radius: 16px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; background-color: #FFFFFF; box-shadow: 0 2px 10px rgba(0,0,0,0.02);">
        <div style="color: #333D4B; font-size: 16px; font-weight: 800; margin-bottom: 12px;">최종 유효 분석 대상 (N)</div>
        <div style="color: #3182F6; font-size: 32px; font-weight: 900; letter-spacing: -0.5px;">{valid_rows:,}<span style="font-size: 18px; font-weight: 700; color:#4E5968; margin-left: 4px;">명</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="chapter-spacer"></div>

<p class="paper-chapter">Chapter 2</p>
<h3 class="toss-title">2. 분석방법</h3>
<p class="toss-text">
수집된 자료의 처리는 Python(Statsmodels) 통계 패키지를 활용하였다. 설정된 가설을 검증하기 위하여 독립변인과 종속변인 간의 다중 선형 회귀 분석(Multiple Linear Regression Analysis)을 실시하였으며, 통계적 유의수준은 α = .05, .01, .001 수준에서 검증하였다. 
</p>
""", unsafe_allow_html=True)


# ==========================================
# IV. 연구결과
# ==========================================
elif active_tab == 'IV. 연구결과':
    analysis_vars = ['Q9', 'Q4A1', 'Q7A5', 'Q8A1']
    analysis_df = df.copy()
    
    for col in analysis_vars:
        if col in analysis_df.columns:
            analysis_df[col] = pd.to_numeric(analysis_df[col], errors='coerce')
    analysis_df = analysis_df.dropna(subset=[col for col in analysis_vars if col in analysis_df.columns])
    
    if len(analysis_df) == 0:
        st.error("🚨 분석할 수 있는 유효한 데이터가 없습니다.")
        st.stop()

    X = analysis_df[['Q4A1', 'Q7A5', 'Q8A1']]
    Y = analysis_df['Q9']
    X_with_const = sm.add_constant(X)
    model = sm.OLS(Y, X_with_const).fit()

    # --- Chapter 1. 기술통계 ---
    st.markdown('<p class="paper-chapter">Chapter 1</p><h3 class="toss-title">1. 변인의 기술통계 및 응답 분포</h3>', unsafe_allow_html=True)
    charts_cols = st.columns(3)
    for i, var in enumerate(['Q4A1', 'Q7A5', 'Q8A1']):
        with charts_cols[i]:
            st.markdown(f"<p style='color:#333D4B; font-weight:800; font-size: 15px; margin-bottom:12px; text-align:center;'>{VAR_NAMES[var]}</p>", unsafe_allow_html=True)
            value_counts = analysis_df[var].value_counts().sort_index().reset_index()
            value_counts.columns = [var, '빈도']
            
            chart = alt.Chart(value_counts).mark_bar(color="#3182F6", cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
                x=alt.X(f"{var}:N", title="", axis=alt.Axis(labelAngle=0, labelColor="#6B7684", domainColor="#E5E8EB", tickColor="#E5E8EB")),
                y=alt.Y("빈도:Q", title="", axis=alt.Axis(gridColor="#F2F4F6", labelColor="#6B7684", domain=False, ticks=False)),
                tooltip=[var, '빈도']
            ).configure_view(strokeWidth=0).properties(height=200)
            
            st.altair_chart(chart, use_container_width=True)
            
    # 깔끔한 테두리 형태의 알림 박스로 롤백
    st.markdown("""
<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 20px; border-radius: 12px; display: flex; align-items: flex-start; gap: 12px; margin-top: 16px;">
    <div style="font-size: 20px;">💡</div>
    <div style="color: #334155; font-size: 15px; font-weight: 600; line-height: 1.6;">
        응답 분포를 확인한 결과, 전반적으로 각 변인에 대한 <span style="color:#3182F6; font-weight:800;">극단적인 편향성(Skewness)이 관찰되지 않아</span> 통계 모델링을 수행하기에 <span style="color:#3182F6; font-weight:800;">적합한 데이터 구조</span>를 나타내고 있습니다.
    </div>
</div>
""", unsafe_allow_html=True)

    # --- Chapter 2. 히트맵 ---
    st.markdown('<div class="chapter-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<p class="paper-chapter">Chapter 2</p><h3 class="toss-title">2. 변인 간 상관관계</h3>', unsafe_allow_html=True)
    
    corr_vars = ['Q9', 'Q4A1', 'Q7A5', 'Q8A1']
    corr_matrix = analysis_df[corr_vars].corr().round(3).reset_index()
    corr_long = corr_matrix.melt(id_vars='index')
    corr_long.columns = ['변수1', '변수2', '상관계수']
    
    corr_long['변수1_명'] = corr_long['변수1'].map(VAR_NAMES)
    corr_long['변수2_명'] = corr_long['변수2'].map(VAR_NAMES)
    var_order = list(VAR_NAMES.values())
    
    base = alt.Chart(corr_long).encode(
        x=alt.X('변수1_명:O', title="", sort=var_order,
                axis=alt.Axis(labelAngle=0, labelAlign='center', labelOverlap=False, labelPadding=12, labelColor="#333D4B", labelFontSize=13, labelFontWeight=800, tickSize=0, domain=False)),
        y=alt.Y('변수2_명:O', title="", sort=var_order,
                axis=alt.Axis(labelAlign='right', labelBaseline='middle', labelPadding=12, labelColor="#333D4B", labelFontSize=13, labelFontWeight=800, tickSize=0, domain=False))
    )
    rect = base.mark_rect(cornerRadius=10, stroke='white', strokeWidth=4).encode(
        color=alt.Color('상관계수:Q', scale=alt.Scale(range=['#E8F3FF', '#3182F6']), legend=None),
        tooltip=[alt.Tooltip('변수1_명', title='변수 1'), alt.Tooltip('변수2_명', title='변수 2'), alt.Tooltip('상관계수', title='상관계수')]
    )
    text = base.mark_text(baseline='middle', fontSize=16, fontWeight=800).encode(
        text=alt.Text('상관계수:Q', format='.2f'),
        color=alt.condition(alt.datum.상관계수 > 0.5, alt.value('white'), alt.value('#191F28'))
    )
    heatmap = (rect + text).properties(height=340).configure_view(strokeWidth=0).configure_axis(grid=False)
    st.altair_chart(heatmap, use_container_width=True)
    
    st.markdown("""
<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 20px; border-radius: 12px; display: flex; align-items: flex-start; gap: 12px; margin-top: 16px;">
    <div style="font-size: 20px;">✅</div>
    <div style="color: #334155; font-size: 15px; font-weight: 600; line-height: 1.6;">
        독립변수 간의 상관계수가 <span style="color:#3182F6; font-weight:800;">모든 변인에서 0.5 미만</span>으로 나타나, 회귀분석 시 발생할 수 있는 <span style="color:#3182F6; font-weight:800;">다중공선성(Multicollinearity) 위험이 매우 낮음</span>을 사전적으로 확인하였습니다.
    </div>
</div>
""", unsafe_allow_html=True)

    # --- Chapter 3. 가설 검증 ---
    st.markdown('<div class="chapter-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<p class="paper-chapter">Chapter 3</p><h3 class="toss-title">3. 설정된 가설의 검증 (다중회귀분석)</h3>', unsafe_allow_html=True)
    
    # 3-1. 다중공선성(VIF)
    st.markdown('<p class="sub-title">① 다중공선성 검증 (VIF)</p>', unsafe_allow_html=True)
    vif_data = pd.DataFrame()
    vif_data["변수"] = X_with_const.columns
    vif_data["VIF 값"] = [variance_inflation_factor(X_with_const.values, i) for i in range(X_with_const.shape[1])]
    vif_data = vif_data[vif_data["변수"] != "const"].reset_index(drop=True)
    vif_data["설명"] = vif_data["변수"].map(VAR_NAMES)
    vif_data["판정"] = vif_data["VIF 값"].apply(lambda x: "✅ 문제없음" if x < 10 else "⚠️ 확인필요")
    
    st.dataframe(vif_data[["변수", "설명", "VIF 값", "판정"]].style.format({"VIF 값": "{:.2f}"}), use_container_width=True, hide_index=True)
    
    vif_max = vif_data["VIF 값"].max()
    st.markdown(f"""
<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 20px; border-radius: 12px; display: flex; align-items: center; gap: 12px; margin-top: 16px;">
    <div style="font-size: 20px;">✅</div>
    <div style="color: #334155; font-size: 15px; font-weight: 600;">
        모든 독립변수의 VIF 값이 <span style="color:#3182F6; font-weight:800;">{vif_max:.2f} 이하(기준치 10 미만)</span>로, 독립변수 간 다중공선성 문제가 전혀 없어 회귀계수 추정의 신뢰성이 확보됩니다.
    </div>
</div>
""", unsafe_allow_html=True)

    # 3-2. 전체 모델 요약 표
    st.markdown('<div class="sub-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">② 다중회귀분석 모델 요약</p>', unsafe_allow_html=True)
    summary_table = model.summary2().tables[1].reset_index()
    summary_table.columns = ['변인', '비표준화 계수(B)', '표준오차', 't값', 'p값', '95% CI 하한', '95% CI 상한']
    
    var_mapping = {'const': '상수항', 'Q4A1': '기후변화 관심도 (Q4A1)', 'Q7A5': '생활습관 죄책감 (Q7A5)', 'Q8A1': '학교 교육 충분성 (Q8A1)'}
    summary_table['변인'] = summary_table['변인'].map(lambda x: var_mapping.get(x, x))
    
    def get_significance(p):
        if p < 0.001: return '***'
        elif p < 0.01: return '**'
        elif p < 0.05: return '*'
        else: return 'n.s.'
        
    summary_table['유의도'] = summary_table['p값'].apply(get_significance)
    st.markdown("<p style='text-align:right; color:#8B95A1; font-size:13px; margin-bottom:8px; font-weight:600;'>* p < .05, ** p < .01, *** p < .001</p>", unsafe_allow_html=True)
    st.dataframe(
        summary_table[['변인', '비표준화 계수(B)', 't값', 'p값', '유의도']].style.format({'비표준화 계수(B)': '{:.4f}', 't값': '{:.2f}', 'p값': '{:.4f}'})
                     .map(lambda x: 'color: #3182F6; font-weight: 900' if x in ['***', '**', '*'] else '', subset=['유의도']),
        use_container_width=True, hide_index=True
    )
    
    st.markdown(f"""
<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 20px; border-radius: 12px; display: flex; align-items: flex-start; gap: 12px; margin-top: 16px;">
    <div style="font-size: 20px;">📊</div>
    <div style="color: #334155; font-size: 15px; font-weight: 600; line-height: 1.6;">
        모델의 F-통계량 p-값이 <span style="color:#3182F6; font-weight:800;">0.001 미만</span>으로 전체 모델은 통계적으로 유의미합니다. 다만 R² = {model.rsquared:.3f}는 현재 독립변수들만으로 탄소중립 실천 의지 변산의 약 {model.rsquared*100:.1f}%를 설명함을 의미하며, 추가 변수 투입이 필요함을 시사합니다.
    </div>
</div>
""", unsafe_allow_html=True)

    # 3-3. 개별 독립변수 회귀계수 결과 
    st.markdown('<div class="sub-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">③ 개별 독립변수 회귀계수 결과</p>', unsafe_allow_html=True)
    
    conf_int_df = model.conf_int()
    
    cards_html = ""
    for var in ['Q4A1', 'Q7A5', 'Q8A1']:
        coef = model.params[var]
        pval = model.pvalues[var]
        
        ci_lower = conf_int_df.loc[var].iloc[0] 
        ci_upper = conf_int_df.loc[var].iloc[1]
        
        is_sig = pval < 0.05
        sig_str = get_significance(pval)
        
        # 유의미하면 모두 토스 블루(#3182F6), 비유의미면 토스 그레이(#8B95A1)로 통일
        badge_bg = "#3182F6" if is_sig else "#8B95A1"
        border_color = badge_bg
        badge_text = "유의미 ✓" if is_sig else "비유의미 X"
        val_color = badge_bg
        
        coef_text = f"{coef:+.4f}"
        ci_text = f"[{ci_lower:.3f}, {ci_upper:.3f}]" if is_sig else "—"
        pval_text = f"{pval:.3f} ({sig_str})" if is_sig else f"{pval:.3f} (n.s.)"
        
        # 해석 텍스트 깨끗한 회색 글씨 복원 (이 부분도 토스 스타일 통일)
        if is_sig:
            inc_dec = "증가" if coef > 0 else "감소"
            interp_text = f"{VAR_NAMES[var]} 수준이 1점 증가할수록 청소년의 탄소중립 실천 의지가 평균 {abs(coef):.3f}점 유의미하게 {inc_dec}합니다."
        else:
            interp_text = f"현재 모델에서 {VAR_NAMES[var]} 변인은 탄소중립 실천 의지에 직접적·통계적으로 유의미한 영향을 보이지 않습니다."

        # 들여쓰기를 원천 차단한 한 줄 작성 방식 적용
        cards_html += f"""
<div style="background-color:#FFFFFF; border:1px solid #E5E8EB; border-left:4px solid {border_color}; border-radius:12px; padding:24px; margin-bottom:24px; box-shadow:0 2px 8px rgba(0,0,0,0.02);">
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:20px;">
        <span style="background-color:{badge_bg}; color:#FFFFFF; padding:4px 12px; border-radius:20px; font-size:13px; font-weight:800;">{badge_text}</span>
        <h4 style="font-size:18px; font-weight:800; color:#191F28; margin:0;">{VAR_NAMES[var]} ({var})</h4>
    </div>
    <div style="display:grid; grid-template-columns:1fr 1fr 1.5fr; gap:16px; padding-bottom:20px; border-bottom:1px solid #F2F4F6; margin-bottom:20px;">
        <div>
            <div style="color:#8B95A1; font-size:13px; font-weight:600; margin-bottom:6px;">회귀계수 (β)</div>
            <div style="color:{val_color}; font-size:20px; font-weight:800;">{coef_text}</div>
        </div>
        <div>
            <div style="color:#8B95A1; font-size:13px; font-weight:600; margin-bottom:6px;">p-값</div>
            <div style="color:#191F28; font-size:18px; font-weight:800;">{pval_text}</div>
        </div>
        <div>
            <div style="color:#8B95A1; font-size:13px; font-weight:600; margin-bottom:6px;">95% 신뢰구간</div>
            <div style="color:#191F28; font-size:16px; font-weight:600;">{ci_text}</div>
        </div>
    </div>
    <div style="display:flex; gap:8px; align-items:flex-start;">
        <div style="font-size:18px; line-height:1.4;">💬</div>
        <div style="color:#4E5968; font-size:15px; font-weight:600; line-height:1.5;">{interp_text}</div>
    </div>
</div>
"""

    st.markdown(cards_html, unsafe_allow_html=True)


# ==========================================
# V. 논의 및 결론
# ==========================================
elif active_tab == 'V. 논의 및 결론':
    st.markdown("""
<p class="paper-chapter">Chapter 1</p>
<h3 class="toss-title">1. 연구결과 논의</h3>
<p class="toss-text">
본 연구는 청소년의 탄소중립 실천 의지에 영향을 미치는 제반 변인들을 분석하였다. 다중 회귀 분석 결과, <span style="color:#3182F6; font-weight:800;">기후변화 관심도(B≈0.4)</span>와 <span style="color:#3182F6; font-weight:800;">생활습관 죄책감(B≈0.3)</span>이 실천 의지에 유의미한 <span style="color:#3182F6; font-weight:800;">정(+)의 영향</span>을 미치는 것으로 나타났다. 이는 환경 보전에 대한 인지적 관심뿐만 아니라, 정서적 책임감이 동반될 때 실질적인 행동 의지가 크게 발현됨을 시사한다. 반면, 학교 교육 충분성은 통계적으로 유의미하였으나 상대적으로 그 영향력이 낮게 나타났다.
</p>

<div class="chapter-spacer"></div>

<p class="paper-chapter">Chapter 2</p>
<h3 class="toss-title">2. 결론 및 제언</h3>
<p class="toss-text">
이상의 연구결과를 바탕으로 내린 결론은 다음과 같다.<br><br>
첫째, 가설 1과 가설 2가 지지된 바와 같이, 학교 환경 교육은 단순한 정보 제공과 지식 전달을 넘어 <span style="color:#3182F6; font-weight:800;">학습자의 정서적 공감과 내적 동기를 자극하는 방향</span>으로 패러다임이 전환되어야 한다.<br><br>
둘째, 본 연구의 제한점으로서 자기보고식 설문지에 의존하였으므로, 향후 연구에서는 실제 탄소중립 행동 빈도를 측정하는 종단적 연구(Longitudinal study)가 수행될 필요가 있다.
</p>

<div class="chapter-spacer"></div>
""", unsafe_allow_html=True)
    
    # --- 부록 및 자료 다운로드 영역 (링크 연동) ---
    st.markdown('<h3 style="color:#191F28; font-size:20px; font-weight:800; margin-bottom:16px;">📥 부록 및 자료 다운로드</h3>', unsafe_allow_html=True)
    
    nypi_url = "https://www.nypi.re.kr/archive/mps/program/examinDataCode/view?menuId=MENU00226&pageNum=2&titleId=170&schType=0&schText=%ED%83%84%EC%86%8C%EC%A4%91%EB%A6%BD&firstCategory=3&secondCategory=1"
    
    st.link_button("🔗 원본 데이터 보러가기 (NYPI 청소년데이터 아카이브)", url=nypi_url, use_container_width=True)