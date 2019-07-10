import os
from flask import Flask, render_template, redirect, request, url_for, session, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import json
from bson import json_util
from bson.json_util import dumps

app = Flask(__name__)
app.secret_key = "some_secret"
app.config['MONGO_DBNAME'] = 'online_cookbook'
app.config['MONGO_URI'] = 'mongodb+srv://Admin:0nline_cookbook@myfirstcluster-33ilg.mongodb.net/online_cookbook?retryWrites=true'
mongo = PyMongo(app)

## ------- collections --------

allergens = mongo.db.allergins 
authors = mongo.db.authors
categories = mongo.db.categories
cuisines = mongo.db.cuisines
countries = mongo.db.countries
diets = mongo.db.diets
origins = mongo.db.origins
recipes = mongo.db.recipes
types = mongo.db.types
users = mongo.db.users
ingredients = mongo.db.ingredients
units = mongo.db.units

## ------- functions -------

def find_user(user_input, coll):
    """
        Used to look through a collection to verify that the username is in there and to return the user
    """
    for user in coll:
        if user['username'] == user_input:
            user = users.find_one({"username": user_input})
            return user

def limit_array(arr, offset, limit):
    """
        Used to limit amount of items in an array
    """
    if offset or limit:
        if limit is not None:
            limit = offset + limit        
    else:
        limit = len(arr)
        arr = arr[offset:limit]
    return arr

def pagination_function(recipe):
        recipe.find()
        p_limit = int(request.args['limit'])
        p_offset = int(request.args['offset'])
        if p_offset < 0:
            p_offset = 0
        num_results = recipe.count()
        if p_offset >= num_results:
            p_offset = num_results
        all_recipes = recipe.limit(p_limit).skip(p_offset)
        args = {
            "p_limit" : p_limit,
            "p_offset" : p_offset,
            "num_results" : num_results,
            "next_url" : "/search_recipes?limit=%s&offset=%s"%(p_limit, p_offset+p_limit),
            "prev_url" : "/search_recipes?limit=%s&offset=%s"%(p_limit, p_offset-p_limit),
            "recipes" : all_recipes
        }
        return args
            
## ------- routes -------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_recipes')
def get_recipes():
    """
        Gets the collections from MongoDB Atlas and renders them on the recipes.html page
    """
    p_limit = int(request.args['limit'])
    p_offset = int(request.args['offset'])
    if p_offset < 0:
        p_offset = 0
    num_results = recipes.find().count()
    if p_offset >= num_results:
        p_offset = num_results
    all_recipes = recipes.find().limit(p_limit).skip(p_offset)
    args = {
        "p_limit" : p_limit,
        "p_offset" : p_offset,
        "num_results" : num_results,
        "next_url" : "/get_recipes?limit=%s&offset=%s"%(p_limit, p_offset+p_limit),
        "prev_url" : "/get_recipes?limit=%s&offset=%s"%(p_limit, p_offset-p_limit),
        "recipes" : all_recipes
    }
    return render_template('recipes.html', authors=authors.find(), allergens=allergens.find(), types=types.find(),
    countries=countries.find(), cuisines=cuisines.find(), diets=diets.find(),
    origins=origins.find(), categories=categories.find(), args=args)

@app.route('/search_recipes', methods=['GET', 'POST'])
def search_recipes():
    """
        Creates an index of each recipe name and uses that index to search for recipes with similar names
    """
    user_input = request.form['recipe_name']
    print(user_input)
    if user_input == '':
        return redirect(url_for('get_recipes', limit=2, offset=0))
    else:
        recipes.create_index([('name', 'text')])
        recipe = recipes.find({'$text': {'$search': user_input}})
        p_limit = int(request.args['limit'])
        p_offset = int(request.args['offset'])
        if p_offset < 0:
            p_offset = 0
        num_results = recipe.count()
        if p_offset >= num_results:
            p_offset = num_results
        all_recipes = recipe.limit(p_limit).skip(p_offset)
        args = {
            "p_limit" : p_limit,
            "p_offset" : p_offset,
            "num_results" : num_results,
            "next_url" : "/search_recipes?limit=%s&offset=%s"%(p_limit, p_offset+p_limit),
            "prev_url" : "/search_recipes?limit=%s&offset=%s"%(p_limit, p_offset-p_limit),
            "recipes" : all_recipes
        }
        return render_template('recipes.html', authors=authors.find(), allergens=allergens.find(), types=types.find(),
        countries=countries.find(), cuisines=cuisines.find(), diets=diets.find(),
        origins=origins.find(), categories=categories.find(), args=args)

