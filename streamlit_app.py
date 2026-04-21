import streamlit as st
import pandas as pd
import numpy as np
import statsmodels.api as sm
import altair as alt
import requests
import time

# --- 페이지 설정 ---
st.set_page_config(
    page_title="Eco-Analysis",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 상수 및 초기 데이터 설정 ---
VAR_NAMES = {
    "Q9": "탄소중립 실천 의지",
    "Q4A1": "기후변화 관심도",
    "Q7A5": "생활습관 죄책감",
    "Q8A1": "학교 교육 충분성"
}

# 가상의 초기 데이터 생성 함수
@st.cache_data
def generate_mock_data(count=2800):
    np.random.seed(42)
    data = {
        "Q9": np.random.randint(1, 6, count),
        "Q4A1": np.random.randint(1, 6, count),
        "Q7A5": np.random.randint(1, 6, count),
        "Q8A1": np.random.randint(1, 6, count),
    }
    # 실제와 비슷한 회귀 결과를 위해 상관관계 부여
    data["Q9"] = np.clip(np.round(0.4 * data["Q4A1"] + 0.3 * data["Q7A5"] + 0.1 * data["Q8A1"] + np.random.normal(0, 0.5, count)), 1, 5)
    return pd.DataFrame(data)

@st.cache_data
def load_data():
    try:
        # 실제 eco.csv 파일이 같은 폴더에 있으면 우선 로드합니다.
        return pd.read_csv("eco.csv")
    except FileNotFoundError:
        # 파일이 없을 경우 2800개의 가상 데이터를 사용합니다.
        st.warning("⚠️ 'eco.csv' 파일을 찾을 수 없어 2,800개의 테스트용 임시 데이터를 사용합니다.")
        return generate_mock_data(2800)

# --- 커스텀 CSS (React 버전의 Tailwind CSS 스타일 모방) ---
st.markdown("""
<style>
    /* 전체 폰트 및 백그라운드 */
    .stApp { background-color: #F9FAFB; }
    
    /* 카드 디자인 */
    .styled-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        margin-bottom: 1rem;
    }
    .dark-card {
        background-color: #0F172A;
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        margin-bottom: 1rem;
    }
    
    /* 알림 박스 */
    .alert-box {
        background-color: #FFFBEB;
        border: 1px solid #FDE68A;
        padding: 1.5rem;
        border-radius: 1rem;
        color: #92400E;
        display: flex;
        gap: 1rem;
    }
    
    /* 요약 박스 */
    .summary-box {
        background-color: white;
        border-left: 4px solid #2563EB;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* 사이드바 스타일링 */
    [data-testid="stSidebar"] {
        background-color: white;
        border-right: 1px solid #E2E8F0;
    }
    .sidebar-title { color: #2563EB; font-size: 1.5rem; font-weight: 800; margin-bottom: 0; }
    .sidebar-subtitle { color: #94A3B8; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 2rem;}
</style>
""", unsafe_allow_html=True)

# --- 사이드바 ---
with st.sidebar:
    st.markdown('<p class="sidebar-title">📊 Eco-Analysis</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-subtitle">CARBON NEUTRAL RESEARCH</p>', unsafe_allow_html=True)
    
    active_tab = st.radio(
        "메뉴 이동",
        ["과제 소개", "데이터 안내", "회귀 분석", "결과 및 회고"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # 들여쓰기 오류 수정됨
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.info(f"**종속변수:**\n{VAR_NAMES['Q9']} (Q9)\n\n**독립변수:**\nQ4A1, Q7A5, Q8A1")

# --- 데이터 로드 ---
df = load_data()

# --- 메인 컨텐츠 헤더 ---
if active_tab == '과제 소개':
    st.title("📘 과제형 탄소중립 실천 요인 분석")
    st.caption("청소년의 실천 의지에 영향을 미치는 심리적, 교육적 요인 탐색")
elif active_tab == '데이터 안내':
    st.title("📊 데이터 구조 및 기초 통계")
    st.caption("분석에 사용된 유효 표본 및 변수 구성 확인")
elif active_tab == '회귀 분석':
    st.title("📈 다중 선형 회귀 분석")
    st.caption("OLS(최소자승법)를 이용한 변수 간의 인과관계 추정")
elif active_tab == '결과 및 회고':
    st.title("📝 분석 결과 및 정책 제언")
    st.caption("데이터 기반의 인사이트 도출 및 최종 리포트")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 1. 과제 소개 탭
# ==========================================
if active_tab == '과제 소개':
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="styled-card">
            <h3 style="color: #1E293B; margin-top: 0;">1️⃣ 과제 목표</h3>
            <p style="color: #475569; line-height: 1.6;">
                본 프로젝트는 청소년의 <strong>탄소중립 실천 의지</strong>에 어떠한 요인이 가장 큰 영향을 미치는지 실증적으로 분석합니다. 
                단순한 설문을 넘어 통계적 모델링을 통해 학교 교육의 방향성을 제시하는 것이 핵심입니다.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="styled-card">
            <h3 style="color: #1E293B; margin-top: 0;">2️⃣ 수행 과제</h3>
            <ul style="color: #475569; line-height: 1.6;">
                <li>데이터셋 이해 및 전처리 (결측치 확인)</li>
                <li>지정 변수(Q9, Q4A1, Q7A5, Q8A1) 기반 모델링</li>
                <li>다중 회귀 분석 결과 해석 및 시각화</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="dark-card">
        <h3 style="margin-top: 0; color: white;">⚙️ 분석 로직 가이드</h3>
        <p style="color: #94A3B8; margin-bottom: 0;">
            본 시스템은 Python의 Statsmodels 라이브러리를 활용한 OLS 연산 엔진을 통해 정확한 회귀 계수와 통계적 유의성을 산출합니다.<br>
            [데이터 로드] ➔ [회귀 모델링] ➔ [결과 해석 및 시각화]
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 데이터 안내 탭
# ==========================================
elif active_tab == '데이터 안내':
    # 결측치 실제 계산 로직 추가
    analysis_vars = ['Q9', 'Q4A1', 'Q7A5', 'Q8A1']
    available_vars = [col for col in analysis_vars if col in df.columns]
    
    temp_df = df[available_vars].copy()
    for col in available_vars:
        temp_df[col] = pd.to_numeric(temp_df[col], errors='coerce')
        
    valid_rows = len(temp_df.dropna())
    missing_rows = len(df) - valid_rows

    # 4개 메트릭스
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("전체 표본 수", f"{len(df):,}명")
    m2.metric("유효 데이터", f"{valid_rows:,}건", f"-{missing_rows} 결측치 제외")
    m3.metric("독립 변수 개수", "3개")
    m4.metric("종속 변수 개수", "1개")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 변수 구성 테이블
    st.markdown('<div class="styled-card"><h4 style="margin-top:0;">📋 변수 구성 설명</h4>', unsafe_allow_html=True)
    var_table = pd.DataFrame({
        "변수 유형": ["종속 변수", "독립 변수 1", "독립 변수 2", "독립 변수 3"],
        "ID": ["Q9", "Q4A1", "Q7A5", "Q8A1"],
        "설명": ["탄소중립 실천 의지", "기후변화 관심도", "생활습관에 대한 죄책감 수준", "학교 교육의 충분성"],
        "척도": ["5점 리커트", "5점 리커트", "5점 리커트", "5점 리커트"]
    })
    st.dataframe(var_table, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 알림 박스
    st.markdown("""
    <div class="alert-box">
        <div>💡</div>
        <div>
            <h4 style="margin: 0 0 0.5rem 0; color: #92400E;">데이터 특이사항</h4>
            <p style="margin: 0; font-size: 0.9rem;">
                세 독립변수는 각각 <strong>관심(인지)</strong>, <strong>감정(정서)</strong>, <strong>교육(외부)</strong> 측면을 대표하며, 다중회귀 분석에서 각 영역의 기여를 비교할 수 있도록 구성되었습니다.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. 회귀 분석 탭
# ==========================================
elif active_tab == '회귀 분석':
    # 전처리: 결측치 제거 및 타입 변환 (회귀분석 에러 방지용 핵심 코드)
    analysis_vars = ['Q9', 'Q4A1', 'Q7A5', 'Q8A1']
    analysis_df = df.copy()
    
    for col in analysis_vars:
        if col in analysis_df.columns:
            # 문자형 데이터(공백 등)가 섞여 있으면 숫자로 강제 변환 (오류는 NaN 처리)
            analysis_df[col] = pd.to_numeric(analysis_df[col], errors='coerce')
            
    # 결측치(NaN)가 하나라도 포함된 행은 분석에서 제외
    analysis_df = analysis_df.dropna(subset=[col for col in analysis_vars if col in analysis_df.columns])
    
    if len(analysis_df) == 0:
        st.error("🚨 분석할 수 있는 유효한 데이터가 없습니다. CSV 파일 내의 데이터 포맷을 확인해주세요.")
        st.stop()
        
    st.info(f"✅ 결측치 처리 후 실제 회귀 분석에 사용된 표본 수: **{len(analysis_df):,}개**")

    # OLS 회귀 분석 실행
    X = analysis_df[['Q4A1', 'Q7A5', 'Q8A1']]
    Y = analysis_df['Q9']
    X_with_const = sm.add_constant(X)
    model = sm.OLS(Y, X_with_const).fit()
    
    # 1. 히스토그램 (Altair)
    st.markdown('#### 📊 독립변수 분포')
    charts_cols = st.columns(3)
    for i, var in enumerate(['Q4A1', 'Q7A5', 'Q8A1']):
        with charts_cols[i]:
            value_counts = analysis_df[var].value_counts().sort_index().reset_index()
            value_counts.columns = [var, '빈도']
            chart = alt.Chart(value_counts).mark_bar(color="#60A5FA", cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                x=alt.X(f"{var}:N", title=f"{VAR_NAMES[var]} ({var})", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("빈도:Q", title="응답 수"),
                tooltip=[var, '빈도']
            ).properties(height=250)
            st.markdown(f"**{VAR_NAMES[var]}**")
            st.altair_chart(chart, use_container_width=True)

    st.markdown("---")

    # 2. 결과 테이블 & 평가 지표 (2단 레이아웃)
    col_results, col_metrics = st.columns([1.5, 1])
    
    with col_results:
        st.markdown('#### 📋 OLS 회귀 계수 (Coefficients)')
        
        # 보다 안전하게 summary table 추출 (배열 길이 오류 원천 차단)
        summary_table = model.summary2().tables[1].reset_index()
        summary_table.columns = ['변수', 'B (계수)', '표준오차', 't-값', 'p-값', '95% CI 하한', '95% CI 상한']
        
        # 변수명 매핑
        var_mapping = {
            'const': '상수항 (Intercept)',
            'Q4A1': 'Q4A1 (관심도)',
            'Q7A5': 'Q7A5 (죄책감)',
            'Q8A1': 'Q8A1 (교육)'
        }
        summary_table['변수'] = summary_table['변수'].map(lambda x: var_mapping.get(x, x))
        
        # p-값 유의성 표시 추가
        def get_significance(p):
            if p < 0.01: return '***'
            elif p < 0.05: return '**'
            elif p < 0.1: return '*'
            else: return 'n.s.'
            
        summary_table['유의성'] = summary_table['p-값'].apply(get_significance)
        
        st.dataframe(
            summary_table[['변수', 'B (계수)', 't-값', 'p-값', '유의성']].style.format({'B (계수)': '{:.4f}', 't-값': '{:.2f}', 'p-값': '{:.4f}'})
                         .map(lambda x: 'color: #10B981; font-weight: bold' if x in ['***', '**'] else '', subset=['유의성']),
            use_container_width=True, hide_index=True
        )

    with col_metrics:
        st.markdown('#### 🎯 모델 적합도 평가')
        st.markdown(f"""
        <div class="styled-card" style="padding: 1rem;">
            <div style="display:flex; justify-content:space-between; margin-bottom:10px; border-bottom:1px solid #eee; padding-bottom:5px;">
                <span style="color:#64748b; font-weight:600;">결정계수 (R²)</span>
                <span style="color:#2563eb; font-weight:800; font-size:1.1em;">{model.rsquared:.4f}</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:10px; border-bottom:1px solid #eee; padding-bottom:5px;">
                <span style="color:#64748b; font-weight:600;">조정 결정계수</span>
                <span style="color:#2563eb; font-weight:800; font-size:1.1em;">{model.rsquared_adj:.4f}</span>
            </div>
            <div style="display:flex; justify-content:space-between; padding-bottom:5px;">
                <span style="color:#64748b; font-weight:600;">F-통계량</span>
                <span style="color:#0f172a; font-weight:800; font-size:1.1em;">{model.fvalue:.2f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 4. 결과 및 회고 탭
# ==========================================
elif active_tab == '결과 및 회고':
    st.markdown("""
    <div class="summary-box">
        <h3 style="margin-top:0; color:#1E293B;">📝 분석 결론 (Summary)</h3>
        <p style="color:#475569; font-size:1.05rem;">
            본 분석 결과, 청소년의 탄소중립 실천 의지에 가장 큰 영향을 미치는 독립변수는 <strong>기후변화 관심도(Q4A1)</strong>와 <strong>생활습관 죄책감(Q7A5)</strong>으로 나타났습니다.
        </p>
        <ul style="color:#475569; background:#F8FAFC; padding:1.5rem 1.5rem 1.5rem 2.5rem; border-radius:0.5rem; line-height:1.8;">
            <li><strong style="color:#2563EB;">인식의 중요성:</strong> 기후변화에 대한 관심이 높을수록 실천 의지가 정비례하여 크게 증가합니다.</li>
            <li><strong style="color:#2563EB;">정서적 동기:</strong> 죄책감과 같은 정서적 요인이 교육적 충분성보다 실천을 유도하는 더 강한 행동 동기로 작용합니다.</li>
            <li><strong style="color:#2563EB;">교육의 질:</strong> 학교 교육 충분성은 유의미하나, 실질적 행동 변화를 위해선 정서 및 인식 개선 교육과의 결합이 필수적입니다.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>#### 📥 산출물 다운로드", unsafe_allow_html=True)
    d1, d2 = st.columns(2)
    with d1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 분석 데이터 세트 (CSV)",
            data=csv,
            file_name="eco_analysis_data.csv",
            mime="text/csv",
            use_container_width=True
        )
    with d2:
        # Streamlit에서는 기본적으로 PDF 생성이 복잡하므로 텍스트 리포트로 대체하여 다운로드 제공
        report = "탄소중립 실천 요인 분석 결과 요약 리포트\n\n(상세 내용은 웹페이지 결과 참조)"
        st.download_button(
            label="📄 최종 결과 리포트 (TXT)",
            data=report,
            file_name="research_report.txt",
            mime="text/plain",
            use_container_width=True
        )