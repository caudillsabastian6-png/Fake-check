# Overlap + flow test for the close-up step (worktree /workspace/work/rorapp-capture/www).
import asyncio, functools, http.server, socket, socketserver, threading, json, os, sys, base64
from playwright.async_api import async_playwright
ROOT = "/workspace/work/rorapp-capture/www"
OUT = "/workspace/work/verdict-fix/capture-test/shots"
CHECK = open("/workspace/work/app-overlap/check.js").read()
os.makedirs(OUT, exist_ok=True)

def serve():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", port), functools.partial(Q, directory=ROOT)); srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{port}/index.html"
URL = serve()

def durl(path):
    return "data:image/jpeg;base64," + base64.b64encode(open(path, "rb").read()).decode()

SHARP = durl("/workspace/work/verdict-fix/web-set/raw/cgcd_taxireal.jpg")
import cv2
im = cv2.imread("/workspace/work/verdict-fix/web-set/raw/cgcd_taxireal.jpg"); cv2.imwrite("/tmp/blur.jpg", cv2.GaussianBlur(im, (0, 0), 6))
BLUR = durl("/tmp/blur.jpg")

async def main():
    res = {}
    async with async_playwright() as p:
        for vp in [(360, 800), (1280, 800)]:
            b = await p.chromium.launch()
            ctx = await b.new_context(viewport={"width": vp[0], "height": vp[1]}, has_touch=vp[0] < 900, is_mobile=vp[0] < 900)
            page = await ctx.new_page(); errs = []
            page.on("pageerror", lambda e: errs.append(str(e)))
            async def api(route):
                await route.fulfill(status=200, content_type="application/json", headers={"Access-Control-Allow-Origin": "*"}, body="{}")
            await page.route("https://api.cardcauldrontcg.com/**", api)
            await page.goto(URL + "?go=picker"); await page.wait_for_timeout(1500)
            await page.evaluate("()=>{try{opHideGate()}catch(e){};try{rewardsHideAll()}catch(e){};try{poolOptinAsked=true}catch(e){}}")
            # real flow: Pokemon card category -> fake front/back captured -> Next on last step
            await page.evaluate("()=>{startCapture(CATEGORIES[0]); capStep=CATEGORIES[0].steps.length-1; capHas=true;}")
            await page.wait_for_timeout(300)
            await page.evaluate("()=>{var p=document.getElementById('capContinuePop'); if(p){p.hidden=true;p.style.display='none'}; document.getElementById('capNext').classList.remove('hidden'); document.getElementById('capNext').click()}")
            await page.wait_for_timeout(500)
            active = await page.evaluate("document.querySelector('.screen.active').id")
            states = {}
            async def snap(name):
                await page.wait_for_timeout(350)
                issues = await page.evaluate(CHECK)
                await page.screenshot(path=f"{OUT}/{vp[0]}-{name}.png")
                states[name] = issues
                if await page.evaluate("document.scrollingElement.scrollHeight-innerHeight>40"):
                    await page.evaluate("scrollTo({top:document.scrollingElement.scrollHeight,behavior:'instant'})"); await page.wait_for_timeout(250)
                    states[name + "-end"] = await page.evaluate(CHECK)
                    await page.screenshot(path=f"{OUT}/{vp[0]}-{name}-end.png")
                    await page.evaluate("scrollTo({top:0,behavior:'instant'})")
            await snap("1-logo-empty")
            await page.evaluate("(d)=>__ccCloseupTest.image(d)", BLUR); await page.wait_for_timeout(500)
            blur_state = await page.evaluate("[document.getElementById('cuState').textContent, document.getElementById('cuNext').classList.contains('hidden')]")
            await snap("2-logo-blurry")
            await page.evaluate("(d)=>__ccCloseupTest.image(d)", SHARP); await page.wait_for_timeout(500)
            sharp_state = await page.evaluate("[document.getElementById('cuState').textContent, document.getElementById('cuNext').classList.contains('hidden')]")
            await snap("3-logo-sharp")
            await page.click("#cuNext"); await page.wait_for_timeout(300)
            await snap("4-edge-empty")
            await page.click("#cuSkip"); await page.wait_for_timeout(300)
            await snap("5-tilt-empty")
            await page.evaluate("(d)=>__ccCloseupTest.image(d)", SHARP); await page.wait_for_timeout(400)
            await snap("6-tilt-taken")
            await page.click("#cuNext"); await page.wait_for_timeout(500)
            after = await page.evaluate("document.querySelector('.screen.active').id")
            await page.click("#ltSkip"); await page.wait_for_timeout(400)
            after2 = await page.evaluate("document.querySelector('.screen.active').id")
            logrec = await page.evaluate("JSON.parse(localStorage.getItem('cc_closeup_log')||'[]')[0]")
            kept = await page.evaluate("Object.keys(window.ccCloseupShots)")
            res[vp[0]] = {"opened_on_last_next": active, "blur": blur_state, "sharp": sharp_state, "after_done": after,
                          "after_light_skip": after2, "log": logrec, "kept_keys": kept, "page_errors": errs,
                          "overlap_issues": {k: v for k, v in states.items()}}
            await b.close()
    json.dump(res, open(f"{OUT}/result.json", "w"), indent=1, default=str)
    for k, v in res.items():
        print(k, json.dumps({kk: vv for kk, vv in v.items() if kk != "overlap_issues"}, default=str)[:900])
        for s, iss in v["overlap_issues"].items():
            print("   ", s, "clean" if not iss else iss[:6])
asyncio.run(main())
