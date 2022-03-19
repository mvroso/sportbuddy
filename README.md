# sportsbuddy

Sports Buddy is a prototype website for the Information Systems (02PDWPH) course with Professor Demartini.
MSc in Engineering and Management at Politecnico di Torino.

The following students were involved in the project:
Corbella Elio					s296315
Liu Guo Alexandre				s293909
Nigro Matheo Lucas				s293949
Nodrini Barbara					s292001
Roso D'Elboux Marcus Vinicius	s293692
Vasconcelos Araujo Gabriela		s293948

Mr. Roso D'Elboux was responsible for developing the website and he used the following technologies:
- Python
- Flask
- MySQL
- HTML5/CSS/JS

The template used for the front-end layout can be accessed here:
https://bootstrapmade.com/flattern-multipurpose-bootstrap-template/

Instructions for download and use:
- Setup a virtual environment (venv) in the project folder
- Install python 3 and mysql
- Install the modules in requirements.txt with 'pip install -r requirements.txt' in the command line
- Create a .env file in the root of the project
- Populate the .env file with environment variables (follow env_example.txt)
- Run the file create_db.py to create the databases in mysql
- Run the file run.py to start the flask app
- If you are running it for the first time, choose between these routes
	> Navigate to http://127.0.0.1:5000/insertdata/necessary if you want to insert only necessary data
	> Navigate to http://127.0.0.1:5000/insertdata if you want to insert necessary and dummy data for testing purposes
- Enjoy the experience :)