@app.route('/search_ingredients', methods=['POST'])
def search_ingredients():
    """
        Uses queries to search the database for matching ingredient names and displays those recipes found.
    """
    ingredient_input = request.form['ingredient_name']
    if ingredient_input == '':
        return redirect(url_for('get_recipes', limit=2, offset=0))
    else: 
        recipe = recipes.find({'ingredients': {"$elemMatch": {'name': ingredient_input.capitalize()}}})
        p_limit = int(request.args['limit'])
        p_offset = int(request.args['offset'])
        if p_offset < 0:
            p_offset = 0
        num_results = recipe.count()
        if p_offset >= num_results:
            p_offset = num_results
        all_recipes = recipe.limit(p_limit).skip(p_offset)
        args = {
            "p_limit" : p_limit,
            "p_offset" : p_offset,
            "num_results" : num_results,
            "next_url" : "/search_recipes?limit=%s&offset=%s"%(p_limit, p_offset+p_limit),
            "prev_url" : "/search_recipes?limit=%s&offset=%s"%(p_limit, p_offset-p_limit),
            "recipes" : all_recipes
        }
        return render_template('recipes.html',args=args, 
        authors=authors.find(), allergens=allergens.find(), types=types.find(),
        countries=countries.find(), cuisines=cuisines.find(), diets=diets.find(),
        origins=origins.find(), categories=categories.find())

