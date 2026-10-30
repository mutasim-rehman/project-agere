"""Render the two statistical PDFs and standalone scientific graphics, offline."""
import html
import json
import math
from pathlib import Path
import re
import subprocess
import textwrap

from reportlab import rl_config
from reportlab.graphics.shapes import Drawing, Line, Rect, String, Circle, PolyLine
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF, renderSVG
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak, Table, TableStyle, Preformatted, KeepTogether
from reportlab.platypus.tableofcontents import TableOfContents

ROOT=Path(__file__).resolve().parents[2]
DATA=json.loads((ROOT/'research/tier16_v2/data/statistical_analysis.json').read_text())
CROSS=json.loads((ROOT/'research/le16_v2/data/cross_tier_analysis.json').read_text())
S=DATA['summaries']; E=DATA['comparisons']['primary']['endpoints']
OUT=ROOT/'output/pdf'; FIG=ROOT/'figures/tier16_v2'; TEMP=ROOT/'.local/reporting'
NAVY=colors.HexColor('#17324D'); TEAL=colors.HexColor('#007F86'); AMBER=colors.HexColor('#D39528')
RED=colors.HexColor('#B54D40'); GRAY=colors.HexColor('#CBD3DB'); INK=colors.HexColor('#24364A')
PALE=colors.HexColor('#EDF3F7'); WHITE=colors.white
for name,file in [('Sans','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf'),('Serif','DejaVuSerif.ttf'),('Mono','DejaVuSansMono.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
pdfmetrics.registerFontFamily('Sans',normal='Sans',bold='Bold',italic='Sans',boldItalic='Bold')
pdfmetrics.registerFontFamily('Serif',normal='Serif',bold='Bold',italic='Serif',boldItalic='Bold')
rl_config.warnOnMissingFontGlyphs=1


def label(d,x,y,text,size=8,color=INK,anchor='start',font='Sans'):
    text=re.sub(r'(?<=[a-z])(?=\d)',' ',str(text)).replace('16GB','16 GB')
    for i,line in enumerate(str(text).split('\n')):
        d.add(String(x,y-i*(size+2),line,fontName=font,fontSize=size,fillColor=color,textAnchor=anchor))


def base(title,sub='',height=280):
    d=Drawing(480,height);label(d,8,height-18,title,11,NAVY,font='Bold')
    if sub:label(d,8,height-34,sub,7.5)
    return d


def axes(d,x,y,w,h,xmin,xmax,ymin,ymax,xticks,yticks,xlabel='',ylabel=''):
    fx=lambda v:x+(v-xmin)/(xmax-xmin)*w
    fy=lambda v:y+(v-ymin)/(ymax-ymin)*h
    for v in yticks:
        yy=fy(v);d.add(Line(x,yy,x+w,yy,strokeColor=GRAY,strokeWidth=.4));label(d,x-7,yy-3,f'{v:g}',7,anchor='end')
    for v in xticks:
        xx=fx(v);label(d,xx,y-14,f'{v:g}',7,anchor='middle')
    d.add(Line(x,y,x+w,y,strokeColor=INK,strokeWidth=.6));d.add(Line(x,y,x,y+h,strokeColor=INK,strokeWidth=.6))
    if xlabel:label(d,x+w/2,y-30,xlabel,7.5,anchor='middle')
    if ylabel:label(d,x,y+h+9,ylabel,7.5)
    return fx,fy


def outcomes(key='01_outcome_profiles',cross=False):
    d=base('All outcomes remain in the denominator' if not cross else 'Descriptive cross-tier recipes: no pooled RAM effect',
        'Reported-answer metric. N=160 for every16GB bar.' if not cross else 'Different report sets, adaptation, precision and serving recipes.',310)
    chart=VerticalBarChart();chart.x=44;chart.y=72;chart.width=422;chart.height=173
    if not cross:
        names=['SAS\nDirect','MAS\nDirect','SAS\nPrimary','MAS\nPrimary','SAS\nRepair','MAS\nRepair']
        selected=[S['tier16-'+a+'-'+p] for p in ['direct_control','primary','repair_ablation'] for a in ['sas','mas']]
        chart.valueAxis.valueMax=160;chart.valueAxis.valueStep=40
    else:
        names=['8G ctrl\nSAS/52','8G ctrl\nMAS/52','8G cross\nSAS/52','8G cross\nMAS/52','8G audit\nSAS/49','8G audit\nMAS/49','16G prim\nSAS/160','16G prim\nMAS/160']
        t=CROSS['tier8_natural']
        selected=[t['model_selection-control_sas-full-01'],t['model_selection-control_mas-full-01'],
            t['model_selection-crossed_sas-full-01'],t['model_selection-crossed_mas-full-01'],
            t['diagnostic_audit-control_sas-full-01'],t['diagnostic_audit-control_mas-full-01'],S['tier16-sas-primary'],S['tier16-mas-primary']]
        chart.valueAxis.valueMax=100;chart.valueAxis.valueStep=25
    chart.data=[tuple(s['metrics']['case_success'][e]*(100/s['n'] if cross else 1) for s in selected) for e in ['correct','wrong','withheld']]
    chart.categoryAxis.categoryNames=names;chart.categoryAxis.style='stacked';chart.categoryAxis.labels.fontName='Sans';chart.categoryAxis.labels.fontSize=6.7
    chart.valueAxis.valueMin=0;chart.valueAxis.labels.fontName='Sans';chart.valueAxis.labels.fontSize=7
    for i,color in enumerate([TEAL,AMBER,GRAY]):chart.bars[i].fillColor=color;chart.bars[i].strokeColor=None
    chart.groupSpacing=11;d.add(chart)
    for i,(name,color) in enumerate([('Correct',TEAL),('Wrong',AMBER),('Withheld',GRAY)]):
        d.add(Rect(60+i*130,18,9,9,fillColor=color,strokeColor=None));label(d,74+i*130,19,name,8)
    label(d,44,255,'Percent of questions' if cross else 'Number of questions',7.5)
    return d


def forest(company=False):
    d=base('Primary dependence sensitivity' if company else 'Primary MAS-minus-SAS contrasts',
        'Report50 versus company36 clusters; percentile95% intervals.' if company else 'Percentage-point differences; report-cluster95% and98.75% intervals.',290)
    x,y,w,h=205,52,245,174
    fx=lambda v:x+(v+80)/100*w
    for value in [-80,-60,-40,-20,0,20]:
        xx=fx(value);d.add(Line(xx,y,xx,y+h,strokeColor=GRAY,strokeWidth=.4));label(d,xx,y-15,str(value),7,anchor='middle')
    d.add(Line(fx(0),y,fx(0),y+h,strokeColor=INK,strokeWidth=1,strokeDashArray=[3,2]))
    for i,(metric,event) in enumerate([('case_success','correct'),('case_success','wrong'),('raw_execution_match','correct'),('raw_execution_match','wrong')]):
        e=E[metric+'/'+event];yy=y+h-20-i*43
        label(d,8,yy+2,('Reported' if metric=='case_success' else 'Raw')+' / '+event,8)
        label(d,8,yy-11,f"{100*e['delta_rate']:+.2f} pp",7,TEAL)
        lo,hi=e['bootstrap95'];broad=e['company_sensitivity']['bootstrap95'] if company else e['bonferroni4_bootstrap98_75']
        if company:
            d.add(Line(fx(100*lo),yy+4,fx(100*hi),yy+4,strokeColor=TEAL,strokeWidth=2.5))
            d.add(Line(fx(100*broad[0]),yy-4,fx(100*broad[1]),yy-4,strokeColor=AMBER,strokeWidth=2.5))
        else:
            d.add(Line(fx(100*broad[0]),yy,fx(100*broad[1]),yy,strokeColor=colors.HexColor('#B7D8DC'),strokeWidth=7))
            d.add(Line(fx(100*lo),yy,fx(100*hi),yy,strokeColor=TEAL,strokeWidth=2.5))
        d.add(Circle(fx(100*e['delta_rate']),yy,3,fillColor=NAVY,strokeColor=None))
    label(d,328,17,'MAS - SAS (percentage points)',8,anchor='middle')
    label(d,8,236,'Negative correct = fewer useful answers. Negative wrong = fewer errors.',7)
    if company:label(d,8,44,'Teal: reports. Amber: companies.\nIndependent-cluster assumptions.',7)
    return d


def funnel():
    d=base('Candidate production constrains the final gate','Primary reported metric, same160 questions.',285)
    fx,fy=axes(d,45,65,395,160,0,3,0,160,[],[0,40,80,120,160])
    label(d,8,238,'Cases',7.5)
    names=['Questions','Executable\ncandidate','Correct\ncandidate','Correct\ndelivered']
    for i,name in enumerate(names):label(d,fx(i),44,name,7,anchor='middle')
    for arm,color,dy in [('sas',TEAL,8),('mas',AMBER,8)]:
        m=S['tier16-'+arm+'-primary']['metrics']['case_success'];values=[160,m['valid_candidates'],m['correct_candidates'],m['correct']]
        points=[(fx(i),fy(v)) for i,v in enumerate(values)]
        d.add(PolyLine(points,strokeColor=color,strokeWidth=2,fillColor=None))
        for i,(xx,yy,v) in enumerate([(fx(i),fy(v),v) for i,v in enumerate(values)]):
            d.add(Circle(xx,yy,3,fillColor=color,strokeColor=None))
            if i or arm=='sas':label(d,xx,yy+dy,str(v),8,color,anchor='middle')
    label(d,50,13,'SAS: teal. MAS: amber. No independence assumption between stages.',7)
    return d


def concordance():
    d=base('Scoring-convention concordance among delivered answers','Cells are counts; reported and raw metrics are not interchangeable.',275)
    for offset,arm,denom in [(36,'sas',126),(272,'mas',8)]:
        m=S['tier16-'+arm+'-primary']['metric_concordance']
        label(d,offset+76,222,arm.upper()+f' / {denom} delivered',9,anchor='middle',font='Bold')
        for i,rep in enumerate(['reported_yes','reported_no']):
            for j,raw in enumerate(['raw_yes','raw_no']):
                value=m.get(rep+' / '+raw,0);alpha=value/44
                color=colors.Color(1-.75*alpha,1-.45*alpha,1-.34*alpha)
                x=offset+j*78;y=74+(1-i)*62
                d.add(Rect(x,y,76,60,fillColor=color,strokeColor=WHITE,strokeWidth=1))
                label(d,x+38,y+25,str(value),15,NAVY,anchor='middle',font='Bold')
        label(d,offset+37,63,'Raw yes',7,anchor='middle');label(d,offset+115,63,'Raw no',7,anchor='middle')
        label(d,offset+76,38,'Top row: reported yes',7,anchor='middle');label(d,offset+76,25,'Bottom row: reported no',7,anchor='middle')
    return d


def cost_ratios():
    d=base('Speed per case is not cost per useful answer','Primary MAS/SAS ratios; correct means reported-correct. Baseline SAS=1.',260)
    sas,mas=S['tier16-sas-primary'],S['tier16-mas-primary']
    metrics=[('Peak process RSS',mas['peak_rss_bytes']/sas['peak_rss_bytes']),
        ('Seconds per case',mas['inference_seconds']/sas['inference_seconds']),
        ('Seconds per correct',mas['inference_seconds']/5/(sas['inference_seconds']/78)),
        ('Prompt tokens',mas['prompt_tokens']/sas['prompt_tokens'])]
    fx=lambda v:170+v/3.6*275
    for i,(name,value) in enumerate(metrics):
        y=190-i*42;label(d,8,y+7,name,8)
        d.add(Rect(170,y,fx(value)-170,20,fillColor=TEAL,strokeColor=None));label(d,fx(value)+5,y+5,f'{value:.2f}x',8)
    d.add(Line(fx(1),42,fx(1),219,strokeColor=AMBER,strokeWidth=1.5,strokeDashArray=[3,2]))
    for x in [0,1,2,3]:label(d,fx(x),23,str(x),7,anchor='middle')
    label(d,307,9,'Ratio relative to SAS primary',7,anchor='middle')
    return d


def repair_cost():
    d=base('Repair cost without a no-loss delivery improvement','Percent increase versus the same-arm no-repair primary.',285)
    xs=[40,200,360]
    for x,metric,title in zip(xs,['prompt_tokens','generated_tokens','inference_seconds'],['Prompt tokens','Generated tokens','Inference time']):
        label(d,x+60,222,title,8,anchor='middle',font='Bold')
        for i,arm in enumerate(['sas','mas']):
            value=100*(S['tier16-'+arm+'-repair_ablation'][metric]/S['tier16-'+arm+'-primary'][metric]-1)
            hh=value/70*145;y=67
            d.add(Rect(x+15+i*50,y,34,hh,fillColor=TEAL if arm=='sas' else AMBER,strokeColor=None))
            label(d,x+32+i*50,y+hh+8,f'{value:.1f}%',7,anchor='middle');label(d,x+32+i*50,51,arm.upper(),7,anchor='middle')
        d.add(Line(x+3,67,x+122,67,strokeColor=GRAY))
    label(d,8,26,'Reported delivery changes: SAS +1 correct / +2 wrong; MAS 0 / 0.',8)
    label(d,8,11,'Raw delivery changes: SAS 0 correct / +3 wrong; MAS 0 / 0.',8)
    return d


def risk_coverage():
    d=base('Coverage and conditional risk: operating points','Reported metric. Six fixed recipes; no fitted confidence threshold.',300)
    fx,fy=axes(d,49,59,392,174,0,1,0,1,[0,.25,.5,.75,1],[0,.25,.5,.75,1],xlabel='Fraction of questions answered',ylabel='Wrong / delivered (conditional risk)')
    for arm,color in [('sas',TEAL),('mas',AMBER)]:
        for profile in ['direct_control','primary','repair_ablation']:
            if arm=='mas' and profile=='repair_ablation':continue
            m=S['tier16-'+arm+'-'+profile]['metrics']['case_success'];xx,yy=fx(m['coverage']),fy(1-m['precision_when_delivered'])
            d.add(Circle(xx,yy,4,fillColor=color,strokeColor=WHITE))
            text=arm.upper()+' '+('primary = repair' if arm=='mas' and profile=='primary' else profile.replace('_control','').replace('_ablation',''))
            if arm=='sas':
                offsets={'primary':(-118,-14),'repair_ablation':(9,10),'direct_control':(-80,12)};dx,dy=offsets[profile]
            else:dx,dy=9,(-6 if profile=='primary' else -12)
            label(d,xx+dx,yy+dy,text,7,color)
    label(d,8,13,'Always-withhold: coverage0, conditional risk undefined; not plotted as risk0.',7)
    return d


def utility():
    d=base('Utility depends on the chosen error penalty','Primary recipes only. Correct benefit1, wrong cost lambda, withhold0.',320)
    for index,metric in enumerate(['case_success','raw_execution_match']):
        x=43+index*235;y=90;w=187;h=155
        ymin=-.4 if index==0 else -1.2;ymax=.6
        fx,fy=axes(d,x,y,w,h,0,2.5,ymin,ymax,[0,1,2],([-.4,0,.4] if index==0 else [-1.2,-.6,0,.6]),xlabel='Wrong-answer penalty lambda')
        label(d,x+w/2,265,'Reported answer' if index==0 else 'Raw execution',9,anchor='middle',font='Bold')
        for arm,color in [('sas',TEAL),('mas',AMBER)]:
            m=S['tier16-'+arm+'-primary']['metrics'][metric]
            pts=[(fx(v/20),fy((m['correct']-v/20*m['wrong'])/160)) for v in range(51)]
            d.add(PolyLine(pts,strokeColor=color,strokeWidth=2,fillColor=None))
        d.add(Line(x,fy(0),x+w,fy(0),strokeColor=NAVY,strokeWidth=1,strokeDashArray=[3,2]))
        switch=73/45 if index==0 else 33/85
        d.add(Line(fx(switch),y,fx(switch),y+h,strokeColor=GRAY,strokeWidth=.7,strokeDashArray=[2,3]))
        label(d,x+5,40,f'Primary switch: {switch:.3f}',7)
    label(d,8,15,'SAS teal; MAS amber; dashed navy always-withhold. Illustrative preferences, not a tuned loss.',6.8)
    return d


def retrieval():
    d=base('Retrieved reference evidence does not ensure candidate production','Post-hoc strata. No gold used for inference or case selection.',280)
    chart=VerticalBarChart();chart.x=49;chart.y=75;chart.width=385;chart.height=150
    selected=[S['tier16-'+arm+'-primary']['retrieval_strata'] for arm in ['sas','mas']]
    keys=['all_annotated_evidence_retrieved','some_annotated_evidence_missing']
    chart.data=[tuple(100*s[k]['correct']/s[k]['n'] for k in keys) for s in selected]
    chart.categoryAxis.categoryNames=['All annotated evidence\n138 questions','Some missing\n22 questions'];chart.categoryAxis.labels.fontName='Sans';chart.categoryAxis.labels.fontSize=7
    chart.valueAxis.valueMin=0;chart.valueAxis.valueMax=60;chart.valueAxis.valueStep=20;chart.valueAxis.labels.fontName='Sans';chart.valueAxis.labels.fontSize=7
    chart.bars[0].fillColor=TEAL;chart.bars[1].fillColor=AMBER;chart.bars.strokeColor=None
    d.add(chart);label(d,49,237,'Correct delivered / stratum (%)',7.5)
    label(d,8,33,'SAS teal; MAS amber. MAS is invalid/insufficient on128/138 complete-retrieval cases.',7)
    label(d,8,18,'Catalog expressibility and semantic sufficiency are not certified by this annotation check.',7)
    return d


def memory():
    d=base('Model disk storage and resident process memory','Primary recipes. File size is a storage proxy, not an RSS decomposition.',280)
    models=DATA['protocol']['tiers']['16']
    values=[sum(v['size_bytes'] for v in models[a].values())/1e9 for a in ['sas','mas']]
    chart=VerticalBarChart();chart.x=50;chart.y=58;chart.width=375;chart.height=165
    chart.data=[tuple(values),tuple(S['tier16-'+a+'-primary']['peak_rss_bytes']/1e9 for a in ['sas','mas'])]
    chart.categoryAxis.categoryNames=['SAS14B Q4','MAS1.5B+3B+.5B F16'];chart.categoryAxis.labels.fontName='Sans';chart.categoryAxis.labels.fontSize=7
    chart.valueAxis.valueMin=0;chart.valueAxis.valueMax=12;chart.valueAxis.valueStep=3;chart.valueAxis.labels.fontName='Sans';chart.valueAxis.labels.fontSize=7
    chart.bars[0].fillColor=GRAY;chart.bars[1].fillColor=TEAL;chart.bars.strokeColor=None;d.add(chart)
    yy=58+11.5/12*165;d.add(Line(50,yy,425,yy,strokeColor=RED,strokeWidth=1,strokeDashArray=[3,2]))
    label(d,429,yy-2,'11.5',7,RED);label(d,50,236,'Decimal GB',7.5)
    label(d,8,23,'Gray: GGUF file bytes. Teal: sampled controller-plus-worker RSS. Red: cap.',7)
    return d


def graphics():
    return {'01_outcome_profiles':outcomes(),'02_primary_effects':forest(),'03_candidate_funnel':funnel(),
        '04_metric_concordance':concordance(),'05_cost_ratios':cost_ratios(),'06_repair_cost':repair_cost(),
        '07_risk_coverage':risk_coverage(),'08_utility_sensitivity':utility(),'09_cross_tier_descriptive':outcomes(cross=True),
        '10_retrieval_strata':retrieval(),'11_cluster_sensitivity':forest(company=True),'12_disk_vs_resident':memory()}


def markup(text):
    text=text.replace('\u2013','-').replace('\u2014','-').replace('\u2011','-')
    text=html.escape(text)
    text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:'<link href="'+html.escape(m[2],quote=True)+'" color="#007F86">'+m[1]+'</link>',text)
    text=re.sub(r'`([^`]+)`',r'<font name="Mono">\1</font>',text)
    text=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',text)
    return text


STYLES={
    'body':ParagraphStyle('Body',fontName='Serif',fontSize=9.4,leading=14,spaceAfter=8,textColor=INK,allowWidows=0,allowOrphans=0),
    'h2':ParagraphStyle('HeadingTwo',fontName='Bold',fontSize=14,leading=18,spaceBefore=16,spaceAfter=8,textColor=NAVY,keepWithNext=True),
    'h3':ParagraphStyle('HeadingThree',fontName='Bold',fontSize=10.4,leading=14,spaceBefore=12,spaceAfter=6,textColor=TEAL,keepWithNext=True),
    'cell':ParagraphStyle('Cell',fontName='Sans',fontSize=7.3,leading=10,spaceAfter=0,splitLongWords=True),
    'headcell':ParagraphStyle('HeaderCell',fontName='Bold',fontSize=7.2,leading=10,textColor=WHITE),
    'caption':ParagraphStyle('Caption',fontName='Sans',fontSize=8,leading=11,textColor=INK,spaceAfter=12),
    'code':ParagraphStyle('Code',fontName='Mono',fontSize=7.6,leading=10.8,backColor=PALE,borderPadding=7,spaceBefore=5,spaceAfter=12),
    'bullet':ParagraphStyle('Bullet',fontName='Serif',fontSize=9.2,leading=13.5,leftIndent=11,firstLineIndent=-8,spaceAfter=6),
}


def pdf_table(lines,width):
    cells=[[v.strip() for v in line.strip().strip('|').split('|')] for line in lines]
    cells=[v for v in cells if not all(re.fullmatch(r':?-+:?',c) for c in v)]
    lengths=[max(min(len(row[i]),38) for row in cells) for i in range(len(cells[0]))]
    weights=[max(9,math.sqrt(v)*3.5) for v in lengths]
    widths=[width*v/sum(weights) for v in weights]
    rows=[[Paragraph(markup(c),STYLES['headcell'] if i==0 else STYLES['cell']) for c in row] for i,row in enumerate(cells)]
    t=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE,PALE]),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,0),.6,NAVY),
        ('LINEBELOW',(0,1),(-1,-1),.25,GRAY)]))
    return [t,Spacer(1,12)]


