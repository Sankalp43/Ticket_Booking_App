# ------------------------Importing Necessary Libraries---------------------------

from flask import Flask , render_template , request , redirect , url_for
from flask_sqlalchemy import SQLAlchemy
import matplotlib
import matplotlib.pyplot as plt
from flask_bcrypt import Bcrypt
matplotlib.use('Agg')

#--------------------------------------------------------------------------------------
#-------------------------------Configurations--------------------------------------

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///project.sqlite3"   
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

bcrypt = Bcrypt()
#-----------------------------------------------------------------------------------------
#---------------------------------------DataBase Models----------------------------------

class UserLogin(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer , primary_key = True , autoincrement = True)
    user_name =  db.Column(db.String , nullable = False)
    user_mail =  db.Column(db.String , nullable = False)
    user_uname = db.Column(db.String , nullable = False)
    user_pass = db.Column(db.String , nullable = False)

class Bookings(db.Model):
    __tablename__ = "bookings"
    booking_id = db.Column(db.Integer , primary_key = True , autoincrement = True)
    booking_user = db.Column(db.Integer ,db.ForeignKey("user.user_id"))
    booking_venue = db.Column(db.Integer ,db.ForeignKey("venues.venue_id"))
    booking_show = db.Column(db.Integer ,db.ForeignKey("shows.show_id"))
    booking_count = db.Column(db.Integer , nullable = False)
    booking_total = db.Column(db.Integer , nullable = False) 


class Venues(db.Model):
    __tablename__ = "venues"
    venue_id = db.Column(db.Integer , primary_key = True , autoincrement = True)
    venue_name = db.Column(db.String , nullable = False)
    # venue_admin = db.Column(db.Integer ,db.ForeignKey("admin.admin_id"))
    venue_place =  db.Column(db.String , nullable = False)
    venue_location =  db.Column(db.String , nullable = False)
    venue_capacity =  db.Column(db.Integer , nullable = False)


class Shows(db.Model):
    __tablename__ = "shows"
    show_id = db.Column(db.Integer , primary_key = True , autoincrement = True)
    show_name = db.Column(db.String , nullable = False)
    show_venue = db.Column(db.Integer ,db.ForeignKey("venues.venue_id"))
    show_rating =  db.Column(db.Numeric , nullable = False) 
    show_date=  db.Column(db.String , nullable = False)
    show_time = db.Column(db.String , nullable = False)
    show_tags =  db.Column(db.String , nullable = False)
    show_price =  db.Column(db.Integer , nullable = False) 
    remaining_cap = db.Column(db.Integer) 


class AdminLogin(db.Model):
    __tablename__ = "admin"
    admin_id = db.Column(db.Integer , primary_key = True , autoincrement = True)
    admin_name = db.Column(db.String , nullable = False)
    admin_pass = db.Column(db.String , nullable = False)



db.create_all()

#------------------------------------------------------------------------------------------
#---------------------------------------Routes----------------------------------------------

@app.route("/")
def hello_world():
     # return "<p>Hello, World!</p>"
    return render_template("index.html")




@app.route("/user_login" , methods = ['GET' , 'POST'])
def user_login():
    if request.method == 'POST':
        uname = request.form['username']
        passw = request.form['password']

        user = UserLogin.query.filter_by(user_uname = uname).all()
        if(len(user)>0):
            if bcrypt.check_password_hash(user[0].user_pass, passw):
                id = user[0].user_id
                # name = user[0].user_name
                return redirect(url_for("venue_list" , id = id ))
            else:
                return render_template("user_login.html" , msg = "Incorrect Password" , msg1 = "Please Inter a Valid Password.")
        else:
            return render_template("user_login.html" , msg = "User not Found." , msg1 = "Please Inter a Valid Usename.") 
    else:
        return render_template("user_login.html")
    
