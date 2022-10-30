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
