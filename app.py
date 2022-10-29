#importing required packages
import flask
from wtforms import Form,StringField
import random
import json
import details
import Postgres
import datetime
app = flask.Flask(__name__, template_folder="Templates")
app.config['SECRET_KEY']='\xd9\x06\xb5Uu\xb7 \xfb\x03\xcc$\xf1'+str(datetime.date.today())
#class for signup form
class SearchForm(Form):
        autocomp = StringField('Anime Name', id='anime_autocomplete',render_kw={"placeholder": "What's The Last Anime You've Seen?"})
        
postgres=details.postgres_auth()
#connecting the login sheet to backend
#auth=details.gspread_auth()
#gc = gspread.service_account_from_dict(auth)
@app.route('/_autocomplete', methods=['GET'])
def autocomplete():
        return flask.Response(json.dumps(details.Form_titles()), mimetype='application/json')
        #return flask.Response(json.dumps(['111','2222']), mimetype='application/json')
@app.route('/administration', methods=['GET','POST'])
def admin():
        if 'id' in flask.session:
                flask.session.pop('id',None)
        
        if flask.request.form:
                if flask.request.form.get('email').lower()=='travellerinterworld@gmail.com' and flask.request.form.get('pwd')=='recanimender2022':
                        flask.session['id']='admin'
                        return flask.redirect(flask.url_for("db"))
                else:
                        return flask.render_template('admin_login.html')        
        else:
                return flask.render_template('admin_login.html')
@app.route('/DB_admin', methods=['GET','POST'])
def db():
        if 'id' in flask.session:
                if flask.session['id']!='admin':
                       return flask.redirect(flask.url_for("admin")) 
                #print(flask.request.form)
                message=""
                if flask.request.form:
                        try:
                                postgres_find_query="""SELECT a.uid from anime.anime_list a 
                                                        where a.title like '{0}';""".format(flask.request.form.get('Anime_name'))
                                res,err=Postgres.postgres_connect(postgres_find_query,commit=0)
                                if len(err)==0:
                                        a=[e[0] for e in res]
                                        if len(a) >0:
                                                postgres_find_query="""SELECT * from anime.anime_banner a 
                                                        where a.uid like '{0}';""".format(a[0])
                                                res,err=Postgres.postgres_connect(postgres_find_query,commit=0)
                                                present_link=[e for e in res]
                                                if len(present_link)==0:
                                                        postgres_insert_query = """ INSERT INTO anime.anime_banner (uid,ori_link,drive_link)
                                                                                        VALUES ('{0}','{1}','{2}')""".format(a[0],flask.request.form.get('ori_link'),flask.request.form.get('img_id')) 
                                                        a=Postgres.postgres_connect(postgres_insert_query,commit=1)
                                                        if a:
                                                                message="Succesfully Inserted"
                                                        else:
                                                                message="Error please Try Again"
                                                else:
                                                        postgres_insert_query="""UPDATE anime.anime_banner
                                                                                        SET ori_link = '{0},{1}',
                                                                                        drive_link = '{2},{3}'
                                                                                        WHERE uid::varchar(255) like '{4}';""".format(present_link[0][1],flask.request.form.get('ori_link'),present_link[0][2],flask.request.form.get('img_id'),a[0])
                                                        a=Postgres.postgres_connect(postgres_insert_query,commit=1)
                                                        if a:
                                                                message="Succesfully Inserted"
                                                        else:
                                                                message="Error please Try Again"
                        except (Exception) as error:
                                print(error)
                return flask.render_template('admin_crud_add_banner.html',title=details.Form_titles(),message=message)
        else:
                return flask.redirect(flask.url_for("admin"))
