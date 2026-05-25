import os
from dataclasses import dataclass, field
from typing import List, Dict


def _is_cloud() -> bool:
    return "STREAMLIT_SERVER_BASE_URL" in os.environ or "STREAMLIT_RUNTIME" in os.environ


def _get_data_dir() -> str:
    if _is_cloud():
        return os.path.join("/tmp", "threads_data")
    return os.path.join(os.path.dirname(__file__), "data")


@dataclass
class Config:
    keywords: List[str] = field(default_factory=lambda: [
        "男友", "戀人", "愛情", "感情問題",
        "男朋友", "女朋友", "曖昧", "分手", "出軌",
        "遠距離", "結婚", "情侶", "感情", "交往",
        "戀愛", "伴侶", "吵架", "渣男", "暖男",
        "暈船", "告白", "前任", "安全感",
        "已讀不回", "冷暴力", "單身", "情緒價值",
        "直男", "控制欲", "儀式感", "雙標",
        "邊界感", "媽寶", "PUA",
    ])

    min_likes: int = 1000
    max_posts: int = 20
    search_days: int = 21
    output_file: str = "threads_posts.json"
    analysis_file: str = "threads_analysis.json"

    @property
    def is_cloud(self) -> bool:
        return _is_cloud()

    @property
    def data_dir_path(self) -> str:
        return _get_data_dir()

    topic_keywords: Dict[str, List[str]] = field(default_factory=lambda: {
        "工具推薦": ["推薦", "好用", "工具", "APP", "軟體", "網站", "書", "課程",
                     "podcast", "頻道", "追蹤", "追劇", "方法", "技巧"],
        "觀點爭論": ["大家覺得", "有人也", "只有我", "是不是", "應該", "難道",
                     "憑什麼", "認同", "不同意", "反對", "贊成", "討論"],
        "案例分享": ["我男友", "我女友", "我老公", "我老婆", "經驗", "分享",
                     "故事", "經歷", "我們", "那天", "上次"],
        "抱怨": ["受不了", "煩", "討厭", "生氣", "吵架", "無奈", "心累",
                 "失望", "爛", "噁心", "傻眼", "無言", "難過"],
        "幽默梗": ["好笑", "笑死", "哈哈", "梗圖", "幽默", "搞笑", "可愛",
                   "有趣", "迷因", "笑瘋"],
        "求助請益": ["怎麼辦", "求解", "求助", "請問", "意見", "建議",
                     "幫幫", "困擾", "迷惘", "該不該"],
    })

    @property
    def output_path(self) -> str:
        import os
        return os.path.join(self.data_dir_path, self.output_file)

    @property
    def analysis_path(self) -> str:
        import os
        return os.path.join(self.data_dir_path, self.analysis_file)