@app.route('/filter_search', methods=['GET','POST'])
def filter_search():
    """
        Filters the search depending on what inputs have values and displays all the matching recipes. 
    """
    ## ----- Inputs ------    
    allergin_input = request.form.get('allergin_name')
    author_input = request.form.get('author_name')
    type_input = request.form.get('type_name')
    cuisine_input = request.form.get('cuisine_name')
    diet_input = request.form.get('diet_name')
    origin_input = request.form.get('origin_name')
    category_input = request.form.get('category_name')
    country_input = request.form.get('country_name')
    ## ----- Queries -------
    allergen_q = {'allergens': allergin_input}
    author_q = {'author': author_input}
    category_q = {'category': category_input}
    cuisine_q = {'cuisine': cuisine_input}
    diet_q = {'diet': diet_input}
    origin_q = {'origin': origin_input}
    type_q = {'type': type_input}
    country_q = {'country': country_input}

    if allergin_input != None:
        recipe = recipes.find(allergen_q)
        p_limit = int(request.args['limit'])
        p_offset = int(request.args['offset'])
        if p_offset < 0:
            p_offset = 0
        num_results = recipe.count()
        if p_offset >= num_results:
            p_offset = num_results
        all_recipes = recipe.limit(p_limit).skip(p_offset)
        args = {
            "p_limit" : p_limit,
            "p_offset" : p_offset,
            "num_results" : num_results,
            "next_url" : "/filter_search?limit=%s&offset=%s"%(p_limit, p_offset+p_limit),
            "prev_url" : "/filter_search?limit=%s&offset=%s"%(p_limit, p_offset-p_limit),
            "recipes" : all_recipes
        }
        return render_template('recipes.html', recipes=recipe, authors=authors.find(), allergens=allergens.find(), 
        types=types.find(), countries=countries.find(), cuisines=cuisines.find(), 
        diets=diets.find(), origins=origins.find(), categories=categories.find(), args=args)
    
    elif author_input != None:
        recipe = recipes.find(author_q)
        p_limit = int(request.args['limit'])
        p_offset = int(request.args['offset'])
        if p_offset < 0:
            p_offset = 0
        num_results = recipe.count()
        if p_offset >= num_results:
            p_offset = num_results
        all_recipes = recipe.limit(p_limit).skip(p_offset)
        args = {
            "p_limit" : p_limit,
            "p_offset" : p_offset,
            "num_results" : num_results,
            "next_url" : "/filter_search?limit=%s&offset=%s"%(p_limit, p_offset+p_limit),
            "prev_url" : "/filter_search?limit=%s&offset=%s"%(p_limit, p_offset-p_limit),
            "recipes" : all_recipes
        }
        return render_template('recipes.html', recipes=recipe, authors=authors.find(), allergens=allergens.find(), 
        types=types.find(), countries=countries.find(), cuisines=cuisines.find(), 
        diets=diets.find(), origins=origins.find(), categories=categories.find(), args=args)
    
    elif category_input != None:
        recipe = recipes.find(category_q)
        p_limit = int(request.args['limit'])
        p_offset = int(request.args['offset'])
        if p_offset < 0:
            p_offset = 0
        num_results = recipe.count()
        if p_offset >= num_results:
            p_offset = num_results
        all_recipes = recipe.limit(p_limit).skip(p_offset)
        args = {
            "p_limit" : p_limit,
            "p_offset" : p_offset,
            "num_results" : num_results,
            "next_url" : "/filter_search?limit=%s&offset=%s"%(p_limit, p_offset+p_limit),
            "prev_url" : "/filter_search?limit=%s&offset=%s"%(p_limit, p_offset-p_limit),
            "recipes" : all_recipes
        }
        return render_template('recipes.html', recipes=recipe, authors=authors.find(), allergens=allergens.find(), 
        types=types.find(), countries=countries.find(), cuisines=cuisines.find(), 
        diets=diets.find(), origins=origins.find(), categories=categories.find(), args=args)
    
    elif cuisine_input != None:
        recipe = recipes.find(cuisine_q)
        p_limit = int(request.args['limit'])
        p_offset = int(request.args['offset'])
        if p_offset < 0:
            p_offset = 0
        num_results = recipe.count()
        if p_offset >= num_results:
            p_offset = num_results
        all_recipes = recipe.limit(p_limit).skip(p_offset)
        args = {
            "p_limit" : p_limit,
            "p_offset" : p_offset,
            "num_results" : num_results,
            "next_url" : "/filter_search?limit=%s&offset=%s"%(p_limit, p_offset+p_limit),
            "prev_url" : "/filter_search?limit=%s&offset=%s"%(p_limit, p_offset-p_limit),
            "recipes" : all_recipes
        }
        return render_template('recipes.html', recipes=recipe, authors=authors.find(), allergens=allergens.find(), 
        types=types.find(), countries=countries.find(), cuisines=cuisines.find(), 
        diets=diets.find(), origins=origins.find(), categories=categories.find(), args=args)
    
    elif diet_input != None:
        recipe = recipes.find(diet_q)
        p_limit = int(request.args['limit'])
        p_offset = int(request.args['offset'])
        if p_offset < 0:
            p_offset = 0
        num_results = recipe.count()
        if p_offset >= num_results:
            p_offset = num_results
        all_recipes = recipe.limit(p_limit).skip(p_offset)
        args = {
            "p_limit" : p_limit,
            "p_offset" : p_offset,
            "num_results" : num_results,
            "next_url" : "/filter_search?limit=%s&offset=%s"%(p_limit, p_offset+p_limit),
            "prev_url" : "/filter_search?limit=%s&offset=%s"%(p_limit, p_offset-p_limit),
            "recipes" : all_recipes
        }
        return render_template('recipes.html', recipes=recipe, authors=authors.find(), allergens=allergens.find(), 
        types=types.find(), countries=countries.find(), cuisines=cuisines.find(), 
        diets=diets.find(), origins=origins.find(), categories=categories.find(), args=args)
    
    elif origin_input != None:
        recipe = recipes.find(origin_q)
        p_limit = int(request.args['limit'])
        p_offset = int(request.args['offset'])
        if p_offset < 0:
            p_offset = 0
        num_results = recipe.count()
        if p_offset >= num_results:
            p_offset = num_results
        all_recipes = recipe.limit(p_limit).skip(p_offset)
        args = {
            "p_limit" : p_limit,
            "p_offset" : p_offset,
            "num_results" : num_results,
            "next_url" : "/filter_search?limit=%s&offset=%s"%(p_limit, p_offset+p_limit),
            "prev_url" : "/filter_search?limit=%s&offset=%s"%(p_limit, p_offset-p_limit),
            "recipes" : all_recipes
        }
        return render_template('recipes.html', recipes=recipe, authors=authors.find(), allergens=allergens.find(), 
        types=types.find(), countries=countries.find(), cuisines=cuisines.find(), 
        diets=diets.find(), origins=origins.find(), categories=categories.find(), args=args)
    
    elif type_input != None:
        recipe = recipes.find(type_q)
        p_limit = int(request.args['limit'])
        p_offset = int(request.args['offset'])
        if p_offset < 0:
            p_offset = 0
        num_results = recipe.count()
        if p_offset >= num_results:
            p_offset = num_results
        all_recipes = recipe.limit(p_limit).skip(p_offset)
        args = {
            "p_limit" : p_limit,
            "p_offset" : p_offset,
            "num_results" : num_results,
            "next_url" : "/filter_search?limit=%s&offset=%s"%(p_limit, p_offset+p_limit),
            "prev_url" : "/filter_search?limit=%s&offset=%s"%(p_limit, p_offset-p_limit),
            "recipes" : all_recipes
        }
        return render_template('recipes.html', recipes=recipe, authors=authors.find(), allergens=allergens.find(), 
        types=types.find(), countries=countries.find(), cuisines=cuisines.find(), 
        diets=diets.find(), origins=origins.find(), categories=categories.find(), args=args)
    
    elif country_input != None:
        found_authors = authors.find(country_q)
        for author in found_authors:
            recipe = recipes.find({'author': author['name']})
            p_limit = int(request.args['limit'])
            p_offset = int(request.args['offset'])
            if p_offset < 0:
                p_offset = 0
            num_results = recipe.count()
            if p_offset >= num_results:
                p_offset = num_results
            all_recipes = recipe.limit(p_limit).skip(p_offset)
            args = {
                "p_limit" : p_limit,
                "p_offset" : p_offset,
                "num_results" : num_results,
                "next_url" : "/filter_search?limit=%s&offset=%s"%(p_limit, p_offset+p_limit),
                "prev_url" : "/filter_search?limit=%s&offset=%s"%(p_limit, p_offset-p_limit),
                "recipes" : all_recipes
            }
        return render_template('recipes.html', recipes=recipe, authors=authors.find(), allergens=allergens.find(), 
        types=types.find(), countries=countries.find(), cuisines=cuisines.find(), 
        diets=diets.find(), origins=origins.find(), categories=categories.find(), args=args)
        
