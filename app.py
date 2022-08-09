from sqlite3 import SQLITE_OK
from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc,select,update

#Config
app = Flask(__name__)
app.config['SECRET_KEY'] = 'abc123'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comics.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pvaarthoxuwbdz:693e223971abf0331755f2499892b898bc38f350e9a10935da1c46642f408f45@ec2-54-225-234-165.compute-1.amazonaws.com:5432/de9odpiav52fde'
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

@app.route('/',methods=['GET','POST'])
def home():
    query = select(comics).order_by(desc(comics.comic_like)).order_by(comics.comic_id)
    comicsData = db.session.execute(query)
    if request.method == 'POST':
        comic = request.form['comic']
        comicsData = comics.query.filter(comics.comic_name.like(f"%{comic}%")).order_by(desc(comics.comic_like)).all()
        return render_template('search.html',comicsData=comicsData)
    return render_template('search.html',comicsData=comicsData.scalars().all())

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
