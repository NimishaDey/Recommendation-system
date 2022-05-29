# Recommendation-system

## Installation

```bash
  pip install django
  pip install django-crispy-forms
  pip install scikit-learn
  pip install pandas
  pip install fuzzywuzzy
  pip install requests
  pip install pillow
```

    
## Tech Stack

Django, Python, HTML, CSS, Javascript


## Features

- User can Sign Up or Sign In
- User can search for movies and it recommends based on the title searched(This solves the cold start problem)
- User can go through movie details obtained using TMDB API
- User can give ratings to movies and it recommends based on the ratings


## Algorithm

- Content Based Filtering: Implemented using cosine similarity
- Collaborative Filtering: Implemented by using the ratings given by the user
## Run Locally

Clone the project 

Go to the project directory

Install dependencies mentioned under Installations

Run the following commands
```bash
  python manage.py makemigrations
  python manage.py migrate
```

Start the server

```bash
  python manage.py runserver
```
Go to your browser and copy this http://127.0.0.1:8000/




## Login Credentials

- Admin

Username: admin

Password: admin123

- Test user

Username: test

Password: t29052022
## API key

Create an account in https://www.themoviedb.org/, click on the API link from the left hand sidebar in your account settings and fill all the details to apply for API key. 
