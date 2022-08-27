from sqlite3 import SQLITE_OK
from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc,select,update
from urllib.request import Request,urlopen
from bs4 import BeautifulSoup
import re
#Config
app = Flask(__name__)
app.config['SECRET_KEY'] = 'abc123'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comics.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pvaarthoxuwbdz:693e223971abf0331755f2499892b898bc38f350e9a10935da1c46642f408f45@ec2-54-225-234-165.compute-1.amazonaws.com:5432/de9odpiav52fde'
#no # app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mowyjvwjbkafsu:b1e3a478e96a4d66d637317084b249a89c4f1793be43d6ac87c70c66e1bf02c7@ec2-54-225-234-165.compute-1.amazonaws.com:5432/dtbrh26fsnmtp'
db = SQLAlchemy(app)

#Create Database
class comics(db.Model):
    comic_id = db.Column(db.Integer(),primary_key=True)
    comic_name = db.Column(db.String(100),nullable=False)
    comic_chapter_completed = db.Column(db.Integer(),nullable=False)
    comic_completed = db.Column(db.String(5),nullable=False)
    comic_from = db.Column(db.String(10))
    comic_url = db.Column(db.String(100))
    comic_reading = db.Column(db.String(5),nullable=False)
    comic_like = db.Column(db.Integer(),nullable=False)
    
    def __init__(self,comic_name,comic_chapter_completed,
                 comic_completed,comic_from,comic_url,comic_reading,
                 comic_like):
        self.comic_name = comic_name
        self.comic_chapter_completed = comic_chapter_completed
        self.comic_completed = comic_completed
        self.comic_from = comic_from
        self.comic_url = comic_url
        self.comic_reading = comic_reading
        self.comic_like = comic_like
    
    def __repr__(self):
        return f"comic({self.comic_id},{self.comic_name},{self.comic_chapter_completed})"

class comicsLatestChapter(db.Model):
    comic_id = db.Column(db.Integer(),primary_key=True,nullable=False)
    comic_latest_chapter = db.Column(db.Float(),default=0)
    def __init__(self,comic_id,comic_latest_chapter):
        self.comic_id = comic_id
        self.comic_latest_chapter = comic_latest_chapter
    def __repr__(self):
        return f"comicLatestChapter({self.comic_id},{self.comic_latest_chapter})"


@app.route('/',methods=['GET','POST'])
def home():
    query = select(comics).order_by(desc(comics.comic_like)).order_by(comics.comic_id)
    comicsData = db.session.execute(query)
    query = select(comicsLatestChapter)
    chapterData = db.session.execute(query)
    chapters = {}
    for x in chapterData.scalars().all():
        chapters[x.comic_id] = x.comic_latest_chapter
    if request.method == 'POST':
        comic = request.form['comic']
        comicsData = comics.query.filter(comics.comic_name.like(f"%{comic}%")).order_by(desc(comics.comic_like)).order_by(comics.comic_id).all()
        return render_template('search.html',comicsData=comicsData,chapterData=chapters)
    return render_template('search.html',comicsData=comicsData.scalars().all(),chapterData=chapters)

@app.route('/refresh/<comicid>')
def refreshChapter(comicid):
    comic = comics.query.where(comics.comic_id == comicid).all()[0]
    url = comic.comic_url
    comicLatestChap = comicsLatestChapter.query.filter(comicsLatestChapter.comic_id == comicid).all()
    if comicLatestChap == []:
        comicExist = 0
    else:
        comicExist = 1
    try:
        req = Request(url,headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        a = BeautifulSoup(webpage,'lxml')
        tags = a.find_all('li',class_="wp-manga-chapter")
        txt = tags[0].a.text
        x = re.sub('Chapter','',txt)
        x = float(re.sub('- END','',x))
        if comicExist:
            upd = update(comicsLatestChapter)
            val = upd.values({'comic_latest_chapter':x})
            cnd = val.where(comicsLatestChapter.comic_id == comicid)
            db.session.execute(cnd)
            db.session.commit()
            return redirect('/')
        else:
            comic = comicsLatestChapter(comicid,x)
            db.session.add(comic)
            db.session.commit()
            return redirect('/')
    except:
        return redirect('/')
    
    

@app.route('/add',methods=['GET','POST'])
def addPage():
    if request.method == 'POST':
        comicName = request.form['comic_name'].lower()
        comicChapterCompleted = int(request.form['chapter_chap_completed'])
        comicCompleted = request.form['comic_completed']
        comicFrom = request.form['comic_from']
        comicUrl = request.form['comic_url']
        comicReading = request.form['comic_reading']
        comicLike = 1 if request.form['comic_like'] == 'yes' else 0
        query = comics(comicName,comicChapterCompleted,comicCompleted,comicFrom,comicUrl,comicReading,comicLike)
        db.session.add(query)
        db.session.commit()
        return redirect('/')
    return render_template('add.html')

@app.route('/updatereading/<comicid>')
def updatereading(comicid):
    comic = comics.query.where(comics.comic_id == comicid).all()[0]
    if comic.comic_reading == 'yes':
        updateReadingText = 'no'
    else:
        updateReadingText = 'yes'
    upd = update(comics)
    val = upd.values({'comic_reading':updateReadingText})
    cnd = val.where(comics.comic_id == comicid)
    db.session.execute(cnd)
    db.session.commit()
    return redirect('/')

@app.route('/updatelike/<comicid>')
def updatelike(comicid):
    comic = comics.query.where(comics.comic_id == comicid).all()[0]
    if comic.comic_like:
        updateLike = 0
    else:
        updateLike = 1
    upd = update(comics)
    val = upd.values({"comic_like":updateLike})
    cnd = val.where(comics.comic_id == comicid)
    db.session.execute(cnd)
    db.session.commit()
    return redirect('/')

@app.route('/update/<comicid>')
def updatecomic(comicid):
    query = select(comics).where(comics.comic_id == comicid)
    data = db.session.execute(query)
    return render_template('update.html',data = data.scalars().all()[0])

@app.route('/doupdate',methods=['GET','POST'])
def doupdate():
    if request.method == 'POST':
        # print('in')
        comicId = int(request.form['comic_id'])
        comicName = request.form['comic_name'].lower()
        comicChapterCompleted = int(request.form['chapter_chap_completed'])
        comicCompleted = request.form['comic_completed']
        comicFrom = request.form['comic_from']
        comicUrl = request.form['comic_url']
        comicReading = request.form['comic_reading']
        upd = update(comics)
        val = upd.values(
            {
            "comic_name":comicName, 
            "comic_chapter_completed":comicChapterCompleted,
            "comic_completed":comicCompleted,
            "comic_from":comicFrom,
            "comic_url":comicUrl,
            "comic_reading":comicReading
            }
        )
        cnd = val.where(comics.comic_id == comicId)
        db.session.execute(cnd)
        db.session.commit()
    return redirect('/')

if __name__ == "__main__":
    app.debug = True
    app.run()