def markdown_body(path,drawings,width):
    lines=path.read_text().splitlines();story=[];i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line or line=='---':i+=1;continue
        if line.startswith('# '):i+=1;continue
        if line.startswith('## '):
            text=line[3:]
            if text.startswith('Paired financial') or text.startswith('Integrated empirical'):i+=1;continue
            story.append(Paragraph(markup(text),STYLES['h2']));i+=1;continue
        if line.startswith('### '):story.append(Paragraph(markup(line[4:]),STYLES['h3']));i+=1;continue
        if line.startswith('```'):
            i+=1;block=[]
            while i<len(lines) and not lines[i].strip().startswith('```'):block.append(lines[i]);i+=1
            story.append(KeepTogether([Preformatted('\n'.join(block),STYLES['code'],maxLineLength=94)]));i+=1;continue
        if line.startswith('|'):
            block=[]
            while i<len(lines) and lines[i].strip().startswith('|'):block.append(lines[i]);i+=1
            story.extend(pdf_table(block,width));continue
        image=re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)',line)
        if image:
            name=Path(image[2]).stem
            drawing=drawings[name]
            pieces=[drawing,Paragraph(markup(image[1]),STYLES['caption'])]
            if story and isinstance(story[-1],Paragraph) and story[-1].style.name in ('HeadingTwo','HeadingThree'):
                pieces.insert(0,story.pop())
            story.append(KeepTogether(pieces));i+=1;continue
        if line.startswith('- '):story.append(Paragraph('• '+markup(line[2:]),STYLES['bullet']));i+=1;continue
        paragraph=[line];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(('#','|','```','![','- ')):
            paragraph.append(lines[i].strip());i+=1
        story.append(Paragraph(markup(' '.join(paragraph)),STYLES['body']))
    return story


