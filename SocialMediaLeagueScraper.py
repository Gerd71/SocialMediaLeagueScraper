
import requests
import re
from bs4 import BeautifulSoup
from datetime import date
import sqlite3

#Das Scrapen der Follower/Like Zahlen von Facebook, Instagram und Twitter
def get_info(name,user,url):
    response=requests.get(f'{url}{user}')
    soup=BeautifulSoup(response.text,'lxml')
    if url=='https://www.facebook.com/':
        searchtxt='Personen gefällt das'
        like=soup.find("div",text=re.compile(searchtxt)).text
        like=like.split(' ')[0]
        print(f'Likes für {name}: {like}\n')
        return like
    if url=='https://www.instagram.com/':        
        like=re.search('"edge_followed_by":{"count":([0-9]+)}',response.text).group(1)    
        print(f'Likes für {name}: {like}\n')
        return like
    if url=='https://www.twitter.com/':        
        li = soup.find('li',{'class':'ProfileNav-item ProfileNav-item--followers'})
        like = li.find('a').find('span',{'class':'ProfileNav-value'})
        like=like.contents[0]
        print(f'Likes für {name}: {like}\n')
        return like
   

# Funktion zum Anlegen von Datenbank Tabellen
def gen_db(conn):        
    c = conn.cursor()
    #c.execute("update clubs set instagram='salzburg_bulls' where instagram='salzburgbulls'")
    #c.execute('''CREATE TABLE clubs
      #  (name, 'Abonnenten'facebook, instagram, twitter)''')
    #c.execute("INSERT INTO clubs VALUES ('Salzburg Ducks','salzburgducks','salzburgducks','salzburgducks')")
    #c.execute("INSERT INTO clubs VALUES ('Salzburg Bulls','salzburgbulls','salzburg_bulls','salzburgbulls')")
    conn.commit()
    conn.close()


#Das Hauprprogramm
if __name__=='__main__':
     
    connection = sqlite3.connect("afboe.db")
    
    #gen_db(connection)
    print("Facebook")
    i=0

    #Die Zählerstände
    cntfb = []
    cntinsta= []
    cnttwitter= []

    #durchlaufe für alle Vereine
    for row in connection.execute('SELECT name,facebook,id FROM clubs ORDER BY name'):   
        #Facebook
        url="https://www.facebook.com/"  
        cntfb.append(get_info(row[0],row[1],url))
        name=row[0]
        id=row[2]
        cnt=int(cntfb[i].replace(".",""))
        insert=True
        for rowcnt in connection.execute("SELECT id FROM likes where id_clubs='" + str(id) + "' and datum='" + str(date.today()) + "'"):   
                connection.execute("update likes set facebook=" + str(cnt) + " where id_clubs='" + str(id) + "' and datum='" + str(date.today()) + "'")
                insert=False
                       
        if insert==True:
            connection.execute("insert into likes (datum,id_clubs,facebook) values ('" + str(date.today()) + "','" + str(id)  + "','" + str(cnt) + "')")       
        i=i+1

    #Instagram
    print("Instagram")
    i=0
    for row in connection.execute('SELECT name,instagram,id FROM clubs ORDER BY name'):
        url="https://www.instagram.com/"  
        cntinsta.append(get_info(row[0],row[1],url))
        name=row[0]
        id=row[2]
        cnt=int(cntinsta[i].replace(".",""))
        connection.execute("update likes set instagram=" + str(cnt) + " where id_clubs='" + str(id) + "' and datum='" + str(date.today()) + "'")
        i=i+1

    #Twitter
    print("Twitter")
    i=0
    for row in connection.execute('SELECT name,twitter,id FROM clubs ORDER BY name'):
        url="https://www.twitter.com/"  
        cnttwitter.append(get_info(row[0],row[1],url))
        name=row[0]
        id=row[2]
        cnt=int(cnttwitter[i].replace(".",""))
        connection.execute("update likes set twitter=" + str(cnt) + " where id_clubs='" + str(id) + "' and datum='" + str(date.today()) + "'")
        i=i+1

    #Lies das Ranking aus der afboe.db und stelle es dar
    for rankrow in connection.execute("SELECT name,likes.facebook+likes.instagram+likes.twitter FROM likes left join clubs on id_clubs=clubs.id where datum='" + str(date.today()) + "' ORDER BY likes.facebook+likes.instagram+likes.twitter desc"):
        print(str(rankrow[0]) +":"+str(rankrow[1]))

    connection.commit()
    connection.close()
   