@app.route('/', methods =['POST', 'GET'])
def home():
        #print(datetime.datetime.now())
        Client_ip=flask.request.environ.get('HTTP_X_FORWARDED_FOR', flask.request.environ['REMOTE_ADDR'])
        form = SearchForm(flask.request.form)
        email=""
        if 'id' not in flask.session:
                flask.session['id']=Client_ip
        if 'email' in flask.session:
                email=flask.session['email']
        postgres_find_query="""
                                with top_anime as ( 
                                        SELECT * from (SELECT *, 
                                        (.35*((a.members::INTEGER -MIN(a.members::INTEGER) over ()):: DOUBLE PRECISION/ (MAX(a.members::INTEGER) over () -MIN(a.members::INTEGER) over ()))+
                                        .35*((a.user_fav::INTEGER -MIN(a.user_fav::INTEGER) over ()):: DOUBLE PRECISION/ (MAX(a.user_fav::INTEGER) over () -MIN(a.user_fav::INTEGER) over ()))+
                                        .30*((a.score::DOUBLE PRECISION -MIN(a.score::DOUBLE PRECISION) over ())/ (MAX(a.score::DOUBLE PRECISION) over () -MIN(a.score::DOUBLE PRECISION) over ()))) as popularity
                                        from anime.anime_list a) s1 WHERE s1.popularity>.40)
                                SELECT * from (SELECT p1.uid,p1.title,p1.synopsis,p1.episodes,p1.members,p1.score,p1.user_fav,p1.start_date,p1.img_url,b.ori_link,b.drive_link, p1.popularity FROM top_anime p1 left join anime.anime_banner b on b.uid=p1.uid
                                order by random()
                                LIMIT 10) c 
                                order by c.drive_link is NOT NULL DESC
                                """
        res,err=Postgres.postgres_connect(postgres_find_query,commit=0)
        Carosel=[]
        if len(err)==0:
                anime_details=[list(e) for e in res]
                Carosel=anime_details[:4]
                Cards=anime_details[4:]
                del anime_details
                random_banner=details.Carosel_image()
                random.shuffle(random_banner)
                counter=0
                for item in Carosel:
                        if item[-2]==None:
                                item[-3]=random_banner[counter][0]
                                item[-2]=random_banner[counter][1]
                                counter+=1
                        else:
                                if len(item[-2].split(','))>1:
                                        temp=random.randint(0,(len(item[-2].split(','))-1))
                                        item[-2]=item[-2].split(',')[temp]
                                        item[-3]=item[-3].split(',')[temp]  
                print(datetime.datetime.now())
                return flask.render_template('Home.html',form=form,carosel=Carosel,cards=Cards\
                ,fst_slide=random_banner[counter],carosel_length=len(Carosel),genres=details.available_genre(),email=email)      
        else:
                #print(datetime.datetime.now())
                return flask.redirect(flask.url_for("home"))   
@app.route('/anime/<id>', methods =['POST', 'GET'])
def anime(id):
        form = SearchForm(flask.request.form)
        Client_ip=flask.request.environ.get('HTTP_X_FORWARDED_FOR', flask.request.environ['REMOTE_ADDR'])
        email=""
        if 'id' in flask.session:
                if 'anime_list_start' in flask.session:
                        start=flask.session['anime_list_start']
                else:
                        start=0    
        else:
                flask.session['id']=Client_ip
                start=0
        if 'email' in flask.session:
                email=flask.session['email']
        postgres_find_query="""SELECT * from anime.anime_list a
                                WHERE a.uid::INTEGER = {0}
                                LIMIT 1
                """.format(id)
        res,err=Postgres.postgres_connect(postgres_find_query,commit=0)
        if len(err)==0:
                row=[list(e) for e in res]
        if len(row)==0:
                return flask.redirect(flask.url_for("home"))
        else:
                return flask.render_template('anime.html',form=form,data=row[0],start=start,email=email)
                
@app.route('/anime_list',methods =['POST', 'GET'])
@app.route('/anime_list/<start>',methods =['POST', 'GET'])
def anime_list(start=-1):
        form = SearchForm(flask.request.form)
        Client_ip=flask.request.environ.get('HTTP_X_FORWARDED_FOR', flask.request.environ['REMOTE_ADDR'])
        if 'id' not in flask.session:
                flask.session['id']=Client_ip
                flask.session['anime_list_start']=start
        elif 'anime_list_start' in flask.session and start==-1:
                start=flask.session['anime_list_start']
        try:
                start=int(start)
        except:
                start=-1
        if start == -1 or start==0: 
                start=1
        email=""
        if 'email' in flask.session:
                email=flask.session['email']
        postgres_find_query="""SELECT * from anime.anime_list a 
                                ORDER BY a.user_fav::INTEGER DESC
                                LIMIT 10
                                OFFSET {0}
                        """.format((start-1))
        #print(postgres_find_query)
        res,err=Postgres.postgres_connect(postgres_find_query,commit=0)
        if len(err)==0:
                Anime_details = [list(e) for e in res]
        else:
                return flask.redirect(flask.url_for("home"))   
        #print(Anime_details[0])
        flask.session['anime_list_start']=start
        return flask.render_template('recommend.html',form=form,anime_list=1,nextpage=int(start)+10,data=Anime_details,email=email)

