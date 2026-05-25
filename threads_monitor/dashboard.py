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

DARK_HEADER = "#121214"
CHART_COLORS = ["#f5a0b5", "#e8a87c", "#b8a9c9", "#d4c5a9", "#a8c5c9", "#c9b8a8", "#d4b8c9"]

st.markdown(f"""
<style>
    .stApp {{ background-color: #ffffff; }}
    .main-header {{
        background: linear-gradient(135deg, {DARK_HEADER}, #1a1a24);
        padding: 1.8rem 2rem; margin: -1rem -1rem 1.5rem -1rem;
        border-bottom: none;
    }}
    .main-header h1 {{
        font-size: 1.6rem; font-weight: 600; color: #f0f0f0; margin: 0;
        letter-spacing: 0.5px;
    }}
    .main-header .meta {{
        font-size: 0.8rem; color: rgba(255,255,255,0.5); margin-top: 0.3rem;
    }}
    .sub-header {{
        font-size: 1.1rem; font-weight: 600;
        color: #212529;
        margin: 1.2rem 0 0.6rem 0;
    }}
    .metric-card {{
        background: #ffffff;
        border-radius: 12px; padding: 1rem 1.2rem;
        border: 1px solid #e9ecef;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    .metric-value {{
        font-size: 1.8rem; font-weight: 700;
        color: #212529;
    }}
    .metric-label {{
        font-size: 0.75rem; color: #868e96;
        margin-top: 0.25rem;
        letter-spacing: 0.3px;
    }}
    .metric-label .icon {{
        font-size: 0.85rem; margin-right: 0.2rem;
    }}
    .topic-card {{
        background: white;
        border-radius: 12px; padding: 1.2rem;
        border: 1px solid #e9ecef;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    .topic-title {{
        font-size: 1rem; font-weight: 600;
        color: #212529;
        margin-bottom: 0.5rem;
    }}
    .summary-text {{
        font-size: 0.9rem; line-height: 1.6;
        color: #495057; padding: 0.6rem 0.8rem;
        background: #f8f9fa; border-radius: 8px;
        border-left: 3px solid #f5a0b5;
    }}
    .post-card {{
        background: white;
        border-radius: 10px; padding: 1rem;
        border: 1px solid #e9ecef;
        margin-bottom: 0.8rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }}
    .post-author {{
        font-weight: 600; color: #212529;
    }}
    .post-meta {{
        font-size: 0.8rem; color: #868e96;
    }}
    .post-text {{
        font-size: 0.9rem; line-height: 1.5;
        color: #495057; margin: 0.5rem 0;
        white-space: pre-wrap;
    }}
    .post-stats {{
        display: flex; gap: 1rem;
        font-size: 0.85rem; color: #868e96;
        margin-top: 0.5rem;
    }}
    .comment-box {{
        background: #f8f9fa; border-radius: 8px;
        padding: 0.5rem 0.8rem; margin: 0.3rem 0;
        font-size: 0.85rem;
    }}
    .comment-author {{
        font-weight: 600; color: #212529;
        font-size: 0.8rem;
    }}
    .comment-text {{
        color: #495057; margin: 0.2rem 0;
    }}
    .comment-likes {{
        font-size: 0.75rem; color: #adb5bd;
    }}
    .footer {{
        text-align: center; color: #adb5bd;
        font-size: 0.8rem; padding: 2rem 0;
        border-top: 1px solid #e9ecef;
        margin-top: 2rem;
    }}
    .stButton button {{
        background: #212529;
        color: white; border-radius: 8px;
        border: none; padding: 0.4rem 1.2rem;
        font-size: 0.85rem;
    }}
    .stButton button:hover {{
        background: #495057;
    }}
    .highlight {{ color: #212529; font-weight: 600; }}
</style>
""", unsafe_allow_html=True)


