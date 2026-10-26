"""Render static, source-backed process-book designs. No website or D3 code.
Run with the project-compatible Python environment plus reportlab and Poppler.
"""
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
W, H = 1080, 760
C = {'paper':'#F4F1E9','ink':'#19392E','muted':'#50635A','line':'#CCD3C9','white':'#FFFFFF',
     'green':'#42765D','pale':'#E5ECE3','terra':'#B05F43','peach':'#F3E0D3','blue':'#466789','light':'#F9FAF6','grey':'#8B928B'}
for k,v in C.items(): C[k] = HexColor(v)

def read(name):
    with (ROOT/'data/processed'/name).open() as f: return list(csv.DictReader(f))
industries = read('uscis_fy2025_industries.csv')
employers = read('opt_h1b_employer_overlap.csv')
audit = read('opt_h1b_match_audit.csv')
assert len(employers) == 47 and len(audit) == 200
for r in employers:
    a,b = r['employer_name'],r['uscis_employer_name']
    r['display_match_type'] = 'verbatim' if a==b else 'case_space' if ' '.join(a.upper().split())==' '.join(b.upper().split()) else 'formatting'
assert Counter(r['display_match_type'] for r in employers) == {'verbatim':15,'case_space':28,'formatting':4}
assert all(r['match_status']=='accepted_unique_name' for r in employers)
national = sum(int(r['initial_approvals']) for r in industries)
assert national == 114804
known = sorted([r for r in industries if r['naics_code']],key=lambda r:-int(r['initial_approvals']))
missing = next(r for r in industries if not r['naics_code'])
byname = {r['employer_name']:r for r in employers}
PDF = HERE/'prototype-v1-design-drafts.pdf'
c = canvas.Canvas(str(PDF),pagesize=(W,H),pageCompression=1)
c.setTitle('CS1710 Prototype V1 - three visualization design drafts')
c.setAuthor('CS1710 project - design documentation; contributor roster pending')

def box(x,y,w,h,fill='white',stroke=None,r=0):
    c.setFillColor(C.get(fill,fill));c.setStrokeColor(C.get(stroke,stroke) if stroke else C.get(fill,fill));c.setLineWidth(.7)
    if r:c.roundRect(x,H-y-h,w,h,r,fill=1,stroke=bool(stroke))
    else:c.rect(x,H-y-h,w,h,fill=1,stroke=bool(stroke))

def line(x1,y1,x2,y2,color='line',width=.7,dash=None):
    c.saveState();c.setStrokeColor(C[color]);c.setLineWidth(width)
    if dash:c.setDash(*dash)
    c.line(x1,H-y1,x2,H-y2);c.restoreState()

def text(x,y,s,size=11,color='ink',font='Helvetica',align='left'):
    c.setFillColor(C[color]);c.setFont(font,size)
    if align=='right':c.drawRightString(x,H-y-size,s)
    elif align=='center':c.drawCentredString(x,H-y-size,s)
    else:c.drawString(x,H-y-size,s)

def para(x,y,w,s,size=11,color='muted',maxh=None,bold=False):
    style=ParagraphStyle('p',fontName='Helvetica-Bold' if bold else 'Helvetica',fontSize=size,leading=size*1.42,textColor=C[color],spaceAfter=0)
    p=Paragraph(s,style);pw,ph=p.wrap(w,1000)
    if maxh is not None:assert ph<=maxh+0.1, f'Text exceeds box: {s[:70]} ({ph}>{maxh})'
    p.drawOn(c,x,H-y-ph);return ph

def pill(x,y,w,s,selected=False):
    box(x,y,w,27,'ink' if selected else 'light','line',r=4)
    text(x+10,y+7,s,10,'white' if selected else 'ink')

