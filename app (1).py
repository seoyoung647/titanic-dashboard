import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Titanic 대시보드 - 심화 3", layout="wide")


def filter_data(df, sexes, classes, age_range, ports):
    f = df[
        df["sex"].isin(sexes)
        & df["pclass"].isin(classes)
        & df["embarked"].isin(ports)
    ]
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
    return px.bar(
        r,
        x="pclass",
        y="survived",
        text="survived",
        title="객실 등급별 생존율(%)",
    )


def age_hist(df):
    return px.histogram(
        df,
        x="age",
        color="survived",
        barmode="overlay",
        opacity=0.6,
        title="생존 여부별 나이 분포",
    )


def group_rate_bar(df, col):
    r = (
        df.groupby(col, observed=False)["survived"]
        .mean()
        .mul(100)
        .round(1)
        .reset_index()
    )
    return px.bar(
        r,
        x=col,
        y="survived",
        text="survived",
        title=f"{col} 기준 생존율(%)",
    )


# [추가] ③ IQR 기준 이상치 개수 계산 함수
def iqr_outlier_count(series):
    s = series.dropna()
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return int(((s < lower) | (s > upper)).sum())


@st.cache_data
def load_data():
    df = pd.read_csv("titanic.csv")
    return df.dropna(subset=["embarked"]).copy()


df = load_data()

st.title("타이타닉, 누가 살아남았나?")

sexes = st.sidebar.multiselect("성별", ["male", "female"], ["male", "female"])
classes = st.sidebar.multiselect("객실 등급", [1, 2, 3], [1, 2, 3])
ages = st.sidebar.slider("나이 범위", 0, 80, (0, 80))
ports = st.sidebar.multiselect("승선 항구", ["S", "C", "Q"], ["S", "C", "Q"])

if not sexes or not classes or not ports:
    st.warning("성별, 등급, 승선 항구를 하나 이상 선택하세요.")
    st.stop()

f = filter_data(df, sexes, classes, ages, ports)

if len(f) == 0:
    st.warning("조건에 맞는 승객이 없습니다.")
    st.stop()

# [추가] ① st.tabs로 개요 / 관계 / 이상치 3개 탭 구성
tab1, tab2, tab3 = st.tabs(["개요", "관계", "이상치"])

with tab1:
    n, rate, age = kpi(f)
    c1, c2, c3 = st.columns(3)
    c1.metric("승객 수", f"{n}명")
    c2.metric("생존율", f"{rate}%", f"{rate - 38.4:+.1f}%p")
    c3.metric("평균 나이", f"{age}세")

    left, right = st.columns(2)
    left.plotly_chart(class_rate_bar(f), use_container_width=True)
    right.plotly_chart(age_hist(f), use_container_width=True)

    selected_col = st.selectbox("생존율 비교 기준 선택", ["sex", "class", "embarked"])
    target_col = "pclass" if selected_col == "class" and "class" not in f.columns else selected_col
    st.plotly_chart(group_rate_bar(f, target_col), use_container_width=True)

    with st.expander("데이터 보기"):
        st.dataframe(f)

with tab2:
    # [추가] ② 수치형 열 상관 히트맵 (px.imshow)
    num_df = f.select_dtypes(include=[np.number])
    corr = num_df.corr(numeric_only=True).round(2)
    fig_corr = px.imshow(corr, text_auto=True, title="수치형 열 상관관계 히트맵")
    st.plotly_chart(fig_corr, use_container_width=True)

with tab3:
    # [추가] ③ 열 선택 -> IQR 이상치 수 + 박스플롯 (px.box)
    num_cols = f.select_dtypes(include=[np.number]).columns.tolist()
    outlier_col = st.selectbox("이상치를 확인할 열 선택", num_cols)
    cnt = iqr_outlier_count(f[outlier_col])
    st.metric("IQR 이상치 수", f"{cnt}개")
    fig_box = px.box(f, y=outlier_col, title=f"{outlier_col} 박스플롯")
    st.plotly_chart(fig_box, use_container_width=True)
