import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from threads_monitor.config import Config
from threads_monitor.scraper import ThreadsScraper
from threads_monitor.analyzer import PostAnalyzer

st.set_page_config(
    page_title="Threads 戀愛話題監測儀表板",
    page_icon="💕",
    layout="wide",
    initial_sidebar_state="expanded",
)

LIGHT_THEME = {
    "bg": "#ffffff",
    "card_bg": "#f8f9fa",
    "text": "#1a1a2e",
    "accent": "#e74c3c",
    "accent2": "#fd79a8",
    "border": "#e0e0e0",
    "success": "#00b894",
    "warning": "#fdcb6e",
}

st.markdown(f"""
<style>
    .stApp {{ background-color: {LIGHT_THEME['bg']}; }}
    .main-header {{
        font-size: 2.2rem; font-weight: 700;
        color: {LIGHT_THEME['accent']};
        padding: 1rem 0; border-bottom: 3px solid {LIGHT_THEME['accent2']};
        margin-bottom: 1.5rem;
    }}
    .sub-header {{
        font-size: 1.3rem; font-weight: 600;
        color: {LIGHT_THEME['text']};
        margin: 1rem 0 0.5rem 0;
    }}
    .metric-card {{
        background: {LIGHT_THEME['card_bg']};
        border-radius: 12px; padding: 1rem 1.2rem;
        border: 1px solid {LIGHT_THEME['border']};
        text-align: center;
    }}
    .metric-value {{
        font-size: 1.8rem; font-weight: 700;
        color: {LIGHT_THEME['accent']};
    }}
    .metric-label {{
        font-size: 0.8rem; color: #666;
        margin-top: 0.2rem;
    }}
    .topic-card {{
        background: white;
        border-radius: 12px; padding: 1.2rem;
        border: 1px solid {LIGHT_THEME['border']};
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }}
    .topic-title {{
        font-size: 1.1rem; font-weight: 600;
        color: {LIGHT_THEME['accent']};
        margin-bottom: 0.5rem;
    }}
    .summary-text {{
        font-size: 0.95rem; line-height: 1.6;
        color: #444; padding: 0.5rem;
        background: #fef9f9; border-radius: 8px;
        border-left: 3px solid {LIGHT_THEME['accent2']};
    }}
    .post-card {{
        background: white;
        border-radius: 10px; padding: 1rem;
        border: 1px solid {LIGHT_THEME['border']};
        margin-bottom: 0.8rem;
    }}
    .post-author {{
        font-weight: 600; color: {LIGHT_THEME['text']};
    }}
    .post-meta {{
        font-size: 0.8rem; color: #999;
    }}
    .post-text {{
        font-size: 0.9rem; line-height: 1.5;
        color: #333; margin: 0.5rem 0;
        white-space: pre-wrap;
    }}
    .post-stats {{
        display: flex; gap: 1rem;
        font-size: 0.85rem; color: #666;
        margin-top: 0.5rem;
    }}
    .comment-box {{
        background: #f5f5f5; border-radius: 8px;
        padding: 0.5rem 0.8rem; margin: 0.3rem 0;
        font-size: 0.85rem;
    }}
    .comment-author {{
        font-weight: 600; color: {LIGHT_THEME['accent']};
        font-size: 0.8rem;
    }}
    .comment-text {{
        color: #444; margin: 0.2rem 0;
    }}
    .comment-likes {{
        font-size: 0.75rem; color: #999;
    }}
    .footer {{
        text-align: center; color: #999;
        font-size: 0.8rem; padding: 2rem 0;
        border-top: 1px solid {LIGHT_THEME['border']};
        margin-top: 2rem;
    }}
    .stButton button {{
        background: {LIGHT_THEME['accent']};
        color: white; border-radius: 8px;
        border: none; padding: 0.4rem 1.2rem;
    }}
    .stButton button:hover {{
        background: {LIGHT_THEME['accent2']};
    }}
    .highlight {{ color: {LIGHT_THEME['accent']}; font-weight: 600; }}
</style>
""", unsafe_allow_html=True)


