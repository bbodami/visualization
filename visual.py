import streamlit as st
import pandas as pd
import plotly.express as px

# 📌 Streamlit 실행 환경 설정
st.set_page_config(page_title="대출 부도율 분석", layout="wide")

# 📌 데이터 로드
@st.cache_data
def load_data():
    df = pd.read_csv("/Users/leejeongmin/Library/Mobile Documents/com~apple~CloudDocs/핀테크/python/lending_club_sample.csv")
    
    # 🚨 필요한 컬럼만 사용
    df = df[["loan_amnt", "int_rate", "annual_inc", "fico_range_low", "dti", "loan_status", "addr_state"]]
    
    # 🚨 결측치 제거
    df = df.dropna()
    
    # 🚨 loan_status 데이터 정리
    df["loan_status"] = df["loan_status"].str.strip().str.lower()
    df["loan_status"] = df["loan_status"].apply(lambda x: 1 if x == "charged off" else 0)
    
    # 🚨 loan_status를 숫자로 변환
    df["loan_status"] = df["loan_status"].astype(int)
    
    return df

df = load_data()  # 최신 데이터 사용

# 📌 Streamlit Sidebar 설정 (디버깅 정보 포함)
st.sidebar.header("📌 사용자 입력")

loan_amnt = st.sidebar.slider("대출 금액 ($)", 1000, 40000, 8000, step=500)
int_rate = st.sidebar.slider("이자율 (%)", 5.0, 30.0, 16.9, step=0.1)
annual_inc = st.sidebar.slider("연 소득 ($)", 20000, 200000, 155000, step=5000)
fico_score = st.sidebar.slider("신용 점수 (FICO)", 300, 850, 430, step=10)
dti = st.sidebar.slider("부채비율 (DTI)", 0.0, 50.0, 34.0, step=0.5)

# 📌 🔥 디버깅 정보 강제 출력 (왼쪽 패널에서 확인 가능)
st.sidebar.write("📌 현재 슬라이더 값")
st.sidebar.write({
    "loan_amnt": loan_amnt,
    "int_rate": int_rate,
    "annual_inc": annual_inc,
    "fico_score": fico_score,
    "dti": dti
})

# 📌 필터링된 데이터 생성
filtered_df = df[
    (df["loan_amnt"].between(loan_amnt - 5000, loan_amnt + 5000)) &
    (df["int_rate"].between(int_rate - 5, int_rate + 5)) &
    (df["annual_inc"].between(annual_inc * 0.5, annual_inc * 1.5)) &
    (df["fico_range_low"].between(fico_score - 50, fico_score + 50)) &
    (df["dti"].between(dti - 10, dti + 10))
]

# 📌 🔥 `loan_status` 값 강제 출력 (왼쪽 패널에서 확인 가능)
st.sidebar.write("📌 `loan_status` 데이터 타입:", filtered_df["loan_status"].dtype)
st.sidebar.write("📌 `loan_status` 값 확인:", filtered_df["loan_status"].unique())
st.sidebar.write("📌 `loan_status` 개수:", filtered_df["loan_status"].value_counts())

# 📌 필터링된 데이터 개수 확인
st.sidebar.write("📌 필터링된 데이터 개수:", len(filtered_df))

# 📌 🚨 필터링된 데이터가 비어 있는지 강제로 확인
st.write("📌 필터링된 데이터 미리보기:")
st.write(filtered_df.head())

# 📌 차트 표시
if filtered_df.empty:
    st.warning("🚨 필터링된 데이터가 없습니다. 슬라이더 값을 조정해보세요.")
else:
    filtered_df["loan_status"] = filtered_df["loan_status"].astype(str)  # 🚨 Plotly 호환을 위해 문자열 변환

    # 📊 이자율별 부도율 차트
    st.subheader("📊 이자율에 따른 부도율 변화")
    fig = px.histogram(filtered_df, x="int_rate", color="loan_status", nbins=20, title="이자율별 부도율")
    st.plotly_chart(fig, use_container_width=True)

    # 📍 주별 대출 부도율 지도
    st.subheader("📍 주별 대출 부도율 지도")

    # 🚨 loan_status를 숫자로 변환 (mean 계산 가능하게)
    filtered_df["loan_status"] = pd.to_numeric(filtered_df["loan_status"], errors="coerce")

    # 🚨 변환 후에도 `loan_status`가 비어 있는 값이 있을 수 있으므로 확인
    st.sidebar.write("📌 변환 후 `loan_status` 데이터 타입:", filtered_df["loan_status"].dtype)
    st.sidebar.write("📌 변환 후 `loan_status` 값 확인:", filtered_df["loan_status"].unique())

    # 🚨 주별 대출 부도율 계산 (이제 정상 작동)
    state_data = filtered_df.groupby("addr_state", as_index=False)["loan_status"].mean()

    fig = px.choropleth(state_data, 
                        locations="addr_state", 
                        locationmode="USA-states", 
                        color="loan_status",
                        color_continuous_scale="Reds",
                        title="미국 주(State)별 부도율")
    st.plotly_chart(fig, use_container_width=True)

# 📌 강제 업데이트 버튼 추가
if st.sidebar.button("🔄 강제 업데이트"):
    st.rerun()
