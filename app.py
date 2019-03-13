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

## ------- functions -------

def find_user(user_input, coll):
    """
    Used to look through a collection to verify that the username is in there and to return the user
    """
    for user in coll:
        if user['username'] == user_input:
            user = users.find_one({"username": user_input})
            return user
        

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
    """
    
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
        return render_template('viewrecipeowner.html', recipe=the_recipe, recipe_id=recipe_id, username=username, authors=authors.find(), 
        allergins=allergins.find(), types=types.find(), cuisines=cuisines.find(), diets=diets.find(), origins=origins.find(), 
        categories=categories.find())
    else:
        return render_template('viewrecipe.html', recipe=the_recipe, recipe_id=recipe_id, username=username)
        


@app.route('/save_recipe/<recipe_id>/<username>/')
def save_recipe(recipe_id, username):
    if username == "no_user":
        return redirect(url_for('login', recipe_id=recipe_id))
    else:
        recipes.update({'_id': ObjectId(recipe_id) }, {'$inc': {'votes': 1 }})
        user = users.find_one({'username': username})
        users.update({'_id': user['_id']}, {'$addToSet': {"saved_recipes": ObjectId(recipe_id)}})
        message = "Recipe saved to favorites"
        the_recipe =  recipes.find_one({"_id": ObjectId(recipe_id)})
        if username == "Admin" or username == the_recipe['user']:
            return render_template('viewrecipeowner.html', recipe=the_recipe, message=message, authors=authors.find(), 
            allergins=allergins.find(), types=types.find(), cuisines=cuisines.find(), diets=diets.find(), origins=origins.find(), 
            categories=categories.find())
        else:
            return render_template('viewrecipe.html', recipe=the_recipe, message=message )
            


@app.route('/saved_recipes/<recipe_id>/<username>')
def saved_recipes(recipe_id, username):
    if username == "no_user" and recipe_id == "no_id":
        return redirect(url_for('login', recipe_id=recipe_id))
    else:
        user = users.find_one({'username': username})
        all_recipes = recipes.find()
        recipes_saved = []
        for recipe in all_recipes:
            if recipe['_id'] in user['saved_recipes']:
                recipes_saved.append(recipe)
        return render_template("savedrecipes.html", recipes=recipes_saved)
        


@app.route('/view_recipes/<recipe_id>/<username>')
def view_recipes(recipe_id, username):
    if username == "no_user" and recipe_id == "no_id":
        return redirect(url_for('login', recipe_id=recipe_id))
    else:
        recipes_created = []
        all_recipes = recipes.find()
        for recipe in all_recipes:
            if recipe['user'] == username:
                recipes_created.append(recipe)
        return render_template("viewrecipes.html", recipes=recipes_created)



@app.route('/edit_recipe/<recipe_id>/<username>')
def edit_recipe(recipe_id, username):
    the_recipe = recipes.find_one({'_id': ObjectId(recipe_id)})
    return render_template("editrecipe.html", recipe_id=recipe_id, recipe=the_recipe, username=username, authors=authors.find(), 
    types=types.find(), cuisines=cuisines.find(), diets=diets.find(), 
    origins=origins.find(), categories=categories.find())



@app.route('/update_recipe/<recipe_id>/<username>', methods=['POST'])
def update_recipe(recipe_id, username):
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
    


@app.route('/add_recipe/<recipe_id>/<username>')
def add_recipe(recipe_id, username):
    if username == "no_user" and recipe_id == "add_recipe":
        return redirect(url_for('login', recipe_id=recipe_id))
    else:
        return render_template('addrecipe.html', username=username, authors=authors.find(), types=types.find(), 
        cuisines=cuisines.find(), diets=diets.find(), origins=origins.find(), categories=categories.find())



@app.route('/create_recipe/<username>', methods=['POST'])
def create_recipe(username):
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
        'user': username
    })
    
    new_recipe = recipes.find_one({
        'name':request.form.get('name'),
        'description':request.form.get('description'),
        'prep_time': request.form.get('prep_time'),
        'cooking_time': request.form.get('cooking_time'),
    })
    
    return redirect(url_for('view_recipe', recipe_id=new_recipe['_id'], username=username))



@app.route('/add_allergin/<recipe_id>/<username>', methods=['POST'])
def add_allergin(recipe_id, username):
    recipes.update_one( {'_id': ObjectId(recipe_id)}, {'$addToSet':
        {
            'allergins':request.form.get('allergin')
        }})
    return redirect(url_for("view_recipe", recipe_id=recipe_id, username=username))



@app.route('/add_ingredient/<recipe_id>/<username>', methods=['POST'])
def add_ingredient(recipe_id, username):
    if request.form.get('ingredient') == '':
        message = "Cannot be blank"
        recipe = recipes.find_one({'_id': ObjectId(recipe_id)})
        return render_template("viewrecipeowner.html", recipe_id=recipe_id, username=username, ingredient_message=message, 
        recipe=recipe, authors=authors.find(), allergins=allergins.find(), types=types.find(), cuisines=cuisines.find(), 
        diets=diets.find(), origins=origins.find(), categories=categories.find())
    else:
        recipes.update_one( {'_id': ObjectId(recipe_id)}, {'$addToSet':
            {
                'ingredients':request.form.get('ingredient').capitalize()
            }})
    return redirect(url_for("view_recipe", recipe_id=recipe_id, username=username))
        


@app.route('/add_instruction/<recipe_id>/<username>', methods=['POST'])
def add_instruction(recipe_id, username):
    if request.form.get('instruction') == '':
        message = "Cannot be blank"
        recipe = recipes.find_one({'_id': ObjectId(recipe_id)})
        return render_template("viewrecipeowner.html", recipe_id=recipe_id, username=username, instruction_message=message, 
        recipe=recipe, authors=authors.find(), allergins=allergins.find(), types=types.find(), cuisines=cuisines.find(), 
        diets=diets.find(), origins=origins.find(), categories=categories.find())
    else:
        recipes.update_one( {'_id': ObjectId(recipe_id)}, {'$addToSet':
            {
                'instructions':request.form.get('instruction')
            }})
    return redirect(url_for("view_recipe", recipe_id=recipe_id, username=username))



@app.route('/delete_recipe/<recipe_id>/<username>')
def delete_recipe(recipe_id, username):
    recipes.delete_one({'_id': ObjectId(recipe_id)})
    return redirect(url_for('get_recipes'))

@app.route('/login/<recipe_id>', methods=['GET','POST'])
def login(recipe_id):
    if request.method == "POST":
        username_input = request.form.get('username')
        password_input = request.form.get('password')
        all_users = users.find()
        user = find_user(username_input, all_users)
        if user == None:
            message = "User dosen't exist"
            return render_template("login.html", recipe_id=recipe_id, message=message)
        elif user['password'] == password_input:
            session['username'] = username_input
            if recipe_id == 'no_id':
                return redirect(url_for('saved_recipes', recipe_id=recipe_id, username=session['username']))
            elif recipe_id == 'home':
                return redirect(url_for("get_recipes"))
            elif recipe_id == 'add_recipe':
                return redirect(url_for('add_recipe', recipe_id=recipe_id, username=session['username']))
            else:
                return redirect(url_for("save_recipe", recipe_id=recipe_id, username=session['username']))
        else:
            message = "Incorrect password"
            return render_template("login.html", recipe_id=recipe_id, message=message)
    else:
        return render_template("login.html", recipe_id=recipe_id)
        
        

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))



@app.route('/register', methods=['POST'])
def register():
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
    


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True)