"""Static documentation only: two unimplemented, source-backed design drafts.
Requires ReportLab, openpyxl and Poppler. Reads sources; never writes data/ or src/.
Run from any directory. The intermediate vector PDF stays in tmp/pdfs/.
"""
import csv
import hashlib
import json
import math
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from openpyxl import load_workbook

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
W, H = 1080, 900
C = {k:HexColor(v) for k,v in {'paper':'#F4F1E9','ink':'#19392E','muted':'#50635A','line':'#CCD3C9','white':'#FFFFFF','green':'#42765D','pale':'#E5ECE3','terra':'#A44E34','peach':'#F3E0D3','blue':'#466789','light':'#F9FAF6','grey':'#8B928B'}.items()}

def read(name):
    with (ROOT/'data/processed'/name).open() as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records = read('uscis_fy2025_records.csv')
fields = read('fields_of_study.csv')
assert len(records)==62415 and len({r['record_id'] for r in records})==62415
assert {int(r['source_line']) for r in records}==set(range(1,62416))
assert all(r['fiscal_year']=='2025' for r in records)
states = defaultdict(lambda:dict(initial=0,new=0,concurrent=0,records=0))
for r in records:
    initial,new,concurrent = [int(r[k]) for k in ['initial_approvals','new_employment_approvals','new_concurrent_approvals']]
    assert initial==new+concurrent
    s=states[r['petitioner_state']]
    for k,v in [('initial',initial),('new',new),('concurrent',concurrent),('records',1)]:s[k]+=v
national=sum(s['initial'] for s in states.values())
assert national==114804
assert sum(s['new'] for s in states.values())==113458
assert sum(s['concurrent'] for s in states.values())==1346
# Independent comparison against the preserved UTF-16 tab-delimited original.
raw_states=defaultdict(lambda:dict(initial=0,new=0,concurrent=0,records=0))
raw_path=ROOT/'data/raw/Employer Information (1).csv'
with raw_path.open(encoding='utf-16') as f:
    raw=list(csv.DictReader(f,delimiter='\t'))
for r in raw:
    assert r['Fiscal Year   '].strip()=='2025'
    new=int(r['New Employment Approval'].replace(',','').strip() or '0')
    concurrent=int(r['New Concurrent Approval'].replace(',','').strip() or '0')
    s=raw_states[r['Petitioner State'].strip()]
    for k,v in [('initial',new+concurrent),('new',new),('concurrent',concurrent),('records',1)]:s[k]+=v
assert dict(raw_states)==dict(states)

geometry=HERE/'assets/cb_2024_us_state_20m.zip'
provenance=json.loads(geometry.with_suffix('.provenance.json').read_text())
assert sha(geometry)==provenance['sha256']
ns={'k':'http://www.opengis.net/kml/2.2'}
with zipfile.ZipFile(geometry) as z:tree=ET.fromstring(z.read('cb_2024_us_state_20m.kml'))
geo={}
for place in tree.findall('.//k:Placemark',ns):
    attrs={d.attrib['name']:d.text for d in place.findall('.//k:SimpleData',ns)}
    polygons=[]
    for polygon in place.findall('.//k:Polygon',ns):
        rings=[]
        for coords in polygon.findall('.//k:coordinates',ns):
            rings.append([tuple(map(float,p.split(',')[:2])) for p in coords.text.split()])
        polygons.append(rings)
    geo[attrs['STUSPS']]={'name':attrs['NAME'],'polygons':polygons}
mapped=set(geo)-{'PR'}
assert len(mapped)==51 and mapped<=set(states)
mapped_total=sum(states[s]['initial'] for s in mapped)
territory_codes=['GU','PR','MP','VI','AS']
territory_total=sum(states[s]['initial'] for s in territory_codes)
unlocated_codes=['','XX','AA']
unlocated_total=sum(states[s]['initial'] for s in unlocated_codes)
assert set(states)==mapped|set(territory_codes)|set(unlocated_codes)
assert (mapped_total,territory_total,unlocated_total)==(114396,385,23)
assert mapped_total+territory_total+unlocated_total==national

