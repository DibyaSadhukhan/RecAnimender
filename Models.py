from wtforms import Form,StringField
class SearchForm(Form):
        autocomp = StringField('Anime Name', id='anime_autocomplete',render_kw={"placeholder": "What's The Last Anime You've Seen?"})