@app.route("/user_signup" , methods = ['GET' , 'POST'])
def user_signup():
    if request.method == 'POST':
        name = request.form['name']
        passw = request.form['password']
        uname = request.form['username']
        mail = request.form['email']
        # return [name , passw , uname , mail]

        user_confirm = UserLogin.query.filter_by(user_uname = uname).all()
        # print(user_confirm)
        if(user_confirm == []):
            passw = bcrypt.generate_password_hash(passw)
            user = UserLogin(user_uname = uname , user_name = name , user_pass = passw , user_mail = mail)
            db.session.add(user)
            db.session.commit()

            id = UserLogin.query.filter_by(user_uname = uname).all()[0].user_id
            return redirect(url_for("venue_list" , id = id ))
        else:
            msg = "User already Exist.Please Login."
            # print(1)
            return render_template("user_exist.html")
            # return redirect(url_for("user_login" , msg =msg ))
        

        # [0]
        # return (str(user == None))
    
        # pass
    else:
        return render_template("user_signup.html")
    

@app.route("/<id>/venue_list" , methods = ['GET' , 'POST'])
def venue_list(id):
    if request.method == "POST":
        param = request.form["search"]
        venueList = Venues.query.filter_by(venue_name = param).all()
        venueList.reverse()
        user = UserLogin.query.filter_by(user_id = id).first()
        name = user.user_name
        return render_template("venue_list.html" , id=id , venues = venueList , name = name)


        # pass
    else:
        venueList = Venues.query.all()
        user = UserLogin.query.filter_by(user_id = id).first()
        name = user.user_name
        venueList.reverse()


        # print(venueList)

        return render_template("venue_list.html" , id=id , venues = venueList , name = name)
    


@app.route("/<user_id>/user_profile" , methods = ['GET' , 'POST'])
def user_profile(user_id):
    if request.method == "POST":
        pass
    else:
        my_bookings = Bookings.query.filter_by(booking_user =  user_id).all()

        my_bookings.reverse()
        l = []
        for i in my_bookings:
            d= {}
            d["booking_id"] = i.booking_id
            user = UserLogin.query.filter_by(user_id = i.booking_user).first().user_name
            d["booking_user"] = user
            venue = Venues.query.filter_by(venue_id = i.booking_venue).first().venue_name
            d["booking_venue"] = venue
            show = Shows.query.filter_by(show_id = i.booking_show).first()
            show_name = show.show_name
            show_date = show.show_date
            show_time = show.show_time
            show_rating = show.show_rating
            show_tags = show.show_tags
            d["booking_date"] = show_date
            d["booking_time"] = show_time
            d["booking_rating"] = show_rating
            d["booking_tags"] = show_tags
            d["booking_show"] = show_name
            d["booking_count"] = i.booking_count
            d["booking_total"] = i.booking_total
            # print(d)

            l.append(d)
        # print(l)

            

        # print(venueList)
        user = UserLogin.query.filter_by(user_id = user_id).first()
        user_name = user.user_name
        user_mail = user.user_mail
        # user_mail = UserLogin.query.filter_by(user_uname = uname).all()[0].user_id


        return render_template("user_profile.html" , id=user_id, bookings = l , user_name = user_name , user_mail = user_mail)
    

@app.route("/<user_id>/<venue_id>/<show_id>/<book_id>/cancel_booking" , methods = ['GET' , 'POST'])
def cancel_booking(user_id ,venue_id , show_id , book_id):
    if request.method == "POST":
        pass
    else:
        return render_template("confirm_cancel_booking.html" , user_id = user_id ,venue_id = venue_id , show_id = show_id ,  book_id = book_id )
        # my_bookings = Bookings.query.filter_by(booking_user =  user_id).all()
        # print(venueList)

        # return render_template("user_profile.html" , id=user_id, bookings = my_bookings)