def load_data(config: Config) -> Optional[Dict]:
    if os.path.exists(config.analysis_path):
        try:
            with open(config.analysis_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return None


def run_scrape(config: Config) -> Dict:
    with st.spinner("正在爬取 Threads 熱門貼文..."):
        scraper = ThreadsScraper(config)
        posts = scraper.scrape()
        analyzer = PostAnalyzer(config)
        result = analyzer.analyze_posts(posts)
        os.makedirs(config.data_dir_path, exist_ok=True)
        with open(config.output_path, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        with open(config.analysis_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        return result


def render_metrics(data: Dict):
    cols = st.columns(5)
    metrics = [
        ("📊 貼文總數", data["total_posts"]),
        ("❤️ 總讚數", f"{data['total_likes']:,}"),
        ("💬 總留言數", f"{data['total_replies']:,}"),
        ("⭐ 平均讚數", f"{data['avg_likes']:,}"),
        ("📝 平均留言", f"{data['avg_replies']:,}"),
    ]
    for col, (label, value) in zip(cols, metrics):
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-value">{value}</div>'
                f'<div class="metric-label">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


def render_topic_pie(data: Dict):
    dist = data.get("topic_distribution", {})
    if not dist:
        return
    df = pd.DataFrame([
        {"主題": t, "貼文數": c} for t, c in dist.items()
    ])
    colors = px.colors.qualitative.Set2[:len(df)]
    fig = px.pie(
        df, values="貼文數", names="主題",
        color_discrete_sequence=colors,
        hole=0.4,
    )
    fig.update_traces(
        textposition="outside",
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>貼文數: %{value}<br>佔比: %{percent}<extra></extra>",
    )
    fig.update_layout(
        height=320, margin=dict(t=0, b=0, l=0, r=0),
        font=dict(size=12),
        showlegend=False,
    )
    st.plotly_chart(fig, width="stretch")


def render_likes_chart(posts: List[Dict]):
    if not posts:
        return
    df = pd.DataFrame(posts)
    df["short_text"] = df["text"].str[:30].str.replace("\n", " ") + "⋯"
    df = df.sort_values("likes")
    fig = px.bar(
        df, x="likes", y="short_text", orientation="h",
        text_auto=".0s",
        color="likes", color_continuous_scale="Reds",
    )
    fig.update_traces(
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>❤️ %{x:,}<extra></extra>",
    )
    fig.update_layout(
        title=None,
        height=500,
        xaxis_title="讚數", yaxis_title="",
        margin=dict(l=0, r=40, t=0, b=0),
        font=dict(size=11),
        yaxis=dict(autorange="reversed"),
        showlegend=False,
    )
    st.plotly_chart(fig, width="stretch")


def render_timeline_chart(posts: List[Dict]):
    if not posts:
        return
    df = pd.DataFrame(posts)
    df["date_only"] = pd.to_datetime(df["date"]).dt.date
    daily = df.groupby("date_only").agg(
        貼文數=("id", "count"),
        總讚數=("likes", "sum"),
    ).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["date_only"], y=daily["貼文數"],
        mode="lines+markers", name="貼文數",
        line=dict(color="#e74c3c", width=2),
        marker=dict(size=8, color="#e74c3c"),
        yaxis="y",
    ))
    fig.add_trace(go.Bar(
        x=daily["date_only"], y=daily["總讚數"],
        name="總讚數", marker_color="#fd79a8",
        opacity=0.6, yaxis="y2",
    ))
    fig.update_layout(
        height=300, margin=dict(t=10, b=0, l=0, r=0),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="貼文數", side="left"),
        yaxis2=dict(title="總讚數", side="right", overlaying="y", showgrid=False),
    )
    st.plotly_chart(fig, width="stretch")