@app.route('/recommend',methods=['POST','GET'])
@app.route('/recommend/uid=<uid>&start=<start>&title=<title>',methods=['POST','GET'])
def recommendation(uid=-1,start=0,title=""):
        form = SearchForm(flask.request.form)
        Client_ip=flask.request.environ.get('HTTP_X_FORWARDED_FOR', flask.request.environ['REMOTE_ADDR'])
        if form.autocomp.data:
                title=form.autocomp.data
        try:
                start=int(start)
        except:
                start=0
        if 'id' not in flask.session:
                flask.session['id']=Client_ip  
        if uid!=-1 and title=="" and start!=0:
                return flask.redirect(flask.url_for("anime_list"))     
        email=""
        if flask.request.form:
                if flask.request.form.get('email'):
                        email=flask.request.form.get('email')
                        flask.session['email']=email  
        if 'email' in flask.session:
                email=flask.session['email']

        if uid!=-1:
                rec_list=details.get_recommendations(uid)
        #print(uid)
        if uid==-1 and form.autocomp.data:
                postgres_find_query="""SELECT a.uid from anime.anime_list a 
                                                        where a.title like '{0}' 
                                                        LIMIT 1;""".format(form.autocomp.data)
                res,err=Postgres.postgres_connect(postgres_find_query,commit=0)
                if len(err)==0:
                        row=[list(e) for e in res]
                        rec_list=details.get_recommendations(row[0][0])
                        uid=row[0][0]
                        #print(uid)
                        #print(rec_list)
                else:
                        return flask.redirect(flask.url_for("home"))
        if start==0:
                start=1
        if start+10>len(rec_list[0]):
                rec_list=rec_list[0][-10:]
                last=1
        else: 
                rec_list=rec_list[0][start:start+10]
                last=0
                postgres_find_query="""SELECT * from anime.anime_list a 
                                                where a.uid in {0};""".format(tuple(rec_list))
                #print(postgres_find_query)
                res,err=Postgres.postgres_connect(postgres_find_query,commit=0)
                if len(err)==0:
                        row=[list(e) for e in res]
                        if start==1 and len(email)>0:
                                postgres_insert_query = """ INSERT INTO users.recommendations (email,client_ip,uid,rec_date)
                                                                                                VALUES ('{0}','{1}','{2}',CURRENT_TIMESTAMP)""".format(email,Client_ip,row[0][0]) 
                                a=Postgres.postgres_connect(postgres_insert_query,commit=1)
                                        
                        #print(row)
                        return flask.render_template('recommend.html',form=form,anime_list=0,nextpage=start+10,data=row,\
                                uid=uid,search=title,last=last,email=email)
                else:
                        return flask.redirect(flask.url_for("home"))