@app.route('/view_recipe/<recipe_id>/<username>')
def view_recipe(recipe_id, username):
    """
        View of the recipe clicked from the menu page, if no user is present they can view the recipe however if 
        a user is logged on depending on whether they are the owner/Admin they have a different view of the recipe.
    """
    the_recipe =  recipes.find_one({"_id": ObjectId(recipe_id)})
    allergens_saved = []
    all_allergens = allergens.find()
    for allergen in all_allergens:
        if allergen['_id'] in the_recipe['allergens']:
            allergens_saved.append(allergen)
    if username == "no_user":
        return render_template('viewrecipe.html', recipe=the_recipe, recipe_allergens=allergens_saved)
    elif username == "Admin" or username == the_recipe['user']:
        return render_template('viewrecipeowner.html',recipe=the_recipe, recipe_id=recipe_id ,username=username, 
        authors=authors.find(), allergens=allergens.find(), types=types.find(), cuisines=cuisines.find(), diets=diets.find(), 
        origins=origins.find(), categories=categories.find(), ingredients=ingredients.find(), units=units.find(), recipe_allergens=allergens_saved)
    else:
        return render_template('viewrecipe.html', recipe=the_recipe, recipe_id=recipe_id, username=username, recipe_allergens=allergens_saved)

@app.route('/save_recipe/<recipe_id>/<username>/')
def save_recipe(recipe_id, username):
    """
        When a user clicks the favorite/save button the user saves it to thier saved recipes page and gives the recipe an upvote
        however if the user isnt logged on then the user is redirected to login. 
    """
    if username == "no_user":
        return redirect(url_for('login', page_id='no_id'))
    else:
        recipes.update({'_id': ObjectId(recipe_id) }, {'$inc': {'votes': 1 }})
        user = users.find_one({'username': username})
        users.update({'_id': user['_id']}, {'$addToSet': {"saved_recipes": ObjectId(recipe_id)}})
        message = "Recipe saved to favorites"
        the_recipe =  recipes.find_one({"_id": ObjectId(recipe_id)})
        if username == "Admin" or username == the_recipe['user']:
            return render_template('viewrecipeowner.html', recipe=the_recipe, message=message, authors=authors.find(), 
            allergens=allergens.find(), types=types.find(), cuisines=cuisines.find(), diets=diets.find(), origins=origins.find(), 
            categories=categories.find())
        else:
            return render_template('viewrecipe.html', recipe=the_recipe, message=message )

@app.route('/saved_recipes/<page_id>/<username>')
def saved_recipes(page_id, username):
    """
        User redirected to the login page if they aren't logged in however if they are then they can view thier saved recipes
    """
    if username == "no_user" and page_id == "saved_recipes":
        return redirect(url_for('login', page_id=page_id))
    else:
        user = users.find_one({'username': username})
        all_recipes = recipes.find()
        recipes_saved = []
        for recipe in all_recipes:
            if recipe['_id'] in user['saved_recipes']:
                recipes_saved.append(recipe)
        p_limit = int(request.args['limit'])
        p_offset = int(request.args['offset'])
        if p_offset < 0:
            p_offset = 0
        num_results = recipes.find().count()
        if p_offset > num_results:
            p_offset = num_results
        saved_recipes = limit_array(recipes_saved, p_limit, p_offset)
        print(saved_recipes)
        args = {
            "p_limit" : p_limit,
            "p_offset" : p_offset,
            "num_results" : num_results,
            "next_url" : "../saved_recipes/%s?limit=%s&offset=%s"%(username, p_limit, p_offset+p_limit),
            "prev_url" : "../saved_recipes/%s?limit=%s&offset=%s"%(username, p_limit, p_offset-p_limit),
            "recipes" : saved_recipes
        }
        return render_template("savedrecipes.html", args=args)

@app.route('/view_recipes/<page_id>/<username>')
def view_recipes(page_id, username):
    """
        User redirected to the login page if they aren't logged in however if they are then they can view thier created recipes
    """
    if username == "no_user" and page_id == "view":
        return redirect(url_for('login', page_id=page_id))
    else:
        recipes_created = []
        all_recipes = recipes.find()
        for recipe in all_recipes:
            if recipe['user'] == username:
                recipes_created.append(recipe)
        p_limit = int(request.args['limit'])
        p_offset = int(request.args['offset'])
        if p_offset < 0:
            p_offset = 0
        num_results = recipes.find().count()
        if p_offset > num_results:
            p_offset = num_results
        saved_recipes = limit_array(recipes_created, p_limit, p_offset)
        print(saved_recipes)
        args = {
            "p_limit" : p_limit,
            "p_offset" : p_offset,
            "num_results" : num_results,
            "next_url" : "../view/%s?limit=%s&offset=%s"%(username,p_limit, p_offset+p_limit),
            "prev_url" : "../view/%s?limit=%s&offset=%s"%(username,p_limit, p_offset-p_limit),
            "recipes" : saved_recipes
        }
        return render_template("viewrecipes.html", args=args)

