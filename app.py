import pandas as pd
import plotly.express as px
import streamlit as st

# [추가] 실습 4-3: 가장 먼저 실행되는 st 명령어로 페이지 제목과 wide 레이아웃 설정
st.set_page_config(page_title="Titanic 대시보드", layout="wide")


def filter_data(df, sexes, classes, age_range):
    # [수정] 실습 4-5: 성별·등급 조건 먼저 적용
    f = df[df["sex"].isin(sexes) & df["pclass"].isin(classes)]
    # [수정] 실습 4-5: 나이 슬라이더가 전체 범위(0~80)가 아닐 때만 between 적용 (기본 891명 유지)
    if age_range != (0, 80):
        f = f[f["age"].between(*age_range)]
    return f


def kpi(df):
    if len(df) == 0:
        return 0, 0, 0
    n = len(df)
    rate = round(df["survived"].mean() * 100, 1)
    age = round(df["age"].mean(), 1)
    return n, rate, age


def class_rate_bar(df):
    r = (
        df.groupby("pclass")["survived"]
        .mean()
        .mul(100)
        .round(1)
        .reset_index()
    )
    fig = px.bar(
        r,
        x="pclass",
        y="survived",
        text="survived",
        title="객실 등급별 생존율(%)",
    )
    return fig


def age_hist(df):
    fig = px.histogram(
        df,
        x="age",
        color="survived",
        barmode="overlay",
        opacity=0.6,
        title="생존 여부별 나이 분포",
    )
    return fig


@st.cache_data
def load_data():
    return pd.read_csv("titanic.csv")


df = load_data()

st.title("타이타닉, 누가 살아남았나?")

# 사이드바 위젯
sexes = st.sidebar.multiselect("성별", ["male", "female"], ["male", "female"])
classes = st.sidebar.multiselect("객실 등급", [1, 2, 3], [1, 2, 3])
ages = st.sidebar.slider("나이 범위", 0, 80, (0, 80))

# [수정] 실습 4-5: 성별이나 등급을 하나도 고르지 않으면 경고 후 실행 중단
if not sexes or not classes:  # [수정]
    st.warning("성별과 등급을 하나 이상 선택하세요.")  # [수정]
    st.stop()  # [수정]

f = filter_data(df, sexes, classes, ages)

# [수정] 실습 4-5: 필터 결과가 0명이면 안내 후 실행 중단
if len(f) == 0:  # [수정]
    st.warning("조건에 맞는 승객이 없습니다.")  # [수정]
    st.stop()  # [수정]

# [추가] 실습 4-2: st.write 대신 st.columns(3) KPI 카드 3개 추가
n, rate, age = kpi(f)  # [추가]
c1, c2, c3 = st.columns(3)  # [추가]
c1.metric("승객 수", f"{n}명")  # [추가]
c2.metric("생존율", f"{rate}%")  # [추가]
c3.metric("평균 나이", f"{age}세")  # [추가]

# [추가] 실습 4-3: KPI 아래 st.columns(2)에 차트 2개 나란히 배치
left, right = st.columns(2)  # [추가]
left.plotly_chart(class_rate_bar(f), use_container_width=True)  # [추가]
right.plotly_chart(age_hist(f), use_container_width=True)  # [추가]

# [추가] 실습 4-3: 맨 아래 st.expander("데이터 보기") 안에 필터된 표 출력
with st.expander("데이터 보기"):  # [추가]
    st.dataframe(f)  # [추가]
