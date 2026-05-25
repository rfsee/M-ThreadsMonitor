import json
import time
import re
import random
import sys
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from threads_monitor.config import Config
from threads_monitor.sample_data import generate_sample_data


def _safe_print(text: str):
    try:
        print(text)
    except UnicodeEncodeError:
        cleaned = text.encode("ascii", "replace").decode("ascii")
        print(cleaned)


class ThreadsScraper:
    BASE_URL = "https://www.threads.net"
    API_GRAPHQL = "https://www.threads.net/api/graphql"

    SEARCH_QUERY_HASH = "2438c3c4ae5b29b01e5b7951b05c53ef"

    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        })
        self._init_cookies()

    def _init_cookies(self):
        try:
            self.session.get(self.BASE_URL, timeout=15)
        except requests.RequestException:
            pass

    def _query_graphql(self, query_hash: str, variables: dict) -> Optional[Dict]:
        payload = {
            "fb_dtsg": "",
            "variables": json.dumps(variables, separators=(",", ":")),
            "server_timestamps": "true",
            "doc_id": query_hash,
        }
        try:
            resp = self.session.post(
                self.API_GRAPHQL,
                data=payload,
                timeout=20,
            )
            if resp.status_code == 200:
                return resp.json()
            return None
        except (requests.RequestException, json.JSONDecodeError):
            return None

    def _fetch_search_html(self, query: str) -> Optional[str]:
        try:
            params = {"q": query}
            resp = self.session.get(
                f"{self.BASE_URL}/search",
                params=params,
                timeout=20,
                allow_redirects=True,
            )
            if resp.status_code == 200:
                return resp.text
            return None
        except requests.RequestException:
            return None

    def _extract_texts_from_scripts(self, html: str) -> List[Dict]:
        results = []
        patterns = re.compile(
            r'"(?:text|caption|description)"\s*:\s*'
            r'"((?:[^"\\]|\\.)*)"'
        )
        likes_pat = re.compile(r'"(?:like_count|likes)"\s*:\s*(\d+)')

        for match in patterns.finditer(html):
            raw = match.group(1)
            text = raw.replace("\\n", "\n").replace("\\t", "\t") \
                      .replace("\\/", "/").replace('\\"', '"')
            try:
                text = json.loads(f'"{raw}"')
            except json.JSONDecodeError:
                pass
            if len(text) >= 10:
                results.append({"text": text, "likes": 0})

        like_matches = likes_pat.findall(html)
        for i, l in enumerate(like_matches):
            if i < len(results):
                results[i]["likes"] = int(l)

        return results

    def _extract_struct_from_next_data(self, html: str) -> List[Dict]:
        posts = []
        try:
            soup = BeautifulSoup(html, "lxml")
            tag = soup.find("script", id="__NEXT_DATA__")
            if tag and tag.string:
                data = json.loads(tag.string)
                props = data.get("props", {}).get("pageProps", {})
                items = (props.get("searchData", {})
                         .get("data", {}).get("items", []))

                for item in items:
                    post_node = item.get("post", {})
                    if not post_node:
                        continue
                    user = post_node.get("user", {}) or {}
                    caption = post_node.get("caption", {}) or {}
                    entities = caption.get("text_entities", []) or []
                    text = " ".join(e.get("text", "") for e in entities)

                    likes = post_node.get("like_count", 0) or 0
                    replies = post_node.get("reply_count", 0) or 0
                    code = post_node.get("code", "") or ""
                    taken_at = post_node.get("taken_at", 0) or 0
                    username = user.get("username", "") or ""

                    if taken_at:
                        date_str = datetime.fromtimestamp(taken_at).strftime("%Y-%m-%d %H:%M")
                    else:
                        date_str = ""

                    comments_raw = post_node.get("comments", []) or []
                    top_comments = []
                    for c in (comments_raw or [])[:5]:
                        cu = c.get("user", {}) or {}
                        top_comments.append({
                            "author": cu.get("full_name", "") or cu.get("username", ""),
                            "text": c.get("text", "") or "",
                            "likes": c.get("like_count", 0) or 0,
                            "time_ago": "",
                        })

                    posts.append({
                        "id": code or f"ts_{int(time.time())}_{random.randint(100,999)}",
                        "author": user.get("full_name", "") or username,
                        "handle": username,
                        "date": date_str,
                        "timestamp": taken_at or int(time.time()),
                        "text": text,
                        "likes": likes,
                        "replies": replies,
                        "url": f"https://www.threads.net/@{username}/post/{code}" if username and code else "",
                        "top_comments": top_comments,
                    })
        except Exception:
            pass
        return posts

    def _search_via_api(self, keyword: str) -> List[Dict]:
        _safe_print(f"  [搜尋] 關鍵字: {keyword}")
        found = []

        html = self._fetch_search_html(keyword)
        if html:
            found = self._extract_struct_from_next_data(html)
            if found:
                _safe_print(f"    從 Next.js data 解析到 {len(found)} 則")
                return found

            raw_texts = self._extract_texts_from_scripts(html)
            if raw_texts:
                _safe_print(f"    從 script tags 解析到 {len(raw_texts)} 則原始文字")
                for rt in raw_texts[:5]:
                    found.append({
                        "id": f"st_{int(time.time())}_{random.randint(100,999)}",
                        "author": "",
                        "handle": "",
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "timestamp": int(time.time()),
                        "text": rt["text"],
                        "likes": rt["likes"],
                        "replies": 0,
                        "url": "",
                        "top_comments": [],
                    })
                return found

        _safe_print(f"    [INFO] 無資料")
        return found

    def _is_low_quality(self, posts: List[Dict]) -> bool:
        if len(posts) < 5:
            return True
        no_author = sum(1 for p in posts if not p.get("author"))
        no_text = sum(1 for p in posts if len(p.get("text", "")) < 15)
        if no_author > len(posts) * 0.5:
            return True
        if no_text > len(posts) * 0.3:
            return True
        return False

    def scrape(self, force_sample: bool = False) -> List[Dict]:
        if force_sample:
            _safe_print("[INFO] 使用模擬資料模式")
            return generate_sample_data(self.config.max_posts)

        _safe_print("=" * 50)
        _safe_print("  Threads 熱門貼文爬取")
        _safe_print("=" * 50)

        all_posts = []
        keywords = self.config.keywords

        for i, kw in enumerate(keywords):
            if len(all_posts) >= self.config.max_posts * 3:
                break
            posts = self._search_via_api(kw)
            all_posts.extend(posts)
            time.sleep(1.0)

        seen = set()
        unique = []
        for p in all_posts:
            key = p.get("text", "")[:80]
            if key and key not in seen:
                seen.add(key)
                unique.append(p)
        all_posts = unique

        all_posts.sort(key=lambda x: x.get("likes", 0), reverse=True)
        result = all_posts[:self.config.max_posts]

        if self._is_low_quality(result):
            _safe_print(f"\n[WARN] 真實資料品質不足（{len(result)} 則，缺乏作者/文字資訊）")
            _safe_print("[WARN] 自動切換至模擬資料以展示完整儀表板功能\n")
            result = generate_sample_data(self.config.max_posts)
        else:
            _safe_print(f"\n[OK] 共收集 {len(result)} 則真實 Threads 貼文")

        return result