@app.route('/edit_recipe/<recipe_id>/<username>')
def edit_recipe(recipe_id, username):
    """
        View used to redirect the user to the edit recipe page for the purpose of updating the recipe later.
    """
    the_recipe = recipes.find_one({'_id': ObjectId(recipe_id)})
    return render_template("editrecipe.html", recipe_id=recipe_id, recipe=the_recipe, username=username, authors=authors.find(), 
    types=types.find(), cuisines=cuisines.find(), diets=diets.find(), 
    origins=origins.find(), categories=categories.find())

@app.route('/update_recipe/<recipe_id>/<username>', methods=['GET','POST'])
def update_recipe(recipe_id, username):
    """
        Updates the recipe on the database and redirects to the recipe page. 
    """
    recipes.update_one( {'_id': ObjectId(recipe_id)}, {'$set':
        {
            'name':request.form.get('name'),
            'description':request.form.get('description'),
            'prep_time': request.form.get('prep_time'),
            'cooking_time': request.form.get('cooking_time'),
            'servings':request.form.get('servings'),
            'category': request.form.get('category'),
            'diet': request.form.get('diet'),
            'cuisine':request.form.get('cuisine'),
            'type': request.form.get('type'),
            'author': request.form.get('author'),
            'origin':request.form.get('origin'),
            'image_url':request.form.get('image_url')
        }})
    return redirect(url_for('view_recipe', recipe_id=recipe_id, username=username))

@app.route('/add_recipe/<page_id>/<username>')
def add_recipe(page_id, username):
    """
        If User isnt logged in they are redirected to the login page, otherwise the user will be redirected to the add recipe page.
    """
    if username == "no_user" and page_id == "add_recipe":
        return redirect(url_for('login', page_id=page_id))
    else:
        return render_template('addrecipe.html', username=username, authors=authors.find(), types=types.find(), 
        cuisines=cuisines.find(), diets=diets.find(), origins=origins.find(), categories=categories.find())

@app.route('/create_recipe/<username>', methods=['GET','POST'])
def create_recipe(username):
    """
        Creates a recipe with basic information in the database and redirects to the recipe page using the new id created. 
    """
    recipes.insert_one(
    {
        'name':request.form.get('name'),
        'description':request.form.get('description'),
        'prep_time': request.form.get('prep_time'),
        'cooking_time': request.form.get('cooking_time'),
        'servings':request.form.get('servings'),
        'category': request.form.get('category'),
        'diet': request.form.get('diet'),
        'cuisine':request.form.get('cuisine'),
        'type': request.form.get('type'),
        'author': request.form.get('author'),
        'origin':request.form.get('origin'),
        'image_url':request.form.get('image_url'),
        'allergens':[],
        'user': username
    })
    
    new_recipe = recipes.find_one({
        'name':request.form.get('name'),
        'description':request.form.get('description'),
        'prep_time': request.form.get('prep_time'),
        'cooking_time': request.form.get('cooking_time'),
    })
    
    return redirect(url_for('view_recipe', recipe_id=new_recipe['_id'], username=username))

@app.route('/add_allergen/<recipe_id>/<username>', methods=['GET','POST'])
def add_allergen(recipe_id, username):
    """
        Adds an allergen to the recipe and checks if an input is present if not then it returns an error message. 
    """
    user_input =  request.form.get('allergens')
    if user_input == None or user_input == '':
        message = "Cannot be blank"
        recipe = recipes.find_one({'_id': ObjectId(recipe_id)})
        return render_template("viewrecipeowner.html", recipe_id=recipe_id, username=username, allergin_message=message, 
        recipe=recipe, authors=authors.find(), allergens=allergens.find(), 
        types=types.find(), cuisines=cuisines.find(), diets=diets.find(), origins=origins.find(), categories=categories.find())
    else:
        all_allergens = allergens.find()
        for allergen in all_allergens:
            if user_input == allergen['name']:
                recipes.update_one( {'_id': ObjectId(recipe_id)}, {'$addToSet':
                    {
                        'allergens': allergen['_id']
                    }})
        return redirect(url_for("view_recipe", recipe_id=recipe_id, username=username))