@app.route("/<user_id>/<venue_id>/<show_id>/<book_id>/confirm_cancel_booking" , methods = ['GET' , 'POST'])
def confirm_cancel_booking(user_id ,venue_id , show_id , book_id):
    if request.method == "POST":
        pass
    else:
        booking = Bookings.query.filter_by(booking_id = book_id).first()
        count = booking.booking_count
        show_id = booking.booking_show

        curr_cap = Shows.query.filter_by(show_id = show_id).first().remaining_cap 
        Shows.query.filter_by(show_id = show_id).first().remaining_cap = int(curr_cap) + int(count)
        # db.session.commit()


        # print(ven)
        db.session.delete(booking)
        db.session.commit()
        return redirect(url_for("user_profile" , user_id = user_id ))

        # return "Kaisa chal rha h"
        # return render_template("confirm_cancel_booking.html" , user_id = user_id ,venue_id = venue_id , show_id = show_id ,  book_id = book_id )
        # my_bookings = Bookings.query.filter_by(booking_user =  user_id).all()
    

# @app.route("/<user_id>/<venue_id>/create_show" , methods = ['GET' , 'POST'])
# def create_show(user_id , venue_id):
#     if request.method == "POST":
#         # return "I am here."
#         show_name = request.form["show_name"]
#         show_rating = request.form["show_rating"]
#         show_date = request.form["show_date"]
#         show_time = request.form["show_time"]
#         tags = request.form["tags"]
#         show_price = request.form["show_price"]


#         show = Shows(show_name = show_name ,show_venue = venue_id, show_rating = show_rating, show_date = show_date , show_time = show_time, show_tags = tags , show_price = show_price)
#         db.session.add(show)
#         db.session.commit()
#         return redirect(url_for("show_list" , venue_id = venue_id , user_id = user_id ))
        # return([venue_name, venue_place ,venue_loc , venue_capacity ])


        # return("ruko jara sabar kro")
    # else:
    #     return render_template("create_show.html" , venue_id = venue_id , user_id = user_id )
    
@app.route("/<user_id>/<venue_id>/show_list" , methods = ['GET' , 'POST'])
def show_list(user_id , venue_id):
    if request.method == "POST":
        param = request.form["search"]
        showList = Shows.query.filter_by(show_name = param).all()
        showList.reverse()
        user = UserLogin.query.filter_by(user_id = user_id).first()
        user_name = user.user_name
        return render_template("show_list.html" , user_id=user_id ,venue_id=venue_id, user_name = user_name ,shows = showList)

        return ["Search Param : ",param]
    else:
        showList = Shows.query.filter_by(show_venue =venue_id ).all()
        ven_name = Venues.query.filter_by(venue_id=venue_id).first().venue_name
        showList.reverse()
        user = UserLogin.query.filter_by(user_id = user_id).first()
        user_name = user.user_name
        

        return render_template("show_list.html" , user_id=user_id ,venue_id=venue_id, user_name = user_name ,shows = showList,venue_name = ven_name)
    
@app.route("/<user_id>/<venue_id>/<show_id>/booking" , methods =  ['GET' , 'POST'])
def booking(user_id , venue_id , show_id ):
    if request.method == "POST":
        count = request.form['booking_count']
        show = Shows.query.filter_by(show_id = show_id).all()[0]
        rem_cap = show.remaining_cap
        if(int(rem_cap) - int(count) < 0):
            return render_template("overbooked.html", user_id = user_id , venue_id = venue_id , show_id = show_id) 




        

        price = Shows.query.filter_by(show_id = show_id).all()[0].show_price
        print(price)
        total = price * int(count)
        booking = Bookings(booking_user = user_id , booking_venue = venue_id , booking_show = show_id , booking_count = count , booking_total = total)
        db.session.add(booking)
        curr_cap = Shows.query.filter_by(show_id = show_id).first().remaining_cap 
        Shows.query.filter_by(show_id = show_id).first().remaining_cap = int(curr_cap) - int(count)
        db.session.commit()
        return render_template("booking_success.html" , total = total , user_id = user_id)
    else:
        show = Shows.query.filter_by(show_id = show_id).all()[0]
        price = show.show_price
        rem_cap = show.remaining_cap
        user = UserLogin.query.filter_by(user_id = user_id).first()
        user_name = user.user_name
        return render_template("booking.html", user_id = user_id , venue_id = venue_id , show_id = show_id , price = price ,rem_seats= rem_cap , user_name= user_name) 

