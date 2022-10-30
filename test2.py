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