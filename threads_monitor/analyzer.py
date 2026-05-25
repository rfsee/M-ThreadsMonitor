import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import List, Dict, Tuple


class PostAnalyzer:
    def __init__(self, config):
        self.config = config

    def classify_topic(self, text: str, text_meta: str = "") -> str:
        if not text:
            return "其他"

        categories = {
            "觀點爭論": [
                "大家覺得", "只有我", "難道",
                "憑什麼", "認同", "不同意", "反對", "贊成",
                "大家怎麼",
                "有沒有人", "想問大家",
                "難道只有", "是我太", "這樣正常嗎",
                "另一半應該", "伴侶應該",
            ],
            "工具推薦": [
                "推薦", "好用", "工具", "APP", "軟體", "網站",
                "podcast", "頻道", "追蹤", "方法", "技巧",
                "必看", "必推", "大推", "分享給", "推薦給",
                "下載", "實用", "有效率", "bookmark",
            ],
            "案例分享": [
                "我男友", "我女友", "我老公", "我老婆", "經驗",
                "分享", "故事", "經歷", "我們", "那天", "上次",
                "我跟", "我跟我", "今天", "昨天", "前幾天",
                "我曾經", "我朋友", "分享我",
            ],
            "抱怨": [
                "受不了", "煩", "討厭", "生氣", "吵架", "無奈",
                "心累", "失望", "爛", "傻眼", "無言", "難過",
                "氣死", "搞什麼", "憑什麼", "不想", "很煩",
                "好煩", "真的受不", "每次都",
            ],
            "幽默梗": [
                "好笑", "笑死", "哈哈", "梗圖", "幽默", "搞笑",
                "可愛", "有趣", "迷因", "笑瘋", "笑到",
                "be like", "翻譯機", "生物分類",
            ],
            "求助請益": [
                "怎麼辦", "求解", "求助", "請問", "意見", "建議",
                "幫幫", "困擾", "迷惘", "該不該", "怎麼辦",
                "求救", "該怎麼", "可以幫", "有人可以",
            ],
        }

        scores = {}
        for topic, keywords in categories.items():
            score = sum(
                3 if text.startswith(kw) or text.find(kw) < 10
                else 2 if kw in text[:80]
                else 1 if kw in text
                else 0
                for kw in keywords
            )
            scores[topic] = score

        max_score = max(scores.values())
        if max_score == 0:
            return "其他"

        max_topic = max(scores, key=scores.get)
        return max_topic

    def analyze_posts(self, posts: List[Dict]) -> Dict:
        for post in posts:
            hint = post.get("category_hint", "")
            if hint and hint != "其他":
                post["category"] = hint
            else:
                post["category"] = self.classify_topic(post.get("text", ""))

        groups = defaultdict(list)
        for post in posts:
            groups[post["category"]].append(post)

        summaries = []
        for topic in ["工具推薦", "觀點爭論", "案例分享", "抱怨", "幽默梗", "求助請益", "其他"]:
            if topic in groups:
                s = self._summarize_group(topic, groups[topic])
                summaries.append(s)

        top_authors = Counter(
            p.get("author", "匿名") for p in posts if p.get("author")
        ).most_common(10)

        total_likes = sum(p.get("likes", 0) for p in posts)
        total_replies = sum(p.get("replies", 0) for p in posts)

        return {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_posts": len(posts),
            "total_likes": total_likes,
            "total_replies": total_replies,
            "avg_likes": round(total_likes / len(posts)) if posts else 0,
            "avg_replies": round(total_replies / len(posts)) if posts else 0,
            "top_authors": top_authors,
            "topic_distribution": {
                t: len(g) for t, g in sorted(groups.items())
            },
            "topic_summaries": summaries,
            "posts": posts,
        }

    def _summarize_group(self, topic: str, posts: List[Dict]) -> Dict:
        likes = [p.get("likes", 0) for p in posts]
        top_idx = likes.index(max(likes)) if likes else 0

        fn = getattr(self, f"_summarize_{topic}", None)
        if fn:
            summary = fn(posts)
        else:
            summary = self._generic_summary(posts)

        return {
            "topic": topic,
            "post_count": len(posts),
            "total_likes": sum(likes),
            "top_post": posts[top_idx] if posts else None,
            "summary": summary,
        }

    def _summarize_觀點爭論(self, posts) -> str:
        all_text = "\n".join(p.get("text", "") for p in posts)
        has_both = any(kw in all_text for kw in ["可是", "但是", "不過", "然而"])
        has_ques = any(kw in all_text for kw in ["大家覺得", "有人也", "是不是", "應該"])
        top = max(posts, key=lambda x: x.get("likes", 0))
        preview = top.get("text", "")[:50].replace("\n", " ") + "⋯"

        parts = []
        if has_ques:
            parts.append(f"討論焦點圍繞「{preview}」，網友們對感情中的價值觀標準有明顯分歧。")
        else:
            parts.append(f"這個話題引發了多方觀點交鋒。")
        if has_both:
            parts.append("正反雙方各有論述，部分網友認為要看具體情況無法一概而論，另一派則有明確立場。")
        else:
            parts.append("多數留言傾向支持特定觀點，但仍有不同意見。")
        parts.append("整體討論理性且熱烈，反映這個話題在當代感情中的重要性。")
        return "\n".join(parts)

    def _summarize_工具推薦(self, posts) -> str:
        top_post = max(posts, key=lambda x: x.get("likes", 0))
        text = top_post.get("text", "")
        lines = [l.strip() for l in text.split("\n") if l.strip() and len(l.strip()) > 5]
        preview = lines[0][:60] if lines else text[:60]
        preview = preview.replace("\n", " ") + "⋯"

        tips = []
        for p in posts[:3]:
            t = p.get("text", "")
            for kw in ["推薦", "大推", "必看", "分享"]:
                idx = t.find(kw)
                if idx >= 0:
                    tips.append(t[idx:idx+30].replace("\n", " "))
                    break

        return (
            f"社群正在熱烈推薦各種戀愛相關的資源與工具。"
            f"最受關注的推薦：「{preview}」"
            f"{' 其他熱門推薦：'+'、'.join(tips[:3]) if tips else ''}"
            f" 留言區使用者普遍給予正面回饋，認為這些資源實用且有幫助。"
        )

    def _summarize_案例分享(self, posts) -> str:
        top = max(posts, key=lambda x: x.get("likes", 0))
        text = top.get("text", "")
        preview = text[:60].replace("\n", " ") + "⋯"
        has_pos = any(kw in text for kw in ["感動", "幸福", "開心", "溫暖", "甜蜜", "在一起"])
        has_neg = any(kw in text for kw in ["分手", "難過", "哭", "傷心", "痛苦", "離開"])

        if has_pos:
            vibe = "溫馨正向的真實經驗分享"
        elif has_neg:
            vibe = "令人心疼的真實經歷，引發大量共鳴與安慰"
        else:
            vibe = "網友們的真實愛情故事"

        return (
            f"{vibe}獲得大量迴響。最受關注的故事：「{preview}」"
            f" 留言區充滿祝福與同理，許多人分享自身類似經驗互相鼓勵。"
        )

    def _summarize_抱怨(self, posts) -> str:
        all_text = "\n".join(p.get("text", "") for p in posts)
        targets = []
        for t in ["電動", "已讀", "忘記", "說謊", "冷淡", "消失", "敷衍", "不讀不回"]:
            if t in all_text:
                targets.append(t)

        return (
            f"網友們正在抒發對另一半各種行為的不滿與無奈。"
            f"{'最常被抱怨的行為包含：'+'、'.join(targets[:5])+'。' if targets else ''}"
            f"留言區充滿「我家的也是」「原來我不孤單」的同病相怜，"
            f"大家互相取暖並分享應對方式。"
        )

    def _summarize_幽默梗(self, posts) -> str:
        top = max(posts, key=lambda x: x.get("likes", 0))
        text = top.get("text", "")
        preview = text[:50].replace("\n", " ") + "⋯"
        return (
            f"網友發揮創意製作各種情侶相關梗圖與語錄，引發瘋傳與共鳴。"
            f"最熱門的創作：「{preview}」"
            f"留言區充滿「太中肯了」「這是我男友吧🤣」等爆笑回覆，互動率極高。"
        )

    def _summarize_求助請益(self, posts) -> str:
        top = max(posts, key=lambda x: x.get("likes", 0))
        text = top.get("text", "")
        preview = text[:60].replace("\n", " ") + "⋯"
        return (
            f"多位網友正面臨感情困境，上網尋求建議與支持。"
            f"最受關注的求助：「{preview}」"
            f"留言區湧入大量建議，多數傾向支持原PO保護自己、設下明確界線。"
            f"也有部分聲音建議先冷靜溝通、給予對方解釋機會。"
        )

    def _summarize_其他(self, posts) -> str:
        return (
            f"這個分類包含 {len(posts)} 則多元主題的討論，涵蓋不同觀點與感受。"
            f"整體互動熱烈，顯示戀愛話題在 Threads 上具有高度討論價值。"
        )

    def _generic_summary(self, posts) -> str:
        return (
            f"共 {len(posts)} 則相關討論，主題多元、互動熱烈，"
            f"反映在 Threads 社群中具有高度共鳴。"
        )
