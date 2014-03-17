import model  #this is the file model.py that has the database structure, from our computer
import csv #this is a built-in library
from datetime import datetime 
import re 

def load_users(session):
    with open("seed_data/u.user") as f:  #seed_data/u.user is the name 
    #of the path and the file from which we are importing the data. 
    #"with open" is a way of opening a file and closing automatically, 
    #without having to manually close it at the end
        line_reader = csv.reader(f, delimiter="|")
        for row in line_reader:
            #id, age, gender, occupation, zipcode = row
            id = int(row[0])
            age = int(row[1])
            zipcode = row[4]
            u = model.User(id=id,   #this is calling the funciton on model.py, which makes the table
                           age=age, 
                           email=None,
                           password=None,
                           zipcode=zipcode)
            session.add(u)
        session.commit() #if buggy, commit after every add, so that an error gives a specific line
    

def load_movies(session):
    with open("seed_data/u.item") as f:
        line_reader = csv.reader(f, delimiter="|")
        for row in line_reader:
            #id, title, released_at, imbd_url=row
            id = int(row[0])
            # name = str(re.search("[^\((\d{4})\)]", row[1]))
            name = re.sub("[\((\d{4})\)]","", row[1])
            # print name

            if row[2]:
                released_at = datetime.strptime(row[2], "%d-%b-%Y")    #01-Jan-1995
            else:
                pass
            imdb_url = row[3]
            u = model.Movie(id= id,
                            released_at = released_at,
                            imdb_url = imdb_url,
                            name = name.decode("latin-1"))
            session.add(u)
        session.commit()


def load_ratings(session):
    with open("seed_data/u.data") as f:
        line_reader = csv.reader(f, delimiter="|")
        for row in line_reader:
            # id, user_id, item_id, rating, timestamp = row
            row_list = row[0].split()
            #print row_list
            user_id = int(row_list[0])
            item_id = int(row_list[1])
            rating = int(row_list[2])
            # # rating = int(row[3])
            u = model.Rating(movie_id = item_id,
                             user_id = user_id,
                             rating = rating)

            session.add(u)
        session.commit()





def main(session):
    load_users(session)
    load_movies(session)
    load_ratings(session)


if __name__ == "__main__":
    s= model.connect()
    main(s)