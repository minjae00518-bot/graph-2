import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")

# 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    
    # [수정된 부분] 장르가 비어있는(결측치) 행(데이터)을 아예 삭제합니다.
    df = df.dropna(subset=['genre'])
    
    # 장르 열 전처리: 세로막대 기호(|)로 나뉘어 있으면 첫 번째 장르만 사용
    df['genre'] = df['genre'].astype(str).apply(lambda x: x.split('|')[0].strip() if pd.notna(x) and '|' in x else str(x).strip())
    
    # [수정된 부분] 혹시라도 문자열 'nan'으로 바뀐 데이터가 남아있다면 그것도 제외합니다.
    df = df[df['genre'] != 'nan']
    
    return df

df = load_data()

# -------------------------------------------------------------------
# 구역 1: 장르별 영화 편수 (도넛 그래프)
# -------------------------------------------------------------------
st.divider()

with st.container():
    st.subheader("📌 장르별 영화 편수 분포")
    
    genre_counts = df['genre'].value_counts().reset_index()
    genre_counts.columns = ['장르', '편수']

    fig1 = px.pie(
        genre_counts, 
        names='장르', 
        values='편수', 
        title='장르별 영화 편수 (도넛 차트)',
        hole=0.4
    )
    
    # 텍스트가 밖으로 튀어나오지 않도록 안쪽에만 표시되게 설정
    fig1.update_traces(
        textposition='inside',
        hovertemplate="<b>%{label}</b><br>편수: %{value}편<br>비율: %{percent}<extra></extra>"
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.info("💡 **이 그래프로 알 수 있는 것:** 상위 몇 개 장르가 전체 개봉작 중 상당한 비중을 차지하고 있어, 특정 장르 선호 현상이 뚜렷하게 나타남을 알 수 있습니다.")


# -------------------------------------------------------------------
# 구역 2: 장르 안의 영화 (트리맵)
# -------------------------------------------------------------------
st.divider()

with st.container():
    st.subheader("📌 장르별 총 관객 수 및 세부 영화")
    
    fig2 = px.treemap(
        df, 
        path=['genre', 'movieNm'], 
        values='total_audi',
        title='장르 및 영화별 총 관객 수 비중 (트리맵)'
    )
    
    fig2.update_traces(
        hovertemplate="<b>%{label}</b><br>총 관객: %{value:,.0f}명<extra></extra>"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.info("💡 **이 그래프로 알 수 있는 것:** 같은 장르 안에서도 소수의 흥행 대작(큰 칸)이 전체 관객 수의 대부분을 견인하고 있음을 확인할 수 있습니다.")


# -------------------------------------------------------------------
# 구역 3: 총 관객 수 분포 (히스토그램)
# -------------------------------------------------------------------
st.divider()

with st.container():
    st.subheader("📌 총 관객 수 분포")
    
    fig3 = px.histogram(
        df, 
        x='total_audi', 
        nbins=20,
        title='총 관객 수 히스토그램',
        labels={'total_audi': '총 관객 수'}
    )
    
    fig3.update_traces(
        hovertemplate="총 관객 수 범위: %{x}<br>영화 편수: %{y}편<extra></extra>"
    )

    st.plotly_chart(fig3, use_container_width=True)

    max_movie_name = df.loc[df['total_audi'].idxmax(), 'movieNm']
    counts, bins = np.histogram(df['total_audi'].dropna(), bins=20)
    max_bin_idx = counts.argmax()
    min_audi_range = int(bins[max_bin_idx])
    max_audi_range = int(bins[max_bin_idx + 1])

    st.info(f"💡 **이 그래프로 알 수 있는 것:** 대부분의 영화가 **{min_audi_range:,}명 ~ {max_audi_range:,}명** 구간에 몰려 있으며, 가장 관객이 많은 영화는 **'{max_movie_name}'**입니다.")


# -------------------------------------------------------------------
# 구역 4: 개봉일 스크린수와 총 관객 수 (산점도)
# -------------------------------------------------------------------
st.divider()

with st.container():
    st.subheader("📌 개봉일 스크린수와 총 관객 수의 관계")
    
    fig4 = px.scatter(
        df, 
        x='first_scrn', 
        y='total_audi', 
        color='genre',          
        hover_name='movieNm',   
        title='개봉일 스크린수 vs 총 관객 수 (산점도)',
        labels={
            'first_scrn': '개봉일 스크린수 (개)', 
            'total_audi': '총 관객 수 (명)',
            'genre': '장르'
        }
    )
    
    fig4.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린수: %{x}개<br>총 관객 수: %{y}명<extra></extra>"
    )

    st.plotly_chart(fig4, use_container_width=True)

    st.info("💡 **이 그래프로 알 수 있는 것:** 개봉일 스크린수가 많을수록 대체로 총 관객 수도 늘어나는 경향(양의 상관관계)이 있으며, 특정 영화가 스크린수 대비 얼마나 흥행했는지 장르별로 비교해 볼 수 있습니다.")


# -------------------------------------------------------------------
# 구역 5: 주요 장르별 총 관객 수 분포 (상자 그림)
# -------------------------------------------------------------------
st.divider()

with st.container():
    st.subheader("📌 주요 장르별 총 관객 수 분포")
    
    genre_counts_series = df['genre'].value_counts()
    major_genres = genre_counts_series[genre_counts_series >= 10].index
    df_box = df[df['genre'].isin(major_genres)]
    
    fig5 = px.box(
        df_box, 
        x='genre', 
        y='total_audi', 
        color='genre',          
        hover_name='movieNm',   
        title='영화 10편 이상 장르의 총 관객 수 상자 그림(Box Plot)',
        labels={
            'genre': '장르', 
            'total_audi': '총 관객 수 (명)'
        }
    )
    
    st.plotly_chart(fig5, use_container_width=True)

    st.info("💡 **이 그래프로 알 수 있는 것:** 주요 장르들의 일반적인 관객 수 범위(상자의 크기와 위치)를 비교할 수 있으며, 일반적인 범위를 벗어나 예외적으로 큰 흥행을 기록한 영화(상자 밖의 점)들을 파악할 수 있습니다.")


# -------------------------------------------------------------------
# 구역 6: 개봉일 스크린수, 첫 주 관객, 총 관객 수 (버블 그래프)
# -------------------------------------------------------------------
st.divider()

with st.container():
    st.subheader("📌 초반 화력과 최종 흥행의 관계 (버블 그래프)")
    
    fig6 = px.scatter(
        df, 
        x='first_scrn', 
        y='total_audi', 
        size='first_week_audi', 
        color='genre',          
        hover_name='movieNm',   
        custom_data=['first_week_audi'], 
        title='개봉일 스크린수 vs 총 관객 수 (점 크기: 개봉 첫 주 관객)',
        labels={
            'first_scrn': '개봉일 스크린수 (개)', 
            'total_audi': '총 관객 수 (명)',
            'first_week_audi': '개봉 첫 주 관객 (명)',
            'genre': '장르'
        },
        size_max=40 
    )
    
    fig6.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "개봉일 스크린수: %{x}개<br>"
            "총 관객 수: %{y}명<br>"
            "첫 주 관객 수: %{customdata[0]}명<extra></extra>"
        )
    )

    st.plotly_chart(fig6, use_container_width=True)

    st.info("💡 **이 그래프로 알 수 있는 것:** 점의 크기(개봉 첫 주 관객)가 클수록 그래프 위쪽(총 관객 수)에 위치하는 경향을 통해, 초반 화력이 최종 흥행 성적과 매우 깊게 연관되어 있음을 시각적으로 확인할 수 있습니다.")


