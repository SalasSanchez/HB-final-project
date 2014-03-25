import model  #this is the file model.py that has the database structure, from our computer
import csv #this is a built-in library
import datetime 
import re 



def load_users(session):
    with open("seed_data/u.user.tsv") as f:  #seed_data/u.user is the name 
    #of the path and the file from which we are importing the data. 
    #"with open" is a way of opening a file and closing automatically, 
    #without having to manually close it at the end
        line_reader = csv.reader(f, delimiter="\t")
        for row in line_reader:
            #id, first_name, last_name, email, password, created_on = row
            first_name = row[0]
            last_name = row[1]
            email = row[2]
            p=row[3]
            if row[4]:
                created_on = datetime.datetime.strptime(row[4], "%Y,%m,%d")    #1992,12,31
            else:
                created_on = datetime.datetime.today()
            u = model.User(  #this is calling the function on model.py, which makes the table
                           first_name=first_name,                            
                           last_name=last_name,
                           email=email,
                           password=p,
                           created_on=created_on)
            u.set_password(p)
            session.add(u)
        session.commit() #if buggy, commit after every add, so that an error gives a specific line
    
    


def load_codes(session):
    with open("seed_data/u.code.tsv") as f:
        line_reader = csv.reader(f, delimiter="\t")
        for row in line_reader:
            #referral_code, company_id, expiry_date, user_id, date_added, 
            # description, url = row
            #id = int(row[0]) The id is given automatically
            referral_code = row[0]
            company_id = int(row[1])
            if row[2]:
                expiry_date = datetime.datetime.strptime(row[2], "%Y,%m,%d")    
            else:
                expiry_date = datetime.datetime(3000, 1, 1)
            user_id = row[3]
            if row[4]:
                date_added = datetime.datetime.strptime(row[4], "%Y,%m,%d")
            else:
                date_added = datetime.datetime.today()
            description = row[5]
            url =row [6]
            u = model.Code(referral_code=referral_code,
                           company_id=company_id,
                           expiry_date=expiry_date,
                           user_id=user_id,
                           date_added=date_added,
                           description=description,
                           url=url)
            session.add(u)
        session.commit()


def load_friendships(session):
    with open("seed_data/u.friendship.tsv") as f:
        line_reader = csv.reader(f, delimiter="\t")
        for row in line_reader:
            # user_id, buddy_id, is_active = row
            print row
            user_id = row[0]
            buddy_id = row[1]
            is_active = row[2]

            u = model.Friendship(user_id = user_id,
                             buddy_id = buddy_id,
                             is_active = is_active)

            session.add(u)
        session.commit()

def load_companies(session):
    with open("seed_data/u.company.tsv") as f:
        line_reader = csv.reader(f, delimiter="\t")
        for row in line_reader:
            name = row[0]
            if row[1]:
                date_added = datetime.datetime.strptime(row[1], "%Y,%m,%d")
            else:
                date_added = datetime.datetime.today()


            u=model.Company(name=name, date_added=date_added)
            session.add(u)

        session.commit()


def load_categories(session):
    with open("seed_data/u.category.tsv") as f:
        line_reader = csv.reader(f, delimiter="\t")
        for row in line_reader:
            name = row[0]

            u=model.Category(name=name)
            session.add(u)

        session.commit()


def load_codescats(session):
    with open("seed_data/u.codescat.tsv") as f:
        line_reader = csv.reader(f, delimiter= "\t")
        for row in line_reader:
            code_id=row[0]
            category_id=row[1]

            u=model.CodesCat(code_id=code_id, category_id=category_id)
            session.add(u)

        session.commit()



def main(session):
    load_users(session)
    load_companies(session)
    load_codes(session)
    load_friendships(session)
    load_categories(session)
    load_codescats(session)
    


if __name__ == "__main__":
    s= model.connect()
    main(s)







