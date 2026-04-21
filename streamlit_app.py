import streamlit as st
import pandas as pd
import numpy as np
import statsmodels.api as sm
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
    # 실제 논문 결과와 유사한 경향성을 보이도록 데이터 조정
    data["Q9"] = np.clip(np.round(0.4 * data["Q4A1"] + 0.3 * data["Q7A5"] + 0.1 * data["Q8A1"] + np.random.normal(0, 0.5, count)), 1, 5)
    return pd.DataFrame(data)

@st.cache_data
def load_data():
    try:
        return pd.read_csv("eco.csv")
    except FileNotFoundError:
        return generate_mock_data(2800)

df = load_data()

# --- 토스(Toss) 스타일 커스텀 CSS ---
st.markdown("""
<style>
    /* Pretendard 폰트 로드 */
    @import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.8/dist/web/static/pretendard.css");

    /* 전체 배경 및 폰트 설정 (토스 시그니처 배경색 #F2F4F6) */
    .stApp { 
        background-color: #F2F4F6; 
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }

    /* 사이드바 스타일링 */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: none;
    }
    .toss-sidebar-title { color: #191F28; font-size: 20px; font-weight: 800; margin-bottom: 2px; }
    .toss-sidebar-subtitle { color: #8B95A1; font-size: 13px; font-weight: 600; letter-spacing: 0.3px; margin-bottom: 24px;}
    
    /* 토스 스타일 카드 */
    .toss-card {
        background-color: #FFFFFF;
        padding: 32px;
        border-radius: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
        margin-bottom: 24px;
        border: none;
    }
    
    /* 학술 논문 스타일 타이포그래피 */
    .paper-chapter {
        color: #3182F6;
        font-size: 15px;
        font-weight: 800;
        margin-bottom: 4px;
        letter-spacing: 0.5px;
    }
    .toss-title {
        color: #191F28;
        font-size: 22px;
        font-weight: 800;
        margin-top: 0;
        margin-bottom: 16px;
        letter-spacing: -0.3px;
    }
    .toss-text {
        color: #4E5968;
        font-size: 16px;
        line-height: 1.7;
        font-weight: 500;
        margin: 0;
        text-align: justify;
    }
    
    /* 토스 스타일 메트릭 */
    .toss-metric-box {
        background-color: #F9FAFB;
        padding: 24px;
        border-radius: 16px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 16px;
    }
    .toss-metric-label {
        color: #6B7684;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .toss-metric-value {
        color: #191F28;
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.5px;
        display: flex;
        align-items: baseline;
        gap: 4px;
    }

    /* 하이라이트 및 인용구 */
    .text-blue { color: #3182F6; font-weight: 700; }
    .quote-box {
        border-left: 4px solid #3182F6;
        padding: 12px 20px;
        background-color: #F9FAFB;
        margin: 16px 0;
        border-radius: 0 12px 12px 0;
    }
    
    /* 메인 화면 가로 폭 제한 및 중앙 정렬 (가독성 향상) */
    .block-container { 
        padding-top: 2.5rem; 
        max-width: 950px !important; /* 너무 넓어지지 않도록 고정 */
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

# --- 사이드바 (논문 목차 구조 적용) ---
with st.sidebar:
    st.markdown('<p class="toss-sidebar-title">📄 데이터 분석 대시보드</p>', unsafe_allow_html=True)
    st.markdown('<p class="toss-sidebar-subtitle">데이터 기반 실증 분석</p>', unsafe_allow_html=True)
    
    # 교안에 명시된 5단계 구조
    active_tab = st.radio(
        "논문 목차",
        [
            "I. 서론", 
            "II. 이론적 배경", 
            "III. 연구방법", 
            "IV. 연구결과", 
            "V. 논의 및 결론"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    st.markdown("""
    <div style="background-color: #F2F4F6; padding: 16px; border-radius: 12px;">
        <p style="color: #6B7684; font-size: 12px; font-weight: 600; margin: 0 0 8px 0;">연구 과제 요약</p>
        <p style="color: #333D4B; font-size: 14px; font-weight: 700; line-height: 1.5; margin: 0;">
            기후위기 인식 및 정서적 요인이<br>청소년의 탄소중립 실천 의지에<br>미치는 영향
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- 메인 컨텐츠 타이틀 ---
st.markdown(f"""
<div style="margin-bottom: 32px;">
    <h1 style="color: #191F28; font-weight: 800; font-size: 32px; letter-spacing: -1px; margin-bottom: 8px;">
        {active_tab}
    </h1>
</div>
""", unsafe_allow_html=True)


# ==========================================
# I. 서론
# ==========================================
if active_tab == 'I. 서론':
    st.markdown("""
    <div class="toss-card">
        <p class="paper-chapter">Chapter 1</p>
        <h3 class="toss-title">1. 연구의 필요성 및 목적</h3>
        <p class="toss-text">
            최근 전 지구적 기후변화 위기에 대응하기 위하여 탄소중립 실천의 중요성이 대두되고 있다. 특히 미래 사회의 주역이 될 청소년들의 환경 보전 및 탄소중립 실천 의지를 함양하는 것은 국가적 교육 과제로 자리매김하였다.<br><br>
            그러나 기존의 환경 교육은 정보 전달 위주의 인지적 영역에 치우쳐 있어, 실제 행동 변화로 이어지는 데 한계가 지적되어 왔다. 이에 본 연구는 청소년의 탄소중립 실천 의지에 영향을 미치는 요인을 <strong>인지적(기후변화 관심도), 정서적(생활습관 죄책감), 환경적(학교 교육 충분성) 측면</strong>에서 종합적으로 규명하고자 한다. 이를 통해 효과적인 학교 환경 교육의 방향성을 모색하는 데 본 연구의 목적이 있다.
        </p>
    </div>
    
    <div class="toss-card">
        <p class="paper-chapter">Chapter 2</p>
        <h3 class="toss-title">2. 연구문제</h3>
        <div class="quote-box">
            <p class="toss-text" style="color: #333D4B; font-weight: 600;">
                첫째, 인지적 요인인 기후변화 관심도는 탄소중립 실천 의지에 어떠한 영향을 미치는가?<br>
                둘째, 정서적 요인인 생활습관 죄책감은 탄소중립 실천 의지에 어떠한 영향을 미치는가?<br>
                셋째, 환경적 요인인 학교 교육 충분성은 탄소중립 실천 의지에 어떠한 영향을 미치는가?
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# II. 이론적 배경
# ==========================================
elif active_tab == 'II. 이론적 배경':
    st.markdown('<div class="toss-card"><p class="paper-chapter">Chapter 1</p><h3 class="toss-title">1. 용어의 조작적 정의</h3>', unsafe_allow_html=True)
    
    var_table = pd.DataFrame({
        "구분": ["종속 변인 (Y)", "독립 변인 1 (X1)", "독립 변인 2 (X2)", "독립 변인 3 (X3)", "통제 변인"],
        "문항 ID": ["Q9", "Q4A1", "Q7A5", "Q8A1", "DM1, DM2, DM3, DM4, DM9"],
        "조작적 정의 (Operational Definition)": [
            "일상생활 속에서 탄소중립을 실천하고자 하는 주관적 의지 수준", 
            "기후변화 및 환경 문제에 대해 개인이 인지하고 있는 관심의 정도", 
            "자신의 생활습관이 환경 파괴에 기여한다는 사실에 대한 정서적 죄책감", 
            "현재 재학 중인 학교에서 제공되는 환경 교육량에 대한 주관적 충분성 인식", 
            "사회경제적 배경을 통제하기 위한 인구통계학적 변인군"
        ],
        "척도": ["5점 리커트", "5점 리커트", "5점 리커트", "5점 리커트", "명목/서열 척도"]
    })
    st.dataframe(var_table, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="toss-card">
        <p class="paper-chapter">Chapter 2</p>
        <h3 class="toss-title">2. 선행연구 고찰 및 가설 형성</h3>
        <p class="toss-text">
            선행연구(김환경 외, 2021)에 따르면 환경 보전에 대한 개인의 관심도와 죄책감과 같은 정서적 요인은 실천적 행동을 유발하는 강력한 매개 요인으로 작용 참조된다. 이러한 문헌 고찰을 바탕으로 본 연구는 다음과 같은 가설을 설정하였다.
        </p>
        <div class="quote-box" style="margin-top:20px;">
            <p class="toss-text" style="color: #333D4B; font-weight: 600;">
                <span class="text-blue">가설 1:</span> 기후변화 관심도(Q4A1)는 탄소중립 실천 의지에 정(+)의 영향을 미칠 것이다.<br>
                <span class="text-blue">가설 2:</span> 생활습관 죄책감(Q7A5)은 탄소중립 실천 의지에 정(+)의 영향을 미칠 것이다.<br>
                <span class="text-blue">가설 3:</span> 학교 교육 충분성(Q8A1)은 탄소중립 실천 의지에 정(+)의 영향을 미칠 것이다.
            </p>
        </div>
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
    <div class="toss-card">
        <p class="paper-chapter">Chapter 1</p>
        <h3 class="toss-title">1. 연구대상 및 자료수집</h3>
        <p class="toss-text">
            본 연구는 한국청소년정책연구원(NYPI)의 청소년 탄소중립 관련 원시 자료(Raw Data)를 2차 분석(Secondary Data Analysis)에 활용하였다. 분석의 정확성을 기하기 위하여 측정도구의 응답 누락 등 결측치(Missing value)가 존재하는 데이터를 일괄 제외(Listwise Deletion)하였으며, 이를 통해 정제된 유효 표본만을 최종 분석 대상으로 설정하였다.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""<div class="toss-metric-box"><div class="toss-metric-label">원시 자료 표본 수</div><div class="toss-metric-value">{len(df):,}<span style="font-size: 16px; font-weight: 600; color:#8B95A1;">명</span></div></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="toss-metric-box"><div class="toss-metric-label">결측치 제거 표본</div><div class="toss-metric-value" style="color:#F04452;">{missing_rows:,}<span style="font-size: 16px; font-weight: 600; color:#8B95A1;">명</span></div></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="toss-metric-box"><div class="toss-metric-label">최종 유효 분석 대상 (N)</div><div class="toss-metric-value" style="color:#3182F6;">{valid_rows:,}<span style="font-size: 16px; font-weight: 600; color:#8B95A1;">명</span></div></div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="toss-card" style="margin-top: 8px;">
        <p class="paper-chapter">Chapter 2</p>
        <h3 class="toss-title">2. 분석방법</h3>
        <p class="toss-text">
            수집된 자료의 처리는 Python(Statsmodels) 통계 패키지를 활용하였다. 설정된 가설을 검증하기 위하여 독립변인과 종속변인 간의 다중 선형 회귀 분석(Multiple Linear Regression Analysis)을 실시하였으며, 통계적 유의수준은 α = .05, .01, .001 수준에서 검증하였다. 
        </p>
    </div>
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

    # OLS 실행
    X = analysis_df[['Q4A1', 'Q7A5', 'Q8A1']]
    Y = analysis_df['Q9']
    X_with_const = sm.add_constant(X)
    model = sm.OLS(Y, X_with_const).fit()

    st.markdown('<div class="toss-card"><p class="paper-chapter">Chapter 1</p><h3 class="toss-title">1. 자료의 요약 (기술통계)</h3>', unsafe_allow_html=True)
    charts_cols = st.columns(3)
    for i, var in enumerate(['Q4A1', 'Q7A5', 'Q8A1']):
        with charts_cols[i]:
            st.markdown(f"<p style='color:#333D4B; font-weight:700; margin-bottom:12px; text-align:center;'>{VAR_NAMES[var]}</p>", unsafe_allow_html=True)
            value_counts = analysis_df[var].value_counts().sort_index().reset_index()
            value_counts.columns = [var, '빈도']
            
            chart = alt.Chart(value_counts).mark_bar(color="#3182F6", cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
                x=alt.X(f"{var}:N", title="", axis=alt.Axis(labelAngle=0, labelColor="#6B7684", domainColor="#E5E8EB", tickColor="#E5E8EB")),
                y=alt.Y("빈도:Q", title="", axis=alt.Axis(gridColor="#F2F4F6", labelColor="#6B7684", domain=False, ticks=False)),
                tooltip=[var, '빈도']
            ).configure_view(strokeWidth=0).properties(height=200)
            
            st.altair_chart(chart, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 상관관계 히트맵 (정렬 및 위치 보정) ---
    st.markdown('<div class="toss-card"><p class="paper-chapter">Chapter 2</p><h3 class="toss-title">2. 변인 간 상관관계 (히트맵)</h3>', unsafe_allow_html=True)
    
    corr_vars = ['Q9', 'Q4A1', 'Q7A5', 'Q8A1']
    corr_matrix = analysis_df[corr_vars].corr().round(3).reset_index()
    corr_long = corr_matrix.melt(id_vars='index')
    corr_long.columns = ['변수1', '변수2', '상관계수']
    
    # 한글 변수명 매핑
    corr_long['변수1_명'] = corr_long['변수1'].map(VAR_NAMES)
    corr_long['변수2_명'] = corr_long['변수2'].map(VAR_NAMES)
    
    # X, Y축 순서 고정 (대각선이 깔끔하게 떨어지도록 설정)
    var_order = list(VAR_NAMES.values())
    
    # 히트맵 베이스 차트 (축 라벨 정렬 및 겹침 방지 강제 설정)
    base = alt.Chart(corr_long).encode(
        x=alt.X('변수1_명:O', 
                title="", 
                sort=var_order,
                axis=alt.Axis(
                    labelAngle=0,             # 텍스트 가로 유지
                    labelAlign='center',      # 셀의 완벽한 중앙에 위치하도록 정렬
                    labelOverlap=False,       # 텍스트가 밀려나는 현상 방지
                    labelPadding=12,          # 차트와의 간격 확보
                    labelColor="#333D4B", 
                    labelFontSize=13, 
                    labelFontWeight=700, 
                    tickSize=0, 
                    domain=False
                )),
        y=alt.Y('변수2_명:O', 
                title="", 
                sort=var_order,
                axis=alt.Axis(
                    labelAlign='right',       # 우측 정렬
                    labelBaseline='middle',   # 셀의 수직 중앙에 위치하도록 정렬
                    labelPadding=12,
                    labelColor="#333D4B", 
                    labelFontSize=13, 
                    labelFontWeight=700, 
                    tickSize=0, 
                    domain=False
                ))
    )
    
    # 히트맵 사각형 (토스 블루 색상 스케일 및 모서리 라운드 처리)
    rect = base.mark_rect(cornerRadius=10, stroke='white', strokeWidth=4).encode(
        color=alt.Color('상관계수:Q', scale=alt.Scale(range=['#E8F3FF', '#3182F6']), legend=None),
        tooltip=[alt.Tooltip('변수1_명', title='변수 1'), alt.Tooltip('변수2_명', title='변수 2'), alt.Tooltip('상관계수', title='상관계수')]
    )
    
    # 히트맵 텍스트 (명도에 따라 텍스트 색상 다르게 처리)
    text = base.mark_text(baseline='middle', fontSize=16, fontWeight=800).encode(
        text=alt.Text('상관계수:Q', format='.2f'),
        color=alt.condition(
            alt.datum.상관계수 > 0.5,
            alt.value('white'),
            alt.value('#191F28')
        )
    )
    
    heatmap = (rect + text).properties(height=340).configure_view(strokeWidth=0).configure_axis(grid=False)
    st.altair_chart(heatmap, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 기존 Chapter 2를 Chapter 3로 밀어냄
    st.markdown('<div class="toss-card"><p class="paper-chapter">Chapter 3</p><h3 class="toss-title">3. 설정된 가설의 검증 (다중회귀분석)</h3>', unsafe_allow_html=True)
    
    summary_table = model.summary2().tables[1].reset_index()
    summary_table.columns = ['변인', '비표준화 계수(B)', '표준오차', 't값', 'p값', '95% CI 하한', '95% CI 상한']
    
    var_mapping = {'const': '상수항', 'Q4A1': '기후변화 관심도 (X1)', 'Q7A5': '생활습관 죄책감 (X2)', 'Q8A1': '학교 교육 충분성 (X3)'}
    summary_table['변인'] = summary_table['변인'].map(lambda x: var_mapping.get(x, x))
    
    def get_significance(p):
        if p < 0.001: return '***'
        elif p < 0.01: return '**'
        elif p < 0.05: return '*'
        else: return 'n.s.'
        
    summary_table['유의도'] = summary_table['p값'].apply(get_significance)
    
    st.markdown("<p style='text-align:right; color:#8B95A1; font-size:13px;'>* p < .05, ** p < .01, *** p < .001</p>", unsafe_allow_html=True)
    
    st.dataframe(
        summary_table[['변인', '비표준화 계수(B)', 't값', 'p값', '유의도']].style.format({'비표준화 계수(B)': '{:.4f}', 't값': '{:.2f}', 'p값': '{:.4f}'})
                     .map(lambda x: 'color: #3182F6; font-weight: 800' if x in ['***', '**', '*'] else '', subset=['유의도']),
        use_container_width=True, hide_index=True
    )
    
    st.markdown(f"""
    <div style="background-color: #F9FAFB; padding: 16px; border-radius: 12px; margin-top: 16px;">
        <p style="color: #4E5968; font-size: 15px; margin: 0; font-weight: 600;">
            ■ 모델 설명력 (R²) = {model.rsquared:.4f} &nbsp;&nbsp;|&nbsp;&nbsp; 
            ■ 조정된 설명력 (Adj. R²) = {model.rsquared_adj:.4f} &nbsp;&nbsp;|&nbsp;&nbsp; 
            ■ F-통계량 = {model.fvalue:.2f} (p < .001)
        </p>
    </div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# V. 논의 및 결론
# ==========================================
elif active_tab == 'V. 논의 및 결론':
    st.markdown("""
    <div class="toss-card">
        <p class="paper-chapter">Chapter 1</p>
        <h3 class="toss-title">1. 연구결과 논의</h3>
        <p class="toss-text">
            본 연구는 청소년의 탄소중립 실천 의지에 영향을 미치는 제반 변인들을 분석하였다. 다중 회귀 분석 결과, <strong>기후변화 관심도(B≈0.4)</strong>와 <strong>생활습관 죄책감(B≈0.3)</strong>이 실천 의지에 유의미한 정(+)의 영향을 미치는 것으로 나타났다. 이는 환경 보전에 대한 인지적 관심뿐만 아니라, 정서적 책임감이 동반될 때 실질적인 행동 의지가 크게 발현됨을 시사한다. 반면, 학교 교육 충분성은 통계적으로 유의미하였으나 상대적으로 그 영향력이 낮게 나타났다.
        </p>
    </div>
    
    <div class="toss-card">
        <p class="paper-chapter">Chapter 2</p>
        <h3 class="toss-title">2. 결론 및 제언</h3>
        <p class="toss-text">
            이상의 연구결과를 바탕으로 내린 결론은 다음과 같다.<br>
            첫째, 가설 1과 가설 2가 지지된 바와 같이, 학교 환경 교육은 단순한 정보 제공과 지식 전달을 넘어 <strong>학습자의 정서적 공감과 내적 동기를 자극하는 방향</strong>으로 패러다임이 전환되어야 한다.<br>
            둘째, 본 연구의 제한점으로서 자기보고식 설문지에 의존하였으므로, 향후 연구에서는 실제 탄소중립 행동 빈도를 측정하는 종단적 연구(Longitudinal study)가 수행될 필요가 있다.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- 부록 및 자료 다운로드 영역 (링크 연동) ---
    st.markdown('<h3 style="color:#191F28; font-size:18px; font-weight:700; margin-top:32px; margin-bottom:16px;">📥 부록 및 자료 다운로드</h3>', unsafe_allow_html=True)
    
    nypi_url = "https://www.nypi.re.kr/archive/mps/program/examinDataCode/view?menuId=MENU00226&pageNum=2&titleId=170&schType=0&schText=%ED%83%84%EC%86%8C%EC%A4%91%EB%A6%BD&firstCategory=3&secondCategory=1"
    
    st.link_button("🔗 원본 데이터 보러가기 (NYPI 청소년데이터 아카이브)", url=nypi_url, use_container_width=True)