@app.route('/add_ingredient/<recipe_id>/<username>', methods=['GET','POST'])
def add_ingredient(recipe_id, username):
    """
        Adds an ingredient to the recipe and checks if an input is present if not then it returns an error message. 
    """
    user_input = request.form.get('ingredients')
    amount = request.form.get('amount')
    unit = request.form.get('unit')
    if user_input == None or user_input == '':
        message = "Cannot be blank"
        recipe = recipes.find_one({'_id': ObjectId(recipe_id)})
        return render_template("viewrecipeowner.html", recipe_id=recipe_id, username=username, ingredient_message=message, 
        recipe=recipe, authors=authors.find(), allergens=allergens.find(), types=types.find(), cuisines=cuisines.find(), 
        diets=diets.find(), origins=origins.find(), categories=categories.find(), ingredients=ingredients.find(), units=units.find())
    else:
        all_ingredients = ingredients.find()
        for ingredient in all_ingredients:
            if user_input == ingredient['name']:
                if unit == '' or unit == None:
                    recipes.update_one( {'_id': ObjectId(recipe_id)}, {'$addToSet':
                        {
                            'ingredients':
                            {
                                'name': ingredient['name'], 
                                'image': ingredient['image'], 
                                'amount': amount
                            }
                        }})
                else:
                    recipes.update_one( {'_id': ObjectId(recipe_id)}, {'$addToSet':
                        {
                            'ingredients':
                            {
                                'name': ingredient['name'], 
                                'image': ingredient['image'], 
                                'amount': amount, 
                                'unit': unit
                            }
                        }})
    return redirect(url_for("view_recipe", recipe_id=recipe_id, username=username))

@app.route('/add_instruction/<recipe_id>/<username>', methods=['POST'])
def add_instruction(recipe_id, username):
    """
        Adds an instruction to the recipe and checks if an input is present if not then it returns an error message. 
    """
    if request.form.get('instruction') == None or request.form.get('instruction') == '':
        message = "Cannot be blank"
        recipe = recipes.find_one({'_id': ObjectId(recipe_id)})
        return render_template("viewrecipeowner.html", recipe_id=recipe_id, username=username, instruction_message=message, 
        recipe=recipe, authors=authors.find(), allergens=allergens.find(), types=types.find(), cuisines=cuisines.find(), 
        diets=diets.find(), origins=origins.find(), categories=categories.find())
    else:
        recipes.update_one( {'_id': ObjectId(recipe_id)}, {'$addToSet':
            {
                'instructions':request.form.get('instruction')
            }})
    return redirect(url_for("view_recipe", recipe_id=recipe_id, username=username))

@app.route('/delete_recipe/<recipe_id>/<username>')
def delete_recipe(recipe_id, username):
    """
        Deletes the entire recipe from the database.
    """
    recipes.delete_one({'_id': ObjectId(recipe_id)})
    return redirect(url_for('get_recipes'))

@app.route('/delete_allergen/<recipe_id>/<username>/<recipe_allergen>')
def delete_allergen(recipe_id, username, recipe_allergen):
    """
        Delete any allergen using its value and update the database. 
    """
    recipes.update_one({'_id': ObjectId(recipe_id)}, {'$pull': { 'allergens': ObjectId(recipe_allergen)}})
    return redirect(url_for('view_recipe', recipe_id=recipe_id, username=username))

@app.route('/delete_instruction/<recipe_id>/<username>/<recipe_instruction>')
def delete_instruction(recipe_id, username, recipe_instruction):
    """
        Delete any instruction using its value and update the databse. 
    """
    recipes.update_one({'_id': ObjectId(recipe_id)}, {'$pull': { 'instructions': recipe_instruction}})
    return redirect(url_for('view_recipe', recipe_id=recipe_id, username=username))

@app.route('/delete_ingredient/<recipe_id>/<username>/<recipe_ingredient>')
def delete_ingredient(recipe_id, username, recipe_ingredient):
    """
        Delete any ingredient using its value and update the database. 
    """
    recipes.update_one({'_id': ObjectId(recipe_id)}, {'$pull': { 'ingredients': {'name': recipe_ingredient}}})
    return redirect(url_for('view_recipe', recipe_id=recipe_id, username=username))

@app.route('/manage_categories/<page_id>/<username>')
def manage_categories(page_id, username):
    """
        View the manage categories page and if user isnt logged in then they're redirected tthe login page. 
    """
    if username == "no_user" and page_id == "manage_categories":
        return redirect(url_for('login', page_id=page_id))
    else:
        return render_template('managecategories.html', page_id=page_id, username=username, authors=authors.find(), 
        allergens=allergens.find(), types=types.find(), countries=countries.find(), countries_=countries.find(), cuisines=cuisines.find(), 
        diets=diets.find(), origins=origins.find(), categories=categories.find(), ingredients=ingredients.find(), units=units.find())
        
@app.route('/edit_category/<username>/<category_id>', methods=['GET','POST'])
def edit_category(username, category_id):
    """
        Edit any category using category_id and update the database. 
    """
    country = countries.find_one({'_id': ObjectId(category_id)})
    cuisine = cuisines.find_one({'_id': ObjectId(category_id)})
    category = categories.find_one({'_id': ObjectId(category_id)})
    diet = diets.find_one({'_id': ObjectId(category_id)})
    origin = origins.find_one({'_id': ObjectId(category_id)})
    type_of_food = types.find_one({'_id': ObjectId(category_id)})
    
    if country:
        countries.update_one(
            {
                '_id': ObjectId(category_id)}, 
                {'$set': { 'name': request.form.get('country')}
            })
        return redirect(url_for('manage_categories', username=username, category_id=category_id, page_id="manage_categories"))