# Every field-year cell is checked against its source-workbook coordinates.
assert len(fields)==405 and len({(r['academic_year'],r['field_of_study']) for r in fields})==405
assert all(r['students']!='' for r in fields)
book=load_workbook(ROOT/'data/raw/open_doors_fields.xlsx',data_only=True)
for r in fields:
    cell=book.active.cell(int(r['source_row']),int(r['source_column'])).value
    assert int(r['students'])==int(cell), (r,cell)
years=sorted({r['academic_year'] for r in fields})
assert len(years)==27 and years[0]=='1998/99' and years[-1]=='2024/25'
assert [int(y[:4]) for y in years]==list(range(1998,2025))
by_year={y:{r['field_of_study']:int(r['students']) for r in fields if r['academic_year']==y} for y in years}
assert all(len(v)==15 for v in by_year.values())
totals={y:sum(v.values()) for y,v in by_year.items()}
order=['Math and Computer Science','Engineering','Business and Management','Physical and Life Sciences','Social Sciences','Other Fields of Study','Fine and Applied Arts','Health Professions','Communications and Journalism','Humanities','Education','Agriculture','Legal Studies and Law Enforcement','Intensive English','Undeclared']
assert set(order)==set(by_year[years[0]])
palette=['#19392E','#42765D','#466789','#8CA89B','#A44E34','#CC987A','#C4B17B','#96A4BE','#705A6A','#9D8D9D','#70807A','#A1AF7E','#8C744C','#BCC4C0','#DED9CC']
short=['Math & computer science','Engineering','Business & management','Physical & life sciences','Social sciences','Other fields of study','Fine & applied arts','Health professions','Communications & journalism','Humanities','Education','Agriculture','Legal studies & law enforcement','Intensive English','Undeclared']
latest=years[-1];sel='Math and Computer Science';value=by_year[latest][sel]
assert value==305377 and totals[latest]==1177766

out=ROOT/'tmp/pdfs/additional-unimplemented-designs.pdf'
out.parent.mkdir(parents=True,exist_ok=True)
c=canvas.Canvas(str(out),pagesize=(W,H),pageCompression=1)
c.setTitle('Proposed CS1710 visualizations - geography and fields of study')

def color(k):return C[k] if isinstance(k,str) and k in C else HexColor(k) if isinstance(k,str) else k
def box(x,y,w,h,fill='white',stroke=None,r=0):
    c.setFillColor(color(fill));c.setStrokeColor(color(stroke or fill));c.setLineWidth(.6)
    if r:c.roundRect(x,H-y-h,w,h,r,fill=1,stroke=bool(stroke))
    else:c.rect(x,H-y-h,w,h,fill=1,stroke=bool(stroke))
def text(x,y,s,size=11,fill='ink',font='Helvetica',align='left'):
    c.setFillColor(color(fill));c.setFont(font,size)
    if align=='right':c.drawRightString(x,H-y-size,s)
    elif align=='center':c.drawCentredString(x,H-y-size,s)
    else:c.drawString(x,H-y-size,s)
def para(x,y,w,s,size=11,fill='muted',maxh=1000):
    p=Paragraph(s,ParagraphStyle('p',fontName='Helvetica',fontSize=size,leading=size*1.4,textColor=color(fill)))
    _,h=p.wrap(w,1000);assert h<=maxh+.1,(s[:60],h,maxh)
    p.drawOn(c,x,H-y-h)
def line(x,y,x2,y2,fill='line',width=.7,dash=None):
    c.saveState();c.setStrokeColor(color(fill));c.setLineWidth(width)
    if dash:c.setDash(*dash)
    c.line(x,H-y,x2,H-y2);c.restoreState()
def pill(x,y,w,s,active=False):
    box(x,y,w,30,'ink' if active else 'light','line',4);text(x+11,y+9,s,10,'white' if active else 'ink')
def heading(n,title,subtitle):
    box(0,0,W,H,'paper');box(0,0,W,7,'ink')
    text(36,28,'INTERNATIONAL TALENT IN AMERICA',10,'muted','Helvetica-Bold')
    text(1044,28,'PROPOSED / NOT IMPLEMENTED',9,'terra','Helvetica-Bold','right')
    text(36,56,n+'  /  '+title,32,font='Times-Roman')
    para(36,102,1008,subtitle,11,maxh=32)