def dot(x,y,kind='verbatim',size=4,selected=False):
    color={'verbatim':'green','case_space':'blue','formatting':'terra'}[kind]
    c.saveState();c.setStrokeColor(C[color]);c.setFillColor(C[color]);c.setLineWidth(1.4)
    if selected:c.setStrokeColor(C['terra']);c.circle(x,H-y,size+4,stroke=1,fill=0)
    if kind=='verbatim':c.circle(x,H-y,size,fill=1,stroke=0)
    elif kind=='case_space':c.circle(x,H-y,size,fill=0,stroke=1)
    else:
        p=c.beginPath();p.moveTo(x,H-y+size+1);p.lineTo(x+size+1,H-y);p.lineTo(x,H-y-size-1);p.lineTo(x-size-1,H-y);p.close();c.drawPath(p,fill=1,stroke=0)
    c.restoreState()

def header(n,title,subtitle,status='DESIGN DRAFT / STATIC MOCKUP'):
    box(0,0,W,H,'paper');box(0,0,W,7,'ink')
    text(36,27,'INTERNATIONAL TALENT IN AMERICA',10,'muted','Helvetica-Bold')
    text(W-36,27,status,9,'terra','Helvetica-Bold','right')
    text(36,51,n+'  /  '+title,30,'ink','Times-Roman')
    para(36,94,W-72,subtitle,11,maxh=38)

def footer(page,source):
    line(36,714,W-36,714)
    para(36,723,850,source,8,'muted',maxh=26)
    text(W-36,726,f'CS1710 / PROCESS-BOOK INSERT / {page:02}',8,'muted',align='right')

def section(x,y,label):text(x,y,label.upper(),10,'terra','Helvetica-Bold')

def bullets(x,y,w,items,size=11,gap=13):
    for label,body in items:
        text(x,y,label,size,'ink','Helvetica-Bold');y+=size+6
        y+=para(x,y,w,body,size,'muted')+gap
    return y

def plot_scatter(x,y,w,h,rows,metric='total_opt_or_stem_opt_participants',selected='Harvard University',xmax=2000,ymax=300,labels=False):
    for t in [0,50,100,150,200,250,300]:
        if t>ymax:continue
        yy=y+h-h*t/ymax;line(x,yy,x+w,yy)
        text(x-9,yy-5,str(t),9,'muted',align='right')
    ticks=[0,500,1000,1500,2000] if xmax==2000 else [0,100,200,300,400,500]
    for t in ticks:
        if t>xmax:continue
        xx=x+w*t/xmax;line(xx,y,xx,y+h,'line',.6)
        text(xx,y+h+9,f'{t:,}',9,'muted',align='center')
    line(x,y+h,x+w,y+h,'muted',1)
    selected_row=None
    for r in rows:
        if not r[metric]:continue
        xx=x+w*int(r[metric])/xmax;yy=y+h-h*int(r['h1b_initial_approvals'])/ymax
        assert x<=xx<=x+w and y<=yy<=y+h
        if r['employer_name']==selected:selected_row=(r,xx,yy);continue
        dot(xx,yy,r['display_match_type'])
    if selected_row:
        r,xx,yy=selected_row;line(xx,yy,xx,y+h,'terra',.8,(3,3));line(x,yy,xx,yy,'terra',.8,(3,3));dot(xx,yy,r['display_match_type'],5,True)
        if labels:text(xx+12,yy-18,'Harvard University',9,'terra','Helvetica-Bold')
    if labels:
        for name,dy in [('Infosys Limited',-19),('Arizona State University',-22)]:
            r=byname[name];xx=x+w*int(r[metric])/xmax;yy=y+h-h*int(r['h1b_initial_approvals'])/ymax
            text(xx-5,yy+dy,name,9,'muted',align='right' if name.startswith('Arizona') else 'left')