@app.route("/log_out" , methods =  ['GET' , 'POST'])
def log_out():

    return redirect("/")



    
@app.route("/admin_login" , methods = ['GET' , 'POST'])
def admin_login():
    if request.method == 'POST':
        ad_name = request.form['adminname']
        passw = request.form['password']
        print(ad_name , passw)
        # admin = AdminLogin.query.filter_by(admin_name = ad_name).all()
        admin = {"admin_name" : "Sankalp" , "admin_pass" : "12345" }
        print(admin)
        if(admin["admin_name"] == ad_name):
            if(admin["admin_pass"] == passw):
                name = admin["admin_name"]
                return redirect(url_for("venue_list_admin" , name = name ))
            else:
                return render_template("admin_login.html" , msg = "Incorrect Password")
        else:
            return render_template("admin_login.html" , msg = "Please input valid UserName.")
    else:
        return render_template("admin_login.html" )
    
@app.route("/<name>/venue_list_admin" , methods = ['GET' , 'POST'])
def venue_list_admin(name):
    if request.method == "POST":
        pass
    else:
        venueList = Venues.query.all()
        venueList.reverse()
        # print(venueList)

        return render_template("venue_list_admin.html" , name=name , venues = venueList)
    
@app.route("/<name>/create_venue" , methods = ['GET' , 'POST'])
def create_venue(name):
    print(name)
    if request.method == "POST":
        venue_name = request.form["venue_name"]
        venue_place = request.form["venue_place"]
        venue_loc = request.form["venue_location"]
        venue_capacity = request.form["venue_capacity"]

        venue = Venues(venue_name = venue_name , venue_place = venue_place, venue_location = venue_loc , venue_capacity = venue_capacity )
        db.session.add(venue)
        db.session.commit()
        return redirect(url_for("venue_list_admin" , name = name ))
        # return([venue_name, venue_place ,venue_loc , venue_capacity ])


        # return("ruko jara sabar kro")
    else:
        return render_template("create_venue.html" , name = name)
    
@app.route("/<admin_name>/<venue_id>/remove_venue" , methods = ['GET' , 'POST'])
def remove_venue(admin_name , venue_id):
    if request.method == "POST":
        pass
    else:
        print("inside remove_vanue" ,venue_id )
        return render_template("venue_delete_confirmation.html" , admin_name=admin_name , venue_id=venue_id)
        return redirect(url_for("confirm_remove", venue_id = venue_id , admin_name = admin_name))
    # ven = Venues.query.filter_by(venue_id=venue_id)
    # pass   

@app.route("/<admin_name>/<venue_id>/confirm_remove" , methods = ['GET' , 'POST'])
def confirm_remove(admin_name,venue_id):
    if request.method == "POST":
        pass
    
    else:
        print("inside confirm" , venue_id)
        ven = Venues.query.filter_by(venue_id=venue_id).first()
        print(ven)
        db.session.delete(ven)

        db.session.query(Shows).filter(Shows.show_venue==venue_id).delete()
        # db.session.commit()

        db.session.commit() 
        return render_template("succesfully_deleted.html", admin_name = admin_name)
    