@app.route('/add_category/<category>/<username>/<page_id>', methods=['GET', 'POST'])
def add_category(page_id, category, username):
    """
        Add any category using the value of the category and update the database. 
        If no value is entered then user is prompted with a message.
    """
    allergen = request.form.get('allergen')
    allergen_image = request.form.get('allergen_image')
    author = request.form.get('author')
    author_country = request.form.get('author_country')
    ingredient = request.form.get('ingredient').capitalize()
    ingredient_image = request.form.get('ingredient_image')
    
    if category == "allergen":
        if allergen == None or allergen == '':
            message = "Allergen name can't be empty"
            return redirect(url_for('manage_categories', username=username, page_id=page_id, allergen_error=message))
        elif allergen_image == None or allergen_image == '':
            message = "Allergen image can't be empty"
            return redirect(url_for('manage_categories', username=username, page_id=page_id, allergen_error=message))
        else:
            allergens.insert_one(
                {
                    'name': allergen, 
                    'image':allergen_image
                })
            return redirect(url_for('manage_categories', username=username, page_id=page_id))
    
    elif category == "author":
        if author_country == None or author_country == '':
            message = "Country name can't be empty"
            return redirect(url_for('manage_categories', username=username, page_id=page_id, author_country_error=message))
        elif author == None or author =='':
            message = "Author name can't be empty"
            return redirect(url_for('manage_categories', username=username, page_id=page_id, author_name_error=message))
        else:
            authors.insert_one(
                {
                    'name': author,
                    'country': author_country
                })
        return redirect(url_for('manage_categories', username=username, page_id=page_id))
    
    elif category == "country":
        if request.form.get('country') == None or request.form.get('country') == '':
            message = "Country name can't be empty"
            return redirect(url_for('manage_categories', username=username, page_id=page_id, country_error=message))
        else:
            countries.insert_one({'name': request.form.get('country')})
            return redirect(url_for('manage_categories', username=username, page_id=page_id))
    
    elif category == "cuisine":
        if request.form.get('cuisine') == None or request.form.get('cuisine') == '':
            message = "Cuisine name can't be empty"
            return redirect(url_for('manage_categories', username=username, page_id=page_id, cuisine_error=message))
        else:
            cuisines.insert_one({'name': request.form.get('cuisine')})
            return redirect(url_for('manage_categories', username=username, page_id=page_id))
            
    elif category == "category":
        if request.form.get('category') == None or request.form.get('category') == '':
            message = "Category name can't be empty"
            return redirect(url_for('manage_categories', username=username, page_id=page_id, category_error=message))
        else:
            categories.insert_one({'name': request.form.get('category')})
            return redirect(url_for('manage_categories', username=username, page_id=page_id))
        
    elif category == "diet":
        if request.form.get('diet') == None or request.form.get('diet') == '':
            message = "Diet name can't be empty"
            return redirect(url_for('manage_categories', username=username, page_id=page_id, diet_error=message))
        else:
            diets.insert_one({'name': request.form.get('diet')})
            return redirect(url_for('manage_categories', username=username, page_id=page_id))
    elif category == "ingredient":
        if ingredient == None or ingredient == '':
            message = "Ingredient name can't be empty"
            return redirect(url_for('manage_categories', username=username, page_id=page_id, ingredient_error=message))
        elif ingredient_image == None or ingredient_image == '':
            message = "Ingredient image can't be empty"
            return redirect(url_for('manage_categories', username=username, page_id=page_id, ingredient_error=message))
        else:
            ingredients.insert_one({'name': ingredient, 'image':ingredient_image})
            return redirect(url_for('manage_categories', username=username, page_id=page_id))
    elif category == "origin":
        if request.form.get('origin') == None or request.form.get('origin') == '':
            message = "Origin name can't be empty"
            return redirect(url_for('manage_categories', username=username, page_id=page_id, origin_error=message))
        else:
            origins.insert_one({'name': request.form.get('origin')})
            return redirect(url_for('manage_categories', username=username, page_id=page_id))
    
    elif category == "type":
        if request.form.get('type') == None or request.form.get('type') == '':
            message = "Type name can't be empty"
            return redirect(url_for('manage_categories', username=username, page_id=page_id, type_error=message))
        else:
            types.insert_one({'name': request.form.get('type')})
            return redirect(url_for('manage_categories', username=username, page_id=page_id))
    
    elif category == "units":
        if request.form.get('units') == None or request.form.get('units') == '':
            message = "Unit name can't be empty"
            return redirect(url_for('manage_categories', username=username, page_id=page_id, units_error=message))
        else:
            units.insert_one({'name': request.form.get('units')})
            return redirect(url_for('manage_categories', username=username, page_id=page_id))

