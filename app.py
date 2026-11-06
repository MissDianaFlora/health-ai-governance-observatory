from pathlib import Path
import pandas as pd,plotly.express as px,streamlit as st
BASE=Path(__file__).resolve().parent; FILE=BASE/'data'/'health_ai_risks.csv'
st.set_page_config(page_title='Health AI Governance Observatory',page_icon='🩺',layout='wide')
st.title('Health AI Governance Observatory'); st.caption('Risk signals → ethical principles → governance controls → mitigation')
st.info('Governance mappings are analytical interpretations, not automatic findings that a principle was violated. Verify source evidence before client or public use.')
if not FILE.exists(): st.error('Run: python collector.py'); st.stop()
df=pd.read_csv(FILE,encoding='utf-8-sig'); df['published_date']=pd.to_datetime(df.published_at,errors='coerce',utc=True).dt.date
with st.sidebar:
 st.header('Filters'); cond=st.multiselect('Health condition',sorted(df.health_condition.unique())); risk=st.multiselect('Risk',sorted(df.risk_category.unique())); principle=st.multiselect('Principle potentially at risk',sorted(df.governance_principle.unique())); use=st.multiselect('AI use case',sorted(df.ai_use_case.unique())); sev=st.slider('Minimum severity',1,5,1)
 dates=df.published_date.dropna(); dr=st.date_input('Published/released',value=(dates.min(),dates.max()),min_value=dates.min(),max_value=dates.max()) if len(dates) else ()
f=df.copy()
if cond:f=f[f.health_condition.isin(cond)]
if risk:f=f[f.risk_category.isin(risk)]
if principle:f=f[f.governance_principle.isin(principle)]
if use:f=f[f.ai_use_case.isin(use)]
f=f[f.severity>=sev]
if isinstance(dr,(tuple,list)) and len(dr)==2:f=f[(f.published_date>=dr[0])&(f.published_date<=dr[1])]
tabs=st.tabs(['Executive Overview','Risk → Principle → Mitigation','Principles at Risk','Mitigation Library','Evidence & Analyst View','Methodology'])
with tabs[0]:
 a,b,c,d=st.columns(4); a.metric('Signals',len(f)); b.metric('High severity',int((f.severity>=4).sum())); c.metric('Principles exposed',f.governance_principle.nunique()); d.metric('High-confidence analysis',int((f.analyst_confidence=='High').sum()))
 x=f.risk_category.value_counts().reset_index(); x.columns=['Risk','Signals']; st.plotly_chart(px.bar(x,x='Signals',y='Risk',orientation='h',title='Health AI risk signals'),use_container_width=True)
with tabs[1]:
 st.subheader('Risk → Principle → Mitigation')
 opts={f"{r.title[:90]} | {r.risk_category}":i for i,r in f.iterrows()}
 if opts:
  row=f.loc[opts[st.selectbox('Select a signal',list(opts))]]
  c1,c2,c3=st.columns(3); c1.metric('Risk',row.risk_category); c2.metric('Severity',f'{int(row.severity)}/5'); c3.metric('Analyst confidence',row.analyst_confidence)
  st.markdown(f'**Principle potentially at risk:** {row.governance_principle}'); st.markdown(f'**Assessment status:** {row.principle_status}'); st.write(row.principle_rationale)
  st.markdown('**Recommended mitigations**'); [st.markdown(f'- {x}') for x in str(row.recommended_mitigation).split('; ')]
  st.markdown(f'**Suggested control owner:** {row.control_owner}'); st.markdown('**Analyst view**'); st.write(row.analyst_view); st.link_button('Open underlying source ↗',row.url)
with tabs[2]:
 mat=pd.crosstab(f.governance_principle,f.risk_category); st.plotly_chart(px.imshow(mat,text_auto=True,aspect='auto',title='Governance principle × risk heatmap'),use_container_width=True)
with tabs[3]:
 lib=f[['risk_category','governance_principle','recommended_mitigation','control_owner']].drop_duplicates(); st.dataframe(lib,hide_index=True,use_container_width=True)
with tabs[4]:
 disp=f[['published_date','title','url','publisher','risk_category','governance_principle','principle_status','analyst_confidence','review_status']].copy(); disp['Read']=disp.url
 st.dataframe(disp[['published_date','title','Read','publisher','risk_category','governance_principle','principle_status','analyst_confidence','review_status']],column_config={'Read':st.column_config.LinkColumn('Source',display_text='Open source ↗')},hide_index=True,use_container_width=True)
with tabs[5]:
 st.markdown('''### Interpretation model
**Source evidence → AI use case → risk → principle potentially at risk → likely control gap → mitigation → owner.**

Principles are mapped using a health-AI ethics framing. NIST-style governance is operationalised through ownership, mapping, measurement, monitoring and mitigation. Automated mappings are screening aids. “Violated” should only be used when supported by sufficiently authoritative evidence.

### Publication discipline
Keep source facts, automated classifications and analyst interpretation visibly separate. All new signals default to **Pending human review**.''')
