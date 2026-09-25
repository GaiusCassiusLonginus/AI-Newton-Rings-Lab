from pathlib import Path
from zipfile import ZipFile
from PIL import Image
from io import BytesIO
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import json,hashlib,csv

BASE=Path(__file__).resolve().parent
OUT=BASE/'generated';OUT.mkdir(exist_ok=True)
PROVENANCE=json.loads((BASE.parent/'data'/'image_provenance.json').read_text(encoding='utf-8'))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
manifest=[]
if True:
    for number,members,labels in [(5,['image64.png','image67.png','image70.png'],['621 nm','520 nm','471 nm']), (6,['image73.jpeg','image76.jpeg','image79.jpeg','image82.jpeg'],['255:255:255','127:255:255','255:127:255','255:255:127'])]:
        fig=plt.figure(figsize=(6.8,4.4 if number==6 else 3.9),dpi=300)
        grid=fig.add_gridspec(len(members),2,width_ratios=[1.1,2.7],left=.15,right=.98,bottom=.13,top=.90,hspace=.27,wspace=.4)
        for row,(member,label) in enumerate(zip(members,labels)):
            raw=(BASE/(f'fig{number}_source_{row+1}'+Path(member).suffix)).read_bytes()
            source_name=f'fig{number}_source_{row+1}'+Path(member).suffix
            (OUT/source_name).write_bytes(raw)
            rgb=np.asarray(Image.open(BytesIO(raw)).convert('RGB'))
            h,w=rgb.shape[:2];side=min(h,w);x=(w-side)//2;y=(h-side)//2
            crop=rgb[y:y+side,x:x+side]
            # Square crop, no anisotropic resizing, warping, or intensity correction.
            ax=fig.add_subplot(grid[row,0]);ax.imshow(crop,aspect='equal');ax.axis('off')
            ax.text(-.10,.5,label,transform=ax.transAxes,ha='right',va='center',fontsize=9)
            plot=fig.add_subplot(grid[row,1]);xx=np.linspace(-1,1,side)
            if number==5:
                yy=crop[side//2].astype(float)@np.array([.2126,.7152,.0722])/255
                plot.plot(xx,yy,color=['#bd252b','#167240','#284bb5'][row],lw=.8)
            else:
                for channel,c in enumerate(['#bd252b','#167240','#284bb5']):plot.plot(xx,crop[side//2,:,channel]/255,color=c,lw=.7,label='RGB'[channel])
                if row==0:plot.legend(ncol=3,fontsize=8,loc='upper right',frameon=False)
            plot.set(xlim=(-1,1),ylim=(0,1.04),yticks=[0,.5,1]);plot.tick_params(labelsize=8,length=2)
            plot.grid(alpha=.17)
            if row<len(members)-1:plot.set_xticklabels([])
            else:plot.set_xlabel('Normalised horizontal position',fontsize=8)
            if row==0:ax.set_title('Recorded centre region',fontsize=8,pad=8);plot.set_title('Centre-line intensity' if number==5 else 'RGB centre-line profiles',fontsize=8,pad=8)
            manifest.append({'figure':number,'row':row+1,'source_member':'ppt/media/'+member,'source_file':source_name,'source_size':[w,h],'crop_xywh':[x,y,side,side],'sha256':hashlib.sha256(raw).hexdigest(),'operation':'centred square crop; equal x/y pixel scale; no anisotropic resampling','profile':'centre row of displayed crop; weighted greyscale / 255 (Figure 5) or RGB / 255 (Figure 6)'})
        fig.text(.365,.52,'Normalised intensity',rotation=90,ha='center',va='center',fontsize=8)
        fig.savefig(OUT/f'figure{number}.png',dpi=300);plt.close(fig)

with (BASE.parent/'data'/'questionnaire_counts.csv').open(encoding='utf-8-sig',newline='') as f:
    counts=np.array([[int(row[c]) for c in 'ABCDE'] for row in csv.DictReader(f)])
assert np.all(counts.sum(axis=1)==54)
# Each item has its own denominator; do not pool the eight questions.
titles=['Q1  Theory and\nexperimental skills','Q2  Comparison and\nguided inquiry','Q3  Records, judgement\nand teamwork','Q4  Match with\npersonal interests','Q5  Overall learning','Q6  Manual-first\ncomparison','Q7  Teacher guidance','Q8  Laboratory sequence']
fig,axes=plt.subplots(2,4,figsize=(7.8,5.5),dpi=300)
fig.subplots_adjust(left=.015,right=.985,bottom=.23,top=.86,wspace=.08,hspace=.64)
palette=['#235d83','#79acc8','#d5dce0','#cfa394','#9c4c43']
for row,ax in enumerate(axes.flat):
    values=counts[row];colours=list(palette)
    if row<3:colours[4]='#eee4b7'
    active=np.flatnonzero(values)
    wedges,_=ax.pie(values[active],colors=[colours[i] for i in active],startangle=90,counterclock=False,
        wedgeprops={'edgecolor':'white','linewidth':.7},radius=1)
    for col,wedge in zip(active,wedges):
        if row<3 and col==4:
            wedge.set_hatch('////');wedge.set_edgecolor('#665c35');wedge.set_linewidth(.3)
        if col in [0,1]:
            angle=np.deg2rad((wedge.theta1+wedge.theta2)/2)
            distance=.53 if col==0 else .68
            ax.text(distance*np.cos(angle),distance*np.sin(angle),
                f"{'ABCDE'[col]}: {values[col]}\n{values[col]/54*100:.1f}%",
                ha='center',va='center',fontsize=8.5,color='white' if col==0 else '#142932',linespacing=1.05)
    ax.set_title(titles[row],fontsize=9.5,pad=8)
    ax.text(.5,-.09,f'A+B: {values[:2].sum()}/54 ({values[:2].sum()/54*100:.1f}%)',
        transform=ax.transAxes,ha='center',va='top',fontsize=8.7)
    ax.set_aspect('equal')
handles=[Patch(facecolor=c,label='ABCDE'[i]) for i,c in enumerate(palette)]
handles.append(Patch(facecolor='#eee4b7',edgecolor='#665c35',hatch='////',label='E: unable to judge (Q1–3)'))
fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.5,.99),ncol=6,fontsize=9,frameon=False,handlelength=1.2,columnspacing=1.3)
fig.text(.025,.11,'Each pie represents 54 responses. A and B labels show counts and percentages.',fontsize=9)
fig.text(.025,.065,'Q1–3: attainment. Q4: interest match. Q5–8: satisfaction. Option meanings differ.',fontsize=9)
fig.text(.025,.02,'Small slices are unlabelled; Table 7 gives every count, including zero responses.',fontsize=9)
fig.savefig(OUT/'figure7.png',dpi=300);fig.savefig(OUT/'figure7.pdf');plt.close(fig)
with (OUT/'questionnaire_counts.csv').open('w',newline='',encoding='utf-8-sig') as f:
    writer=csv.writer(f);writer.writerow(['Item','A','B','C','D','E','N','A+B','A+B (%)'])
    for i,row in enumerate(counts,1):writer.writerow([i,*row,54,row[:2].sum(),round(row[:2].sum()/54*100,1)])
(OUT/'image_provenance.json').write_text(json.dumps({'archive':'1117ppt.pptx','archive_sha256':PROVENANCE['archive_sha256'],'panels':manifest},indent=2),encoding='utf-8')
print(OUT)