@app.route("/<admin_name>/<venue_id>/edit_venue" , methods = ['GET' , 'POST'])
def edit_venue(admin_name , venue_id):
    if request.method == "POST":
        venue_name = request.form["venue_name"]
        venue_place = request.form["venue_place"]
        venue_loc = request.form["venue_location"]
        venue_capacity = request.form["venue_capacity"]
        ven = Venues.query.filter_by(venue_id=venue_id).first()
        ven.venue_name  = venue_name
        ven.venue_place = venue_place
        ven.venue_location = venue_loc
        ven.venue_capacity = venue_capacity
        db.session.commit()
        return  render_template("succesfully_edited_venue.html", admin_name = admin_name)
    

        return [venue_name , venue_place , venue_loc , venue_capacity]
    else:
        print("inside remove_vanue" ,venue_id )
        ven = Venues.query.filter_by(venue_id=venue_id).first()
        venue_name = ven.venue_name
        venue_place = ven.venue_place
        venue_location = ven.venue_location
        venue_capacity = ven.venue_capacity
        # print("venue_capacity" , venue_capacity)
        return render_template("edit_venue.html" , admin_name=admin_name , venue_id=venue_id, venue_name = venue_name , venue_place = venue_place ,venue_location = venue_location, venue_capacity = venue_capacity ) 
        return redirect(url_for("confirm_remove", venue_id = venue_id , admin_name = admin_name))



@app.route("/<admin_name>/<venue_id>/create_show" , methods = ['GET' , 'POST'])
def create_show(admin_name , venue_id):
    if request.method == "POST":
        # return "I am here."
        show_name = request.form["show_name"]
        show_rating = request.form["show_rating"]
        show_date = request.form["show_date"]
        show_time = request.form["show_time"]
        tags = request.form["tags"]
        show_price = request.form["show_price"]

        show_capacity = Venues.query.filter_by(venue_id = venue_id).first().venue_capacity

        show = Shows(show_name = show_name ,show_venue = venue_id, show_rating = show_rating, show_date = show_date , show_time = show_time, show_tags = tags , show_price = show_price , remaining_cap = show_capacity)
        db.session.add(show)
        db.session.commit()
        #can add venue name.
        return redirect(url_for("show_list_admin" , venue_id = venue_id ,admin_name = admin_name))
        # return([venue_name, venue_place ,venue_loc , venue_capacity ])


        # return("ruko jara sabar kro")
    else:
        return render_template("create_show.html" , venue_id = venue_id , admin_name = admin_name)
  
@app.route("/<admin_name>/<venue_id>/<show_id>/remove_show" , methods = ['GET' , 'POST'])
def remove_show(admin_name , venue_id , show_id):
    if request.method == "POST":
        pass
    else:
        return render_template("show_delete_confirmation.html" , admin_name = admin_name , show_id = show_id , venue_id=venue_id)


@app.route("/<admin_name>/<venue_id>/<show_id>/confirm_remove_show" , methods = ['GET' , 'POST'])
def confirm_remove_show(admin_name , venue_id , show_id):
    if request.method == "POST":
        pass
    else:
        show = Shows.query.filter_by(show_id = show_id).first()
        # print(ven)
        db.session.delete(show)
        db.session.commit()
        return redirect(url_for("show_list_admin" , venue_id = venue_id , admin_name = admin_name))
        #  return [show_id , venue_id]

@app.route("/<admin_name>/<venue_id>/<show_id>/edit_show" , methods = ['GET' , 'POST'])
def edit_show(admin_name , venue_id , show_id):
    if request.method == "POST":
        show_name = request.form["show_name"]
        show_rating = request.form["show_rating"]
        # show_date = request.form["show_date"]
        # show_time = request.form["show_time"]
        tags = request.form["tags"]
        show_price = request.form["show_price"]

        show = Shows.query.filter_by(show_id = show_id).first()
        show.show_name = show_name
        show.show_rating = show_rating
        # show.show_date = show_date
        # show.show_time = show_time
        show.show_tags = tags
        show.show_price = show_price

        db.session.commit()
        return  render_template("succesfully_edited_show.html", admin_name = admin_name , venue_id = venue_id)

        return [show_name,show_rating]
    else:
        show = Shows.query.filter_by(show_id=show_id).first()
        show_name = show.show_name
        show_rating = show.show_rating
        show_date = show.show_date
        show_time = show.show_time
        show_tags = show.show_tags
        show_price = show.show_price
        
        return render_template("edit_show.html" , admin_name=admin_name , venue_id=venue_id,show_id = show_id, show_name = show_name , show_rating=show_rating,show_date=show_date,show_time=show_time,tags=show_tags,show_price=show_price ) 
        
