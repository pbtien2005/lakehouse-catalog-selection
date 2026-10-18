"""Build the blind printable artifact; separate from the stdlib decision runtime."""
import json
from pathlib import Path
from xml.sax.saxutils import escape

import pypdfium2 as pdfium
from PIL import Image
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak,Paragraph,SimpleDocTemplate,Spacer,Table,TableStyle

ROOT=Path(__file__).resolve().parents[1]
registry=json.loads((ROOT.parent/'catalog-knowledge-base/form-v2-registry.json').read_text(encoding='utf-8'))
questions={q['id']:q for q in registry['questions']}
kb=json.loads((ROOT.parent/'catalog-knowledge-base/layer-1-data.json').read_text(encoding='utf-8-sig'))
cases=[c for split in ['calibration','holdout'] for c in json.loads((ROOT/'cases'/f'{split}.json').read_text())['cases']]
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialBold','C:/Windows/Fonts/arialbd.ttf'))
body=ParagraphStyle('BodyVI',fontName='Arial',fontSize=9,leading=12,spaceAfter=4)
heading=ParagraphStyle('HeadingVI',fontName='ArialBold',fontSize=14,leading=18,spaceAfter=9)
def para(value):return Paragraph(escape(str(value)),body)
flow=[]
for index,case in enumerate(cases):
    if index:flow.append(PageBreak())
    flow.extend([Paragraph(escape(case['id']+' - DỮ LIỆU TỔNG HỢP'),heading),para(case['description'])])
    for qid,value in case['form_answers']['answers'].items():
        q=questions[qid];labels={a['id']:a['label'] for a in q['answers']}
        if isinstance(value,list):text=', '.join(labels.get(x,x) for x in value)
        elif isinstance(value,dict):
            ranks={r['id']:r['label'] for r in q.get('ranks',[])}
            text=labels['none'] if value.get('none') else '; '.join(labels.get(x['feature'],x['feature'])+': '+ranks.get(x.get('rank'),'CHƯA CHỌN MỨC ƯU TIÊN') for x in value.get('selected',[]))
        else:text=labels.get(value,value)
        flow.append(para(qid+' - '+q['label']+': '+text))
    flow.extend([Spacer(1,3*mm),para('Phạm vi: đọc/load metadata; số bảng trong một catalog; concurrent append; branching catalog; atomic publication metadata. Không kèm kết quả hệ thống.')])
    rows=[[para('Ứng viên / scope'),para('Hạng'),para('Lý do / chưa đủ thông tin')]]
    for scope in sorted(kb['scopes'],key=lambda x:x['name']):rows.append([para(scope['name']+' / '+scope['id']),para('_____'),para('________________________')])
    table=Table(rows,colWidths=[80*mm,18*mm,70*mm])
    table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,'#bbbbbb'),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    flow.extend([table,Spacer(1,4*mm),para('Độ tự tin: ______   Thông tin cần hỏi thêm: ________________________'),para('Nhận xét: __________________________________________________')])
output=ROOT/'output/pdf/expert-score-sheet.pdf';output.parent.mkdir(parents=True,exist_ok=True)
SimpleDocTemplate(str(output),pagesize=A4,leftMargin=16*mm,rightMargin=16*mm,topMargin=14*mm,bottomMargin=14*mm,title='Phiếu chuyên gia - hồ sơ tổng hợp',author='Catalog Review MVP').build(flow)
reader=PdfReader(output)
assert len(reader.pages)==10
for page,case in zip(reader.pages,cases):assert case['id'] in page.extract_text()
qa=ROOT/'tmp/pdfs';qa.mkdir(parents=True,exist_ok=True)
doc=pdfium.PdfDocument(str(output));contact=Image.new('RGB',(1500,860),'#dddddd')
for index in range(len(doc)):
    im=doc[index].render(scale=0.65).to_pil();im.thumbnail((280,400));contact.paste(im,((index%5)*300+10,(index//5)*430+10))
    if index in [0,9]:doc[index].render(scale=1.5).to_pil().save(qa/f'expert-page-{index+1}.png')
contact.save(qa/'expert-pages.png')
print(json.dumps({'pdf':str(output),'pages':len(reader.pages),'one_profile_per_page':True,'system_results_included':False},ensure_ascii=False))
