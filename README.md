---
title: Citation to BibTeX
emoji: 📖
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 6.10.0
app_file: app.py
pinned: false
---

You found the perfect paper. You scroll down to "Cite this paper" and... no BibTeX export. Just paste the citation here — or highlight it on any page and click one bookmark.

Powered by [GROBID](https://github.com/grobidOrg/grobid) — results are automatically extracted and may contain errors. Always review the output before use.

## Bookmarklet

Highlight a citation on any webpage, click the bookmarklet, and the BibTeX is copied to your clipboard.

**Install:** drag this link to your bookmarks bar:

<a href="javascript:void(function(){var G='https://lfoppiano-grobid-dev-full.hf.space',t=window.getSelection().toString().trim();if(!t){T('Select a citation first',1);return}T('Converting...');fetch(G+'/api/processCitation',{method:'POST',headers:{Accept:'application/x-bibtex'},body:new URLSearchParams({citations:t,consolidateCitations:'1'})}).then(function(r){if(!r.ok)throw new Error('GROBID '+r.status);return r.text()}).then(function(b){b=b.trim();if(!b)throw new Error('Could not parse citation');return navigator.clipboard.writeText(b).then(function(){T('BibTeX copied!')})}).catch(function(e){T(e.message,1)});function T(m,err){var e=document.getElementById('_bt');if(e)e.remove();e=document.createElement('div');e.id='_bt';e.textContent=m;e.style.cssText='position:fixed;bottom:24px;right:24px;z-index:2147483647;padding:12px 20px;border-radius:8px;font:14px/1.4 system-ui,sans-serif;color:%23fff;background:'+(err?'%23c0392b':'%232ecc71')+';box-shadow:0 4px 12px rgba(0,0,0,.3);transition:opacity .3s;opacity:1';document.body.appendChild(e);setTimeout(function(){e.style.opacity='0';setTimeout(function(){e.remove()},300)},3000)}}())">Citation → BibTeX</a>

Or create a bookmark manually with this URL (see [`bookmarklet.js`](bookmarklet.js) for the readable source):

```
javascript:void(function(){var G='https://lfoppiano-grobid-dev-full.hf.space',t=window.getSelection().toString().trim();if(!t){T('Select a citation first',1);return}T('Converting...');fetch(G+'/api/processCitation',{method:'POST',headers:{Accept:'application/x-bibtex'},body:new URLSearchParams({citations:t,consolidateCitations:'1'})}).then(function(r){if(!r.ok)throw new Error('GROBID '+r.status);return r.text()}).then(function(b){b=b.trim();if(!b)throw new Error('Could not parse citation');return navigator.clipboard.writeText(b).then(function(){T('BibTeX copied!')})}).catch(function(e){T(e.message,1)});function T(m,err){var e=document.getElementById('_bt');if(e)e.remove();e=document.createElement('div');e.id='_bt';e.textContent=m;e.style.cssText='position:fixed;bottom:24px;right:24px;z-index:2147483647;padding:12px 20px;border-radius:8px;font:14px/1.4 system-ui,sans-serif;color:%23fff;background:'+(err?'%23c0392b':'%232ecc71')+';box-shadow:0 4px 12px rgba(0,0,0,.3);transition:opacity .3s;opacity:1';document.body.appendChild(e);setTimeout(function(){e.style.opacity='0';setTimeout(function(){e.remove()},300)},3000)}}())
```