@app.route("/<admin_name>/<venue_id>/show_list_admin" , methods = ['GET' , 'POST'])
def show_list_admin(admin_name , venue_id):
    if request.method == "POST":
        pass
    else:
        showList = Shows.query.filter_by(show_venue =venue_id ).all()
        print(showList)
        showList.reverse()
        # show_list.reverse()
        ven_name = Venues.query.filter_by(venue_id=venue_id).first().venue_name

        

        return render_template("show_list_admin.html" ,admin_name = admin_name , venue_id=venue_id, shows = showList , venue_name = ven_name)
    
@app.route("/<admin_name>/summary" , methods = ['GET' , 'POST'])
def summary(admin_name):
    if request.method == "POST":
        pass
    else:
        total_venues = Venues.query.all()
        total_venues_count = len(total_venues)
        total_shows = Shows.query.all()
        total_shows_count = len(total_shows)
        total_bookings = Bookings.query.all()
        total_bookings_count = len(total_bookings)

        # ---------------------------------------
        total_revenue_sum = 0
        total_person_count = 0
        for i in total_bookings:
            total_revenue_sum += i.booking_total
            total_person_count += i.booking_count

        # ---------------------------------------------
        if int(total_venues_count) < 5 or int(total_shows_count) < 5:
            return render_template("summary_short.html" , admin_name = admin_name, total_venues = total_venues_count , total_shows = total_shows_count , total_bookings = total_bookings_count , total_revenue = total_revenue_sum , total_person = total_person_count)


        # --------------------------------------------
                          # OVER VENUES
        bookings_over_venues = {}
        person_over_venues = {}
        revenue_over_venues = {}
        for i in total_venues:
            venue_id = i.venue_id
            venue_name = i.venue_name
            bookings = Bookings.query.filter_by(booking_venue = venue_id).all()
            total_book = len(bookings)
            bookings_over_venues[venue_name] = total_book

            person_count = 0
            revenue_sum = 0
            for j in bookings:
                person_count += j.booking_count
                revenue_sum += j.booking_total

            person_over_venues[venue_name] = person_count
            revenue_over_venues[venue_name] = revenue_sum
        print(bookings_over_venues)
        # print(person_over_venues)
        # print(revenue_over_venues)


        # --------------------------------------------------
                            # OVER SHOWS
        bookings_over_shows = {}
        person_over_shows = {}
        revenue_over_shows = {}

        for i in total_shows:
            show_id = i.show_id
            show_name = i.show_name
            bookings = Bookings.query.filter_by(booking_show = show_id).all()
            total_book = len(bookings)
            bookings_over_shows[show_name] = total_book

            person_count = 0
            revenue_sum = 0
            for j in bookings:
                person_count += j.booking_count
                revenue_sum += j.booking_total

            person_over_shows[show_name] = person_count
            revenue_over_shows[show_name] = revenue_sum

        #-------------------------------------------------
                    # SOME SHORTING OVER HERE
        bookings_over_venues = dict(sorted(bookings_over_venues.items(), key=lambda x:x[1], reverse=True))
        person_over_venues = dict(sorted(person_over_venues.items(), key=lambda x:x[1], reverse=True))
        revenue_over_venues = dict(sorted(revenue_over_venues.items(), key=lambda x:x[1], reverse=True))
        bookings_over_shows = dict(sorted(bookings_over_shows.items(), key=lambda x:x[1], reverse=True))
        person_over_shows = dict(sorted(person_over_shows.items(), key=lambda x:x[1], reverse=True))
        revenue_over_shows = dict(sorted(revenue_over_shows.items(), key=lambda x:x[1], reverse=True))
        image_chart_path = []
        # plt.clf()
        # plt.figure(figsize=(8,4))

        fig, ax = plt.subplots()
        
        # ------------------------------------------------------------
        # 1
        venues_booking_keys = list(bookings_over_venues.keys())[:5]
        venue_booking_values = list(bookings_over_venues.values())[:5]

        # fruits = ['apple', 'blueberry', 'cherry', 'orange']
        # counts = [40, 100, 30, 55]
        # bar_labels = ['red', 'blue', '_red', 'orange']
        # bar_colors = ['tab:red', 'tab:blue', 'tab:red', 'tab:orange']

        ax.bar(venues_booking_keys, venue_booking_values)

        ax.set_ylabel('Number Of Bookings')
        ax.set_title('Booking Over Venues--Top 5')
        plt.savefig("./static/venue_book.png")
        image_chart_path.append("/static/venue_book.png")

        # --------------------------------------------------
        # 2
        fig, ax = plt.subplots()

        venues_person_keys = list(person_over_venues.keys())[:5]
        venue_person_values = list(person_over_venues.values())[:5]


        ax.bar(venues_person_keys, venue_person_values)

        ax.set_ylabel('Number Of Persons')
        ax.set_title('Persons Over Venues--Top 5')
        plt.savefig("./static/venue_person.png")
        image_chart_path.append("/static/venue_person.png")

        # --------------------------------------------------
        # 3
        fig, ax = plt.subplots()

        venues_revenue_keys = list(revenue_over_venues.keys())[:5]
        venue_revenue_values = list(revenue_over_venues.values())[:5]


        ax.bar(venues_revenue_keys, venue_revenue_values)

        ax.set_ylabel('Total Revenue')
        ax.set_title('Revenue Over Venues--Top 5')
        plt.savefig("./static/venue_revenue.png")
        image_chart_path.append("/static/venue_revenue.png")

        # --------------------------------------------------
        # 4
        shows_booking_keys = list(bookings_over_shows.keys())[:5]
        shows_booking_values = list(bookings_over_shows.values())[:5]
        fig, ax = plt.subplots()



        ax.bar(shows_booking_keys, shows_booking_values)

        ax.set_ylabel('Number Of Bookings')
        ax.set_title('Booking Over Shows--Top 5')
        plt.savefig("./static/shows_book.png")
        image_chart_path.append("/static/shows_book.png")

        # --------------------------------------------------
        # 5
        fig, ax = plt.subplots()

        show_person_keys = list(person_over_shows.keys())[:5]
        show_person_values = list(person_over_shows.values())[:5]
       

        ax.bar(show_person_keys, show_person_values)

        ax.set_ylabel('Number Of Persons')
        ax.set_title('Persons Over Shows--Top 5')
        plt.savefig("./static/show_person.png")
        image_chart_path.append("/static/show_person.png")

        # --------------------------------------------------
        # 6
        fig, ax = plt.subplots()

        shows_revenue_keys = list(revenue_over_shows.keys())[:5]
        shows_revenue_values = list(revenue_over_shows.values())[:5]
        print(shows_revenue_keys,shows_revenue_values)


        ax.bar(shows_revenue_keys, shows_revenue_values)

        ax.set_ylabel('Total Revenue')
        ax.set_title('Revenue Over Shows--Top 5')
        plt.savefig("./static/show_revenue.png")
        image_chart_path.append("/static/show_revenue.png")

        # --------------------------------------------------

        # ax.legend(title='Fruit color')

        # plt.show()

        # print("#-------------------------------#")
        # print(bookings_over_shows)
        # print(person_over_shows)   
        # print(revenue_over_shows)   
        # print(bookings_over_venues)
        # print(list(bookings_over_venues.keys()))
        # print(bookings_over_venues.values())

        return render_template("summary_wide.html" , admin_name = admin_name, total_venues = total_venues_count , total_shows = total_shows_count , total_bookings = total_bookings_count , total_revenue = total_revenue_sum , total_person = total_person_count , charts = image_chart_path)

#----------------------------------------------------------------------------------------------------------------
#------------------------Running the App--------------------------------------------------


if __name__ == "__main__":
    app.run(debug=True , port = 5600)

#---------------------------------------------------------------