# -------------------------------------------------------------------
# 구역 7: 제작 국가 및 장르 분포 (선버스트 그래프)
# -------------------------------------------------------------------
st.divider()

with st.container():
    st.subheader("📌 제작 국가 및 장르 계층 분포 (선버스트 그래프)")
    
    df_sunburst = df.copy()
    df_sunburst['movie_count'] = 1
    
    # 국가 데이터가 없는 경우만 '알 수 없음'으로 처리
    df_sunburst['nation'] = df_sunburst['nation'].fillna('알 수 없음')
    
    fig7 = px.sunburst(
        df_sunburst,
        path=['nation', 'genre'],
        values='movie_count',
        title='제작 국가별 장르 분포',
        labels={'nation': '제작 국가', 'genre': '장르'}
    )
    
    fig7.update_traces(
        hovertemplate="<b>%{label}</b><br>영화 편수: %{value}편<extra></extra>"
    )
    
    st.plotly_chart(fig7, use_container_width=True)

    st.info("💡 **이 그래프로 알 수 있는 것:** 각 제작 국가별로 주력하는 장르가 무엇인지, 전체 영화 편수 중 국가와 장르가 차지하는 비중을 중심에서 바깥쪽으로 한눈에 파악할 수 있습니다.")


# -------------------------------------------------------------------
# 구역 8: 월별 개봉 편수 흐름 (막대 그래프)
# -------------------------------------------------------------------
st.divider()

with st.container():
    st.subheader("📌 질문: 월별 개봉 편수 흐름은 어떻게 되는가?")
    
    # 1. 개봉일 데이터(openDt)에서 월(month) 추출
    df_month = df.copy()
    df_month['month'] = pd.to_datetime(df_month['openDt'], format='%Y%m%d', errors='coerce').dt.month
    
    df_month = df_month.dropna(subset=['month'])
    df_month['month'] = df_month['month'].astype(int)
    
    # 2. 월별 영화 개봉 편수 집계
    monthly_stats = df_month.groupby('month').agg(
        movie_count=('movieNm', 'count')
    ).reindex(range(1, 13), fill_value=0).reset_index() 
    
    monthly_stats['month_str'] = monthly_stats['month'].astype(str) + '월'
    
    # 3. 플롯리 막대 그래프 생성 (단일 지표)
    fig8 = px.bar(
        monthly_stats,
        x='month_str',
        y='movie_count',
        title='월별 개봉 편수 흐름은 어떻게 되는가?',
        labels={'month_str': '개봉 월', 'movie_count': '개봉 편수 (편)'},
        text_auto=True 
    )
    
    fig8.update_traces(
        marker_color="#636EFA",
        hovertemplate="<b>%{x}</b><br>개봉 편수: %{y}편<extra></extra>"
    )
    
    st.plotly_chart(fig8, use_container_width=True)

    st.info("💡 **이 그래프로 알 수 있는 것:** 일 년 중 어느 달에 새로운 영화가 가장 많이 극장에 걸리는지 직관적으로 확인할 수 있습니다.")

st.divider()
