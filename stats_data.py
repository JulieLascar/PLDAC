import mysql.connector
import matplotlib.pyplot as plt
import pickle
from wordcloud import WordCloud
import random
import numpy as np
from PIL import Image

# creation de la liste des users presents dans les communautes de 1 ou 2 noeuds
small_community = pickle.load(open("1-2_communities_nodes.p", "rb"))
small_community_ = '('
for i in range(len(small_community)-1):
    small_community_ += str(small_community[i]) + ', '
small_community_ += str(small_community[-1]) + ')'

connection_params = {
    'host' : 'localhost',
    'user' : 'root',
    #'password' : 'K@wa11',
    'password' : 'MatRap2212',
    'database' : 'pldac'
}

r1 = 'select count(*) from users_0401_0415'
r2 = 'select count(*) from tweets_0401_0415'
r3 = 'select count(*) from tweets_0401_0415 where in_reply_to_user_id is not null and retweeted_user_id is null and quoted_user_id is null'
r4 = 'select count(*) from tweets_0401_0415 where in_reply_to_user_id is null and retweeted_user_id is not null and quoted_user_id is null'
r5 = 'select count(*) from tweets_0401_0415 where in_reply_to_user_id is null and retweeted_user_id is null and quoted_user_id is not null'
r6 = 'select count(*) from tweets_0401_0415 where in_reply_to_user_id is null and retweeted_user_id is null and quoted_user_id is null'
r7 = 'select count(*) from tweets_0401_0415 where in_reply_to_user_id is not null and retweeted_user_id is not null and quoted_user_id is not null'
r8 = 'select count(*) from tweets_0401_0415 where in_reply_to_user_id is not null and retweeted_user_id is not null and quoted_user_id is null'
r9 = 'select count(*) from tweets_0401_0415 where in_reply_to_user_id is not null and retweeted_user_id is null and quoted_user_id is not null'
r10 = 'select count(*) from tweets_0401_0415 where in_reply_to_user_id is null and retweeted_user_id is not null and quoted_user_id is not null'
r11 = 'select count(distinct hash_id) from hashs_0401_0415'
r12 = 'select max(h.hash), count(h.hash_id) from hashs_0401_0415 as h natural join tweet_hash_0401_0415 as t group by h.hash_id order by count(h.hash_id) desc'
r13 = 'select lang, count(lang) from tweets_0401_0415 group by lang order by count(lang) desc'
r14 = 'select hour(created_at), count(hour(created_at)) from tweets_0401_0415 where day(created_at) = "04" group by hour(created_at)'
r15 = 'select date_format(created_at, "%m/%d"), count(*) from tweets_0401_0415 group by date_format(created_at, "%m/%d") order by date_format(created_at, "%m/%d")'
r16 = 'select * from users_0401_0415'
r17 = 'describe tweets_0401_0415'
r18 = 'select * from tweets_0401_0415'
r19 = 'select followers_count from users_0401_0415'
r20 = 'select friends_count from users_0401_0415'
r21 = 'select lang, count(lang) from users_0401_0415 where user_id in' + small_community_ + 'group by lang order by lang desc'
r22 = 'select count(followers_count) from users_0401_0415 where user_id in' + small_community_ + 'and followers_count > 5000'
r23 = 'select t.lang, count(t.lang) from users_0401_0415 as u inner join tweets_0401_0415 as t on u.user_id = t.user_id where u.user_id in' + small_community_ + 'group by t.lang order by count(t.lang) desc'
r24 = 'select count(*) from tweets_0401_0415 group by user_id'
'''
file = open('stats_data.txt', 'w')
file_hash = open('hashs_data.txt', 'w')
file_small_community = open('small_community.txt', 'w')
'''