def footer(s):
    line(36,856,1044,856);para(36,865,825,s,8,maxh=26)
    text(1044,866,'CS1710 / DESIGN DRAFT',8,'muted',align='right')
def section(x,y,s):text(x,y,s.upper(),10,'terra','Helvetica-Bold')

# Spherical Albers equal-area projection of original Census lon/lat vertices.
# Inset Alaska and Hawaii are independently fitted and explicitly labeled.
def project(lon,lat,region='lower48'):
    lon0,p1,p2 = (-96,29.5,45.5) if region=='lower48' else (-154,55,65) if region=='AK' else (-157,8,18)
    if region=='AK' and lon>0:lon-=360
    rad=math.pi/180;p1*=rad;p2*=rad;n=(math.sin(p1)+math.sin(p2))/2
    const=math.cos(p1)**2+2*n*math.sin(p1)
    rho=math.sqrt(const-2*n*math.sin(lat*rad))/n;theta=n*(lon-lon0)*rad
    return rho*math.sin(theta),rho*math.cos(theta) # screen y points downward

def ring_centroid(ring):
    pairs=list(zip(ring,ring[1:]+ring[:1]));a=sum(x*y2-x2*y for (x,y),(x2,y2) in pairs)
    return (sum((x+x2)*(x*y2-x2*y) for (x,y),(x2,y2) in pairs)/(3*a),sum((y+y2)*(x*y2-x2*y) for (x,y),(x2,y2) in pairs)/(3*a),abs(a))

def map_color(v):
    a=HexColor('#E5ECE3');b=C['ink'];t=v/states['CA']['initial']
    return Color(a.red+(b.red-a.red)*t,a.green+(b.green-a.green)*t,a.blue+(b.blue-a.blue)*t)
def draw_map(codes,x,y,w,h,region='lower48'):
    shapes={code:[[[project(lon,lat,region) for lon,lat in ring] for ring in polygon] for polygon in geo[code]['polygons']] for code in codes}
    pts=[p for polys in shapes.values() for poly in polys for ring in poly for p in ring]
    xmin,xmax=min(p[0] for p in pts),max(p[0] for p in pts);ymin,ymax=min(p[1] for p in pts),max(p[1] for p in pts)
    scale=min(w/(xmax-xmin),h/(ymax-ymin));ox=x+(w-scale*(xmax-xmin))/2;oy=y+(h-scale*(ymax-ymin))/2
    centers={}
    for code,polys in shapes.items():
        rings=[]
        for poly in polys:
            p=c.beginPath()
            for ring in poly:
                r=[(ox+(a-xmin)*scale,oy+(b-ymin)*scale) for a,b in ring];rings.append(r)
                p.moveTo(r[0][0],H-r[0][1])
                for a,b in r[1:]:p.lineTo(a,H-b)
                p.close()
            c.setFillColor(map_color(states[code]['initial']));c.setStrokeColor(C['white']);c.setLineWidth(.65);c.drawPath(p,fill=1,stroke=1,fillMode=0)
        centers[code]=max((ring_centroid(r) for r in rings),key=lambda p:p[2])[:2]
    # Selection changes outline, never the approval-count fill encoding.
    if 'CA' in codes:
        c.setStrokeColor(C['terra']);c.setLineWidth(2)
        for poly in shapes['CA']:
            for ring in poly:
                p=c.beginPath();r=[(ox+(a-xmin)*scale,oy+(b-ymin)*scale) for a,b in ring];p.moveTo(r[0][0],H-r[0][1])
                for a,b in r[1:]:p.lineTo(a,H-b)
                p.close();c.drawPath(p,fill=0,stroke=1)
    return centers