# 01 Industry: ready data, proposed interactions.
header('01','Across the economy','A ranked view of FY2025 initial H-1B approvals by employer industry. Bar lengths use actual processed USCIS records.')
box(36,139,1008,51,'ink',r=5)
text(53,150,f'{national:,}',22,'white','Helvetica-Bold');text(163,154,'initial approvals',11,'white')
text(376,154,'20 reported sectors',11,'white');text(656,154,f'{int(missing["initial_approvals"]):,} approvals: industry not reported',11,'white')
pill(36,202,136,'Approvals  [selected]',True);pill(180,202,128,'National share (%)');pill(316,202,137,'Order: largest first');pill(461,202,137,'Search industry...')
text(1044,211,'PROPOSED CONTROLS',9,'muted',align='right')
box(36,241,675,365,'white',r=5);box(728,241,316,365,'white',r=5)
text(53,252,'TOP 10 REPORTED INDUSTRIES',10,'muted','Helvetica-Bold')
text(695,252,'10 of 20 sectors shown',9,'muted',align='right')
startx,endx,top=329,636,292
for t in [0,10000,20000,30000,40000]:
    xx=startx+(endx-startx)*t/45000;line(xx,281,xx,555,'line',.6)
    text(xx,565,'0' if not t else f'{t//1000}k',9,'muted',align='center')
labels={'54':'Professional, scientific & technical','61':'Educational services','31-33':'Manufacturing','51':'Information','62':'Health care & social assistance','52':'Finance & insurance','44-45':'Retail trade','56':'Admin., support & waste services','23':'Construction','42':'Wholesale trade'}
for i,r in enumerate(known[:10]):
    yy=top+i*26
    if r['naics_code']=='61':box(45,yy-5,657,25,'peach',r=3)
    text(53,yy,f'{i+1:02}',9,'muted');text(77,yy,labels[r['naics_code']],10)
    v=int(r['initial_approvals']);box(startx,yy, (endx-startx)*v/45000,14,'terra' if r['naics_code']=='61' else 'green')
    text(startx+(endx-startx)*v/45000+6,yy-1,f'{v:,}',9,'ink')
text(485,585,'Initial approvals (petitions)',9,'muted',align='center')
section(747,257,'Selected industry / NAICS 61');text(747,280,'Educational Services',22,font='Times-Roman')
r=next(r for r in industries if r['naics_code']=='61');v=int(r['initial_approvals'])
text(747,319,f'{v:,}',35,font='Helvetica-Bold');text(747,362,f'{100*v/national:.1f}% of all initial approvals',12,'terra','Helvetica-Bold')
line(747,395,1025,395)
for yy,label,key in [(410,'New employment','new_employment_approvals'),(439,'New concurrent employment','new_concurrent_approvals')]:
    text(747,yy,label,11,'muted');text(1025,yy,f'{int(r[key]):,}',12,'ink','Helvetica-Bold','right')
para(747,478,272,'Hover or focus previews a sector. Click or Enter pins this detail. Escape clears the selection.',11,maxh=68)
text(747,556,'Source: USCIS export / FY2025',9,'muted');text(747,575,'View all 20 sectors  +  data table',10,'terra','Helvetica-Bold')
box(36,621,1008,70,'pale',r=4)
para(51,632,475,'<b>Keep missing industry visible.</b> The 2,215 approvals without a code stay in a separate pinned row/card. They remain in the national-share denominator.',10,maxh=52)
para(549,632,477,'<b>Interpretation.</b> Industries describe employers, not occupations. Initial approvals include new and concurrent employment; they are not unique workers.',10,maxh=52)
footer(1,'Source: data/processed/uscis_fy2025_industries.csv. National total 114,804; reported sectors 112,589; missing industry 2,215. Short display labels expand on focus.')
c.showPage()