prop = []
lang_src = {'Amharic': 'am', 'German': 'de', 'Malayalam': 'ml', 'Slovak': 'sk', 'Arabic': 'ar', 'Greek': 'el', 'Maldivian': 'dv', 'Slovenian': 'sl', 'Armenian': 'hy', 'Gujarati': 'gu', 'Marathi': 'mr', 'Sorani Kurdish': 'ckb', 'Basque': 'eu', 'Haitian Creole': 'ht', 'Nepali': 'ne', 'Spanish': 'es', 'Bengali': 'bn', 'Hebrew': 'iw', 'Norwegian': 'no', 'Swedish': 'sv', 'Bosnian': 'bs', 'Hindi': 'hi', 'Oriya': 'or', 'Tagalog': 'tl', 'Bulgarian': 'bg', 'Latinized Hindi': 'hi-Latn', 'Panjabi': 'pa', 'Tamil': 'ta', 'Burmese': 'my', 'Hungarian': 'hu', 'Pashto': 'ps', 'Telugu': 'te', 'Croatian': 'hr', 'Icelandic': 'is', 'Persian': 'fa', 'Thai': 'th', 'Catalan': 'ca', 'Indonesian': 'in', 'Polish': 'pl', 'Tibetan': 'bo', 'Czech': 'cs', 'Italian': 'it', 'Portuguese': 'pt', 'Traditional Chinese': 'zh-TW', 'Danish': 'da', 'Japanese': 'ja', 'Romanian': 'ro', 'Turkish': 'tr', 'Dutch': 'nl', 'Kannada': 'kn', 'Russian': 'ru', 'Ukrainian': 'uk', 'English': 'en', 'Khmer': 'km', 'Serbian': 'sr', 'Urdu': 'ur', 'Estonian': 'et', 'Korean': 'ko', 'Simplified Chinese': 'zh-CN', 'Chinese': 'zh','Uyghur': 'ug', 'Finnish': 'fi', 'Lao': 'lo', 'Sindhi': 'sd', 'Vietnamese': 'vi', 'French': 'fr', 'Latvian': 'lv', 'Sinhala': 'si', 'Welsh': 'cy', 'Georgian': 'ka', 'Lithuanian': 'lt'}
lang = {v:k for k,v in lang_src.items()}
prop_lang = {}
prop_date = {}
prop_heure = {}
users = {}
tweets = {}
prop_hash = {}
nb_tweets = []

