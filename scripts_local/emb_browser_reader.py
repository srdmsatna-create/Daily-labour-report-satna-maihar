"""Normal local Chrome session for the user's scheduled e-MB reader.

No certificate bypass, cookie extraction, authentication bypass, or stealth flags.
The optional CDP URL must be explicitly configured by the local user.
"""
import asyncio
import os
from pathlib import Path
import threading
from urllib.parse import urlparse


class BrowserReader:
 def __init__(self):
  self.loop=asyncio.new_event_loop()
  self.thread=threading.Thread(target=self.loop.run_forever,daemon=True)
  self.thread.start()
  self.owned=False
  try:asyncio.run_coroutine_threadsafe(self.start(),self.loop).result(timeout=90)
  except Exception:
   self.close()
   raise
 async def start(self):
  from playwright.async_api import async_playwright
  self.p=await async_playwright().start()
  cdp=os.environ.get('VBGRAM_CDP_URL','').strip()
  if cdp:
   parsed=urlparse(cdp)
   if parsed.scheme not in ('http','https') or parsed.hostname not in ('localhost','127.0.0.1','::1'):raise ValueError('Local browser connection required')
   self.browser=await self.p.chromium.connect_over_cdp(cdp)
   if not self.browser.contexts:raise ValueError('Configured local Chrome context unavailable')
   self.context=self.browser.contexts[0]
  else:
   base=Path(os.environ.get('LOCALAPPDATA') or Path.home()/'.local'/'share')
   profile=base/'SRDM'/'VBGRAM-eMB-Chrome'
   profile.mkdir(parents=True,exist_ok=True)
   args=dict(user_data_dir=str(profile),headless=os.name!='nt',accept_downloads=True)
   try:self.context=await self.p.chromium.launch_persistent_context(channel='chrome',**args)
   except Exception:self.context=await self.p.chromium.launch_persistent_context(**args)
   self.owned=True
  self.slots=asyncio.Semaphore(5)
 async def read(self,url):
  parsed=urlparse(url)
  if parsed.scheme!='https' or parsed.hostname!='vbgramgrep.dord.gov.in':raise ValueError('Official VBGRAMG report URL required')
  async with self.slots:
   for attempt in range(3):
    try:return await self.read_once(url)
    except ValueError:raise # bad URL or a permanent HTTP refusal
    except Exception as exc:
     if attempt==2:raise
     print(f'Retrying official report page ({attempt+2}/3): {exc}',flush=True)
     await asyncio.sleep(2*(attempt+1))
 async def read_once(self,url):
  page=await self.context.new_page()
  try:
   response=await page.goto(url,wait_until='domcontentloaded',timeout=90000)
   if response is not None and response.status>=400:
    error=f'Official report HTTP {response.status}; previous data retained'
    if response.status in (408,429,500,502,503,504):raise RuntimeError(error)
    raise ValueError(error)
   await page.locator('table').first.wait_for(state='visible',timeout=30000)
   return await page.content(),page.url
  finally:
   try:await page.close()
   except Exception:pass
 def get(self,url):
  future=asyncio.run_coroutine_threadsafe(self.read(url),self.loop)
  try:return future.result(timeout=420)
  except TimeoutError:
   future.cancel()
   raise
 async def shutdown(self):
  if self.owned and hasattr(self,'context'):await self.context.close()
  if hasattr(self,'p'):await self.p.stop()
 def close(self):
  if not self.loop.is_running():return
  try:asyncio.run_coroutine_threadsafe(self.shutdown(),self.loop).result(timeout=20)
  finally:self.loop.call_soon_threadsafe(self.loop.stop);self.thread.join(timeout=5)