def load_data(config: Config) -> Optional[Dict]:
    path = config.analysis_path
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    fallback = os.path.join(os.path.dirname(__file__), "data", config.analysis_file)
    if fallback != path and os.path.exists(fallback):
        try:
            with open(fallback, "r", encoding="utf-8") as f:
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
        try:
            with open(config.output_path, "w", encoding="utf-8") as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
            with open(config.analysis_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except (IOError, OSError):
            pass
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


def render_topic_bar(data: Dict):
    dist = data.get("topic_distribution", {})
    if not dist:
        return
    df = pd.DataFrame([
        {"主題": t, "貼文數": c} for t, c in sorted(dist.items(), key=lambda x: x[1], reverse=True)
    ])
    fig = px.bar(
        df, x="貼文數", y="主題", orientation="h",
        text_auto=True,
        color="貼文數", color_continuous_scale=["#f8f0f2", "#f5a0b5", "#e880a0"],
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(size=11, color="#495057"),
        hovertemplate="<b>%{y}</b><br>%{x} 篇<extra></extra>",
        cliponaxis=False,
    )
    fig.update_layout(
        height=300,
        margin=dict(t=10, b=10, l=0, r=30),
        font=dict(size=12, color="#495057"),
        yaxis=dict(autorange="reversed", title=None),
        xaxis=dict(title=None, showgrid=False, visible=False, fixedrange=True),
        showlegend=False,
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, width="stretch")


def render_likes_chart(posts: List[Dict]):
    if not posts:
        return
    df = pd.DataFrame(posts)
    df["label"] = df.apply(
        lambda r: f'{r.get("author","匿名")} {r.get("text","")[:15].replace(chr(10)," ")}⋯',
        axis=1,
    )
    df = df.sort_values("likes")
    fig = px.bar(
        df, x="likes", y="label", orientation="h",
        text_auto=".0s",
        color="likes", color_continuous_scale=["#f8f0f2", "#f5a0b5", "#e880a0"],
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(size=10, color="#495057"),
        hovertemplate="<b>%{y}</b><br>❤️ %{x:,}<extra></extra>",
        cliponaxis=False,
    )
    fig.update_layout(
        title=None,
        height=480,
        xaxis_title=None,
        yaxis_title=None,
        margin=dict(l=0, r=60, t=10, b=10),
        font=dict(size=10, color="#495057"),
        yaxis=dict(autorange="reversed"),
        xaxis=dict(fixedrange=True),
        showlegend=False,
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
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
        line=dict(color="#b8a9c9", width=2),
        marker=dict(size=6, color="#b8a9c9"),
        yaxis="y",
    ))
    fig.add_trace(go.Bar(
        x=daily["date_only"], y=daily["總讚數"],
        name="總讚數", marker_color="#f5a0b5",
        opacity=0.5, yaxis="y2",
    ))
    fig.update_layout(
        height=280,
        margin=dict(t=10, b=10, l=0, r=0),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
        yaxis=dict(title=None, side="left", showgrid=False, color="#adb5bd"),
        yaxis2=dict(title=None, side="right", overlaying="y", showgrid=False),
        xaxis=dict(showgrid=False, color="#adb5bd"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, width="stretch")


def render_topic_summaries(data: Dict):
    summaries = data.get("topic_summaries", [])
    for s in summaries:
        with st.container():
            st.markdown(
                f'<div class="topic-card">'
                f'<div class="topic-title">📌 {s["topic"]} '
                f'<span style="font-weight:400;color:#868e96;font-size:0.85rem;">'
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
    post_url = post.get("url", "")
    url_btn = ""
    if post_url:
        url_btn = f'<a href="{post_url}" target="_blank" rel="noopener" style="display:inline-block;margin-top:0.5rem;padding:0.3rem 1rem;background:#212529;color:#fff;border-radius:6px;text-decoration:none;font-size:0.85rem;">🔗 前往 Threads 原文</a>'
    st.markdown(
        f'<div class="post-card">'
        f'<div class="post-author">👤 {post.get("author", "匿名")} '
        f'<span style="font-weight:400;color:#868e96;">@{post.get("handle", "")}</span>'
        f'<span class="post-meta"> · {post.get("date", "")}</span>'
        f'</div>'
        f'<div class="post-text">{post.get("text", "")}</div>'
        f'<div class="post-stats">'
        f'❤️ {post.get("likes", 0):,}  '
        f'💬 {post.get("replies", 0):,}  '
        f'🏷️ {post.get("category", post.get("category_hint", "未分類"))}'
        f'</div>'
        f'{url_btn}'
        f'</div>',
        unsafe_allow_html=True,
    )

    top_cmts = post.get("top_comments", [])
    if top_cmts:
        st.markdown(
            f'<div style="font-size:0.9rem;font-weight:600;color:#212529;margin:0.5rem 0;">'
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
        f'<h1>💕 Threads 戀愛話題熱門貼文監測</h1>'
        f'<div class="meta">每日 09:00 自動更新 · 資料來源：Threads.net</div>'
        f'</div>',
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
        f'<div style="font-size:0.8rem;color:#868e96;text-align:center;padding:0.5rem;">'
        f'🕐 最後更新：{last_update}</div>',
        unsafe_allow_html=True,
    )

    posts = data.get("posts", [])
    punchlines = data.get("punchlines", [])

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
        f'<div style="font-size:0.8rem;color:#868e96;">'
        f'🔍 目前顯示 <span class="highlight">{len(posts)}</span> 則貼文'
        f'</div>',
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 總覽分析", "📂 主題分群", "📋 貼文列表", "🔍 貼文詳情"
    ])

    with tab1:
        render_metrics(data)
        if punchlines:
            st.markdown('<div class="sub-header">💥 本週爆發金句</div>', unsafe_allow_html=True)
            cols = st.columns(min(len(punchlines), 3))
            for col, pl in zip(cols, punchlines):
                with col:
                    st.markdown(
                        f'<div style="background:#f8f9fa;border-radius:12px;padding:1.2rem;text-align:center;'
                        f'box-shadow:0 1px 4px rgba(0,0,0,0.06);">'
                        f'<div style="font-size:1.05rem;font-weight:600;color:#212529;line-height:1.5;margin-bottom:0.4rem;">'
                        f'「{pl["text"]}」</div>'
                        f'<div style="font-size:0.8rem;color:rgba(0,0,0,0.45);">'
                        f'— {pl["source"]} · ❤️ {pl["likes"]:,}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

        col_left, col_right = st.columns([1.2, 1])
        with col_left:
            st.markdown('<div class="sub-header">📈 讚數排行</div>', unsafe_allow_html=True)
            render_likes_chart(posts)
        with col_right:
            st.markdown('<div class="sub-header">🎯 主題分佈</div>', unsafe_allow_html=True)
            render_topic_bar(data)
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
