from flask import Flask,render_template,request,url_for,redirect,flash
import pandas as pd
import sqlite3 as sql
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app=Flask(__name__)
app.secret_key='saurabh_mittal'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sign_up')
def sign_up():
    return render_template('sign_up.html')

def top_rated_movies():
    data=pd.read_csv('Dataset For Recommendation.csv')
    data=data[data['votes']>50000].sort_values(by='ratings',ascending=False).head(10)
    genres=data['genres'].values
    movie_title=data['original_title'].values
    overview=data['overview'].values
    ratings=data['ratings'].values
    vote_count=data['votes'].values
    return genres,movie_title,overview,ratings,vote_count

@app.route('/addrec', methods=['POST','GET'])
def addrec():
    if request.method=='POST':
        first_name=request.form['first']
        last_name=request.form['last']
        email=request.form['email']
        password=request.form['password']
        password=str(password)
        confirm_password=request.form['confirm_password']
        confirm_password=str(confirm_password)

        if password==confirm_password:

            print('ghgfvbhgfgfdcvhtffghgfghyfghg')

            con = sql.connect('database1.db')
            cur=con.cursor()
            cur.execute('INSERT INTO records1 (First_Name,Last_Name,Email,Password) VALUES (?,?,?,?)',(first_name,last_name,email,password))

            con.commit()
            con.close()
            genres,movie_title,overview,ratings,vote_count=top_rated_movies()
                    
            msg="You've Successfully Registered, Hope You Like Our Website"
            return render_template('Home.html',message=msg,genres=genres,movie_title=movie_title,overview=overview,ratings=ratings,votes=vote_count)

        else:

            flash("There is some error while registering, Please Check if the values entered are correct")
            return redirect(url_for('sign_up'))

@app.route('/list')
def list():
    con=sql.connect('database1.db')
    con.row_factory = sql.Row

    cur=con.cursor()
    cur.execute('SELECT * FROM records1')
    rows=cur.fetchall();
    con.close()
    return render_template('list.html',rows=rows)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/checkrec', methods=['POST','GET'])
def checkrec():
    if request.method=='POST':
        login_email=request.form['email']
        login_email=str(login_email)
        login_password=request.form['password']
        login_password=str(login_password)

        check_email=[]
        check_password=[]

        con=sql.connect('database1.db')
        con.row_factory = sql.Row

        cur=con.cursor()

        cursors = cur.execute("SELECT Email, Password from records1")
        for row in cursors:
            check_email.append(row[0])
            check_password.append(row[1])

        con.close()

        genres,movie_title,overview,ratings,vote_count=top_rated_movies()

        for i in range(len(check_email)):
            if check_email[i]==login_email:
                if check_password[i]==login_password:
                    msg="Welcome Back!!"
                    return render_template('Home.html',message=msg,genres=genres,movie_title=movie_title,overview=overview,ratings=ratings,votes=vote_count)

                else:
                    flash("There is some error while login, Please Check if the values entered are correct")
                    return redirect(url_for('login'))
            
        
        flash("There is some error while registering, Please Check if the values entered are correct")
        return redirect(url_for('login'))

def give_rec(title):
    title=title.lower()

    data=pd.read_csv('Dataset For Recommendation.csv')
    cv = TfidfVectorizer()
    count_matrix = cv.fit_transform(data['overview_new'])
    similarity = cosine_similarity(count_matrix)

    if title not in data['original_title'].unique():
        return 'Sorry! The movie you requested is not in our database. Please check the spelling or try another movie'
    else:
        main_index=data.loc[data['original_title']==title].index[0]
        info_main=data.iloc[main_index,:].values.tolist() 
        indexes=similarity[main_index].argsort().tolist()[-2:-12:-1]
        l=[]
        for i in range(len(indexes)):
            a=indexes[i]
            l.append(data['original_title'][a])

        info_main.extend(l)
        info_main=[str(x) for x in info_main]
        return info_main

@app.route('/content')
def content():
    return render_template('content.html')

@app.route('/recommendation_content', methods=['POST','GET'])
def recommendation_content():
    if request.method=='POST':
        movie=request.form['movie']
        movie=str(movie)
        rc=give_rec(movie)

        if type(rc)==type('string'):
            return render_template('content.html',outputs=rc) 
        else:
            m_str="---".join(rc)
            return render_template('content.html',outputs=m_str)

@app.route('/home')
def home():
    genres,movie_title,overview,ratings,vote_count=top_rated_movies()
    msg=''
    return render_template('Home.html',message=msg,genres=genres,movie_title=movie_title,overview=overview,ratings=ratings,votes=vote_count)

def get_action(category):
    data=pd.read_csv('Dataset For Recommendation.csv')
    action=data[data['genres'].str.contains(category,case=False)]
    action=action[action['votes']>50000].sort_values(by='ratings',ascending=False).head(10)

    movie_title=action['original_title'].values
    overview=action['overview'].values
    ratings=action['ratings'].values
    vote_count=action['votes'].values
    return movie_title,overview,ratings,vote_count

@app.route('/genre',methods=['POST','GET'])
def genre():
    if request.method=='POST':
        genre=request.form.get('please')
        genre=str(genre)
        print(genre)
        movie_title,overview,ratings,vote_count=get_action(genre)
        return render_template('genre.html',movie_title=movie_title,overview=overview,ratings=ratings,votes=vote_count,category=genre)
    else:    
        genre='Action'
        movie_title,overview,ratings,vote_count=get_action('Action')
        return render_template('genre.html',movie_title=movie_title,overview=overview,ratings=ratings,votes=vote_count,category=genre)


if __name__=='__main__':
    app.run(debug=True)