# 02 Industry specification and alternate state.
header('01','Interaction & inclusion rules','Design specification / ranked industry view. These states are proposals, not implemented controls.')
box(36,144,493,543,'white',r=5);box(547,144,497,543,'white',r=5)
section(54,161,'Why this view');
bullets(54,188,455,[('Comparable lengths, clear units','Horizontal bars share a zero baseline. Descending order makes breadth visible without assuming that every large sector is a technology company.'),('Stable meaning when filtering','Search and Top 10 / All 20 affect visibility only. National-share mode always divides by 114,804, including missing industry; the denominator never becomes a filtered subtotal.'),('Show small sectors without distorting scale','The All 20 state increases chart height and scrolls within the section. No broken axis or log-scaled bars. Exact values and a data table support the smallest counts.'),('Provenance stays nearby','A pinned selection exposes NAICS, new/concurrent components, fiscal year and original file. NFAP is a comparison source only: its national total is two higher.')],10.5,14)
section(565,161,'Alternate state / share of national total')
for i,code in enumerate(['61','62','31-33']):
    r=next(r for r in industries if r['naics_code']==code);v=int(r['initial_approvals'])/national*100;yy=198+i*52
    text(565,yy,labels[code],11)
    box(565,yy+19,400*v/100,14,'terra' if code=='61' else 'green')
    text(565+400*v/100+7,yy+18,f'{v:.1f}%',10)
text(565,358,'Illustrated subset; denominator remains all 114,804 approvals.',9,'muted')
line(565,387,1026,387)
bullets(565,406,456,[('Keyboard and touch','Tab reaches the search, mode controls and bars. Focus reveals the same information as hover; Enter pins it. Touch targets include the full row, not only the bar.'),('Mobile layout','Long sector names wrap above full-width bars. Move detail directly below the chart and announce updates. Missing-industry context stays visible before the collapsed source note.'),('Before implementation is accepted','Check 20 sectors + missing; values sum to 114,804; display share matches exact counts; changing sort preserves the selected NAICS; no-data searches offer Reset.')],10.5,14)
footer(2,'Draft rationale and states. Share values are computed from the same supplied FY2025 USCIS CSV. No industry classification or residual value is invented.')
c.showPage()

# 03 Wage mockup deliberately has no data marks, axis ticks or salaries.
header('02','Offered wages, in context','Proposed occupation-level comparison of DOL offered wages with BLS occupational medians. No salary data are available.', 'PROPOSED / DATA UNAVAILABLE')
box(36,139,1008,58,'peach',r=5)
text(52,149,'DATA GATE CLOSED',11,'terra','Helvetica-Bold')
para(52,168,970,'The matched DOL and BLS inputs are unavailable. No wage values, differences, ranks or quantitative positions are shown in this draft.',11,maxh=22)
pill(36,211,230,'Occupation: choose after SOC audit');pill(275,211,201,'Reference year: not yet chosen');pill(485,211,192,'Geography: must be matched');pill(686,211,195,'Annual wage basis: pending')
text(1044,250,'PLANNED CONTROLS / DISABLED UNTIL DATA VALIDATE',9,'muted',align='right')
box(36,274,674,322,'white',r=5);box(728,274,316,322,'white',r=5)
section(55,292,'Planned comparison canvas')
text(55,319,'One row per matched occupation',20,font='Times-Roman')
box(55,362,636,156,'light','line',r=4)
para(94,389,555,'<b>No quantitative marks yet.</b><br/>Once matched records exist, each occupation row will place a DOL filing-level offered-wage median and a BLS occupational median on a common annual-USD scale.',13,maxh=100)
text(373,538,'Annual USD / numeric ticks withheld until data validate',10,'muted',align='center')
text(55,569,'Missing or incompatible occupations receive an explicit status row.',10,'muted')
section(747,291,'Legend / encoding only')
dot(755,330,'verbatim',5);para(774,319,245,'DOL: median offered annual wage across eligible filings.',11,maxh=48)
dot(755,391,'formatting',5);para(774,380,245,'BLS: published annual occupational median for the matched geography and reference period.',11,maxh=65)
line(747,457,1025,457)
para(747,477,275,'<b>When available:</b> select an occupation to inspect sample size, exclusions, wage units, years and source definitions.',11,maxh=82)
box(36,613,1008,78,'ink',r=5)
para(53,627,470,'<b>Two distinct measurements</b><br/>Offered filing wages do not establish actual pay. A filing-level median and a worker-based occupational statistic have different weighting and coverage.',10,'white',maxh=54)
para(552,627,475,'<b>No conclusion in advance</b><br/>No claim of a wage premium, underpayment, or causal effect is made. Occupations and comparison periods are chosen only after source inspection.',10,'white',maxh=54)
footer(3,'Planned sources: DOL FY2025 Q4 LCA disclosure + record layout; BLS occupational wage estimates with compatible SOC, annual units, geography and reference period. No matched wage dataset exists.')
c.showPage()

