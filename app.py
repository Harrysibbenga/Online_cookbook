import os
from flask import Flask, render_template, redirect, request, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "some_secret"
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
users = mongo.db.users

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
    country_input = request.form.get('country_name')

## ----- Queries -------
    allergin_q = {'allergins': allergin_input}
    author_q = {'author': author_input}
    category_q = {'category': category_input}
    cuisine_q = {'cuisine': cuisine_input}
    diet_q = {'diet': diet_input}
    origin_q = {'origin': origin_input}
    type_q = {'type': type_input}
    country_q = {'country': country_input}
    
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
    
    elif country_input != None:
        found_authors = authors.find(country_q)
        for author in found_authors:
            recipe = recipes.find({'author': author['name']})
        return render_template('recipes.html', recipes=recipe, authors=authors.find(), allergins=allergins.find(), 
        types=types.find(), countries=countries.find(), cuisines=cuisines.find(), 
        diets=diets.find(), origins=origins.find(), categories=categories.find())
        


@app.route('/view_recipe/<recipe_id>/<username>')
def view_recipe(recipe_id, username):
    the_recipe =  recipes.find_one({"_id": ObjectId(recipe_id)})
    if username == "no_user":
        return render_template('viewrecipe.html', recipe=the_recipe)
    elif username == "Admin" or username == the_recipe['user']:
        return render_template('viewrecipeowner.html', recipe=the_recipe)
    else:
        return render_template('viewrecipe.html', recipe=the_recipe)
        


@app.route('/save_recipe/<recipe_id>/<username>')
def save_recipe(recipe_id, username):
    if username == "no_user":
        return redirect(url_for('login', recipe_id=recipe_id))
    else:
        recipes.update({'_id': ObjectId(recipe_id) }, {'$inc': {'votes': 1 }})
        user = users.find_one({'username': username})
        users.update({'_id': user['_id']}, {'$addToSet': {"saved_recipes": ObjectId(recipe_id)}})
        return redirect(url_for("saved_recipes", username=username, recipe_id=recipe_id))
            


@app.route('/saved_recipes/<recipe_id>/<username>')
def saved_recipes(recipe_id, username):
    if username == "no_user" and recipe_id == "no_id":
        return redirect(url_for('login', recipe_id=recipe_id))
    else:
        user = users.find_one({'username': username})
        recipes_saved = []
        rs = recipes.find()
        for r in rs:
            if r['_id'] in user['saved_recipes']:
                recipes_saved.append(r)
        return render_template("savedrecipes.html", recipes=recipes_saved)
        

@app.route('/view_recipes/<recipe_id>/<username>')
def view_recipes(recipe_id, username):
    if username == "no_user" and recipe_id == "no_id":
        return redirect(url_for('login', recipe_id=recipe_id))
    else:
        recipes_saved = []
        rs = recipes.find()
        for r in rs:
            if r['user'] == username:
                recipes_saved.append(r)
        return render_template("viewrecipes.html", recipes=recipes_saved)
            
            

@app.route('/login/<recipe_id>', methods=['GET','POST'])
def login(recipe_id):
    if request.method == "POST":
        username_input = request.form.get('username')
        password_input = request.form.get('password')
        user = users.find_one({'username': username_input, 'password': password_input})
        if user:
           session['username'] = username_input
           if recipe_id == 'no_id':
               return redirect(url_for('saved_recipes', recipe_id=recipe_id, username=session['username']))
           elif recipe_id == 'home':
               return redirect(url_for("get_recipes"))
           else:
               return redirect(url_for("save_recipe", recipe_id=recipe_id, username=session['username']))
    else:
        return render_template("login.html", recipe_id=recipe_id)
        
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/register')
def register():
    return render_template("register.html")
    
    

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True)