with mysql.connector.connect(**connection_params) as db:
    with db.cursor() as c:
        '''
###  Requetes sur les utilisateurs
        c.execute(r1)
        result = c.fetchall()
        nb_users = result[0][0]
        file.write("nombre d'utilisateurs : " + str(result[0][0]) + '\n')
        c.execute(r19)
        result = c.fetchall()
        result = list(np.array(result)[:,0])
        mediane = np.median(result)
        moyenne = np.mean(result)
        ecartType = np.std(result)
        mini = min(result)
        maxi = max(result)
        file.write("nombre de followers :  min = " + str(mini) + " ; max = " + str(maxi) + " ; mediane = " + str(mediane) + " ; moyenne = " + str(moyenne) + " ; écart-type = " + str(ecartType) + '\n')
        c.execute(r20)
        result = c.fetchall()
        result = list(np.array(result)[:,0])
        mediane = np.median(result)
        moyenne = np.mean(result)
        ecartType = np.std(result)
        mini = min(result)
        maxi = max(result)
        file.write("nombre de friends :  min = " + str(mini) + " ; max = " + str(maxi) + " ; mediane = " + str(mediane) + " ; moyenne = " + str(moyenne) + " ; écart-type = " + str(ecartType) + '\n')
###  Requetes sur les types de tweets
        c.execute(r2)
        result = c.fetchall()
        nb_tweets = result[0][0]
        file.write('\n' + "nombre de tweets : " + str(nb_tweets) + '\n')
        c.execute(r3)
        result = c.fetchall()
        prop.append(round(int(result[0][0])*100 / nb_tweets,1))
        file.write("nombre de réponses seules : " + str(result[0][0]) + ' (' + str(round(int(result[0][0])*100 / nb_tweets,1)) + '%)' + '\n')
        c.execute(r4)
        result = c.fetchall()
        prop.append(round(int(result[0][0])*100 / nb_tweets,1))
        file.write("nombre de retweets seuls : " + str(result[0][0]) + ' (' + str(round(int(result[0][0])*100 / nb_tweets,1)) + '%)' + '\n')
        c.execute(r5)
        result = c.fetchall()
        prop.append(round(int(result[0][0])*100 / nb_tweets,1))
        file.write("nombre de commentaires seuls : " + str(result[0][0]) + ' (' + str(round(int(result[0][0])*100 / nb_tweets,1)) + '%)' + '\n')
        c.execute(r6)
        result = c.fetchall()
        prop.append(round(int(result[0][0])*100 / nb_tweets,1))
        file.write("autres tweets (ni réponse, ni retweet, ni commentaire) : " + str(result[0][0]) + ' (' + str(round(int(result[0][0])*100 / nb_tweets,1)) + '%)' + '\n')
        c.execute(r7)
        result = c.fetchall()
        prop.append(round(int(result[0][0])*100 / nb_tweets,1))
        file.write("nombre de réponses, retweets et commentaires : " + str(result[0][0]) + ' (' + str(round(int(result[0][0])*100 / nb_tweets,1)) + '%)' + '\n')
        c.execute(r8)
        result = c.fetchall()
        prop.append(round(int(result[0][0])*100 / nb_tweets,1))
        file.write("nombre de réponses et retweets : " + str(result[0][0]) + ' (' + str(round(int(result[0][0])*100 / nb_tweets,1)) + '%)' + '\n')
        c.execute(r9)
        result = c.fetchall()
        prop.append(round(int(result[0][0])*100 / nb_tweets,1))
        file.write("nombre de réponses et commentaires : " + str(result[0][0]) + ' (' + str(round(int(result[0][0])*100 / nb_tweets, 1)) + '%)' + '\n')
        c.execute(r10)
        result = c.fetchall()
        prop.append(round(int(result[0][0])*100 / nb_tweets,1))
        file.write("nombre de retweets et commentaires : " + str(result[0][0]) + ' (' + str(round(int(result[0][0])*100 / nb_tweets,1)) + '%)' + '\n')
###   Requetes sur les hastags
        c.execute(r11)
        result = c.fetchall()
        file.write('\n' + "nombre de hashtags  : " + str(result[0][0]) + '\n')
        c.execute(r12)
        result = c.fetchall()
        file_hash.write("Fréquence d'apparition des hashtags" + '\n')
        for i in range(100):
             prop_hash[result[i][0]]=result[i][1]
             file_hash.write(str(result[i][0]) + " : " + str(result[i][1])+ '\n')
        result = list(np.array(result)[:,1])
        mini = min(result)
        maxi = max(result)
        file.write("statistiques sur les hashtags :  min = " + str(mini) + " ; max = " + str(maxi) +  '\n')
###  Requetes sur la langue du tweet
        c.execute(r13)
        result = c.fetchall()
        file.write('\n' + 'Distribution des tweets par langue (langue : nb de tweets) :' + '\n')
        for i in range(len(result)):
            if result[i][0] != 'und':
                prop_lang[str(result[i][0])]=round(result[i][1]*100/nb_tweets, 2)
                file.write(lang[str(result[i][0])] + '(' + str(result[i][0]) + ')' + ' : ' + str(result[i][1]) + '(' + str(round(result[i][1]*100/nb_tweets, 2)) + '%)' + '\n')
            else:
                file.write('indéfini' + '(' + str(result[i][0]) + ')' + ' : ' + str(result[i][1]) + '(' + str(round(result[i][1]*100/nb_tweets, 2)) + '%)' + '\n')
###   Requetes sur la répartition temporelle des tweets
        c.execute(r14)
        result = c.fetchall()
        for i in range(len(result)):
            prop_heure[str(result[i][0])]=result[i][1]
        c.execute(r15)
        result = c.fetchall()
        file.write('\n' + 'Distribution des tweets par date :' + '\n')
        for i in range(len(result)):
            prop_date[str(result[i][0])]=round(result[i][1]*100/nb_tweets, 1)
            file.write(str(result[i][0]) + ' : ' + str(result[i][1]) + ' (' + str(round(result[i][1]*100/nb_tweets, 1)) + '%)' + '\n')
### Requete sur les users presents dans les petites communautes
        file_small_community.write("langue du user : \n")
        c.execute(r21)
        result = c.fetchall()
        for i in range(len(result)):
            file_small_community.write(str(result[i][0]) + ' : ' + str(result[i][1]) + '\n')
        file_small_community.write("\n nb users avec plus de 5000 followers : \n")
        c.execute(r22)
        result = c.fetchall()
        file_small_community.write(str(result[0][0]) + '\n')
        file_small_community.write("\n langue du tweet : \n")
        c.execute(r23)
        result = c.fetchall()
        for i in range(len(result)):
            file_small_community.write(str(result[i][0]) + ' : ' + str(result[i][1]) + '\n')
        '''
        c.execute(r24)
        result = c.fetchall()
        result = list(np.array(result)[:,0])
        mini = min(result)
        maxi = max(result)
        mediane = np.median(result)
        moyenne = np.mean(result)
        print("nombre de tweets :  min = " + str(mini) + " ; max = " + str(maxi) + " ; mediane = " + str(mediane) + " ; moyenne = " + str(moyenne))

