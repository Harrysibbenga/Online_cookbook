# Online Cookbook

## UX

## Features

## Technology Used

## Testing

Did a manual test to see if the database results displayed on the recipes page.

Did some manual test on the recipes search box to see if the recipes with the typed name show on the cards. 

Did some manual test on the ingredients search box to see if the recipes with the typed ingredient show on the cards. 
Had to make sure the ingredient names entered were capitalized as they are in the database.

Used Text index's to to support text search queries on string content for searching recipes by name. 

Queryed the ingresdients array to search for the data with the specific user input value.

Filter search
* To take the filter to the next level would be to filter and only find results that match both or all queries selected but i 
found this difficult unless i used text indexing which i had used on the recipe search but found it hard to implement on other searches at the same time.
* filter search lookes for any recipes that have the chosen fields and displays them.
* test was done manually to make sure that what ever was filtered through displayed. 

Selected recipe pages
* The testing done on these pages was to make sure that when the user isnt logged on or the logged on username
dosent match the recipe username or Admin, then the user can only view the information of the recipes plus click 
on the favorite button. This was done manually by changing the username in the url from no user to Admin or Test and 
seeing which page rendered for that recipe.
* Admins and recipe creators can view the recipe, favroite it, edit and delete the recipe and its properties.  
* Manual tests where done to make sure that once the favorite button is clicked then the user should be able to
view the recipe on the saved recipe page and get redirected to this page to view all their saved recipes. Also 
if a user isnt logged on then they will be redirected to the login page to log on/register.
* Manual testing was done to make sure that when the favorite button is clicked the recipe votes increments by one
also if the recipe is already saved then it doesnt get added on to the saved recipes page again.

## Deployment

* [Online Cookbook](https://online-cookbook-hs.herokuapp.com/)


## Credits

* [Title page background image](https://www.shutterstock.com/image-photo/kitchen-cooking-utensils-ceramic-storage-pot-327210395?src=w9EwWJ6WlsWUoHoxjA7O-g-1-1)
* [Eggs and Toast](https://image.shutterstock.com/image-photo/sandwich-avocado-fried-egg-on-450w-346094294.jpg)
