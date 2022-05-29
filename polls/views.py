from django.http import HttpRequest
from django.shortcuts import render,HttpResponse,redirect, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User,Group
from . forms import UserRegisterForm, ReviewForm
from . models import Movie,Ratings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import requests
from math import ceil
import pandas as pd
from collections import Counter
import re
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import process
import json


TMDB_API_KEY='49f04b1c5c4d75918aba0813f529ccc5'

# Create your views here.
x=[]

def movie_details(request,movie_id):
    data = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US")
    return render(request, "movie_details.html", {
        "m": data.json(),
        "type": "movie",
    })
    

def results(request):
    #Content based filtering using cosine similarity

    #Load the data
    query=request.GET.get('q')
    movie_ob=Movie.objects.all().values()
    movie=pd.DataFrame(movie_ob)

    '''Data Cleaning and Exploration
    1. To remove | in genres and form a list of genres for each movies
    2. Extracting the year from the title name and creating a separate column'''

    #1.
    movie['genres'] = movie['genres'].apply(lambda x: x.split("|"))
    for i in movie['genres']:
        i[-1]=i[-1][:-1]
    #print(movie['genres'])
    #print(movie.head())
    genres_counts = Counter(g for genres in movie['genres'] for g in genres)
    print(f"There are {len(genres_counts)} genre labels.")
    #print(genres_counts)
    movie = movie[movie['genres']!='(no genres listed)']
    del genres_counts['(no genres listed)']
    print("The 5 most common genres: \n", genres_counts.most_common(5))
    
    #2.
    def extract_year_from_title(title):
        t = title.split(' ')
        year = None
        if re.search(r'\(\d+\)', t[-2]):
            year = t[-2].strip('()')
            #print(year)
            year = int(year)
        return year
    movie['year'] = movie['title'].apply(extract_year_from_title)
    #print(movie.head())
    #print(movie['year'].nunique())
    print(f"Original number of movies: {movie['id'].nunique()}")
    movies = movie[~movie['year'].isnull()]
    print(f"Number of movies after removing null years: {movie['id'].nunique()}")

    # To get the decade of the year
    def round_down(year):
        return year - (year%10)
    movie['decade'] = movie['year'].apply(round_down)
    #print(movie.head())
    genres = list(genres_counts.keys())


    #Transforming the data
    #Rows represent movies and columns represent genres and decades
    for g in genres:
        movie[g] = movie['genres'].transform(lambda x: int(g in x))
    #print(movie[genres].head())

    

    movie_decades = pd.get_dummies(movie['decade'])
    #print(movie_decades.head())

    movie_features = pd.concat([movie[genres], movie_decades], axis=1)
    #print(movie_features.head())

    #Recommending using cosine similarity
    cosine_sim = cosine_similarity(movie_features, movie_features)
    print(f"Dimensions of our movie features cosine similarity matrix: {cosine_sim.shape}")

    if query:
        '''process is imported from fuzzywuzzy which allows us to use a string 
            matching algorithm to make it more user friendly by finding a movie 
            title closest to the user's input'''
        def movie_finder(title):
            all_titles = movie['title'].tolist()
            closest_match = process.extractOne(title,all_titles)
            return closest_match[0]
        #title = movie_finder('juminji')
        #print(title)
        movie_idx = dict(zip(movie['title'], list(movie.index)))
        #idx = movie_idx[title]
        #print(idx)

        def get_content_based_recommendations(title_string, n_recommendations=10):
            title = movie_finder(title_string)
            idx = movie_idx[title]
            sim_scores = list(enumerate(cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[0:(n_recommendations+1)]
            similar_movies = [i[0] for i in sim_scores]
            print(f"Recommendations for {title}:")
            return movie['title'].iloc[similar_movies]
        mov_series=get_content_based_recommendations(query)
        recommended_movies=pd.DataFrame(mov_series)
        recommended_list= recommended_movies['title'].to_list()

        #Acquiring the movie ID of the recommended movies
        list_index=[]
        for i in recommended_list:
            list_index.append(movie_idx[i])
        print(list_index)

        #Mapping with the movie ID with the TMDB ID
        links_db=pd.read_csv("./links with database index.csv")
        tmdb=dict(zip(links_db['movieId_db'],links_db['tmdbId']))

        tmdb_api=[]
        for i in list_index:
            tmdb_api.append(tmdb[i+1])

        
        #Obtaining the movie details using TMDB API
        movie_searched=requests.get(f"https://api.themoviedb.org/3/movie/{tmdb_api[0]}?api_key={TMDB_API_KEY}&language=en-US")
        y=movie_searched.json()
        tmdb_api=tmdb_api[1:]
        for i in tmdb_api:
            data=requests.get(f"https://api.themoviedb.org/3/movie/{i}?api_key={TMDB_API_KEY}&language=en-US")
            x.append(data.json())
    else:
        return HttpResponse("Please enter a search query")
    
    return render(request, 'search_results.html',{"searched_movie":y,"data": x})

#Search bar
def new_user(request):
    return render(request, 'new_user.html')

#Home page
def index(request):
    return render(request, 'index.html')

#Sign Up page
def signup(request):
    if not request.user.is_authenticated:
        if request.method=='POST':
            form=UserRegisterForm(request.POST)
            if form.is_valid():
                form.save()
                username=form.cleaned_data.get('username')
                messages.success(request,f'Hi {username} your account was created successfully')
                return redirect('/SignIn')
        else:
            form=UserRegisterForm()
        return render(request, 'SignUp.html',{'form': form})
    else:
        return HttpResponseRedirect('/SignIn')

#Profile page
@login_required()
def profile(request):
    return render(request, 'profile.html')


def explicit_recommend(u):
    #Item to item based collaborative recommendation

    #Loading the dataset(from kaggle) having ratings given by the user.
    rate_merged=pd.read_csv("./ratings_with_db.csv")
    #print(rate_merged)

    #Preprocessing
    rate=rate_merged.drop(['genres','timestamp'],axis=1)
    #print(rate.shape)
    #print(rate.head())
    userRatings = rate.pivot_table(index=['userId'],columns=['title'],values='rating')
    #print(userRatings.head())

    #Correlation matrix 
    corrMatrix = userRatings.corr(method='pearson')
    #print(corrMatrix.head(100))  

    def get_similar(movie_name,rating):
        similar_ratings = corrMatrix[movie_name]*(rating-2.5)
        similar_ratings = similar_ratings.sort_values(ascending=False)
        return similar_ratings

    #All the ratings given by a particular user i.e., filter based on user ID is obtained and is used to for recommendation
    rating_ob=Ratings.objects.filter(user=u).values()
    #print(rating_ob)

    rate=[]
    # A tuple ('title','rating') is appended to the list 'rate'
    for dic in rating_ob:
        m=dic['movie_id']
        movie_ob=Movie.objects.filter(pk=m).values()
        t=movie_ob[0]['title']
        r=dic['rating']
        rate.append((t,r))
    #print(rate)


    similar_movies = pd.DataFrame()
    for movie,rating in rate:
        similar_movies = similar_movies.append(get_similar(movie,rating),ignore_index = True)
    #similar_movies.head(10)


    recommended_movies=[]
    x=similar_movies.sum().sort_values(ascending=False).head(20).to_dict()
    for title,rating in x.items():
        recommended_movies.append(title)

    recommended_ids=[]
    for i in recommended_movies:
        recommended_movie_dict=Movie.objects.filter(title=i).values()
        recommended_ids.append(recommended_movie_dict[0]['id'])
    
    links_db=pd.read_csv("./links with database index.csv")
    tmdb=dict(zip(links_db['movieId_db'],links_db['tmdbId']))

    tmdb_api=[]
    for j in recommended_ids:
        tmdb_api.append(tmdb[j])
    
    return tmdb_api

    


def submit_review(request, movie_id):
    url = request.META.get('HTTP_REFERER')
    links_db=pd.read_csv("./links with database index.csv")
    id_db=dict(zip(links_db['tmdbId'],links_db['movieId_db']))
    movie_db=id_db[movie_id]
    #print(movie)
    #movie = Movie.objects.get(id=movie)
	#user = request.user
    if request.user.is_authenticated: 
        #A user must be logged in to rate a movie
        if request.method=='POST':
            user=request.user
            movieid=movie_db
            movie=Movie.objects.all()
            u=User.objects.get(pk=user.id)
            m=Movie.objects.get(pk=movieid)
            rfm=ReviewForm(request.POST)
            if rfm.is_valid():
                rat=rfm.cleaned_data['rating']
                sub=rfm.cleaned_data['subject']
                rew=rfm.cleaned_data['review']
                count=Ratings.objects.filter(user=u,movie=m).count()
                if(count>0):
                    #A user cannot rate a movie more than once
                    messages.warning(request,'You have already submitted your review!!')
                    return redirect(url)
                
                action=Ratings(user=u,movie=m,subject=sub,review=rew,rating=rat)
                action.save()
                messages.success(request,'You have submitted'+' '+str(rat)+' '+"star")
                recommended_tmdb_api=explicit_recommend(u)
                z=[]
                for i in recommended_tmdb_api:
                    data=requests.get(f"https://api.themoviedb.org/3/movie/{i}?api_key={TMDB_API_KEY}&language=en-US")
                    z.append(data.json())
                #print(z)
                return render(request,"rating.html",{"data":z})
            else:
                #To debug the errors in the form(if any)
                print(rfm.errors.as_data())
        else:
            rfm=ReviewForm()
            movie=Movie.objects.all()
            return redirect(url)
    else:
        return HttpResponseRedirect('/SignIn/')

    
#Ratings page
def rating(request,movie_id):
    return render(request, 'rating.html', {"movie_id":movie_id})






