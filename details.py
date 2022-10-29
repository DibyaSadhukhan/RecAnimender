import urllib.request
def Carosel_image():
  line=urllib.request.urlopen('https://raw.githubusercontent.com/DibyaSadhukhan/Anime_recommender_data/main/Data/random_images.txt').read()        
  return [e.split(',') for e in str(line,'utf-8').split('|')]
def Form_titles():
    line=urllib.request.urlopen('https://raw.githubusercontent.com/DibyaSadhukhan/Anime_recommender_data/main/Data/titles.txt').read()        
    return str(line,'utf-8').split('||')
def available_genre():
    line=urllib.request.urlopen('https://raw.githubusercontent.com/DibyaSadhukhan/Anime_recommender_data/main/Data/genre.txt').read()        
    return str(line,'utf-8').split('||')
def postgres_auth():
    f = open("random_texts.txt", "r")
    a=f.read()
    return a.split(',')
def get_recommendations(uid):
    line=urllib.request.urlopen('https://raw.githubusercontent.com/DibyaSadhukhan/Anime_recommender_data/main/Data/recommendations.txt').read()
    rec=[e.split(',') for e in str(line,'utf-8').split('\n')]
    result = [element for element in rec if element[0] == str(uid)]
    return result
#postgres_auth()
    #return str(line,'utf-8').split('||')
#gspread_auth()