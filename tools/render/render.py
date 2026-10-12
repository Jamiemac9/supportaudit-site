import asyncio
from playwright.async_api import async_playwright
I='/home/claude/seaaudit/src/assets/img/'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        async def shot(html,w,h,out,clip=None):
            pg=await b.new_page(viewport={'width':w,'height':h})
            await pg.goto('file:///home/claude/seaaudit/tools/render/'+html); await pg.wait_for_timeout(500)
            await pg.screenshot(path=out); await pg.close()
        await shot('og.html',1200,630,I+'og.png')
        await shot('icon.html',512,512,I+'icon-512.png')
        await shot('preview.html',900,250,'/tmp/claude-0/-home-claude-supportaudit-site/6aa66719-94ba-535c-a5b7-a79febef80ed/scratchpad/logo-preview.png')
        await b.close()
asyncio.run(main())
from PIL import Image
im=Image.open(I+'icon-512.png'); im.resize((192,192),Image.LANCZOS).save(I+'icon-192.png'); im.resize((180,180),Image.LANCZOS).save(I+'apple-touch-icon.png')
im.resize((48,48),Image.LANCZOS).save('/home/claude/seaaudit/src/static/favicon.ico',sizes=[(48,48),(32,32),(16,16)])
og=Image.open(I+'og.png').convert('RGB'); og.save(I+'og.jpg',quality=86,optimize=True)
