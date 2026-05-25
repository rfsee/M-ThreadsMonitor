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
                "大家怎麼", "有沒有人", "想問大家",
                "難道只有", "是我太", "這樣正常嗎",
                "另一半應該", "伴侶應該",
                "這才是", "到底是", "不是為了",
                "大部分原因", "最可怕", "真正",
                "為什麼", "明明",
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
                "單親", "出軌", "結婚後", "結束這段",
            ],
            "抱怨": [
                "受不了", "煩", "討厭", "生氣", "吵架", "無奈",
                "心累", "失望", "爛", "傻眼", "無言", "難過",
                "氣死", "搞什麼", "憑什麼", "不想", "很煩",
                "好煩", "真的受不", "每次都",
                "卑微", "為什麼要分手", "靈魂考驗",
                "把我", "逼瘋", "情緒不穩定",
            ],
            "幽默梗": [
                "好笑", "笑死", "哈哈", "梗圖", "幽默", "搞笑",
                "可愛", "有趣", "迷因", "笑瘋", "笑到",
                "be like", "翻譯機", "生物分類",
                "一人一袋", "正面 背面",
                "gym", "處理別人的",
            ],
            "求助請益": [
                "怎麼辦", "求解", "求助", "請問", "意見", "建議",
                "幫幫", "困擾", "迷惘", "該不該", "怎麼辦",
                "求救", "該怎麼", "可以幫", "有人可以",
                "都怎麼", "不懂", "到底是什麼",
                "走出來", "分手後",
            ],
        }

        scores = {}
        for topic, keywords in categories.items():
            score = sum(
                3 if (pos := text.find(kw)) >= 0 and pos < 10
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

        punchlines = self._extract_punchlines(posts)

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
            "punchlines": punchlines,
            "posts": posts,
        }

    def _extract_punchlines(self, posts: List[Dict]) -> List[Dict]:
        candidates = []
        for p in posts:
            lines = p.get("text", "").split("\n")
            for line in lines:
                line = line.strip()
                if len(line) < 8 or len(line) > 100:
                    continue
                if line.startswith("#") or line.startswith("http"):
                    continue
                q_score = 0
                if "?" in line or "？" in line:
                    q_score += 2
                if "!" in line or "！" in line:
                    q_score += 2
                if any(kw in line for kw in ["其實", "根本", "真的", "難道", "只有我", "笑死"]):
                    q_score += 3
                score = (p.get("likes", 0) // 1000) * q_score
                if q_score > 0:
                    candidates.append({
                        "text": line,
                        "source": p.get("author", "匿名"),
                        "likes": p.get("likes", 0),
                        "score": score,
                    })
        candidates.sort(key=lambda x: x["score"], reverse=True)
        seen = []
        result = []
        for c in candidates:
            if c["text"] not in seen:
                seen.append(c["text"])
                result.append(c)
                if len(result) >= 3:
                    break
        return result

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

    def _quote(self, text: str, max_len: int = 40) -> str:
        t = text.replace("\n", " ").strip()
        if len(t) <= max_len:
            return t
        return t[:max_len] + "⋯"

    def _summarize_觀點爭論(self, posts) -> str:
        top = max(posts, key=lambda x: x.get("likes", 0))
        top_text = self._quote(top.get("text", ""), 50)

        parts = [f"【爭什麼】「{top_text}」"]

        lines = []
        for p in posts:
            lines.extend(p.get("text", "").split("\n"))
        all_text = " ".join(lines)

        pos_quotes = []
        neg_quotes = []
        for line in lines:
            l = line.strip()
            if len(l) < 6:
                continue
            if any(kw in l for kw in ["同意", "+1", "認同", "支持", "沒錯", "真的", "就是啊"]):
                pos_quotes.append(self._quote(l, 35))
            if any(kw in l for kw in ["可是", "但是", "不同意", "不一定", "看情況", "也未必"]):
                neg_quotes.append(self._quote(l, 35))

        pos_kw = ["其實", "應該", "本來就", "很正常", "不合理", "誇張"]
        neg_kw = ["不一定", "看人", "互相", "溝通", "每個人"]
        for line in lines:
            l = line.strip()
            if len(l) < 6:
                continue
            if any(kw in l for kw in pos_kw):
                if self._quote(l, 35) not in pos_quotes:
                    pos_quotes.append(self._quote(l, 35))
            if any(kw in l for kw in neg_kw):
                if self._quote(l, 35) not in neg_quotes:
                    neg_quotes.append(self._quote(l, 35))

        if pos_quotes:
            parts.append(f"【正方金句】{pos_quotes[0]}")
        if neg_quotes:
            parts.append(f"【反方駁斥】{neg_quotes[0]}")
        if len(pos_quotes) > 1 or len(neg_quotes) > 1:
            parts.append(f"【其他聲音】{'｜'.join((pos_quotes+neg_quotes)[:4])}")

        parts.append(f"（共 {len(posts)} 篇交鋒，最高讚 {top.get('likes',0):,}）")
        return " ".join(parts)

    def _summarize_工具推薦(self, posts) -> str:
        top = max(posts, key=lambda x: x.get("likes", 0))
        text = top.get("text", "")
        first_line = text.split("\n")[0].strip()
        top_preview = self._quote(text, 45)

        recommended = []
        for p in posts[:5]:
            t = p.get("text", "")
            for kw in ["推薦", "大推", "必看"]:
                idx = t.find(kw)
                if idx >= 0:
                    item = t[idx:idx+25].replace("\n", " ")
                    if item not in recommended:
                        recommended.append(item)
                    break

        parts = [f"【本週最推】{top_preview}"]
        if recommended:
            parts.append(f"【熱門清單】{'｜'.join(recommended[:4])}")
        parts.append(f"（{len(posts)} 篇推薦文，最高 {top.get('likes',0):,} 讚）")
        return " ".join(parts)

    def _summarize_案例分享(self, posts) -> str:
        top = max(posts, key=lambda x: x.get("likes", 0))
        text = top.get("text", "")
        preview = self._quote(text, 50)

        has_pos = any(kw in text for kw in ["感動", "幸福", "開心", "溫暖", "甜蜜", "在一起"])
        has_neg = any(kw in text for kw in ["分手", "難過", "哭", "傷心", "痛苦", "離開"])

        if has_pos:
            vibe = "甜到蛀牙的真實經驗"
        elif has_neg:
            vibe = "讓人心疼的分手敘事"
        else:
            vibe = "真實愛情切片"

        key_detail = ""
        lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 10]
        for l in lines:
            if any(kw in l for kw in ["他說", "我說", "罵", "哭", "抱", "親", "感動", "心碎"]):
                key_detail = self._quote(l, 40)
                break

        parts = [f"【{vibe}】{preview}"]
        if key_detail:
            parts.append(f"【關鍵瞬間】{key_detail}")
        parts.append(f"（{len(posts)} 篇故事，最高 {top.get('likes',0):,} 讚）")
        return " ".join(parts)

    def _summarize_抱怨(self, posts) -> str:
        all_text = "\n".join(p.get("text", "") for p in posts)

        targets = []
        for t in ["電動", "已讀", "忘記", "說謊", "冷淡", "消失", "敷衍", "不讀不回", "手遊", "裝死"]:
            if t in all_text:
                targets.append(t)

        worst = max(posts, key=lambda x: x.get("likes", 0))
        worst_preview = self._quote(worst.get("text", ""), 45)

        parts = [f"【最爆怨】{worst_preview}"]
        if targets:
            parts.append(f"【雷點排行】{'、'.join(targets[:5])}")
        parts.append(f"（{len(posts)} 篇抱怨文，最高 {worst.get('likes',0):,} 讚）")
        return " ".join(parts)

    def _summarize_幽默梗(self, posts) -> str:
        top = max(posts, key=lambda x: x.get("likes", 0))
        text = top.get("text", "")
        preview = self._quote(text, 45)

        punchline = ""
        lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 5]
        for l in lines:
            if "=" in l or "：" in l or ":" in l or "笑" in l:
                punchline = self._quote(l, 40)
                break

        parts = [f"【最好笑】{preview}"]
        if punchline:
            parts.append(f"【金句】{punchline}")
        parts.append(f"（{len(posts)} 篇搞笑梗，最高 {top.get('likes',0):,} 讚）")
        return " ".join(parts)

    def _summarize_求助請益(self, posts) -> str:
        top = max(posts, key=lambda x: x.get("likes", 0))
        text = top.get("text", "")
        preview = self._quote(text, 50)

        dilemma = ""
        lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 8]
        for l in lines:
            if "?" in l or "？" in l or "該" in l:
                dilemma = self._quote(l, 45)
                break

        parts = [f"【最糾結】{preview}"]
        if dilemma:
            parts.append(f"【核心問題】{dilemma}")
        parts.append(f"（{len(posts)} 篇求助，最高 {top.get('likes',0):,} 讚）")
        return " ".join(parts)

    def _summarize_其他(self, posts) -> str:
        top = max(posts, key=lambda x: x.get("likes", 0))
        preview = self._quote(top.get("text", ""), 45)
        return f"【混合話題】{preview}（{len(posts)} 篇，最高{top.get('likes',0):,}讚）"

    def _generic_summary(self, posts) -> str:
        top = max(posts, key=lambda x: x.get("likes", 0)) if posts else None
        preview = self._quote(top.get("text", ""), 40) if top else ""
        return f"【綜合】{preview}（{len(posts)} 篇）"
