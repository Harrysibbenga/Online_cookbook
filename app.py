import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'online_cookbook'
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')

mongo = PyMongo(app)

## ------- collections --------

allergins = mongo.db.allergins 
authors = mongo.db.authors
categories=mongo.db.categories
cuisines = mongo.db.cuisines
countries = mongo.db.countries
diets = mongo.db.diets
origins=mongo.db.origins
recipes = mongo.db.recipes
types=mongo.db.types

## ------- routes -------

@app.route('/')
@app.route('/get_recipes')
def get_recipes():
    '''
        gets the collections from MongoDB Atlas and renders them on the recipes.html page
    '''
    return render_template('recipes.html', recipes=recipes.find(), 
    authors=authors.find(), allergins=allergins.find(), types=types.find(),
    countries=countries.find(), cuisines=cuisines.find(), diets=diets.find(),
    origins=origins.find(), categories=categories.find())
    
@app.route('/search_recipes', methods=['POST'])
def search_recipes():
    user_input = request.form['recipe_name']
    recipes.create_index([('name', 'text')])
    return render_template('recipes.html', recipes=recipes.find({'$text': {'$search': user_input}}))

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True)