@app.route('/delete_category/<category_id>/<username>/<page_id>')
def delete_category(page_id, category_id, username):
    """
        Delete any category using category_id and update the database. 
    """
    
    allergen = allergens.find_one({'_id': ObjectId(category_id)})
    author = authors.find_one({'_id': ObjectId(category_id)})
    country = countries.find_one({'_id': ObjectId(category_id)})
    cuisine = cuisines.find_one({'_id': ObjectId(category_id)})
    category = categories.find_one({'_id': ObjectId(category_id)})
    diet = diets.find_one({'_id': ObjectId(category_id)})
    origin = origins.find_one({'_id': ObjectId(category_id)})
    type_of_food = types.find_one({'_id': ObjectId(category_id)})
    ingredient = ingredients.find_one({'_id': ObjectId(category_id)})
    unit = units.find_one({'_id': ObjectId(category_id)})
    
    if allergen:
        allergens.delete_one({'_id': ObjectId(category_id)})
        return redirect(url_for('manage_categories', username=username, page_id=page_id))
    elif author:
        authors.delete_one({'_id': ObjectId(category_id)})
        return redirect(url_for('manage_categories', username=username, page_id=page_id))
    elif country:
        countries.delete_one({'_id': ObjectId(category_id)})
        return redirect(url_for('manage_categories', username=username, page_id=page_id))
    elif cuisine:
        cuisines.delete_one({'_id': ObjectId(category_id)})
        return redirect(url_for('manage_categories', username=username, page_id=page_id))
    elif category:
        categories.delete_one({'_id': ObjectId(category_id)})
        return redirect(url_for('manage_categories', username=username, page_id=page_id))
    elif diet:
        diets.delete_one({'_id': ObjectId(category_id)})
        return redirect(url_for('manage_categories', username=username, page_id=page_id))
    elif origin:
        origins.delete_one({'_id': ObjectId(category_id)})
        return redirect(url_for('manage_categories', username=username, page_id=page_id))
    elif type_of_food:
        types.delete_one({'_id': ObjectId(category_id)})
        return redirect(url_for('manage_categories', username=username, page_id=page_id))
    elif ingredient:
        ingredients.delete_one({'_id': ObjectId(category_id)})
        return redirect(url_for('manage_categories', username=username, page_id=page_id))
    elif unit:
        units.delete_one({'_id': ObjectId(category_id)})
        return redirect(url_for('manage_categories', username=username, page_id=page_id))

@app.route('/login/<page_id>', methods=['GET','POST'])
def login(page_id):
    """
        Checks username and password input to make sure they match values on the databsae if not promts user with 
        messages if user dosen't exist/password is wrong. 
        Redirects to pages based on page_id value. 
    """
    if request.method == "POST":
        username_input = request.form.get('username')
        password_input = request.form.get('password')
        all_users = users.find()
        user = find_user(username_input, all_users)
        if user == None:
            message = "User dosen't exist"
            return render_template("login.html", page_id=page_id, message=message)
        elif user['password'] == password_input:
            session['username'] = username_input
            if page_id == 'saved_recipes':
                return redirect(url_for('saved_recipes', page_id=page_id, username=session['username'], limit=6, offset=0))
            elif page_id == 'view':
                return redirect(url_for('view_recipes', page_id=page_id, username=session['username'], limit=6, offset=0))
            elif page_id == 'manage_categories':
                return redirect(url_for('manage_categories', page_id=page_id, username=session['username']))
            elif page_id == 'home':
                return redirect(url_for("get_recipes", limit=6, offset=0))
            elif page_id == 'add_recipe':
                return redirect(url_for('add_recipe', page_id=page_id, username=session['username']))
            else:
                return redirect(url_for("save_recipe", page_id=page_id, username=session['username']))
        else:
            message = "Incorrect password"
            return render_template("login.html", page_id=page_id, message=message)
    else:
        return render_template("login.html", page_id=page_id)

@app.route('/logout')
def logout():
    """
        Removes session user once they logout
    """
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET','POST'])
def register():
    """
        Registers user and checks if user exists or if passwords mismatch, prompts user when account has been created. 
    """
    if request.method == "POST":
        username_input = request.form.get('username')
        password_input = request.form.get('password')
        confirmation = request.form.get('confirm_password')
        user = users.find_one({'username': username_input})
        if user:
            message = "User already exists"
            return render_template('register.html', message=message)
        elif password_input == confirmation:
            users.insert_one({'username': username_input, 'password': password_input, 'saved_recipes': []})
            message = "User created please login"
            return render_template('register.html', message=message)
        else:
            message = "Password mismatch"
            return render_template('register.html', message=message)
    else:
        return render_template("register.html")
    
@app.route('/dashboard')
def dashboard():
    """
        Renders the dashboard page.
    """
    return render_template('dashboard.html')

@app.route("/onlinecookbook/recipes")
def onlinecookbook_recipes():
    """
        Used to get the values of all the recipes for later use to display them using d3.js/dc.js
    """
    all_recipes = recipes.find()
    json_recipes = []
    for recipe in all_recipes:
        json_recipes.append(recipe)
    json_recipes = json.dumps(json_recipes, default=json_util.default)
    return json_recipes

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)