heading('04','Where sponsorship is registered','FY2025 initial H-1B petition approvals by petitioner state. Locations describe the filing employer, not employee worksites.')
box(36,148,1008,52,'ink',r=5)
text(53,160,f'{national:,}',23,'white','Helvetica-Bold');text(164,169,'initial approvals nationally',11,'white')
text(470,160,f'{mapped_total:,}',23,'white');text(577,169,'in 50 states + DC',11,'white')
text(810,160,f'{territory_total+unlocated_total:,}',23,'white');text(863,169,'shown separately',11,'white')
pill(36,214,173,'State: California  [selected]',True);pill(217,214,146,'Search state or territory');pill(371,214,123,'View accessible table')
text(1044,224,'PROPOSED CONTROLS / CLICK TO PIN',9,'muted',align='right')
box(36,261,675,443,'white',r=5);box(728,261,316,443,'white',r=5)
text(54,276,'INITIAL APPROVALS / LINEAR COLOR SCALE',10,'muted','Helvetica-Bold')
for i in range(220):box(54+i,299,1.2,10,map_color(states['CA']['initial']*i/219))
text(54,314,'0',9,'muted');text(164,314,'10,776',9,'muted',align='center');text(274,314,'21,552',9,'muted',align='right')
box(439,299,12,10,'white','terra');text(459,298,'Outline = selected state',9,'muted')
centers=draw_map(sorted(mapped-{'AK','HI'}),52,335,637,276)
for code in ['CA','TX','NY','VA','IL','WA','FL','CO','ND','AZ']:
    x,y=centers[code];text(x,y-5,code,9,'white' if states[code]['initial']>7000 else 'ink','Helvetica-Bold','center')
# DC leader uses its polygon centroid; it is not a geocoded observation.
x,y=centers['DC'];line(x,y,675,y+20,'muted');text(681,y+15,'DC',8,'muted')
draw_map(['AK'],63,602,135,60,'AK');draw_map(['HI'],220,611,78,45,'HI')
text(130,669,'Alaska',9,'muted',align='center');text(260,669,'Hawaii',9,'muted',align='center')
text(54,688,'Insets repositioned and independently scaled; Census 2024 boundaries.',8,'muted')
# A real-value hover preview shown alongside the selected California detail.
x,y=centers['TX'];line(x,y,480,621,'terra',.9,(3,3))
box(472,614,220,75,'ink',r=4);text(485,624,'HOVER PREVIEW / TEXAS',9,'white','Helvetica-Bold')
text(485,643,f"{states['TX']['initial']:,} initial approvals",13,'white')
text(485,666,f"{states['TX']['initial']/national:.1%} of national total  |  FY2025",10,'white')
section(747,279,'Selected state / CA');text(747,304,'California',28,font='Times-Roman')
text(747,347,f"{states['CA']['initial']:,}",40,font='Helvetica-Bold');text(747,397,'initial petition approvals',11,'muted')
text(747,420,f"{states['CA']['initial']/national:.1%} of the national total",13,'terra','Helvetica-Bold')
line(747,454,1025,454)
for yy,label,key in [(470,'New employment','new'),(500,'New concurrent employment','concurrent')]:
    text(747,yy,label,11,'muted');text(1025,yy,f"{states['CA'][key]:,}",12,font='Helvetica-Bold',align='right')
para(747,546,275,'Hover or focus previews a location. Click or Enter pins its details; Escape clears. A searchable selector makes small states and DC reachable.',11,maxh=80)
text(747,648,'FY2025: Oct 2024 - Sep 2025',10,'muted');text(747,671,'Source: USCIS Employer Data Hub',9,'muted')
box(36,721,1008,55,'pale',r=4)
para(52,731,980,'<b>Outside the 50-state/DC map: 408 approvals, retained in national shares.</b><br/>Territories: Guam 312; Puerto Rico 31; Northern Mariana Islands 28; U.S. Virgin Islands 14; American Samoa 0. Unlocated: blank 22; XX 1; AA 0. These are separate rows in the proposed table.',10,maxh=43)
box(36,788,1008,53,'peach',r=4)
para(52,799,475,'<b>Petitions, not people.</b> Initial = new employment + new concurrent employment. Continuing approvals and denials are excluded.',10,maxh=35)
para(548,799,477,'<b>Location is a limitation.</b> Headquarters or filing addresses may differ from worksites. Counts are not rates per resident or worker.',10,maxh=35)
footer('Counts: USCIS FY2025, uscis_fy2025_records.csv; all 62,415 source rows counted once. Geometry: U.S. Census Bureau, 2024 state boundaries (1:20m). Proposed interactions only.')
c.showPage()

