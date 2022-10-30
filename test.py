
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