def render_topic_summaries(data: Dict):
    summaries = data.get("topic_summaries", [])
    for s in summaries:
        with st.container():
            st.markdown(
                f'<div class="topic-card">'
                f'<div class="topic-title">📌 {s["topic"]} '
                f'<span style="font-weight:400;color:#999;font-size:0.85rem;">'
                f'（{s["post_count"]} 則貼文 · ❤️ {s["total_likes"]:,}）</span>'
                f'</div>'
                f'<div class="summary-text">{s["summary"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


def render_posts_table(posts: List[Dict]):
    if not posts:
        st.info("尚無貼文資料")
        return

    df = pd.DataFrame(posts)
    df["顯示文字"] = df["text"].str[:60].str.replace("\n", " ") + "⋯"
    df["日期"] = df["date"]
    df["讚數"] = df["likes"]
    df["留言"] = df["replies"]
    df["作者"] = df["author"]
    df["分類"] = df.get("category", df.get("category_hint", ""))

    display_df = df[["作者", "日期", "顯示文字", "讚數", "留言", "分類"]]
    display_df = display_df.sort_values("讚數", ascending=False)

    st.dataframe(
        display_df,
        width="stretch",
        height=400,
        column_config={
            "讚數": st.column_config.NumberColumn(format="%d"),
            "留言": st.column_config.NumberColumn(format="%d"),
        },
        hide_index=True,
    )


def render_post_detail(post: Dict):
    st.markdown(
        f'<div class="post-card">'
        f'<div class="post-author">👤 {post.get("author", "匿名")} '
        f'<span style="font-weight:400;color:#999;">@{post.get("handle", "")}</span>'
        f'<span class="post-meta"> · {post.get("date", "")}</span>'
        f'</div>'
        f'<div class="post-text">{post.get("text", "")}</div>'
        f'<div class="post-stats">'
        f'❤️ {post.get("likes", 0):,}  '
        f'💬 {post.get("replies", 0):,}  '
        f'🏷️ {post.get("category", post.get("category_hint", "未分類"))}'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    top_cmts = post.get("top_comments", [])
    if top_cmts:
        st.markdown(
            f'<div style="font-size:0.9rem;font-weight:600;color:#666;margin:0.5rem 0;">'
            f'💬 熱門留言（前 {len(top_cmts)} 則）</div>',
            unsafe_allow_html=True,
        )
        for cmt in top_cmts:
            st.markdown(
                f'<div class="comment-box">'
                f'<div class="comment-author">{cmt.get("author", "匿名")}</div>'
                f'<div class="comment-text">{cmt.get("text", "")}</div>'
                f'<div class="comment-likes">❤️ {cmt.get("likes", 0)}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


def main():
    config = Config()
    st.markdown(
        f'<div class="main-header">'
        f'💕 Threads 戀愛話題熱門貼文監測</div>',
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("## 📋 控制面板")

    if st.sidebar.button("🔄 立即更新資料", width="stretch"):
        data = run_scrape(config)
        st.rerun()

    data = load_data(config)

    if data is None:
        st.info("⚠ 尚無資料，請點擊左側「立即更新資料」按鈕開始爬取")
        if st.button("🚀 開始第一次爬取"):
            data = run_scrape(config)
            st.rerun()
        return

    last_update = data.get("generated_at", "未知")
    st.sidebar.markdown(
        f'<div style="font-size:0.8rem;color:#999;text-align:center;padding:0.5rem;">'
        f'🕐 最後更新：{last_update}</div>',
        unsafe_allow_html=True,
    )

    posts = data.get("posts", [])

    topics = ["全部"] + sorted(data.get("topic_distribution", {}).keys())
    selected_topic = st.sidebar.selectbox("📂 篩選主題", topics)

    if selected_topic != "全部":
        posts = [p for p in posts
                 if p.get("category", p.get("category_hint", "")) == selected_topic]

    sort_by = st.sidebar.selectbox(
        "📊 排序方式",
        ["讚數（高到低）", "讚數（低到高）", "留言數（高到低）", "最新貼文"],
    )
    sort_map = {
        "讚數（高到低）": ("likes", True),
        "讚數（低到高）": ("likes", False),
        "留言數（高到低）": ("replies", True),
        "最新貼文": ("timestamp", False),
    }
    sort_key, sort_desc = sort_map[sort_by]
    posts = sorted(posts, key=lambda x: x.get(sort_key, 0), reverse=sort_desc)

    min_likes_filter = st.sidebar.slider(
        "❤️ 最低讚數篩選", 0, max(p.get("likes", 1000) for p in posts) if posts else 10000,
        config.min_likes, step=500,
    )
    posts = [p for p in posts if p.get("likes", 0) >= min_likes_filter]

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f'<div style="font-size:0.8rem;color:#999;">'
        f'🔍 目前顯示 <span class="highlight">{len(posts)}</span> 則貼文'
        f'</div>',
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 總覽分析", "📂 主題分群", "📋 貼文列表", "🔍 貼文詳情"
    ])

    with tab1:
        col_left, col_right = st.columns([1.2, 1])
        with col_left:
            render_metrics(data)
            st.markdown('<div class="sub-header">📈 讚數分布</div>', unsafe_allow_html=True)
            render_likes_chart(posts)
        with col_right:
            st.markdown('<div class="sub-header">🎯 主題分佈</div>', unsafe_allow_html=True)
            render_topic_pie(data)
            st.markdown('<div class="sub-header">📅 時間趨勢</div>', unsafe_allow_html=True)
            render_timeline_chart(posts)

    with tab2:
        st.markdown(
            f'<div class="sub-header">📂 主題分群摘要</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            "以下根據貼文內容自動分群，每組提供 2-3 句摘要說明討論焦點",
        )
        render_topic_summaries(data)

    with tab3:
        st.markdown(
            f'<div class="sub-header">📋 貼文列表</div>',
            unsafe_allow_html=True,
        )
        render_posts_table(posts)

    with tab4:
        st.markdown(
            f'<div class="sub-header">🔍 貼文詳情</div>',
            unsafe_allow_html=True,
        )
        if posts:
            post_options = {
                f'❤️{p.get("likes",0):,} | {p.get("author","")} | {p.get("text","")[:40]}⋯'
                : i for i, p in enumerate(posts)
            }
            selected_label = st.selectbox(
                "選擇貼文查看詳情", list(post_options.keys()),
            )
            idx = post_options[selected_label]
            post = posts[idx]
            render_post_detail(post)

            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if idx > 0:
                    if st.button("⬅ 上一篇", width="stretch"):
                        st.session_state["post_idx"] = idx - 1
            with col3:
                if idx < len(posts) - 1:
                    if st.button("下一篇 ➡", width="stretch"):
                        st.session_state["post_idx"] = idx + 1
        else:
            st.info("沒有符合條件的貼文")

    st.markdown(
        f'<div class="footer">'
        f'Threads 戀愛話題監測工具 | 資料來源：Threads.net | 更新頻率：每日 09:00'
        f'</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