# 04 Method plan, data gate, and future interactions.
header('02','From source records to a fair comparison','Design specification / unavailable wage data. Every analysis choice below is a proposal to validate, not an observed result.')
box(36,143,1008,92,'white',r=5)
for i,(title,body) in enumerate([('1  INSPECT','DOL fields, revisions, statuses and wage units'),('2  ALIGN','SOC edition, geography, periods and annual units'),('3  VALIDATE','Coverage, missingness, ranges and sample sizes'),('4  ENABLE','Only matched occupation rows become plottable')]):
    xx=53+i*250;section(xx,158,title);para(xx,180,218,body,10.5,maxh=43)
box(36,253,492,438,'white',r=5);box(546,253,498,438,'white',r=5)
section(54,270,'Planned marks and interactions')
bullets(54,297,453,[('Aligned dot-pair rows','For each supported occupation, put both medians on one annual-USD scale. A thin connector shows a descriptive difference, not a causal effect or a pay-equity finding. The legend uses shape as well as color.'),('Occupation selection and hover','Hover/focus gives the two definitions and available values. Click pins an evidence panel: SOC label/version, DOL filing count, excluded records, wage-range treatment and BLS period/geography.'),('Filtering without hidden denominator changes','Search an occupation; filter only valid matched periods/geographies. Display the DOL sample and exclusions. Default to alphabetical order; offer signed-difference ordering only after valid values exist.'),('Missing, empty and mobile states','Use text statuses, never a zero for missing data. One absent source means no connector or difference. On phones, stack the two labeled values with a comparison detail drawer.')],10.5,12)
section(564,270,'Proposed analysis contract')
bullets(564,297,459,[('DOL sample and unit','Use a documented H-1B, certified-filing sample, deduplicated by case ID after reviewing revisions. A case is a filing, not a worker; do not silently weight by requested positions.'),('Range and time rules','Proposed primary sample: directly reported annual, single-valued wages. Do not invent range midpoints or hours-per-year. Count range/hourly exclusions and consider separate sensitivity views.'),('BLS pairing','Use the same SOC version and comparable occupation scope; match national geography by aggregating eligible DOL national filings. Inspect dates before choosing BLS vintage; disclose any mismatch or withhold the comparison.'),('Release checks','No invented values. Display definitions and sample sizes; require a predeclared adequate-sample rule after profiling, expose exclusions, and verify all computed medians against the processed data.')],10.5,12)
footer(4,'A design gate, not a completed analysis. Any unresolved SOC crosswalk, incompatible period, unavailable BLS estimate or mixed wage basis keeps that comparison disabled.')
c.showPage()