heading('05','A changing mix of academic fields','International students by field, academic years 1998/99-2024/25. Open Doors field counts include OPT from 2008/09.')
box(36,148,1008,52,'ink',r=5)
text(53,160,'27',23,'white');text(90,169,'academic years',11,'white')
text(294,160,'15',23,'white');text(332,169,'reported broad fields',11,'white')
text(643,160,f'{totals[latest]:,}',23,'white');text(780,169,'summed field counts / 2024/25',11,'white')
pill(36,214,138,'Student counts',True);pill(182,214,151,'Composition (%)');pill(341,214,211,'Focus: Math & computer science');pill(560,214,116,'Reset all fields')
text(1044,224,'PROPOSED CONTROLS',9,'muted',align='right')
box(36,261,675,354,'white',r=5);box(728,261,316,354,'white',r=5)
text(55,276,'REPORTED STUDENT COUNTS',10,'muted','Helvetica-Bold')
text(693,276,'All 15 fields shown',9,'muted',align='right')
px,py,pw,ph=95,315,585,240;ymax=1200000
for t in [0,300000,600000,900000,1200000]:
    yy=py+ph-ph*t/ymax;line(px,yy,px+pw,yy);text(px-10,yy-5,'0' if t==0 else f'{t/1000000:.1f}m',9,'muted',align='right')
xpos=lambda i:px+pw*i/(len(years)-1)
ypos=lambda v:py+ph-ph*v/ymax
# Connect only adjacent recorded observations within consistent reporting regimes.
# White intervals before 2008/09 and 2020/21 deliberately withhold cross-break interpolation.
segments=[list(range(0,10)),list(range(10,22)),list(range(22,27))]
bottom=[0]*len(years)
for fi,name in enumerate(order):
    top=[bottom[i]+by_year[y][name] for i,y in enumerate(years)]
    for segment in segments:
        pts=[(xpos(i),ypos(top[i])) for i in segment]+[(xpos(i),ypos(bottom[i])) for i in reversed(segment)]
        path=c.beginPath();path.moveTo(pts[0][0],H-pts[0][1])
        for x,y in pts[1:]:path.lineTo(x,H-y)
        path.close();c.setFillColor(HexColor(palette[fi]));c.drawPath(path,fill=1,stroke=0)
    if fi==0:
        for segment in segments:
            for a,b in zip(segment,segment[1:]):line(xpos(a),ypos(top[a]),xpos(b),ypos(top[b]),'terra',1.3)
    bottom=top
assert bottom==[totals[y] for y in years]
for idx,label in [(0,'1998/99'),(6,'2004/05'),(10,'2008/09'),(16,'2014/15'),(22,'2020/21'),(26,'2024/25')]:text(xpos(idx),565,label,9,'muted',align='center')
for idx,label in [(10,'OPT field reporting'),(22,'CIP 2020')]:
    xx=xpos(idx);line(xx,303,xx,555,'terra',.85,(3,3));text(xx-5,298,label,8.5,'terra',align='right')
