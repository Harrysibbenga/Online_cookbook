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
types = mongo.db.types

## ------- routes -------

@app.route('/')
def index():
    return render_template('index.html')
    
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
    return render_template('recipes.html', recipes=recipes.find({'$text': {'$search': user_input}}),
    authors=authors.find(), allergins=allergins.find(), types=types.find(),
    countries=countries.find(), cuisines=cuisines.find(), diets=diets.find(),
    origins=origins.find(), categories=categories.find())
    
@app.route('/search_ingredients', methods=['POST'])
def search_ingredients():
    ingredient_input = request.form['ingredient_name']
    return render_template('recipes.html', recipes=recipes.find({'ingredients': ingredient_input.capitalize()}), 
    authors=authors.find(), allergins=allergins.find(), types=types.find(),
    countries=countries.find(), cuisines=cuisines.find(), diets=diets.find(),
    origins=origins.find(), categories=categories.find())
    
@app.route('/filter_search', methods=['POST'])
def filter_search():
## ----- Inputs ------    
    allergin_input = request.form.get('allergin_name')
    author_input = request.form.get('author_name')
    type_input = request.form.get('type_name')
    cuisine_input = request.form.get('cuisine_name')
    diet_input = request.form.get('diet_name')
    origin_input = request.form.get('origin_name')
    category_input = request.form.get('category_name')

## ----- Queries -------
    allergin_q = {'allergins': allergin_input}
    author_q = {'author': author_input}
    category_q = {'category': category_input}
    cuisine_q = {'cuisine': cuisine_input}
    diet_q = {'diet': diet_input}
    origin_q = {'origin': origin_input}
    type_q = {'type': type_input}
    
    if allergin_input != None:
        recipe = recipes.find(allergin_q)
        return render_template('recipes.html', recipes=recipe, authors=authors.find(), allergins=allergins.find(), 
        types=types.find(), countries=countries.find(), cuisines=cuisines.find(), 
        diets=diets.find(), origins=origins.find(), categories=categories.find())
    
    elif author_input != None:
        recipe = recipes.find(author_q)
        return render_template('recipes.html', recipes=recipe, authors=authors.find(), allergins=allergins.find(), 
        types=types.find(), countries=countries.find(), cuisines=cuisines.find(), 
        diets=diets.find(), origins=origins.find(), categories=categories.find())
    
    elif category_input != None:
        recipe = recipes.find(category_q)
        return render_template('recipes.html', recipes=recipe, authors=authors.find(), allergins=allergins.find(), 
        types=types.find(), countries=countries.find(), cuisines=cuisines.find(), 
        diets=diets.find(), origins=origins.find(), categories=categories.find())
    
    elif cuisine_input != None:
        recipe = recipes.find(cuisine_q)
        return render_template('recipes.html', recipes=recipe, authors=authors.find(), allergins=allergins.find(), 
        types=types.find(), countries=countries.find(), cuisines=cuisines.find(), 
        diets=diets.find(), origins=origins.find(), categories=categories.find())
    
    elif diet_input != None:
        recipe = recipes.find(diet_q)
        return render_template('recipes.html', recipes=recipe, authors=authors.find(), allergins=allergins.find(), 
        types=types.find(), countries=countries.find(), cuisines=cuisines.find(), 
        diets=diets.find(), origins=origins.find(), categories=categories.find())
    
    elif origin_input != None:
        recipe = recipes.find(origin_q)
        return render_template('recipes.html', recipes=recipe, authors=authors.find(), allergins=allergins.find(), 
        types=types.find(), countries=countries.find(), cuisines=cuisines.find(), 
        diets=diets.find(), origins=origins.find(), categories=categories.find())
    
    elif type_input != None:
        recipe = recipes.find(type_q)
        return render_template('recipes.html', recipes=recipe, authors=authors.find(), allergins=allergins.find(), 
        types=types.find(), countries=countries.find(), cuisines=cuisines.find(), 
        diets=diets.find(), origins=origins.find(), categories=categories.find())

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True)