# 05 Novel source-aware linked view.
header('03','Two datasets. One employer lens.','Novel project view / a linked scatterplot and provenance panel for 47 accepted name-level comparisons. All plotted positions use real processed values.')
box(36,137,1008,54,'peach',r=5)
para(52,148,976,'<b>Different populations and periods.</b> ICE: calendar-2024 OPT/STEM OPT participation. USCIS: FY2025 initial petition approvals. These are not individual transitions, conversion rates, or verified legal-entity matches.',11,maxh=38)
pill(36,204,176,'Search accepted employer...');pill(220,204,122,'Combined  [x]',True);pill(350,204,65,'OPT');pill(423,204,92,'STEM OPT')
text(1044,213,'47 / 47 SHOWN  |  153 EXCLUDED FROM JOIN',9,'muted','Helvetica-Bold','right')
for xx,kind,label in [(45,'verbatim','Verbatim exact (15)'),(227,'case_space','Case / spacing only (28)'),(456,'formatting','Formatting-normalized (4)')]:
    dot(xx,251,kind,4);text(xx+12,245,label,10)
text(1044,246,'Proposed filters; shapes describe formatting, not confidence.',9,'muted',align='right')
box(36,272,651,337,'white',r=5);box(703,272,341,337,'white',r=5)
text(53,282,'FY2025 initial H-1B approvals (petitions)',11,'ink','Helvetica-Bold')
plot_scatter(78,311,578,239,employers,labels=True)
text(367,583,'CY2024 total OPT or STEM OPT participation (source count)',10,'muted',align='center')
section(721,285,'Pinned employer');text(721,306,'Harvard University',23,font='Times-Roman')
pill(721,343,167,'Case / spacing-only match')
text(721,384,'ICE / CY2024',9,'muted','Helvetica-Bold');text(1025,381,'1,036',24,'ink','Helvetica-Bold','right')
text(721,409,'OPT 799   |   STEM OPT 407',10,'muted')
text(721,425,'Combined is not OPT + STEM OPT.',9,'terra','Helvetica-Bold')
line(721,448,1025,448)
text(721,462,'USCIS / FY2025 INITIAL',9,'muted','Helvetica-Bold');text(1025,458,'112',24,'ink','Helvetica-Bold','right')
text(721,491,'New employment 110   |   Concurrent 2',10,'muted')
para(721,521,303,'<b>Inspect the match:</b> Harvard University / HARVARD UNIVERSITY. USCIS suffix 3580. Name agreement does not verify identity.',9.5,maxh=47)
text(721,580,'ICE p.1, row 19  |  USCIS source line 24394',9,'muted')
box(36,623,651,68,'pale',r=4);box(703,623,341,68,'pale',r=4)
text(53,632,'PERIOD OVERLAP / NOT A STUDENT COHORT',9,'ink','Helvetica-Bold')
text(53,654,'ICE: Jan-Dec 2024',9,'muted');text(53,674,'USCIS: Oct 2024-Sep 2025',9,'muted')
# 21 months from Jan 2024 to Sep 2025, overlap is Oct-Dec 2024.
xx=234;ww=365
box(xx+ww*9/21,649,ww*3/21,37,'peach')
box(xx,653,ww*12/21,7,'green');box(xx+ww*9/21,675,ww*12/21,7,'blue')
text(xx+ww*10.5/21,634,'Oct-Dec 2024',8,'terra',align='center')
para(720,635,307,'<b>Explore safely.</b> Hover/focus previews. Click pins. Brush zooms a cluster without changing values. All actions have keyboard/list alternatives.',10,maxh=48)
footer(5,'Sources: opt_h1b_employer_overlap.csv (47 accepted rows); opt_h1b_match_audit.csv (200 decisions). One point = one accepted employer-name pair. Equal point sizes; no ratio diagonal or flow arrows.')
c.showPage()