class Report(BaseDocTemplate):
    def __init__(self,path,title,label_text):
        super().__init__(str(path),pagesize=A4,leftMargin=50,rightMargin=50,topMargin=57,bottomMargin=49,
            title=title,author='Project Agere',pageCompression=1)
        self.label_text=label_text;self.bookmarks=0
        self.addPageTemplates(PageTemplate('main',frames=[Frame(self.leftMargin,self.bottomMargin,self.width,self.height,
            leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=self.decorate))
    def beforeDocument(self):
        self.bookmarks=0
    def decorate(self,canvas,doc):
        canvas.saveState();w,h=A4
        if doc.page>1:
            canvas.setFont('Bold',8);canvas.setFillColor(NAVY);canvas.drawString(50,h-31,self.label_text)
            canvas.setStrokeColor(GRAY);canvas.setLineWidth(.5);canvas.line(50,h-39,w-50,h-39)
        canvas.setFont('Sans',7);canvas.setFillColor(INK);canvas.drawString(50,27,'Project Agere | 30 October 2026 | Resource-qualified evidence')
        canvas.drawRightString(w-50,27,str(doc.page));canvas.restoreState()
    def afterFlowable(self,flowable):
        if isinstance(flowable,Paragraph) and flowable.style.name=='HeadingTwo':
            self.bookmarks+=1;key='section-'+str(self.bookmarks)
            self.canv.bookmarkPage(key);self.canv.addOutlineEntry(flowable.getPlainText(),key,0,False)
            self.notify('TOCEntry',(0,flowable.getPlainText(),self.page,key))


def cover(doc,title,subtitle,advanced):
    title_style=ParagraphStyle('CoverTitle',fontName='Bold',fontSize=25,leading=31,textColor=NAVY,spaceAfter=19)
    sub=ParagraphStyle('CoverSub',fontName='Sans',fontSize=12,leading=18,textColor=TEAL,spaceAfter=20)
    body=ParagraphStyle('CoverBody',fontName='Sans',fontSize=10,leading=16,textColor=INK,spaceAfter=16)
    warning=ParagraphStyle('Warning',fontName='Bold',fontSize=10.5,leading=16,textColor=NAVY,spaceAfter=8)
    content=[Spacer(1,60),Paragraph('PROJECT AGERE / EVIDENCE SERIES',sub),Paragraph(title,title_style),Paragraph(subtitle,sub),
        Paragraph('30 October 2026<br/>Completed runs: 28-30 October 2026<br/>Offline, CPU-only financial numerical QA',body),Spacer(1,22)]
    cards=[('160','unique 16 GB questions'),('50','company-year reports'),('960','repeated 16 GB outputs')]
    if advanced:cards=[('3','separate evidence regimes'),('261','core comparative FinQA questions'),('8','conditional propositions')]
    rows=[[Paragraph(value,ParagraphStyle('CardValue',fontName='Bold',fontSize=23,leading=28,textColor=TEAL)) for value,label_text in cards],
        [Paragraph(label_text,ParagraphStyle('CardLabel',fontName='Sans',fontSize=8,leading=12,textColor=INK)) for value,label_text in cards]]
    t=Table(rows,colWidths=[doc.width/3]*3)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PALE),('LEFTPADDING',(0,0),(-1,-1),13),('TOPPADDING',(0,0),(-1,0),12),('BOTTOMPADDING',(0,1),(-1,1),14)]))
    content += [t,Spacer(1,29),Paragraph('ACCURACY AUDITED / RESOURCE FAILURES RETAINED',warning),
        Paragraph('The completed continuation is not an uninterrupted no-swap deployment pass. Both numerical metrics, withholding, failed attempts and source provenance remain visible.',body),
        Paragraph('Supplemental statistical tests are post hoc. Theory supplies conditional identities and bounds, not a proof of universal architecture superiority or algorithmic novelty.',body),PageBreak()]
    toc=TableOfContents();toc.levelStyles=[ParagraphStyle('TOC',fontName='Sans',fontSize=9,leading=14,leftIndent=0,firstLineIndent=0,spaceBefore=4,textColor=INK)]
    content += [Paragraph('Contents',ParagraphStyle('Contents',parent=STYLES['h2'])),Spacer(1,12),toc,PageBreak()]
    return content