###   Creation des dictionnaires users et tweets pour le graphe
        '''
        c.execute(r16)
        result = c.fetchall()
        for i in range(len(result)):
            users[result[i][0]]={'screen_name': result[i][1], 'name' : result[i][2], 'location' : result[i][3], 'url' : result[i][4], 'description' : result[i][5], 'created_at' : result[i][6], 'followers_count' : result[i][7], 'friends_count' : result[i][8], 'statuses_count' : result[i][9], 'lang' : result[i][10], 'listed_count' : result[i][11], 'verified' : result[i][12]}
        c.execute(r17)
        result1 = c.fetchall()
        c.execute(r18)
        result2 = c.fetchall()
        for i in range(len(result2)):
            tweets[result2[i][0]]={result1[j][0]:result2[i][j] for j in range(len(result1))}
pickle.dump(users, open("users.p", "wb"))
pickle.dump(tweets, open("tweets.p", "wb"))
'''

###   Graphiques

def add_value_label(x_list,y_list):
    for i in range(len(x_list)):
        if y_list[i] != 0:
            plt.text(i,y_list[i]+1,str(y_list[i])+'%', ha="center")

# paramètres des graphiques
parameters = {'axes.labelsize': 8,
              'axes.titlesize': 9,
              'figure.titlesize': 12}

'''
# Diagramme en barres de la distribution par type de tweets
x = ['a', 'r', 'q', 'o', 'a+r+q', 'a+r', 'a+q', 'r+q']
plt.bar(x, prop)
add_value_label(x, prop)
plt.xlabel('type de tweet')
plt.ylabel('% de tweets')
plt.text(5, 45, 'Légende :\n' +'a = réponses \n'+'r = retweets \n'+'q = commentaires\n'+'o = autres')
plt.show()

# Diagramme en barres de la distribution par langue
x_l = list(prop_lang.keys())
y_l = list(prop_lang.values())
plt.bar(x_l, y_l)
plt.axis(xmin = 2, xmax = 30, ymax = 0.65)
plt.xlabel('code langue')
plt.ylabel('% de tweets')
plt.xticks(rotation=90)
plt.show()

# Graphique repartition temporelle
x_d = list(prop_date.keys())
y_d = list(prop_date.values())
plt.figure(figsize = [6.4, 7])
plt.annotate('Débat du 1er tour', xy=(4,12.3), xytext=(6.5,12.3), arrowprops=dict(facecolor='red', edgecolor='red',width = 1, headwidth = 8, shrink=0.1))
#plt.plot(x_d, y_d, "o-")
plt.plot(x_d, y_d, ".-")
plt.xlabel('date (mm/jj)')
plt.ylabel('% de tweets')
plt.xticks(rotation=90)
plt.show()

# Graphique suivi chronologique le 04/04
x_h = list(prop_heure.keys())
y_h = list(prop_heure.values())
plt.figure(figsize = [7, 7])
plt.annotate('Début du débat : 18h40 UTC', xy=(18.4,0), xytext=(14.4,155000), arrowprops=dict(facecolor='red', edgecolor='red', arrowstyle = ' - '))
plt.plot(x_h, y_h, ".-")
plt.xlabel('heure')
plt.ylabel('nombre de tweets')
plt.xticks(rotation=90)
plt.show()

###   Nuage de mots
def couleur(*args, **kwargs):
    return "rgb(0, 100, {})".format(random.randint(100, 255))

mask = np.array(Image.open("mask_twitter.png"))
mask[mask == 1] = 255
wordcloud = WordCloud(width=1200, height=800, colormap = 'brg', background_color ='white', mask = mask).generate_from_frequencies(prop_hash)
#plt.imshow(wordcloud.recolor(color_func=couleur_al), interpolation='bilinear')
plt.imshow(wordcloud)
plt.axis("off")
plt.show()
wordcloud.to_file("first_output_brg.png")
'''