text(389,593,'Academic year / gaps mark reporting breaks, not missing counts',9,'muted',align='center')
# Illustrative endpoint tooltip anchored to a real observed Math/CS boundary.
line(xpos(26),ypos(value),xpos(26),555,'terra',1,(2,2))
c.setFillColor(C['terra']);c.circle(xpos(26),H-ypos(value),3,fill=1,stroke=0)
box(112,335,230,82,'ink',r=4)
text(126,346,'HOVER PREVIEW / 2024/25',9,'white','Helvetica-Bold')
text(126,367,'Math and Computer Science',12,'white')
text(126,390,f'{value:,} students  |  {value/totals[latest]:.1%} of fields',11,'white')
section(747,279,'Selected field / 2024/25');para(747,306,274,'Math and<br/>Computer Science',23,'ink',maxh=65)
text(747,383,f'{value:,}',37,font='Helvetica-Bold');text(747,428,'reported students',11,'muted')
text(747,451,f'{value/totals[latest]:.1%} of the summed field counts',12,'terra','Helvetica-Bold')
line(747,486,1025,486)
para(747,502,276,'<b>Read the mix, not a pathway.</b> Field counts describe international students, including OPT participants. They do not identify H-1B applicants or connect people across datasets.',10.5,maxh=80)
text(747,592,'Source: IIE Open Doors 2025',9,'muted')
box(36,632,1008,96,'white',r=5)
text(53,644,'INTERACTIVE LEGEND / select a field to focus it; retain the full stack and denominator',10,'muted','Helvetica-Bold')
for i,(label,col) in enumerate(zip(short,palette)):
    row=i%3;column=i//3;xx=53+column*198;yy=669+row*18
    box(xx,yy+2,9,9,col,'terra' if i==0 else None)
    # Longest label wraps without colliding with the next row by using a compact short label.
    label={'Legal studies & law enforcement':'Legal studies & law enf.','Communications & journalism':'Communications & journalism'}.get(label,label)
    text(xx+15,yy,label,8.7,'ink','Helvetica-Bold' if i==0 else 'Helvetica')
box(36,742,1008,98,'pale',r=4)
para(52,753,474,'<b>Composition mode: a stable denominator.</b> Divide each field by the sum of all 15 reported fields in that year. Focusing a field never rebases the total. Historical field sums may differ from published national totals.',10,maxh=70)
para(550,753,475,'<b>Read across breaks with care.</b> OPT fields first reported in 2008/09; CIP 2020 applies from 2020/21. All categories use Open Doors 2025 definitions. No counts are missing in this extract; future missing cells stay missing.',10,maxh=70)
footer('Source: IIE, Open Doors 2025, fields_of_study.csv and source workbook notes. 405 observed field-year cells; no imputation. Academic years, not calendar or fiscal years. Controls are proposals.')
c.save()

names=['04-h1b-geographic-map','05-fields-of-study-stacked-area']
for page,name in enumerate(names,1):
    subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-singlefile','-r','216','-png',str(out),str(HERE/name)],check=True,capture_output=True)

result={
 'status':'Two static, unimplemented design drafts; no application code',
 'input_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'data/processed/uscis_fy2025_records.csv',ROOT/'data/processed/fields_of_study.csv',raw_path,ROOT/'data/raw/open_doors_fields.xlsx',ROOT/'data/processed/source_notes.json',geometry]},
 'map':{'row_count':len(records),'unique_record_ids':len({r['record_id'] for r in records}),'source_lines_complete':True,'raw_state_components_equal_processed':True,'national_initial':national,'new':113458,'concurrent':1346,'mapped_50_states_and_dc':mapped_total,'territories':territory_total,'unlocated':unlocated_total,'state_totals':dict(sorted(states.items())),'selected_state':'CA','selected_share_percent':states['CA']['initial']/national*100,'tooltip_state':'TX','tooltip_share_percent':states['TX']['initial']/national*100,'geometry_provenance':provenance,'mapped_codes':sorted(mapped),'scale_domain':[0,states['CA']['initial']]},
 'fields':{'rows':len(fields),'source_workbook_cells_verified':405,'missing_cells':0,'year_count':len(years),'field_count':15,'academic_years':years,'field_order':order,'all_plotted_values':by_year,'denominators':totals,'selected_field':sel,'selected_year':latest,'selected_count':value,'selected_share_percent':value/totals[latest]*100,'reporting_breaks':['2008/09','2020/21'],'interpolation_across_reporting_breaks':False,'imputation':False},
 'pngs':{name+'.png':{'width':3240,'height':2700,'sha256':sha(HERE/(name+'.png'))} for name in names}
}
(HERE/'additional-design-data-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'map_records':len(records),'national_initial':national,'mapped_total':mapped_total,'territories':territory_total,'unlocated':unlocated_total,'field_cells_checked':405,'field_years':len(years),'outputs':names},indent=2))