def main():
    OUT.mkdir(parents=True,exist_ok=True);FIG.mkdir(parents=True,exist_ok=True);TEMP.mkdir(parents=True,exist_ok=True)
    drawings=graphics()
    for name,drawing in drawings.items():
        renderSVG.drawToFile(drawing,str(FIG/(name+'.svg')))
        temp=TEMP/(name+'.pdf');renderPDF.drawToFile(drawing,str(temp))
        subprocess.run(['pdftoppm','-singlefile','-scale-to','1800','-png',str(temp),str(FIG/name)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    specs=[('TIER_16_V2_STATISTICAL_EVALUATION_REPORT','16 GB statistical evaluation','Paired outcomes, coverage and resource-qualified evidence','AGERE / 16 GB STATISTICAL AUDIT',False),
        ('TIER_LE_16_ADVANCED_STATISTICAL_EVALUATION_REPORT','Local LLM deployments at or below 16 GB','Integrated statistical evaluation and conditional theoretical framework','AGERE / INTEGRATED <=16 GB EVIDENCE',True)]
    for stem,title,subtitle,header,advanced in specs:
        doc=Report(OUT/(stem+'.pdf'),title,header)
        story=cover(doc,title,subtitle,advanced)+markdown_body(ROOT/(stem+'.md'),drawings,doc.width)
        doc.multiBuild(story)
        print('Rendered',OUT/(stem+'.pdf'))
    print('Exported12 editable SVG and12 high-resolution PNG figures.')


if __name__=='__main__':main()