# 06 Novel alternate filter view and detailed interaction contract.
header('03','Explore the pattern. Inspect the match.','Design specification / the novelty is the linked treatment of values, name evidence and overlapping periods, not the scatterplot alone.')
box(36,142,495,544,'white',r=5);box(548,142,496,544,'white',r=5)
section(54,159,'Proposed state / formatting filter only')
text(54,183,'4 of 47 accepted names',21,font='Times-Roman')
text(54,214,'Same axes as overview; no hidden rescaling.',10,'muted')
formatting=[r for r in employers if r['display_match_type']=='formatting']
plot_scatter(81,259,415,181,formatting,selected=None)
text(81,240,'Initial approvals / FY2025',9,'muted')
text(289,471,'Combined participation / CY2024',9,'muted',align='center')
text(440,496,'CY2024',8,'muted',align='right');text(510,496,'FY2025',8,'muted',align='right')
for i,r in enumerate(formatting):
    yy=515+i*26;dot(58,yy+5,'formatting',3)
    text(70,yy,r['employer_name'],10)
    text(440,yy,f'{int(r["total_opt_or_stem_opt_participants"]):,}',10,'muted',align='right')
    text(510,yy,f'{int(r["h1b_initial_approvals"]):,}',10,'muted',align='right')
para(54,632,457,'Separate columns show CY2024 participation and FY2025 initial approvals. The filter changes visible pairs only, never the acceptance rule.',10,maxh=43)
section(566,159,'Planned behavior and evidence')
bullets(566,187,459,[('Axes and point meaning','X defaults to the ICE combined source count. Y is new + concurrent USCIS approvals. Each equal-sized point is one accepted name pair; missing values never become zero. Both axes start at zero and use linear scales.'),('Selection, hover and cluster inspection','Hover or keyboard focus previews both values, years and name type. Click / Enter pins the panel; Escape clears it. A brush zooms a dense cluster with a visible reset and domain labels. Provide range inputs and an employer list for non-pointer users.'),('Filters and missing STEM participation','Search within the accepted 47 only. Toggle the three name-format types without changing acceptance. Switching X to STEM OPT shows 46 plottable pairs and a notice for Carnegie Mellon University, whose STEM cell is missing.'),('Panel and mobile behavior','Show both original names, match reason, USCIS suffix, source lines and ICE page. Retain combined/OPT/STEM separately. On narrow screens stack chart then sticky selected detail; the period/population warning stays before the plot.'),('Novelty and acceptance criteria','The panel exposes identity evidence and period overlap at the moment a point is inspected. No confidence score, conversion ratio, trend line, causal label or equal-value diagonal. Verify all 47 plotted pairs and derived shape labels against preserved records.')],10.3,12)
footer(6,'Name-format labels are derived for this design from preserved ICE/USCIS names: 15 verbatim, 28 case/spacing only, 4 punctuation/ampersand normalized. They are not new matching outcomes or confidence tiers.')
c.save()

# Design-only record of exactly what is pictured, with data hashes and match-label derivation.
snapshot={
    'purpose':'Static design documentation only; no application or matching-pipeline changes.',
    'input_sha256':{name:hashlib.sha256((ROOT/'data/processed'/name).read_bytes()).hexdigest() for name in ['uscis_fy2025_industries.csv','opt_h1b_employer_overlap.csv','opt_h1b_match_audit.csv']},
    'industry_total':national,'industry_missing':int(missing['initial_approvals']),
    'match_types':dict(Counter(r['display_match_type'] for r in employers)),
    'match_type_rule':'Verbatim if original strings equal; else case_space if uppercase whitespace-collapsed names equal; otherwise formatting. All rows were already accepted by the pipeline.',
    'points':[{k:r[k] for k in ['employer_name','uscis_employer_name','total_opt_or_stem_opt_participants','h1b_initial_approvals','display_match_type']} for r in employers],
    'wage_data_values':[],'wage_data_status':'unavailable; no marks or numeric wage scale shown',
}
(HERE/'design-data-audit.json').write_text(json.dumps(snapshot,indent=2)+'\n')
# Portable vector PDF plus high-resolution images for insertion into a process book.
for page,name in [(1,'01-industry-ranked-bars'),(3,'02-wage-comparison-proposed'),(5,'03-employer-comparison-novel')]:
    subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-scale-to','2400','-png','-singlefile',str(PDF),str(HERE/name)],check=True)
print('Created six-page PDF and three 2400px PNG mockups in',HERE)
