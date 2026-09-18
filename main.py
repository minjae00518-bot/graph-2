import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    
    # 장르 열 전처리: 세로막대 기호(|)로 나뉘어 있으면 첫 번째 장르만 사용
    df['genre'] = df['genre'].astype(str).apply(lambda x: x.split('|')[0].strip() if pd.notna(x) and '|' in x else str(x).strip())
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
    
    fig1.update_traces(
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
    
    df_sunburst['nation'] = df_sunburst['nation'].fillna('알 수 없음')
    df_sunburst['genre'] = df_sunburst['genre'].fillna('알 수 없음')
    
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
# 구역 8: 월별 개봉 편수와 관객 수 흐름 (이중축 차트)
# -------------------------------------------------------------------
st.divider()

with st.container():
    st.subheader("📌 질문: 월별 개봉 편수와 관객 수 흐름은 어떻게 되는가?")
    
    # 1. 개봉일 데이터(openDt)에서 월(month) 추출
    df_month = df.copy()
    # 8자리 숫자(예: 20230514)를 datetime 형식으로 변환하여 월만 추출
    df_month['month'] = pd.to_datetime(df_month['openDt'], format='%Y%m%d', errors='coerce').dt.month
    
    # 월 정보가 없는 결측치 제거 후 정수형으로 변환
    df_month = df_month.dropna(subset=['month'])
    df_month['month'] = df_month['month'].astype(int)
    
    # 2. 월별 영화 개봉 편수와 총 관객 수 집계
    monthly_stats = df_month.groupby('month').agg(
        movie_count=('movieNm', 'count'),
        total_audi=('total_audi', 'sum')
    ).reindex(range(1, 13), fill_value=0).reset_index() # 1월~12월 모든 달 표시
    
    monthly_stats['month_str'] = monthly_stats['month'].astype(str) + '월'
    
    # 3. 플롯리 이중축 차트 생성 (막대 + 꺾은선)
    fig8 = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 첫 번째 Y축 (왼쪽): 월별 개봉 편수 (막대그래프)
    fig8.add_trace(
        go.Bar(
            x=monthly_stats['month_str'], 
            y=monthly_stats['movie_count'], 
            name="개봉 편수", 
            marker_color="#636EFA",
            hovertemplate="%{x}<br>개봉 편수: %{y}편<extra></extra>"
        ),
        secondary_y=False,
    )
    
    # 두 번째 Y축 (오른쪽): 월별 총 관객 수 (꺾은선그래프 - 흐름 비교용)
    fig8.add_trace(
        go.Scatter(
            x=monthly_stats['month_str'], 
            y=monthly_stats['total_audi'], 
            name="총 관객 수", 
            mode='lines+markers',
            marker_color="#EF553B",
            line=dict(width=3),
            marker=dict(size=8),
            hovertemplate="%{x}<br>총 관객 수: %{y:,.0f}명<extra></extra>"
        ),
        secondary_y=True,
    )
    
    # 레이아웃 세부 설정
    fig8.update_layout(
        title_text='월별 개봉 편수와 관객 수 흐름은 어떻게 되는가?',
        hovermode="x unified", # 마우스를 올리면 두 지표가 동시에 보이도록 설정
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Y축 이름 설정
    fig8.update_yaxes(title_text="개봉 편수 (편)", secondary_y=False)
    fig8.update_yaxes(title_text="총 관객 수 (명)", secondary_y=True)
    
    st.plotly_chart(fig8, use_container_width=True)

    st.info("💡 **이 그래프로 알 수 있는 것:** 개봉하는 영화 편수가 많은 달(막대)과 실제로 관객이 많이 극장을 찾는 달(선)의 차이를 비교하여, 특정 성수기(여름 방학, 명절 등)의 관객 쏠림 현상을 시계열 흐름으로 확인할 수 있습니다.")

st.divider()
