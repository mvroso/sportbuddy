from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/index")
def index():
    return render_template('index.html', title='Home')

@main.route("/contact")
def contact():
    return render_template('contact.html', title='Contact')

@main.route("/about")
def about():
    return render_template('about.html', title='About')


# Imports for inserting data
from flask import flash, redirect, url_for
from datetime import datetime
from website import db, bcrypt
from website.models import User, Role, Sport, Coach, Event, Timeperiod, Match

# Populate the database for the first time
@main.route("/insertdata")
def insertdata():

    # Create four timeperiods
    timeperiods = [
        Timeperiod(name='Morning'),
        Timeperiod(name='Afternoon'),
        Timeperiod(name='Evening'),
        Timeperiod(name='Night')
    ]
    db.session.add_all(timeperiods)
    db.session.commit() 

    # Create three standard roles
    roles = [
        Role(name='Common'),
        Role(name='Coach'),
        Role(name='Company')
    ]
    db.session.add_all(roles)
    db.session.commit()
    
    # Create 39 standard sports
    sports = [
        Sport(name='Archery'),
        Sport(name='Artistic Gymnastics'),
        Sport(name='Artistic Swimming'),
        Sport(name='Athletics'),
        Sport(name='Badminton'),
        Sport(name='Basketball'),
        Sport(name='Beach Volleyball'),
        Sport(name='Biathlon'),
        Sport(name='BMX Racing'),
        Sport(name='Boxing'),
        Sport(name='Diving'),
        Sport(name='Equestrian'),
        Sport(name='Fencing'),
        Sport(name='Golf'),
        Sport(name='Handball'),
        Sport(name='Hockey'),
        Sport(name='Judo'),
        Sport(name='Kayak Flatwater'),
        Sport(name='Kayak Slalom'),
        Sport(name='Marathon Swimming'),
        Sport(name='Modern Pentatlhlon'),
        Sport(name='Montain Bike'),
        Sport(name='Rhythmic Gymnastics'),
        Sport(name='Road Cycling'),
        Sport(name='Rowing'),
        Sport(name='Rugby'),
        Sport(name='Sailing'),
        Sport(name='Soccer'),
        Sport(name='Surfing'),
        Sport(name='Swimming'),
        Sport(name='Table Tennis'),
        Sport(name='Tennis'),
        Sport(name='Track Cycling'),
        Sport(name='Trampoline'),
        Sport(name='Triathlon'),
        Sport(name='Volleyball'),
        Sport(name='Water Polo'),
        Sport(name='Weight Lifting'),
        Sport(name='Wrestling')
    ]
    db.session.add_all(sports)
    db.session.commit()

    # Create 20 standard users
    hashed_password = bcrypt.generate_password_hash(
                                    "123").decode('utf-8')

    users = [
        User(name='Susanna Onio',
                email='susannaonio@teste.com',
                password=hashed_password,
                gender_id=2),
        User(name='Agenore Bruno',
                email='agenorebruno@teste.com',
                password=hashed_password,
                gender_id=1),
        User(name='Amalio Davide',
                email='amaliodavide@teste.com',
                password=hashed_password,
                gender_id=1),
        User(name='Sandra Romani',
                email='sandraromani@teste.com',
                password=hashed_password,
                gender_id=2),
        User(name='Maria Pia Udinese',
                email='mariapiaudinese@teste.com',
                password=hashed_password,
                gender_id=2),
        User(name='Ornella Lettiere',
                email='ornellalettiere@teste.com',
                password=hashed_password,
                gender_id=2),
        User(name='Bernardo Genovesi',
                email='bernardogenovesi@teste.com',
                password=hashed_password,
                gender_id=1),
        User(name='Matteo Cattaneo',
                email='matteocattaneo@teste.com',
                password=hashed_password,
                gender_id=1),
        User(name='Antonio Greece',
                email='antoniogreece@teste.com',
                password=hashed_password,
                gender_id=1),
        User(name='Ignazio Loggia',
                email='ignaziologgia@teste.com',
                password=hashed_password,
                gender_id=1),
        User(name='Raffaella Genovesi',
                email='raffaellagenovesi@teste.com',
                password=hashed_password,
                gender_id=2),
        User(name='Cecilia Calabrese',
                email='ceciliacalabrese@teste.com',
                password=hashed_password,
                gender_id=2),
        User(name='Innocenzo Pisano',
                email='innocenzopisano@teste.com',
                password=hashed_password,
                gender_id=1),
        User(name='Amerigo Udinesi',
                email='amerigoudinesi@teste.com',
                password=hashed_password,
                gender_id=1),
        User(name='Aloisa Trentino',
                email='aloisatrentino@teste.com',
                password=hashed_password,
                gender_id=2),
        User(name='Enrico Russo',
                email='enricorusso@teste.com',
                password=hashed_password,
                gender_id=1),
        User(name='Gennaro Milano',
                email='gennaromilano@teste.com',
                password=hashed_password,
                gender_id=1),
        User(name='Erminia Udinese',
                email='erminiaudinese@teste.com',
                password=hashed_password,
                gender_id=2),
        User(name='Brigida Milani',
                email='brigidamilani@teste.com',
                password=hashed_password,
                gender_id=2),
        User(name='Raffaele Lombardi',
                email='raffaelelombardi@teste.com',
                password=hashed_password,
                gender_id=1)
    ]
    db.session.add_all(users)
    db.session.commit()

    # Create 30 standard coaches
    descr = ("I am a skilled Coach with 10 plus years of experience "
        "and in-depth knowledge of college athletic program regulations "
        "and mentoring of athletes. I consistently motivate and inspire "
        "players to bring their best to every game. My mission as a coach "
        "is to take the gifts young athletes have been blessed with and "
        "turn them into skills that will help them succeed on and off "
        "the court. I am an expert in recognizing and working on players' "
        "weakness and strengths by developing customized training sessions.")

    coaches = [
        Coach(name='Adelaide Fiorentini',
                email='adelaidefiorentini@teste.com',
                gender_id=2,
                role_id=2,
                password=hashed_password,
                plan_id=2,
                hourly_rate=40.00, 
                phone_number='3315532635',
                image_file='image-4.jpg',
                card_file='team-2.jpg',
                description = descr),
        Coach(name='Alceo Marchesi',
                email='alceomarchesi@teste.com',
                gender_id=1,
                role_id=2,
                password=hashed_password,
                plan_id=2,
                hourly_rate=45.00, 
                phone_number='3337432636',
                image_file='image-1.jpg',
                card_file='team-1.jpg',
                description = descr),
        Coach(name='Siro Marcelo',
                email='siromarcelo@teste.com',
                gender_id=1,
                role_id=2,
                password=hashed_password,
                plan_id=2,
                hourly_rate=80.00, 
                phone_number='3404332567',
                image_file='image-2.jpg',
                card_file='team-1.jpg',
                description = descr),
        Coach(name='Adele Baresi',
                email='adelebaresi@teste.com',
                gender_id=2,
                role_id=2,
                password=hashed_password,
                plan_id=2,
                hourly_rate=75.00, 
                phone_number='3452435622',
                image_file='image-5.jpg',
                card_file='team-4.jpg',
                description = descr),
        Coach(name='Gabriel Sanches',
                email='gabrielsanches@teste.com',
                gender_id=1,
                role_id=2,
                password=hashed_password,
                plan_id=2,
                hourly_rate=40.00, 
                phone_number='3314432435',
                image_file='image-3.jpg',
                card_file='team-3.jpg',
                description = descr),
        Coach(name='Agatino Fallaci',
                email='agatinofallaci@teste.com',
                gender_id=1,
                role_id=2,
                password=hashed_password,
                plan_id=1,
                hourly_rate=55.00, 
                phone_number='3317312436',
                image_file='image-1.jpg',
                description = descr),
        Coach(name='Gianetto Mazzi',
                email='gianettomazzi@teste.com',
                gender_id=1,
                role_id=2,
                password=hashed_password,
                plan_id=1,
                hourly_rate=60.00, 
                phone_number='3474432599',
                image_file='image-2.jpg',
                description = descr),
        Coach(name='Facondo Lombardo',
                email='facondolombardo@teste.com',
                gender_id=1,
                role_id=2,
                password=hashed_password,
                plan_id=1,
                hourly_rate=90.00, 
                phone_number='3664532892',
                image_file='image-3.jpg',
                description = descr),
        Coach(name='Vittoria Toscano',
                email='vittoriatoscano@teste.com',
                gender_id=2,
                role_id=2,
                password=hashed_password,
                plan_id=2,
                hourly_rate=75.00, 
                phone_number='3317922835',
                image_file='image-6.jpg',
                card_file='team-4.jpg',
                description = descr),
        Coach(name='Marcella Davide',
                email='marcelladavide@teste.com',
                gender_id=2,
                role_id=2,
                password=hashed_password,
                plan_id=2,
                hourly_rate=50.00, 
                phone_number='3397292987',
                image_file='image-4.jpg',
                card_file='team-2.jpg',
                description = descr),
        Coach(name='Cornelio Dellucci',
                email='corneliodellucci@teste.com',
                gender_id=1,
                role_id=2,
                password=hashed_password,
                plan_id=1,
                hourly_rate=30.00, 
                phone_number='3334451932',
                image_file='image-1.jpg',
                description = descr),
        Coach(name='Diego Greco',
                email='diegogreco@teste.com',
                gender_id=1,
                role_id=2,
                password=hashed_password,
                plan_id=1,
                hourly_rate=100.00, 
                phone_number='3234932237',
                image_file='image-2.jpg',
                description = descr),
        Coach(name='Leda Mancini',
                email='ledamancini@teste.com',
                gender_id=2,
                role_id=2,
                password=hashed_password,
                plan_id=1,
                hourly_rate=60.00, 
                phone_number='3664533536',
                image_file='image-5.jpg',
                description = descr),
        Coach(name='Luciano Palermo',
                email='lucianopalermo@teste.com',
                gender_id=1,
                role_id=2,
                password=hashed_password,
                plan_id=1,
                hourly_rate=45.00, 
                phone_number='3338732945',
                image_file='image-3.jpg',
                description = descr),
        Coach(name='Egidio Belluci',
                email='egidiobelluci@teste.com',
                gender_id=1,
                role_id=2,
                password=hashed_password,
                plan_id=1,
                hourly_rate=85.00, 
                phone_number='3884634435',
                image_file='image-1.jpg',
                description = descr),
        Coach(name='Roberto Mancini',
                email='robertomancini@teste.com',
                gender_id=1,
                role_id=2,
                password=hashed_password,
                plan_id=1,
                hourly_rate=95.00, 
                phone_number='3464643235',
                image_file='image-2.jpg',
                description = descr),
        Coach(name='Prospero Russo',
                email='prosperorusso@teste.com',
                gender_id=1,
                role_id=2,
                password=hashed_password,
                plan_id=1,
                hourly_rate=49.00, 
                phone_number='3317832933',
                image_file='image-3.jpg',
                description = descr),
        Coach(name='Aldo Longo',
                email='aldolongo@teste.com',
                gender_id=1,
                role_id=2,
                password=hashed_password,
                plan_id=1,
                hourly_rate=55.00, 
                phone_number='3335634431',
                image_file='image-1.jpg',
                description = descr),
        Coach(name='Pasqualina Lombardi',
                email='pasqualinalombardi@teste.com',
                gender_id=2,
                role_id=2,
                password=hashed_password,
                plan_id=1,
                hourly_rate=60.00, 
                phone_number='3317412936',
                image_file='image-6.jpg',
                description = descr),
        Coach(name='Giulia Li Fonti',
                email='giulialifonti@teste.com',
                gender_id=2,
                role_id=2,
                password=hashed_password,
                plan_id=1,
                hourly_rate=50.00, 
                phone_number='3604433935',
                image_file='image-4.jpg',
                description = descr),
        Coach(name='Aladino Esposito',
                email='aladinoesposito@teste.com',
                gender_id=1,
                role_id=2,
                password=hashed_password,
                plan_id=1,
                hourly_rate=120.00, 
                phone_number='3314937255',
                image_file='image-2.jpg',
                description = descr),
        Coach(name='Norma Sal',
                email='normasal@teste.com',
                gender_id=2,
                role_id=2,
                password=hashed_password,
                plan_id=1,
                hourly_rate=45.00, 
                phone_number='3357042039',
                image_file='image-5.jpg',
                description = descr),
        Coach(name='Consuelo Lucchesi',
                email='consuelolucchesi@teste.com',
                gender_id=1,
                role_id=2,
                password=hashed_password,
                plan_id=1,
                hourly_rate=15.00, 
                phone_number='3334902705',
                image_file='image-3.jpg',
                description = descr),
        Coach(name='Ubalda Lorenzo',
                email='ubaldalorenzo@teste.com',
                gender_id=2,
                role_id=2,
                password=hashed_password,
                plan_id=1,
                hourly_rate=95.00, 
                phone_number='3376534237',
                image_file='image-6.jpg',
                description = descr),
        Coach(name='Emanuelle Pisano',
                email='emanuellepisano@teste.com',
                gender_id=1,
                role_id=2,
                password=hashed_password,
                plan_id=1,
                hourly_rate=70.00, 
                phone_number='3397232921',
                image_file='image-1.jpg',
                description = descr),
        Coach(name='Dora Genovese',
                email='doragenovese@teste.com',
                gender_id=2,
                role_id=2,
                password=hashed_password,
                plan_id=1,
                hourly_rate=110.00, 
                phone_number='3319944713',
                image_file='image-4.jpg',
                description = descr),
        Coach(name='Matteo Lombardi',
                email='matteolombardi@teste.com',
                gender_id=1,
                role_id=2,
                password=hashed_password,
                plan_id=1,
                hourly_rate=60.00, 
                phone_number='3701572448',
                image_file='image-3.jpg',
                description = descr),
        Coach(name='Rodrigo Napolitani',
                email='rodrigonapolitani@teste.com',
                gender_id=1,
                role_id=2,
                password=hashed_password,
                plan_id=1,
                hourly_rate=55.00, 
                phone_number='3312985355',
                image_file='image-2.jpg',
                description = descr),
        Coach(name='Berta Milano',
                email='bertamilano@teste.com',
                gender_id=2,
                role_id=2,
                password=hashed_password,
                plan_id=1,
                hourly_rate=55.00, 
                phone_number='3314317866',
                image_file='image-5.jpg',
                description = descr),
        Coach(name='Paola Longo',
                email='paolalongo@teste.com',
                gender_id=2,
                role_id=2,
                password=hashed_password,
                plan_id=1,
                hourly_rate=90.00, 
                phone_number='3336732961',
                image_file='image-6.jpg',
                description = descr)
    ]
    # Assign sports for each Coach
    coaches[0].sports.extend((sports[1], sports[8], sports[7]))
    coaches[1].sports.extend((sports[14], sports[18], sports[19]))
    coaches[2].sports.extend((sports[16], sports[13], sports[10]))
    coaches[3].sports.extend((sports[9], sports[8], sports[0]))
    coaches[4].sports.extend((sports[14], sports[13], sports[17]))
    coaches[5].sports.extend((sports[6], sports[26], sports[29]))
    coaches[6].sports.extend((sports[30], sports[32], sports[35]))
    coaches[7].sports.extend((sports[24], sports[34], sports[2]))
    coaches[8].sports.extend((sports[1], sports[36], sports[38]))
    coaches[9].sports.extend((sports[14], sports[18], sports[8]))
    coaches[10].sports.extend((sports[10], sports[3], sports[7]))
    coaches[11].sports.extend((sports[11], sports[32], sports[34]))
    coaches[12].sports.extend((sports[5], sports[4], sports[6]))
    coaches[13].sports.extend((sports[16], sports[11], sports[12]))
    coaches[14].sports.extend((sports[17], sports[27], sports[26]))
    coaches[15].sports.extend((sports[16], sports[21], sports[19]))
    coaches[16].sports.extend((sports[22], sports[23], sports[28]))
    coaches[17].sports.extend((sports[23], sports[24], sports[22]))
    coaches[18].sports.extend((sports[25], sports[29], sports[30]))
    coaches[19].sports.extend((sports[31], sports[32], sports[33]))
    coaches[20].sports.extend((sports[15], sports[20], sports[35]))
    coaches[21].sports.extend((sports[38], sports[36], sports[37]))
    coaches[22].sports.extend((sports[18], sports[27], sports[30]))
    coaches[23].sports.extend((sports[16], sports[1], sports[34]))
    coaches[24].sports.extend((sports[7], sports[21], sports[29]))
    coaches[25].sports.extend((sports[16], sports[26], sports[36]))
    coaches[26].sports.extend((sports[8], sports[10], sports[33]))
    coaches[27].sports.extend((sports[13], sports[21], sports[38]))
    coaches[28].sports.extend((sports[26], sports[28], sports[15]))
    coaches[29].sports.extend((sports[6], sports[20], sports[35]))
    print(coaches[0])
    db.session.add_all(coaches)
    db.session.commit()
    
    # Create 20 standard matches
    matches = [
        Match(title='Beach Volley with Friends',
                description=('We play every day to train for a competition '
                    'in October. If you are interested come join us!'),
                date=datetime.strptime('2022-04-02', "%Y-%m-%d").date(),
                players_maxnumber=4,
                location='CUS Torino',
                sport_id=7,
                time_period_id=3,
                user_id=1),
        Match(title='Judo Training Session!',
                description=("I'm trying to get my belt promotion so I'm "
                    "looking for people to train with!! Come join me!"),
                date=datetime.strptime('2022-04-13', "%Y-%m-%d").date(),
                players_maxnumber=6,
                location='CUS Torino',
                sport_id=17,
                time_period_id=1,
                user_id=5),
        Match(title='Soccer with the Piqué Blinders',
                description=('Hello guys, me and my team (the Piqué Blinders) '
                    'are looking for friends to play soccer. Join us!'),
                date=datetime.strptime('2022-05-01', "%Y-%m-%d").date(),
                players_maxnumber=10,
                location='Parco Valentino',
                sport_id=28,
                time_period_id=4,
                user_id=2),
        Match(title='Boxing in Torino!',
                description=('Ciao!!! Looking for a boxing partner for a '
                    'training session next week. See you in the ring!!'),
                date=datetime.strptime('2022-04-22', "%Y-%m-%d").date(),
                players_maxnumber=2,
                location='CUS Torino',
                sport_id=10,
                time_period_id=1,
                user_id=1),
        Match(title='Road to NBA!',
                description=("Do you think you can beat the Dunkin' Donuts? "
                    "Come find out!!!"),
                date=datetime.strptime('2022-05-12', "%Y-%m-%d").date(),
                players_maxnumber=10,
                location='Campi da Basket Braccini',
                sport_id=6,
                time_period_id=3,
                user_id=6),
        Match(title='Rugby team recruiting!',
                description=('Hey big guy! Come to our recruiting session '
                    'to show us your skills!!!'),
                date=datetime.strptime('2022-04-14', "%Y-%m-%d").date(),
                players_maxnumber=20,
                location='Parco Valentino',
                sport_id=26,
                time_period_id=2,
                user_id=7),
        Match(title='Sailing Event - Coconut Grove, Miami',
                description=('It is a-boat time you start learning to sail! '
                    'Come join us!!!'),
                date=datetime.strptime('2022-06-15', "%Y-%m-%d").date(),
                players_maxnumber=25,
                location='Coconut Grove',
                sport_id=27,
                time_period_id=1,
                user_id=4),
        Match(title='Volleyball with Friends',
                description=('We play every day to train for a competition '
                    'in October. If you are interested come join us!'),
                date=datetime.strptime('2022-06-02', "%Y-%m-%d").date(),
                players_maxnumber=8,
                location='LÉMAN ARCHERY',
                sport_id=1,
                time_period_id=2,
                user_id=7),
        Match(title='Archery Training Session!',
                description=("I used to be an adventurer like you, then I "
                    "took an arrow in the knee, so now I'm limited to just "
                    "practice and training"),
                date=datetime.strptime('2022-07-15', "%Y-%m-%d").date(),
                players_maxnumber=8,
                location='LÉMAN ARCHERY',
                sport_id=1,
                time_period_id=2,
                user_id=1),
        Match(title='Tennis Practice for Newbies',
                description=("Ciao ragazzi!!! I just started learning "
                    "Tennis and  I'd like to meet other beginners so we "
                    "can improve together. If you are interested, "
                    "come join me!"),
                date=datetime.strptime('2022-04-15', "%Y-%m-%d").date(),
                players_maxnumber=4,
                location='CUS Torino',
                sport_id=32,
                time_period_id=1,
                user_id=6),
        Match(title='Swimming practice this weekend',
                description='Water you doing this saturday? Come join us!',
                date=datetime.strptime('2022-04-09', "%Y-%m-%d").date(),
                players_maxnumber=15,
                location='CAP10100',
                sport_id=30,
                time_period_id=1,
                user_id=10),
        Match(title='Fencing session for fun',
                description=('Hello guys! Come join me in a Fencing '
                    'training session. Allez!!!'),
                date=datetime.strptime('2022-04-16', "%Y-%m-%d").date(),
                players_maxnumber=10,
                location='Accademia Scherma Milano',
                sport_id=13,
                time_period_id=4,
                user_id=6),
        Match(title='Weight Lifting Practice',
                description=("Do you even lift, bro?!?! Even if you don't, "
                    "come join us for a practice session!!!"),
                date=datetime.strptime('2022-04-16', "%Y-%m-%d").date(),
                players_maxnumber=4,
                location='MCFIT Politecnico',
                sport_id=38,
                time_period_id=4,
                user_id=9),
        Match(title='Badminton Competition in June!',
                description=("Hello guys! I'm trying to find a duo to join "
                    "me in a competition that will occur in June. Join me "
                    "for a training session! I know Badminton is hard, but "
                    "it is not racket science!"),
                date=datetime.strptime('2022-04-10', "%Y-%m-%d").date(),
                players_maxnumber=3,
                location='Mei Jia Badminton Stadium',
                sport_id=5,
                time_period_id=3,
                user_id=11),
        Match(title='Golf Partners',
                description=("Tee-riffic news!!! We are looking for friends "
                    "to play golf with. It doesn't matter if you are a "
                    "beginner or if you taught Tiger Woods how to hold the "
                    "putter, come join us!"),
                date=datetime.strptime('2022-05-16', "%Y-%m-%d").date(),
                players_maxnumber=8,
                location='The Los Angeles Country Club',
                sport_id=14,
                time_period_id=1,
                user_id=16),
        Match(title='Water Polo free lessons',
                description=('Hello guys, my name is Rodrigo and I used to '
                    'play professional water polo in Brazil. Come join me to '
                    'practice and to learn more about this awesome sport!'),
                date=datetime.strptime('2022-04-26', "%Y-%m-%d").date(),
                players_maxnumber=4,
                location='Raia Olímpica da USP',
                sport_id=37,
                time_period_id=3,
                user_id=11),
        Match(title='Hockey team looking for goalie',
                description=('Our hockey team is looking for a goalie for a '
                    'competitions in november. Come practice with us to test '
                    'your abilities!'),
                date=datetime.strptime('2022-04-20', "%Y-%m-%d").date(),
                players_maxnumber=12,
                location='Greenwich Field Hockey Club',
                sport_id=16,
                time_period_id=1,
                user_id=11),
        Match(title='Rowing in Pó',
                description=('We are looking for 2 people to join us in '
                    'the Winter Rowing Competition that will happen in Pó '
                    'river! Come join us for the recruiting session!'),
                date=datetime.strptime('2022-08-26', "%Y-%m-%d").date(),
                players_maxnumber=20,
                location='Parco del Valentino',
                sport_id=25,
                time_period_id=1,
                user_id=19),
        Match(title='Run to the Hills!',
                description='Road Cycling to Basilica di Superga!',
                date=datetime.strptime('2022-5-12', "%Y-%m-%d").date(),
                players_maxnumber=25,
                location='Politecnico di Torino',
                sport_id=24,
                time_period_id=1,
                user_id=13),
        Match(title='Surfing in Malibu!',
                description=("Hello guys, I recently moved to Malibu and "
                    "I'm looking for surfing partners!"),
                date=datetime.strptime('2022-04-12', "%Y-%m-%d").date(),
                players_maxnumber=4,
                location='Malibu Lagoon State Beach',
                sport_id=29,
                time_period_id=2,
                user_id=2)
    ]
    # Assign players for each Match
    matches[0].players.extend((users[1], users[2]))
    matches[1].players.extend((users[3], users[2]))
    matches[2].players.extend((users[3], users[4]))
    matches[3].players.append(users[1])
    matches[4].players.extend((users[6], users[2]))
    matches[5].players.extend((users[9], users[4]))
    matches[6].players.extend((users[14], users[12], users[10]))
    matches[7].players.extend((users[1], users[8]))
    matches[8].players.extend((users[1], users[2]))
    matches[9].players.extend((users[2], users[7]))
    matches[10].players.extend((users[6], users[2]))
    matches[11].players.extend((users[0], users[8]))
    matches[12].players.extend((users[11], users[12]))
    matches[13].players.append(users[1])
    matches[14].players.extend((users[11], users[5]))
    matches[15].players.extend((users[14], users[11]))
    matches[16].players.extend((users[11], users[12]))
    matches[17].players.extend((users[13], users[13]))
    matches[18].players.extend((users[7], users[3]))
    matches[19].players.extend((users[2], users[3]))

    db.session.add_all(matches)
    db.session.commit()

    # Create 9 standard companies
    companies = [
        User(name='UFC',
                email='ufc@teste.com',
                gender_id=3,
                role_id=3,
                password=hashed_password),
        User(name='Nike',
                email='nike@teste.com',
                gender_id=3,
                role_id=3,
                password=hashed_password),
        User(name='Adidas',
                email='adidas@teste.com',
                gender_id=3,
                role_id=3,
                password=hashed_password),
        User(name='Under Armour',
                email='underarmour@teste.com',
                gender_id=3,
                role_id=3,
                password=hashed_password),
        User(name='Puma',
                email='puma@teste.com',
                gender_id=3,
                role_id=3,
                password=hashed_password),
        User(name='Wilson',
                email='wilson@teste.com',
                gender_id=3,
                role_id=3,
                password=hashed_password),
        User(name='WWE',
                email='wwe@teste.com',
                gender_id=3,
                role_id=3,
                password=hashed_password),
        User(name='Speedo',
                email='speedo@teste.com',
                gender_id=3,
                role_id=3,
                password=hashed_password),
        User(name='Lost',
                email='lost@teste.com',
                gender_id=3,
                role_id=3,
                password=hashed_password)
    ]
    
    db.session.add_all(companies)
    db.session.commit()

    # Create 20 standard events
    ev_descr = ("This event in this date will bring recognition to every "
        "participant in a way that nobody has ever witnessed before. "
        "Young athletes will be motivated and inspired by our actions "
        "and players will begin to bring their best to every game. "
        "Come to our event and enjoy the benefits of our services.")

    events = [
        Event(title='Boxing Match',
                date=datetime.strptime('2022-04-12', "%Y-%m-%d").date(),
                price=90.00,
                attendees_maxnumber=150,
                location='Las Vegas',
                sport_id=10,
                user_id=51,
                description=ev_descr),
        Event(title='Soccer Championship',
                date=datetime.strptime('2022-04-20', "%Y-%m-%d").date(),
                price=10.00,
                attendees_maxnumber=300,
                location='Brinco de Ouro da Princesa Stadium',
                sport_id=28,
                user_id=53,
                description=ev_descr),
        Event(title='Basketball Camp',
                date=datetime.strptime('2022-05-10', "%Y-%m-%d").date(),
                price=200.00,
                attendees_maxnumber=130,
                location='New Orleans',
                sport_id=6,
                user_id=52,
                description=ev_descr),
        Event(title='Archery Competition',
                date=datetime.strptime('2022-05-12', "%Y-%m-%d").date(),
                price=40.00,
                attendees_maxnumber=75,
                location='Seoul',
                sport_id=1,
                user_id=52,
                description=ev_descr),
        Event(title='Tennis Match',
                date=datetime.strptime('2022-04-24', "%Y-%m-%d").date(),
                price=90.00,
                attendees_maxnumber=250,
                location='Miami',
                sport_id=32,
                user_id=56,
                description=ev_descr),
        Event(title='Wrestling Match',
                date=datetime.strptime('2022-04-02', "%Y-%m-%d").date(),
                price=110.00,
                attendees_maxnumber=500,
                location='Arlington',
                sport_id=39,
                user_id=57,
                description=ev_descr),
        Event(title='Swimming Competition',
                date=datetime.strptime('2022-05-20', "%Y-%m-%d").date(),
                price=50.00,
                attendees_maxnumber=300,
                location='Rio de Janeiro',
                sport_id=30,
                user_id=58,
                description=ev_descr),
        Event(title='Athletics',
                date=datetime.strptime('2022-04-2', "%Y-%m-%d").date(),
                price=100.00,
                attendees_maxnumber=1000,
                location='São Paulo',
                sport_id=4,
                user_id=54,
                description=ev_descr),
        Event(title='Soccer Match',
                date=datetime.strptime('2022-06-10', "%Y-%m-%d").date(),
                price=40.00,
                attendees_maxnumber=1500,
                location='Torino',
                sport_id=28,
                user_id=55,
                description=ev_descr),
        Event(title='Volleyball Match',
                date=datetime.strptime('2022-05-01', "%Y-%m-%d").date(),
                price=60.00,
                attendees_maxnumber=200,
                location='Paris',
                sport_id=36,
                user_id=53,
                description=ev_descr),
        Event(title='Weight Lifting Competition',
                date=datetime.strptime('2022-04-15', "%Y-%m-%d").date(),
                price=30.00,
                attendees_maxnumber=80,
                location='Oslo',
                sport_id=39,
                user_id=54,
                description=ev_descr),
        Event(title='Rugby Match',
                date=datetime.strptime('2022-07-20', "%Y-%m-%d").date(),
                price=80.00,
                attendees_maxnumber=2000,
                location='Auckland',
                sport_id=10,
                user_id=53,
                description=ev_descr),
        Event(title='Surfing Event',
                date=datetime.strptime('2022-04-07', "%Y-%m-%d").date(),
                price=70.00,
                attendees_maxnumber=700,
                location='Nazaré',
                sport_id=29,
                user_id=59,
                description=ev_descr),
        Event(title='Marathon Swimming Event',
                date=datetime.strptime('2022-04-27', "%Y-%m-%d").date(),
                price=40.00,
                attendees_maxnumber=200,
                location='Rome',
                sport_id=20,
                user_id=58,
                description=ev_descr),
        Event(title='Judo Championship',
                date=datetime.strptime('2022-08-20', "%Y-%m-%d").date(),
                price=80.00,
                attendees_maxnumber=300,
                location='Memphis',
                sport_id=17,
                user_id=52,
                description=ev_descr),
        Event(title='Golf Tour',
                date=datetime.strptime('2022-04-12', "%Y-%m-%d").date(),
                price=200.00,
                attendees_maxnumber=100,
                location='Los Angeles',
                sport_id=14,
                user_id=56,
                description=ev_descr),
        Event(title='Table Tennis Match',
                date=datetime.strptime('2022-04-12', "%Y-%m-%d").date(),
                price=30.00,
                attendees_maxnumber=170,
                location='Tokyo',
                sport_id=31,
                user_id=55,
                description=ev_descr),
        Event(title='Water Polo Match',
                date=datetime.strptime('2022-05-19', "%Y-%m-%d").date(),
                price=40.00,
                attendees_maxnumber=300,
                location='São Paulo',
                sport_id=37,
                user_id=58,
                description=ev_descr),
        Event(title='Badminton Match',
                date=datetime.strptime('2022-06-11', "%Y-%m-%d").date(),
                price=70.00,
                attendees_maxnumber=250,
                location='Bangkok',
                sport_id=5,
                user_id=56,
                description=ev_descr),
        Event(title='Beach Volley Competition',
                date=datetime.strptime('2022-07-22', "%Y-%m-%d").date(),
                price=50.00,
                attendees_maxnumber=270,
                location='Rio de Janeiro',
                sport_id=7,
                user_id=53,
                description=ev_descr)
    ]
    # Assign attendees for each Event
    events[0].attendees.extend((users[1], users[2]))
    events[1].attendees.extend((users[14], users[3], users[1], users[0]))
    events[2].attendees.extend((users[1], users[5]))
    events[3].attendees.extend((users[1], users[6], users[5]))
    events[4].attendees.extend((users[1], users[10]))
    events[5].attendees.extend((users[11], users[12]))
    events[6].attendees.extend((users[3], users[0]))
    events[7].attendees.extend((users[11], users[14]))
    events[8].attendees.extend((users[1], users[12]))
    events[9].attendees.extend((users[1], users[4], users[8], users[9]))
    events[10].attendees.extend((users[1], users[2], users[5], users[10],
                                users[11], users[14]))
    events[11].attendees.extend((users[1], users[5]))
    events[12].attendees.append(users[2])
    events[13].attendees.extend((users[1], users[9]))
    events[14].attendees.extend((users[1], users[18]))
    events[15].attendees.extend((users[1], users[3]))
    events[16].attendees.extend((users[10], users[19]))
    events[17].attendees.extend((users[13], users[15]))
    events[18].attendees.extend((users[3], users[4], users[5], users[6],
                                users[7], users[8]))

    db.session.add_all(events)
    db.session.commit()

    flash('The database was populated', 'info')
    return redirect(url_for('main.index'))