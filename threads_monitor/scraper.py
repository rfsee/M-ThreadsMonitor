import asyncio
import json
import re
import time
import random
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from playwright.async_api import async_playwright

from threads_monitor.config import Config
from threads_monitor.sample_data import generate_sample_data


def _safe_print(text: str):
    try:
        print(text)
    except UnicodeEncodeError:
        cleaned = text.encode("ascii", "replace").decode("ascii")
        print(cleaned)


class ThreadsScraper:
    BASE_URL = "https://www.threads.com"

    def __init__(self, config: Config):
        self.config = config
        self._browser = None
        self._context = None

    async def _ensure_browser(self):
        if not self._browser:
            p = await async_playwright().start()
            self._browser = await p.chromium.launch(headless=True)
            self._context = await self._browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                ),
                locale="zh-TW",
            )

    async def _close_browser(self):
        if self._browser:
            await self._browser.close()
            self._browser = None
            self._context = None

    async def _search_keyword(self, keyword: str) -> List[Dict]:
        _safe_print(f"  [搜尋] 關鍵字: {keyword}")
        await self._ensure_browser()
        page = await self._context.new_page()

        found = []
        try:
            await page.goto(
                f"{self.BASE_URL}/search?q={keyword}",
                timeout=25000,
                wait_until="domcontentloaded",
            )
            await page.wait_for_timeout(6000)

            result = await page.evaluate(r"""
() => {
    const items = {};
    const links = document.querySelectorAll('a[href*="/post/"]');

    links.forEach(a => {
        const href = a.href;
        const parts = href.split('/');
        let handle = '', code = '';
        for (let i = 0; i < parts.length; i++) {
            if (parts[i].startsWith('@')) {
                handle = parts[i].slice(1);
                if (i + 2 < parts.length && parts[i+1] === 'post') {
                    code = parts[i+2];
                }
                break;
            }
        }
        if (!handle || !code || href.includes('/media')) return;

        let card = a;
        for (let i = 0; i < 8 && card; i++) {
            if ((card.innerText || '').length > 100) break;
            card = card.parentElement;
        }

        const fullText = card ? card.innerText || '' : (a.innerText || '');
        items[code] = {handle, code, url: 'https://www.threads.com/@' + handle + '/post/' + code, text: fullText};
    });

    return JSON.stringify(Object.values(items));
}
""")
            found = json.loads(result)
            if found:
                _safe_print(f"    取得 {len(found)} 則貼文")

        except Exception as e:
            _safe_print(f"    [ERROR] {e}")

        finally:
            await page.close()

        return found

    def _parse_card(self, card_text: str, handle: str, code: str = "") -> Dict:
        lines = [l.strip() for l in card_text.split("\n")]
        if not lines:
            return {}

        # Last lines contain engagement numbers
        num_lines = []
        content_lines = []
        for line in reversed(lines):
            clean = line.strip().replace(",", "")
            if clean.replace(".", "").replace(" ", "").isdigit() and len(clean) < 20:
                num_lines.insert(0, line.strip())
            else:
                break
        # Also skip "翻譯" / "Translate" line before numbers
        text_parts = []
        for line in lines:
            stripped = line.strip()
            if stripped in ("翻譯", "Translate") or not stripped:
                continue
            if any(stripped.replace(",", "").replace(".", "").replace(" ", "").isdigit() for n in num_lines if stripped == n):
                continue
            text_parts.append(stripped)

        # Parse numbers
        likes = 0
        replies = 0
        if num_lines:
            try: likes = int(num_lines[0].replace(",", ""))
            except ValueError: pass
        if len(num_lines) > 1:
            try: replies = int(num_lines[1].replace(",", ""))
            except ValueError: pass

        # Check if second line is a display name (not a time pattern)
        author_name = handle
        if len(text_parts) > 1:
            second = text_parts[1]
            if not re.match(r"^\d+[小時天月年]", second) and len(second) > 1:
                author_name = second

        # Skip handle (first line) for text
        text = "\n".join(text_parts[1:]).strip()

        # Try to extract a date
        date_str = datetime.now().strftime("%Y-%m-%d")
        parsed_dt = None
        for line in text_parts[1:8]:
            m = re.match(r"(\d{4})[.\-/]\s*(\d{1,2})[.\-/]\s*(\d{1,2})", line)
            if m:
                try:
                    dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                    date_str = dt.strftime("%Y-%m-%d")
                    parsed_dt = dt
                except ValueError:
                    pass
                break

        return {
            "id": f"ts_{int(time.time())}_{random.randint(100,999)}",
            "author": author_name,
            "handle": handle,
            "date": date_str,
            "_parsed_date": parsed_dt,
            "timestamp": int(datetime.now().timestamp()),
            "text": text,
            "likes": likes,
            "replies": replies,
            "url": f"https://www.threads.com/@{handle}/post/{code}",
            "top_comments": [],
        }

    def scrape(self, force_sample: bool = False) -> List[Dict]:
        if force_sample:
            _safe_print("[INFO] 使用模擬資料模式")
            return generate_sample_data(self.config.max_posts)

        _safe_print("=" * 50)
        _safe_print("  Threads 熱門貼文爬取（Playwright）")
        _safe_print("=" * 50)

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._scrape_all())

            if not result or self._is_low_quality(result):
                _safe_print(f"\n[WARN] Playwright 資料不足（{len(result) if result else 0} 則）")
                _safe_print("[WARN] 自動切換至模擬資料\n")
                return generate_sample_data(self.config.max_posts)

            _safe_print(f"\n[OK] 共收集 {len(result)} 則真實 Threads 貼文")
            return result

        except Exception as e:
            _safe_print(f"\n[ERROR] Playwright 爬取失敗: {e}")
            _safe_print("[WARN] 自動切換至模擬資料\n")
            return generate_sample_data(self.config.max_posts)

    async def _scrape_all(self) -> List[Dict]:
        all_posts = []
        seen_urls = set()
        cutoff = datetime.now() - timedelta(days=self.config.search_days)

        for i, kw in enumerate(self.config.keywords):
            if len(all_posts) >= self.config.max_posts * 3:
                break
            posts = await self._search_keyword(kw)
            for p in posts:
                url = p.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    parsed = self._parse_card(p.get("text", ""), p.get("handle", ""), p.get("code", ""))
                    if parsed.get("text", "").strip():
                        pd = parsed.pop("_parsed_date", None)
                        if pd and pd < cutoff:
                            continue
                        all_posts.append(parsed)
            await asyncio.sleep(1.0)

        all_posts.sort(key=lambda x: x.get("likes", 0), reverse=True)
        return all_posts[: self.config.max_posts]

    def _is_low_quality(self, posts: List[Dict]) -> bool:
        if len(posts) < 3:
            return True
        no_text = sum(1 for p in posts if len(p.get("text", "")) < 15)
        if no_text > len(posts) * 0.5:
            return True
        return False
