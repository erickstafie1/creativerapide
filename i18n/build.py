import json, re, sys, os
from bs4 import BeautifulSoup, NavigableString, Comment
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
keys=json.load(open('/home/claude/i18n/keys.json')) if os.path.exists('/home/claude/i18n/keys.json') else json.load(open(os.path.join(ROOT,'i18n/keys.json')))
PAGES=['index','despre','portofoliu']
LANGS=sorted(f[:-5] for f in os.listdir(os.path.join(ROOT,'i18n')) if f.endswith('.json') and f not in('keys.json','langs.json'))
SITE='https://creativerapide.ro'
META=json.load(open(os.path.join(ROOT,'i18n/langs.json'))) if os.path.exists(os.path.join(ROOT,'i18n/langs.json')) else {}
def load(l):
    d=json.load(open(os.path.join(ROOT,f'i18n/{l}.json'))); m=d.pop('_meta')
    tr={keys[int(i)].strip():v for i,v in d.items()}
    return m,tr
def pagepath(p,l): return ('/' if p=='index' else '/'+p) if l=='ro' else ('/%s/'%l if p=='index' else '/%s/%s'%(l,p))
def build(l):
    m,tr=load(l)
    for p in PAGES:
        soup=BeautifulSoup(open(os.path.join(ROOT,p+'.html'),encoding='utf-8').read(),'html.parser')
        miss=set()
        def T(s):
            k=s.strip()
            if k in tr: return s.replace(k,tr[k])
            return None
        for n in soup.find_all(string=True):
            if isinstance(n,Comment) or n.parent.name in('script','style'): continue
            if n.strip():
                r=T(str(n))
                if r is not None: n.replace_with(NavigableString(r))
                elif re.search('[a-zăâîșț]{3}',str(n)) and n.parent.name!='title' : miss.add(str(n).strip()[:50])
        for t in soup.find_all(True):
            for a in('alt','aria-label','title','content','placeholder'):
                if t.has_attr(a) and isinstance(t[a],str):
                    r=T(t[a])
                    if r is not None: t[a]=r
        if soup.title and soup.title.string and soup.title.string.strip() in tr: soup.title.string=tr[soup.title.string.strip()]
        soup.html['lang']=l
        # WhatsApp prefilled texts
        from urllib.parse import quote,unquote
        for a in soup.find_all('a',href=True):
            h=a['href']
            if 'wa.me' in h and 'text=' in h:
                base,txt=h.split('text=',1); ro=unquote(txt)
                a['href']=base+'text='+quote(m['wa'].get(ro,ro))
        def fix(v,l):
            b=v.split('#')[0].split('?')[0]; frag=v[len(b):]
            if b in('/home','/'): return ('/%s/'%l)+frag
            if b in('/portofoliu','/despre'): return '/%s%s'%(l,b)+frag
            return v
        # paths -> absolute
        for t in soup.find_all(True):
            for a in('src','href','poster','data-src'):
                if t.has_attr(a):
                    v=t[a]
                    if not isinstance(v,str) or re.match(r'(https?:|mailto:|tel:|#|/|data:)',v): 
                        if isinstance(v,str) and v.startswith('/'): t[a]=fix(v,l)
                        continue
                    t[a]=fix('/'+v,l)
        for t in soup.find_all('a',href=True): t['href']=fix(t['href'],l) if t['href'].startswith('/') else t['href']
        # fix anchors-only on index pages for other pages
        for t in soup.find_all('a',href=True):
            if t['href'].startswith('#') and p!='index': pass
        # head: canonical, og, hreflang
        head=soup.head
        for c in head.find_all('link',rel='canonical'): c['href']=SITE+pagepath(p,l)
        for mt in head.find_all('meta',property='og:url'): mt['content']=SITE+pagepath(p,l)
        for mt in head.find_all('meta',property='og:locale'): mt['content']=m['og_locale']
        if not head.find('meta',property='og:locale'):
            x=soup.new_tag('meta',property='og:locale',content=m['og_locale']); head.append(x)
        for h in head.find_all('link',rel='alternate'): h.decompose()
        allang=['ro']+LANGS
        for x in allang:
            h=soup.new_tag('link',rel='alternate',hreflang=x,href=SITE+pagepath(p,x)); head.append(h)
        head.append(soup.new_tag('link',rel='alternate',hreflang='x-default',href=SITE+pagepath(p,'ro')))
        # JSON-LD
        for s in head.find_all('script',type='application/ld+json'):
            try:
                d=json.loads(s.string)
                def tw(o):
                    if isinstance(o,dict):
                        for k,v in list(o.items()):
                            if k=='areaServed': o[k]=m['areaServed']
                            elif k=='inLanguage': o[k]=l
                            elif k=='url' and isinstance(v,str) and v.startswith(SITE): o[k]=SITE+pagepath(p,l)
                            else: tw(v)
                    elif isinstance(o,list):
                        for i in o: tw(i)
                tw(d); s.string=json.dumps(d,ensure_ascii=False)
            except Exception as e: pass
        # language switcher + remember choice
        sw=soup.new_tag('script'); 
        sw.string="document.addEventListener('DOMContentLoaded',function(){var s=document.createElement('div');s.style.cssText='position:fixed;right:12px;bottom:12px;z-index:9999;background:#111;color:#fff;border-radius:10px;padding:6px 10px;font:13px sans-serif';var L=%s;var h='<select aria-label=\"Language\" style=\"background:#111;color:#fff;border:0;font:inherit\">';for(var k in L){h+='<option value=\"'+L[k]+'\"'+(k==='%s'?' selected':'')+'>'+k+'</option>'}s.innerHTML=h+'</select>';s.firstChild.onchange=function(){var c=this.value.split('/')[1];var l=(c.length==2&&c!=='ro')?c:'ro';document.cookie='lang='+l+';path=/;max-age=31536000';location.href=this.value};document.body.appendChild(s)});"%(json.dumps({**{'Română':pagepath(p,'ro')},**{ (load(x)[0]['label']):pagepath(p,x) for x in LANGS}},ensure_ascii=False),m['label'])
        soup.body.append(sw)
        outdir=os.path.join(ROOT,l); os.makedirs(outdir,exist_ok=True)
        open(os.path.join(outdir,p+'.html'),'w',encoding='utf-8').write(str(soup))
        print(l,p,'untranslated text nodes:',sorted(miss)[:8])
for l in LANGS: build(l)

# vercel.json geo redirects
vj=json.load(open(os.path.join(ROOT,'vercel.json')))
base=[r for r in vj['redirects'] if 'has' not in r]
geo=[]
for l in LANGS:
    m,_=load(l)
    for src,dst in(('/','/%s/'%l),('/home','/%s/'%l),('/despre','/%s/despre'%l),('/portofoliu','/%s/portofoliu'%l)):
        geo.append({'source':src,'has':[{'type':'header','key':'x-vercel-ip-country','value':'(?:%s)'%'|'.join(m['countries'])}],'missing':[{'type':'cookie','key':'lang'}],'destination':dst,'permanent':False})
vj['redirects']=base+geo
json.dump(vj,open(os.path.join(ROOT,'vercel.json'),'w'),indent=2)
# sitemap
sm=open(os.path.join(ROOT,'sitemap.xml'),encoding='utf-8').read()
