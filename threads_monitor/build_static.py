import json
import os
import sys
from datetime import datetime


def load_analysis(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_html(data: dict) -> str:
    posts_json = json.dumps(data.get("posts", []), ensure_ascii=False)
    topic_dist_json = json.dumps(data.get("topic_distribution", {}), ensure_ascii=False)
    summaries_json = json.dumps(data.get("topic_summaries", []), ensure_ascii=False)

    total = data["total_posts"]
    total_likes = f"{data['total_likes']:,}"
    avg_likes = f"{data['avg_likes']:,}"
    total_replies = f"{data['total_replies']:,}"
    updated = data.get("generated_at", datetime.now().strftime("%Y-%m-%d %H:%M"))

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Threads 戀愛話題監測</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; background:#f5f5f5; color:#333; }}
.header {{ background:linear-gradient(135deg,#e74c3c,#fd79a8); color:#fff; padding:1.5rem 1rem; text-align:center; }}
.header h1 {{ font-size:1.6rem; margin-bottom:0.3rem; }}
.header .meta {{ font-size:0.85rem; opacity:.85; }}
.tabs {{ display:flex; background:#fff; border-bottom:2px solid #e0e0e0; position:sticky; top:0; z-index:10; overflow-x:auto; }}
.tab {{ flex:1; min-width:80px; padding:0.8rem 0.5rem; text-align:center; cursor:pointer; font-size:0.85rem; color:#666; border-bottom:3px solid transparent; transition:all .2s; white-space:nowrap; }}
.tab:hover {{ background:#fef9f9; }}
.tab.active {{ color:#e74c3c; border-bottom-color:#e74c3c; font-weight:600; }}
.content {{ max-width:960px; margin:0 auto; padding:1rem; }}
.page {{ display:none; }}
.page.active {{ display:block; }}
.metrics {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); gap:0.8rem; margin-bottom:1.5rem; }}
.metric-card {{ background:#fff; border-radius:10px; padding:1rem; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
.metric-value {{ font-size:1.5rem; font-weight:700; color:#e74c3c; }}
.metric-label {{ font-size:0.75rem; color:#999; margin-top:0.2rem; }}
.chart-container {{ background:#fff; border-radius:10px; padding:1rem; margin-bottom:1rem; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
.chart-container h3 {{ font-size:0.95rem; color:#555; margin-bottom:0.5rem; }}
.charts-row {{ display:grid; grid-template-columns:1fr 1fr; gap:1rem; }}
@media(max-width:640px){{ .charts-row {{ grid-template-columns:1fr; }} }}
.topic-card {{ background:#fff; border-radius:10px; padding:1rem; margin-bottom:0.8rem; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
.topic-title {{ font-weight:600; color:#e74c3c; margin-bottom:0.3rem; font-size:1rem; }}
.topic-meta {{ font-size:0.8rem; color:#999; margin-bottom:0.5rem; }}
.topic-summary {{ font-size:0.9rem; line-height:1.6; color:#444; padding:0.5rem; background:#fef9f9; border-radius:8px; border-left:3px solid #fd79a8; }}
.post-card {{ background:#fff; border-radius:8px; padding:0.8rem; margin-bottom:0.6rem; box-shadow:0 1px 2px rgba(0,0,0,.06); }}
.post-card h4 {{ font-size:0.9rem; margin-bottom:0.2rem; }}
.post-card .meta {{ font-size:0.75rem; color:#999; }}
.post-card .text {{ font-size:0.85rem; color:#333; margin:0.3rem 0; white-space:pre-wrap; max-height:4em; overflow:hidden; cursor:pointer; }}
.post-card .text.expanded {{ max-height:none; }}
.post-card .stats {{ font-size:0.8rem; color:#e74c3c; }}
.detail-container {{ background:#fff; border-radius:10px; padding:1rem; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
.detail-container .text {{ white-space:pre-wrap; font-size:0.95rem; line-height:1.6; margin:0.8rem 0; }}
.comment {{ background:#f5f5f5; border-radius:6px; padding:0.5rem 0.8rem; margin:0.3rem 0; font-size:0.85rem; }}
.comment-author {{ font-weight:600; color:#e74c3c; font-size:0.8rem; }}
.post-select {{ width:100%; padding:0.5rem; border:1px solid #ddd; border-radius:6px; margin-bottom:1rem; font-size:0.9rem; }}
.filters {{ display:flex; gap:0.5rem; flex-wrap:wrap; margin-bottom:1rem; }}
.filter-btn {{ padding:0.3rem 0.8rem; border:1px solid #ddd; border-radius:20px; background:#fff; cursor:pointer; font-size:0.8rem; color:#666; }}
.filter-btn.active {{ background:#e74c3c; color:#fff; border-color:#e74c3c; }}
.filter-btn:hover {{ background:#fef9f9; }}
.footer {{ text-align:center; color:#999; font-size:0.75rem; padding:2rem 0; }}
</style>
</head>
<body>
<div class="header">
<h1>&#128149; Threads 戀愛話題熱門貼文監測</h1>
<div class="meta">更新時間：{updated} &middot; 資料來源：Threads.net</div>
</div>

<div class="tabs" id="tabs">
<div class="tab active" data-tab="overview">&#128202; 總覽</div>
<div class="tab" data-tab="topics">&#128218; 主題分群</div>
<div class="tab" data-tab="posts">&#128196; 貼文列表</div>
<div class="tab" data-tab="detail">&#128269; 貼文詳情</div>
</div>

<div class="content">
<div class="page active" id="page-overview">
<div class="metrics">
<div class="metric-card"><div class="metric-value">{total}</div><div class="metric-label">&#128202; 貼文總數</div></div>
<div class="metric-card"><div class="metric-value">{total_likes}</div><div class="metric-label">&#10084; 總讚數</div></div>
<div class="metric-card"><div class="metric-value">{total_replies}</div><div class="metric-label">&#128172; 總留言數</div></div>
<div class="metric-card"><div class="metric-value">{avg_likes}</div><div class="metric-label">&#11088; 平均讚數</div></div>
</div>
<div class="charts-row">
<div class="chart-container"><h3>&#127921; 主題分佈</h3><canvas id="pieChart"></canvas></div>
<div class="chart-container"><h3>&#128200; 讚數排行</h3><canvas id="barChart"></canvas></div>
</div>
</div>

<div class="page" id="page-topics">
<div id="topicContainer"></div>
</div>

<div class="page" id="page-posts">
<div class="filters" id="filterContainer"></div>
<div id="postListContainer"></div>
</div>

<div class="page" id="page-detail">
<select class="post-select" id="postSelect"></select>
<div id="detailContainer"></div>
</div>
</div>

<div class="footer">Threads 戀愛話題監測工具 &middot; 每日 09:00 自動更新</div>

<script>
const DATA = {{
  posts: {posts_json},
  topicDistribution: {topic_dist_json},
  topicSummaries: {summaries_json},
}};

// Tab switching
document.querySelectorAll('.tab').forEach(tab => {{
  tab.addEventListener('click', () => {{
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('page-' + tab.dataset.tab).classList.add('active');
  }});
}});

// Pie chart
new Chart(document.getElementById('pieChart'), {{
  type: 'pie',
  data: {{
    labels: Object.keys(DATA.topicDistribution),
    datasets: [{{
      data: Object.values(DATA.topicDistribution),
      backgroundColor: ['#e74c3c','#fd79a8','#fdcb6e','#00b894','#6c5ce7','#0984e3','#636e72'],
    }}]
  }},
  options: {{ responsive:true, maintainAspectRatio:true, plugins:{{ legend:{{ position:'bottom', labels:{{ font:{{ size:11 }} }} }} }} }}
}});

// Bar chart (top likes)
const sorted = [...DATA.posts].sort((a,b) => b.likes - a.likes).slice(0,10);
new Chart(document.getElementById('barChart'), {{
  type: 'bar',
  data: {{
    labels: sorted.map(p => p.author || '匿名'),
    datasets: [{{
      label: '讚數',
      data: sorted.map(p => p.likes),
      backgroundColor: '#e74c3c',
      borderRadius: 4,
    }}]
  }},
  options: {{
    responsive:true, maintainAspectRatio:true, indexAxis:'y',
    plugins:{{ legend:{{ display:false }} }},
    scales:{{ x:{{ ticks:{{ callback:v=>v>=1000?(v/1000).toFixed(0)+'k':v }} }} }}
  }}
}});

// Topic summaries
const topicContainer = document.getElementById('topicContainer');
DATA.topicSummaries.forEach(s => {{
  const div = document.createElement('div');
  div.className = 'topic-card';
  div.innerHTML = `<div class="topic-title">&#128204; ${{s.topic}} <span class="topic-meta">（${{s.post_count}} 則 · &#10084; ${{s.total_likes?.toLocaleString()}}）</span></div><div class="topic-summary">${{s.summary}}</div>`;
  topicContainer.appendChild(div);
}});

// Filters
const filterContainer = document.getElementById('filterContainer');
const allBtn = document.createElement('button');
allBtn.className = 'filter-btn active';
allBtn.textContent = '全部';
allBtn.dataset.filter = 'all';
filterContainer.appendChild(allBtn);
const topics = [...new Set(DATA.posts.map(p => p.category || p.category_hint || '其他'))];
topics.forEach(t => {{
  const btn = document.createElement('button');
  btn.className = 'filter-btn';
  btn.textContent = t;
  btn.dataset.filter = t;
  filterContainer.appendChild(btn);
}});

let currentFilter = 'all';
function renderPosts() {{
  const filtered = currentFilter === 'all' ? DATA.posts : DATA.posts.filter(p => (p.category || p.category_hint || '其他') === currentFilter);
  const container = document.getElementById('postListContainer');
  container.innerHTML = filtered.map((p,i) => `
    <div class="post-card">
      <h4>&#128100; ${{p.author || '匿名'}} <span class="meta">@${{p.handle||''}} &middot; ${{p.date||''}}</span></h4>
      <div class="text" onclick="this.classList.toggle('expanded')">${{p.text}}</div>
      <div class="stats">&#10084; ${{p.likes?.toLocaleString()}} &middot; &#128172; ${{p.replies}} &middot; ${{p.category || p.category_hint || '未分類'}}</div>
    </div>
  `).join('');
  // Update select
  const sel = document.getElementById('postSelect');
  sel.innerHTML = filtered.map((p,i) => `<option value="${{i}}">&#10084;${{p.likes}} | ${{p.author||'匿名'}} | ${{(p.text||'').slice(0,30)}}...</option>`).join('');
  sel.onchange = () => showDetail(parseInt(sel.value));
}}

filterContainer.querySelectorAll('.filter-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    filterContainer.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentFilter = btn.dataset.filter;
    renderPosts();
  }});
}});

function showDetail(idx) {{
  const posts = currentFilter === 'all' ? DATA.posts : DATA.posts.filter(p => (p.category || p.category_hint || '其他') === currentFilter);
  const p = posts[idx];
  if (!p) return;
  const container = document.getElementById('detailContainer');
  let comments = '';
  (p.top_comments || []).forEach(c => {{
    comments += `<div class="comment"><div class="comment-author">${{c.author||'匿名'}}</div><div>${{c.text}}</div><div style="font-size:0.75rem;color:#999;">&#10084; ${{c.likes}}</div></div>`;
  }});
  container.innerHTML = `
    <div class="detail-container">
      <h3>&#128100; ${{p.author||'匿名'}} <span style="font-weight:400;color:#999;">@${{p.handle||''}}</span></h3>
      <div style="font-size:0.8rem;color:#999;">${{p.date||''}} &middot; ${{p.category||p.category_hint||'未分類'}}</div>
      <div class="text">${{p.text}}</div>
      <div style="color:#e74c3c;font-size:0.9rem;">&#10084; ${{p.likes?.toLocaleString()}} &middot; &#128172; ${{p.replies}}</div>
      <div style="margin-top:0.8rem;font-weight:600;color:#666;">&#128172; 熱門留言（前 ${{(p.top_comments||[]).length}} 則）</div>
      ${{comments || '<div style="color:#999;">暫無留言資料</div>'}}
    </div>
  `;
}}

renderPosts();
showDetail(0);
</script>
</body>
</html>"""


def build(config_path=None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "threads_monitor", "data")
    analysis_path = os.path.join(data_dir, "threads_analysis.json")
    if config_path:
        analysis_path = os.path.join(config_path, "threads_analysis.json")

    if not os.path.exists(analysis_path):
        print(f"[ERROR] 找不到分析資料：{analysis_path}")
        print("請先執行：python -m threads_monitor.main run")
        sys.exit(1)

    data = load_analysis(analysis_path)
    html = build_html(data)
    out_path = os.path.join(base_dir, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] 靜態儀表板已生成：{out_path}")
    print(f"     貼文數：{data['total_posts']}，主題數：{len(data['topic_distribution'])}")

    pages_dir = os.path.join(base_dir, "docs")
    os.makedirs(pages_dir, exist_ok=True)
    with open(os.path.join(pages_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    with open(os.path.join(pages_dir, ".nojekyll"), "w") as f:
        f.write("")
    print(f"[OK] GitHub Pages 用 index.html 已生成：{pages_dir}")


if __name__ == "__main__":
    build()
