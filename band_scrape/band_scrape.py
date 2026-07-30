# -*- coding: utf-8 -*-
"""
밴드 판매실적 수집 - 1단계 (데이터 캡처)

설치:
  pip install playwright
  playwright install chromium

실행:
  python band_scrape.py

동작:
  1) 크롬 창이 하나 열립니다.
  2) 창에서 '직접' 밴드에 로그인하세요 (네이버/밴드 계정).
  3) 판매실적 밴드로 이동해 글 피드가 보이게 하세요.
  4) 터미널로 돌아와 Enter를 누르면, 자동으로 끝까지 스크롤하며
     밴드가 주고받는 게시물 데이터(JSON)를 captured/ 폴더에 저장합니다.
  5) 끝나면 captured/resp_0000_*.json 파일 하나를 열어 구조를 공유해 주세요.

* 로그인 정보는 band_profile/ 폴더(사장님 PC)에만 저장됩니다. 다음 실행부터는
  로그인이 유지돼요. 이 폴더/캡처파일은 저에게 보내지 마세요(개인정보 포함).
"""
import os, json, hashlib
from playwright.sync_api import sync_playwright

OUT = "captured"
os.makedirs(OUT, exist_ok=True)
seen = set()
captured = []


def looks_like_posts(obj):
    """응답 본문이 '게시물 데이터'처럼 보이는지 대략 판별."""
    try:
        s = json.dumps(obj, ensure_ascii=False)
    except Exception:
        return False
    if '"content"' not in s:
        return False
    return any(k in s for k in ('"photo', '"created_at"', '"post_no"',
                                '"post_key"', '"author"'))


def main():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir="band_profile",       # 로그인 유지용 (사장님 PC 로컬)
            headless=False,
            viewport={"width": 1280, "height": 900},
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        def on_response(resp):
            try:
                ct = resp.headers.get("content-type", "")
                if "band.us" not in resp.url or "json" not in ct:
                    return
                body = resp.json()
            except Exception:
                return
            if not looks_like_posts(body):
                return
            h = hashlib.md5(json.dumps(body, ensure_ascii=False).encode()).hexdigest()[:8]
            if h in seen:
                return
            seen.add(h)
            fn = os.path.join(OUT, f"resp_{len(captured):04d}_{h}.json")
            with open(fn, "w", encoding="utf-8") as f:
                json.dump({"url": resp.url, "body": body}, f, ensure_ascii=False, indent=2)
            captured.append(fn)
            print(f"  + 게시물 데이터 캡처: {os.path.basename(fn)}")

        page.on("response", on_response)

        page.goto("https://band.us/")
        print("\n[1] 열린 크롬 창에서 밴드에 '직접' 로그인하세요.")
        print("[2] 판매실적 밴드로 이동해 글 피드가 보이게 하세요.")
        input("[3] 준비되면 여기서 Enter ▶ ")

        print("현재 페이지:", page.url)
        print("자동 스크롤 시작... (창을 건드리지 말고 그대로 두세요)")

        last_h, stable = 0, 0
        for i in range(3000):
            page.mouse.wheel(0, 3200)
            page.wait_for_timeout(1200)
            try:
                h = page.evaluate("document.body.scrollHeight")
            except Exception:
                h = last_h
            if h == last_h:
                stable += 1
                if stable >= 8:          # 8회 연속 변화 없음 → 끝까지 도달
                    break
            else:
                stable, last_h = 0, h
            if i % 15 == 0:
                print(f"  스크롤 {i}회 · 캡처 {len(captured)}건")

        with open(os.path.join(OUT, "final_page.html"), "w", encoding="utf-8") as f:
            f.write(page.content())

        print(f"\n완료 ✅  캡처된 게시물 데이터 {len(captured)}건 → '{OUT}/' 폴더")
        print("→ captured/resp_0000_*.json 파일 하나를 열어 '구조'만 공유해 주세요.")
        print("  (파일 내용 전체 말고, 게시글 1~2개 부분만 보여주셔도 됩니다.)")
        ctx.close()


if __name__ == "__main__":
    main()