@app.route('/recommend/search',methods=['POST','GET'])
def recommend_search():
        form = SearchForm(flask.request.form)
        Client_ip=flask.request.environ.get('HTTP_X_FORWARDED_FOR', flask.request.environ['REMOTE_ADDR'])
        email=""
        if 'id' not in flask.session:
                flask.session['id']=Client_ip
        if 'email' in flask.session:
                email=flask.session['email']
        if flask.request.form:
                if flask.request.form.get('email'):
                        if 'email' not in flask.session:
                                flask.session['email']=flask.request.form.get('email')
                                email=flask.request.form.get('email')
                #print(email)
                #print(flask.request.form)
                postgres_find_query=""
                if flask.request.form.get('special_request'):
                        postgres_find_query="""with tab1 as(
                                                SELECT *,
                                                (.05*((a.members::INTEGER -MIN(a.members::INTEGER) over ()):: DOUBLE PRECISION/ (MAX(a.members::INTEGER) over () -MIN(a.members::INTEGER) over ()))+
                                                .05*((a.user_fav::INTEGER -MIN(a.user_fav::INTEGER) over ()):: DOUBLE PRECISION/ (MAX(a.user_fav::INTEGER) over () -MIN(a.user_fav::INTEGER) over ()))+
                                                .05*((a.score::DOUBLE PRECISION -MIN(a.score::DOUBLE PRECISION) over ())/ (MAX(a.score::DOUBLE PRECISION) over () -MIN(a.score::DOUBLE PRECISION) over ()))+
                                                .30*a.sim_synopsis+.55*a.sim_genre 
                                                ) as popularity
                                                from (select *, similarity(b.genre, '{0}') as sim_genre,similarity(lower(b.synopsis), 'friends') as sim_synopsis            
                                                from anime.anime_list b) a
                                                ORDER by popularity desc
                                                LIMIT 50
                                                )
                                                SELECT * from tab1 t
                                        """.format(','.join(flask.request.form.getlist('genre')),flask.request.form.get('special_request'))
                else:
                        postgres_find_query="""with tab1 as(
                                                SELECT *,
                                                (.13*((a.members::INTEGER -MIN(a.members::INTEGER) over ()):: DOUBLE PRECISION/ (MAX(a.members::INTEGER) over () -MIN(a.members::INTEGER) over ()))+
                                                .15*((a.user_fav::INTEGER -MIN(a.user_fav::INTEGER) over ()):: DOUBLE PRECISION/ (MAX(a.user_fav::INTEGER) over () -MIN(a.user_fav::INTEGER) over ()))+
                                                .12*((a.score::DOUBLE PRECISION -MIN(a.score::DOUBLE PRECISION) over ())/ (MAX(a.score::DOUBLE PRECISION) over () -MIN(a.score::DOUBLE PRECISION) over ()))+
                                                .60*a.sim_genre 
                                                ) as popularity
                                                from (select *, similarity(b.genre, '{0}') as sim_genre , 0 as sim_synopsis           
                                                from anime.anime_list b) a
                                                ORDER by popularity desc
                                                LIMIT 50
                                                )
                                                SELECT * from tab1 t\n
                                        """.format(','.join(flask.request.form.getlist('genre')))

                if flask.request.form.get('Exclude_movies'): 
                        if  flask.request.form.get('complete')=='False':
                                postgres_find_query=postgres_find_query+"WHERE t.episodes::INTEGER>1 and t.end_date IS NOT NULL \n"
                        else:
                                postgres_find_query=postgres_find_query+"WHERE t.episodes::INTEGER>1 \n"
                else:
                        postgres_find_query=postgres_find_query+"WHERE t.episodes::INTEGER>0 \n"
                if flask.request.form.get('popular'):
                        postgres_find_query=postgres_find_query+"order by t.user_fav \n"
                postgres_find_query=postgres_find_query+"LIMIT 10;"
                #print(postgres_find_query)
                res,err=Postgres.postgres_connect(postgres_find_query,commit=0)
                if len(err)==0:
                        row=[list(e) for e in res]
                        #row=[]
                        if len(row)>1:
                                if len(email)>0:
                                        postgres_insert_query = """ INSERT INTO users.recommendations (email,client_ip,uid,rec_date)
                                                                                                VALUES ('{0}','{1}','{2}',CURRENT_TIMESTAMP)""".format(email,Client_ip,row[0][0]) 
                                        a=Postgres.postgres_connect(postgres_insert_query,commit=1)
                                return flask.render_template('recommend.html',form=form,anime_list=0,nextpage=11,data=row,\
                                uid=row[0][0],search="Your Search",last=0,email=email)
                        else:
                                return flask.render_template('recommend.html',form=form,anime_list=0,nextpage=11,data=[],\
                                uid=0,search="Your Search",last=0,error=1)
                else:
                        return flask.redirect(flask.url_for("home"))
        return flask.redirect(flask.url_for("home"))
if __name__ == '__main__':
    app.run(debug = True)