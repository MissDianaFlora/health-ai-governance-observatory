from pathlib import Path
from urllib.parse import quote_plus
from datetime import datetime,timezone
import hashlib,html,re,unicodedata,feedparser,pandas as pd
from bs4 import BeautifulSoup
from ftfy import fix_text
from governance import enrich
BASE=Path(__file__).resolve().parent; DATA=BASE/'data'; DATA.mkdir(exist_ok=True); OUT=DATA/'health_ai_risks.csv'
QUERIES=['healthcare AI patient safety','medical AI diagnostic error','health AI bias patients','AI cancer diagnosis error','AI medical device recall','healthcare AI privacy breach','clinical AI regulatory investigation','generative AI medical misinformation','AI mental health patient safety','AI cardiovascular diagnosis risk','AI maternal health safety']
RISK={'Diagnostic accuracy':['misdiagnosis','missed diagnosis','diagnostic error','false positive','false negative','inaccurate'],'Bias and health inequality':['bias','discrimination','health inequality','disparate'],'Patient safety':['patient harm','patient safety','unsafe','adverse event','injury'],'Privacy and data protection':['privacy','data breach','patient data','health data'],'Hallucination and misinformation':['hallucination','misinformation','false information','incorrect advice'],'Transparency and explainability':['black box','explainability','transparency','opaque'],'Automation bias and oversight':['automation bias','human oversight','human review'],'Dataset and model quality':['model drift','training data','data quality'],'Cybersecurity':['cyberattack','ransomware','prompt injection','security breach'],'Regulatory and legal':['regulator','recall','investigation','lawsuit','fine','enforcement']}
CONDITIONS={'Cancer':['cancer','oncology','tumor','tumour'],'Diabetes':['diabetes','diabetic'],'Cardiovascular':['cardiovascular','heart disease','cardiac','stroke'],'Mental health':['mental health','depression','anxiety','psychiatric'],'Neurological':['neurological','dementia','alzheimer','parkinson'],'Maternal health':['maternal','pregnancy','obstetric']}
USES={'Medical imaging':['radiology','medical imaging','mri','ct scan','mammogram'],'Clinical decision support':['clinical decision','decision support','risk prediction'],'Diagnosis':['diagnosis','diagnostic','detection'],'Patient communication':['chatbot','virtual assistant'],'Medication/prescribing':['prescribing','medication','drug recommendation']}
def clean(v):
 t=BeautifulSoup(html.unescape(str(v or '')),'html.parser').get_text(' '); return re.sub(r'\s+',' ',unicodedata.normalize('NFC',fix_text(t))).strip()
def classify(t,m,d):
 l=t.lower(); s={k:sum(x in l for x in v) for k,v in m.items()}; b=max(s,key=s.get); return b if s[b] else d
def sev(t):
 l=t.lower(); return 5 if any(x in l for x in ['death','fatal','serious injury']) else 4 if any(x in l for x in ['recall','patient harm','lawsuit','data breach']) else 3 if any(x in l for x in ['investigation','diagnostic error','false negative','false positive']) else 2
def ev(t):
 l=t.lower(); return 'Formal/confirmed finding' if any(x in l for x in ['regulator found','court ruled','recall','fine imposed','confirmed']) else 'Reported/alleged' if any(x in l for x in ['investigation','lawsuit','complaint','alleged','reported']) else 'Emerging/potential'
def credibility(p):
 p=p.lower(); return 5 if any(x in p for x in ['fda','nih','who','mhra','nice','ema']) else 4 if any(x in p for x in ['reuters','associated press','bbc','financial times','nature','bmj','lancet']) else 3 if any(x in p for x in ['stat','medscape','fierce healthcare']) else 2
def run():
 rows=[]; now=datetime.now(timezone.utc).isoformat()
 for q in QUERIES:
  f=feedparser.parse(f'https://news.google.com/rss/search?q={quote_plus(q)}&hl=en-GB&gl=GB&ceid=GB:en',request_headers={'User-Agent':'HealthAIGovernanceObservatory/1.0'})
  for e in f.entries[:50]:
   src=e.get('source',{}); pub=clean(src.get('title','')) if isinstance(src,dict) else 'Unknown'; title=clean(e.get('title','')); suffix=f' - {pub}'; title=title[:-len(suffix)] if pub and title.endswith(suffix) else title; summary=clean(e.get('summary','')); text=f' {title} {summary} '; l=text.lower()
   if not any(x in l for x in ['health','medical','patient','clinical','hospital','cancer','diabetes','cardiac','mental health','neurolog','maternal','radiology']):continue
   if not any(x in l for x in ['artificial intelligence',' ai ','machine learning','algorithm','generative ai','chatbot','large language model']):continue
   url=str(e.get('link','')); rid=hashlib.sha256((title+'|'+url).encode()).hexdigest()[:20]; risk=classify(text,RISK,'General AI governance risk')
   rows.append({'record_id':rid,'collected_at':now,'published_at':str(e.get('published','')),'title':title,'summary':summary,'url':url,'publisher':pub,'health_condition':classify(text,CONDITIONS,'Other/General health'),'ai_use_case':classify(text,USES,'Other/Unclassified'),'risk_category':risk,'severity':sev(text),'evidence_level':ev(text),'source_credibility_score':credibility(pub),'review_status':'Pending human review','search_query':q})
 new=enrich(pd.DataFrame(rows)) if rows else pd.DataFrame()
 if OUT.exists(): allrows=pd.concat([new,pd.read_csv(OUT,encoding='utf-8-sig')],ignore_index=True)
 else: allrows=new
 if len(allrows): allrows=allrows.drop_duplicates('record_id',keep='first')
 allrows.to_csv(OUT,index=False,encoding='utf-8-sig'); print(f'Saved {len(allrows)} records')
if __name__=='__main__':run()
