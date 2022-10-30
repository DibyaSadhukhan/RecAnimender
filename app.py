#importing required packages
import flask
import random
import json
import details
import Postgres
import datetime
from Admin.admin import admin
from Recommend.recommend import recommend
from Anime.anime import anime
from Models import SearchForm

app = flask.Flask(__name__, template_folder="Templates")
app.config['SECRET_KEY']='\xd9\x06\xb5Uu\xb7 \xfb\x03\xcc$\xf1'+str(datetime.date.today())
app.register_blueprint(admin,url_prefix='/admin/')
app.register_blueprint(recommend,url_prefix='/recommend/')
app.register_blueprint(anime,url_prefix='/anime/')

@app.route('/_autocomplete', methods=['GET'])
def autocomplete():
        return flask.Response(json.dumps(details.Form_titles()), mimetype='application/json')
        #return flask.Response(json.dumps(['111','2222']), mimetype='application/json')
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
                random.shuffle(Carosel)
                return flask.render_template('Home.html',form=form,carosel=Carosel,cards=Cards\
                ,fst_slide=random_banner[counter],carosel_length=len(Carosel),genres=details.available_genre(),email=email)      
        else:
                #print(datetime.datetime.now())
                return flask.redirect(flask.url_for("home"))   
if __name__ == '__main__':
    app.run(debug='True')