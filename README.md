# Nutshell
Want to skip candies and other sweets but still enjoy snacking? Buy organic dried fruits online for healthy
snacking. For nut enthusiasts, Nutshell is the finest site to buy nuts online. Discover nutritious snacks
for adults as well as healthy snacks for children.

![image of the site](./static/media/am-i-responsive.png)
# Table of contents
* [Design](#design)
    - [Wireframes](#design)
    - [Database schema](#database-schema)
    - [Color scheme](#color-scheme)
* [UX](#ux)
    - [Site-Goals](#site-goals)
    - [The site's ideal user](#the-site's-ideal-user)
* [Agile Development](#agile-development)
    - [Epics](#epics)
    - [User Stories](#user-stories)
    - [Scope](#scope)
* [Features](#features)
* [Testing](#testing)
    - [Bugs](#bugs)
    - [Unsolved bugs](#unsolved-bugs)
    - [Validator Testing](#validator-testing)
    - [Manual Tests](#manual-tests)
* [Deployment](#deployment)
    - [Heroku](#heroku)
    - [Clone the repository](#clone-the-repository)
* [Credits](#credits)


# Design

## Wireframes
Some additional elements that are not apparent on the wireframes were incorporated during the site's development, so the wireframes differ slightly from the actual website.

![image of home page wireframe](./static/media/home-page-wireframe.png)
![image of about page wireframe](./static/media/product-page-wireframe.png)
![image of contact page wireframe](./static/media/shopping-bag-page-wireframe.png)
![image of reservation page wireframe](./static/images/checkout-page-wireframe.png)

## Database schema
Several custom models were created for the development of the site. First of all, in order for the customers to book reservations, a reservations model was created which had tables and user as foreign keys. A table model was then created to link it up with the reservation model. For the menu app two models were created, one for the dishes (Dish) and one for the drinks (Drink). Furthermore a allergens model was created that had a ManyToMany relationship with the dish model.
![image of the database schema](./static/media/images/database-schema.png)

## Color scheme
The color scheme was carefully designed and chosen to ensure that the site has a great color contrast. Furthermore, when selecting colors, the fact that the restaurant is a Middle Eastern restaurant was taken into account in order to provide users with a Middle Eastern vibe and environment.
![image of the color schema](./static/media/images/color-scheme.png)

# UX
## Site-Goals
The site's goal is to allow external users to book one or more guests for a meal in the restaurant on a specific date and time. External users can also manage their reservations on the website. The site also seeks to provide restaurant owners with the option to manage their restaurant bookings system as well as their menu presented on the website.

## The site's ideal user
- The ideal user is a food lover who wants to taste new foods from various cultures. 
- Someone who enjoys Middle Eastern cuisines.
- An Afghan who wishes to experience their homeland in Sweden.

# Agile Development
Agile Methodology was used to create the website. Github was used for agile project planning for this project. The issues on Github were used to build user stories and label them to ensure that the sites' fundamental requirements were met. The user stories defined the issue's aim and included an acceptance criteria section to identify the functionality that marked the user story as complete. The 24 user stories were then organized into 5 epics. Following that, a kanban board with four separate columns was made using github projects. The columns were no status, to do, in progress, and done.

### Epics
- Website's foundations
- Menu
- Admin site control
- Reservation functionality
- Authentication

### User Stories
- Website's foundations:
    * As a user I can easily navigate through the site so that I can access different parts.
    * As a user I feel welcomed by the home page and so that I know that I get attracted to book a reservation.
    * As a user I can use the footer so that I can access the site’s social media.
    * As a user I can send a contact form so that I can send feedback or any other question to the restaurant staff.
    * As a user I can read about the restaurant so that I can get to know what kind of restaurang it is.
    
- Menu:
    * As a User I can click on a menu item so that I can read the full description of it.
    * As a User I can view a list of menu items so that I can select one to order.
    * As a User I can view allergy icons on menu items so that I can avoid menu items that I am allergic to.
    * As a UserI can view the name, picture and description of every menu item so that I can learn about the menu item.
    * As a User I can view nutrition information of every menu item so that I can learn more about the menu item

- Admin site control
    * As a Site Admin I can create, read, update and delete drinks and food so that I can manage my restaurant’s menu
    * As a Site Admin I can approve/disapprove reservations so that I can manage my restaurant’s bookings.
    * As a Site Admin I can login to my account so that I can access and manage the website's backend.
    * As a Site Admin I can view filter options on the database tables so that I can filter them as desired.
    * As a logged in Site Admin I can navigate to the admin page from the navbar so that I can easily access the site’s backend.

- Reservation functionality
    * As a logged in User I can view my bookings so that I can see the status of all my bookings.
    * As a logged in User I can send a reservation request so that i can visit the restaurant if the reservation is approved.
    * As a logged in User I can create, read, update and delete reservations so that I can manage my bookings.
    * As a logged in User I can choose the amount of guests I want to reserve a table for so that I can determine the number of guests.
    * As a logged in User I can submit the reservations form with pre populated details so that I can quickly submit the form.

- Authentication
    * As a User I can login or register an account so that I can book a reservation.
    * As a logged in User I can edit my account information so that I can make sure that my details are correct.
    * As a User I can choose to register an account with my facebook, gmail or twitter account so that I can comfortably create an account.
    * As a User I can choose to save my account login details so that I can efficiently login every time I visit the site.

### Scope
* Reponsive Design.
* Date/Time-based bookings.
* Booking Cancellations.
* Restricted role based features.
* Menu page with food and drinks section.
* Landing page with information about the restaurant.
* Social account login possability.

# Features
- Navigation bar
    * This section includes the logo of the site and a responsive navigation bar with a hamburger menu for smaller screens. This header is present in all of the site’s pages.
    * The nav bar allows users to easily navigate from one section to another and it is responsive for mobile screens with the navigation links turning into a hamburger menu.
    * For logged in users a link to their ‘My Reservations’ page is added and for a logged in admin user a link to the admin page is added.<br>
![image of the navigation bar](./static/media/images/nav-bar.png)
- Landing page
    * The landing page includes a welcoming message and the restaurant's slogan. It also consists of a background image of a served table in the restaurant.
    * The landing page introduces the users to Afghan Cuisine and welcomes them to the restaurant site while the slogan on this section encourages users to learn more about the restaurant and view the menu.<br>
![image of the landing page](./static/media/images/landing-page.png)
- About section
    * This section contains information on the restaurant, its opening hours, and contact information such as an email address and phone number.
    * This section informs people about the type of restaurant Afghan Cuisine is and the varieties of food they provide. It also tells the user what time the restaurant is open for business.<br>
![image of the about section](./static/media/images/about-page.png)
- Contact section
    * The contact area includes a functional form where the user can enter their full name, email address, and a message to send to us. It also includes a photograph of a restaurant entrée.
    * Users can offer us feedback or ask questions about the restaurant via the contact section of the website. The photo in this part gives users a taste of what the restaurant has to offer, encouraging them to make a reservation.<br>
![image of the contact section](./static/media/images/contact-section.png)
- Footer 
    * The footer consists of links to the restaurant's social media accounts so that the user can access.<br>
![image of the footer](./static/media/images/footer.png)
- Booking reservation page
    * This section contains a form that the logged-in user can use to book a reservation. If the user is not logged in, they are advised to log in or create an account before making a reservation.
    * This area is an important part of the website because it is from here that the user may make a reservation to visit the restaurant. For the convenience of the users, the form is also prepopulated. The reservation booking form has form validation features to ensure that the user enters valid values.<br>
![image of the booking reservation page](./static/media/images/book-reservation.png)
- Viewing the reservation
    * This page displays all reservations and associated data in a table for logged-in users.
    * Users can view their reservations as well as their associated details. They can also amend or delete any of their reservations, providing them the opportunity to remedy any errors in the reservation details. In this section, defensive programming is used, so that when a user attempts to delete a specific reservation, a confirmation modal appears for them to affirm their decision.<br>
![image of the my reservations page](./static/media/images/my-reservations.png)
- Menu
    * This page displays all of the restaurant's menu items. There are separate sections for the dishes and drinks. The menu items are all presented as cards. The cards include the item's name and price, a picture of the menu item, a description of the item, and nutrition information.
    * This section allows consumers to see all of the food and drinks that the restaurant offers so that they know what they can order in the restaurant. It also displays nutrition information such as calorie, protein, and fat content, as well as allergen icons, allowing the user to avoid undesirable menu items.<br>
![image of the dishes section](./static/media/images/menu-dishes.png)
![image of the drinks section](./static/media/images/menu-drinks.png)
![image of the dish card](./static/media/images/dish-card.png)

## Future Features
Some Future features that can be implemented are:
- The ability for users to edit their account details
- Avoiding double booking
- Table map for the tables in the restaurant

## Technologies Used

During the development of this project serveral technologies have been used:

- [Django](https://www.djangoproject.com/)
    - Django is the main framework that was utilized to create the overarching project and its applications.
- [Python](https://www.python.org/)
    - Python was used to write the core logic of the site.
- [Bootstrap](https://getbootstrap.com/)
    - Bootstrap was used to creat and design a responsive site.
- [Font Awesome](https://fontawesome.com/)
    - Fontawesome icons are used throughout the website.
- [Google Developer Tools](https://developers.google.com/web/tools/chrome-devtools)
    - Google developer tools was used to detect bugs and manage responsivness.
- [GitHub](https://github.com/)
    - Github is used to store the code of this project.
- [Git](https://git-scm.com/)
    - Git was used for version control
- [Gitpod](https://www.gitpod.io/)
    - Gitpod was used as the development environment.
- [Heroku](https://dashboard.heroku.com/apps)
    - Heroku was used to deploy and host the project.
- [Lucid](https://lucid.app/documents#/dashboard)
    - Lucid was used to create the database schema.
- [Cloudinary](https://cloudinary.com/)
    - Cloudinary was used to store the static files of the site.
- [Favicon.io](https://favicon.io/)
    - Favicon was used to create favicon's for the site.
- [SQLite](https://www.sqlite.org/index.html)
    - SQLite was used to run the database locally under development.
- [ElephantSQL](https://www.elephantsql.com/)
    - ElephantSQL was used to store the data of the site.


# Testing
## Bugs
The following bugs were discovered during the testing of the site:
* **Bug:** After adding extra model fields to the Reservation model the form in the template was not responsive anymore.
* **Fix:** Change the form.as_p to form.as_table and put the form inside a table and bring the submit button outside the table.<hr>

* **Bug:** I wanted the allergens field to be a checkbox list that the admin could choose multiple values from but models.choices only allowed it to be one value.
* **Fix:** I created a separate model for allergens and in the allergens field for the dishes I created a ManyToMany field. After that I added filter_horizontal for the allergens field in the admin panel.<hr>

* **Bug:** The URL in the CSS background-image property for the landing page div with the class 'hero', did not function after deploying the site to Heroku and setting DEBUG to False in the settings.py file.
* **Fix:** I copied the image url from Cloudinary and replaced it with the URL in the css background-image property for the landing page div with the class 'hero'.

## Unsolved bugs
* **Social account login**: I created the Gmail app to generate OAuth 2 credentials for the django-allauth social account login in a specific Gmail account. When attempting to log in with Google on the deployed Heroku site while signed in to Chrome with that specific Gmail account, I receive a 'Deceptive site ahead' error. When trying the same operation in an incognito tab or in the local host, I don't get the error. While at first I thought that the error was not specific to my Gmail account I tried to recreate the app in google Developers but then when I asked friends to try to log in with their google accounts, no such error was displaying for them. I have tried to log in with google with several different accounts but I only get the error with the account that the OAuth 2 credentials were generated.

## Validator Testing

- HTML
    * Validated using [W3C](https://validator.w3.org/) HTML validator and no errors were found.
    ![image of HTML validation](./static/media/images/html-validation.png)

- CSS
    * Validated using [Jigsaw](https://jigsaw.w3.org/css-validator/) validator and no errors were found.
    ![image of css validation](./static/media/images/css-validation.png)

- JavaScript
    * Validated using [JsHint](https://jshint.com/) validator and no errors were found.

- Python
    * Validated using [CI Python Linter](https://pep8ci.herokuapp.com/) validator and no errors were found except in the settings.py file.

- I have also checked and tested the site on different browsers such as Chrome, Firefox, Edge and Safari. By using the chrome dev tools and [Am I Responsive?](https://ui.dev/amiresponsive?url=https://8000-jalalk1244-educationfor-fd3e2i2syhp.ws-eu62.gitpod.io/index.html) website have i also checked and confirmed the responsiveness of the site.

- Lighthouse report (Chrome dev-tool) <br>
    ![image of lighthouse report](.//static/media/images/lighthous-report.png)

## Manual Tests

**Authentication**

Description:

Ensure a user can sign up to the website

Steps:

1. Navigate to [Afghan Cuisine](https://afghan-cuisine.herokuapp.com/) and click on the account icon
2. Click on the sign up link
3. Enter email, username, first name, last name and password 
3. Click Sign up

Expected:

The user is redirected to the home page as a logged in user

Actual: 

The user is redirected to the home page as a logged in user

<hr>

Description:

Ensure a user can login in to the website with thier social accounts

Steps:

1. Navigate to [Afghan Cuisine](https://afghan-cuisine.herokuapp.com/) and click on the account icon
2. Click on the login link
3. Click on the Google button
3. Confirm sign in with social account
4. Enter your social account details

Expected:

The user is logged in with thier social account details

Actual: 

The user is logged in with thier social account details

<hr>

Description:

Ensure a user can log in once signed up

Steps:
1. Navigate to [Afghan Cuisine](https://afghan-cuisine.herokuapp.com/) and click on the account icon
2. Click on the log in
2. Enter login detailscreated in previous test case
3. Click login

Expected:

User is successfully logged in and redirected to the home page

Actual:

User is successfully logged in and redirected to the home page

<hr>

Description:

Ensure a user can sign out

Steps:

1. Login to the website
3. click the account icon
2. Click the logout link
3. Click confirm on the confirm logout page

Expected:

User is logged out

Actual:

User is logged out

<hr>

**Website's foundations**
Description:

Ensure that the home page with navbar and footer displays on loading the page

Steps:

1. Navigate to [Afghan Cuisine](https://afghan-cuisine.herokuapp.com/)

Expected:

A landing page with welcoming message with footer and navbar

Actual:

A landing page with welcoming message with footer and navbar

<hr>

Description:

Ensure that the links in the navbar are linking to the right page

Steps:

1. Navigate to [Afghan Cuisine](https://afghan-cuisine.herokuapp.com/)
2. Click on any of the navbar links

Expected:

if clicked on Home or the Logo, redirected to the index.html<br>
if clicked on About Us, redirected to the index.html#about-section<br>
if clicked on Contact , redirected to the index.html#contact-section<br>
if clicked on Menu, redirected to the menu.html<br>
if clicked on Reservations, redirected to the create_reservation.html<br>
if clicked on account icon then login, redirected to the Allauth sign in page<br>
if clicked on account icon then signup, redirected to the Allauth signup page

Actual:

if clicked on Home or the Logo, redirected to the index.html<br>
if clicked on About Us, redirected to the index.html#about-section<br>
if clicked on Contact , redirected to the index.html#contact-section<br>
if clicked on Menu, redirected to the menu.html<br>
if clicked on Reservations, redirected to the create_reservation.html<br>
if clicked on account icon then login, redirected to the Allauth sign in page<br>
if clicked on account icon then signup, redirected to the Allauth signup page

<hr>

Description:

Ensure that the contact form is working

Steps:
1. Navigate to [Afghan Cuisine](https://afghan-cuisine.herokuapp.com/)
2. Click Contact from the navbar
3. Fill in the contact from details
4. Click on Submit

Expected:

A success message with the submited name on it and an email sent to quizleage26@gmail.com with submited message

Actual:

A success message with the submited name on it and an email sent to quizleage26@gmail.com with submited message

**Reservation functionality**

Description:

Ensure that the reservation form can be sent

Steps:
1. Navigate to [Afghan Cuisine](https://afghan-cuisine.herokuapp.com/) and login or register an account
2. Click on the reservation button on the navbar
3. Fill in the form the details 
4. Click on submit

Expected: 

A success message stating that the reservation was sent and is awaiting approval

Actual : 

A success message stating that the reservation was sent and is awaiting approval

<hr>

Description:

Ensure that reservations can be viewed

Steps:
1. Navigate to [Afghan Cuisine](https://afghan-cuisine.herokuapp.com/) and login or register an account
2. Click on the account icon
3. Click on My Reservations

Exepected: 

if there are booked reservations, a list of all of the booked reservation and their details
if ther are no booked reservations, a message stating that there are no booked reservation and promting to book one

Actual:

if there are booked reservations, a list of all of the booked reservation and their details
if ther are no booked reservations, a message stating that there are no booked reservation and promting to book one

<hr>

Description:

Ensure that reservations can be edited

Steps:
1. Navigate to [Afghan Cuisine](https://afghan-cuisine.herokuapp.com/) and login or register an account
2. Click on the account icon
3. Click on My Reservations
4. click on the edit button on one of the reservations
5. Change the form details

Expected: 

Reservation updated with the changed details

Actual:

Reservation updated with the changed details

<hr>

Description:

Ensure that reservations can be deleted

Steps:
1. Navigate to [Afghan Cuisine](https://afghan-cuisine.herokuapp.com/) and login or register an account
2. Click on the account icon
3. Click on My Reservations
4. click on the edit button on one of the reservations
5. Click the delete button
6. Confirm deletion

Expected:

The reservation deleted from the database

Actual: 

The reservation deleted from the database

<hr>

Description:

Ensure that booking reservations form are prepopulated

Steps:
1. Navigate to [Afghan Cuisine](https://afghan-cuisine.herokuapp.com/) and login or register an account
2. Click on the reservation button on the navbar

Expected:

The reservation form prepopulated with the users email and name

Actual: 

The reservation form prepopulated with the users email and name

<hr>

**Menu**

Description:

Ensure that all of the available menu items can be viewed

Steps:
1. Navigate to [Afghan Cuisine](https://afghan-cuisine.herokuapp.com/)
2. Click Menu from the navbar

Expected: 

A list of menu items as cards with thier name and picture

Actual:

A list of menu items as cards with thier name and picture

<hr>

Description:

Ensure that the menu items has desciption section

Steps:
1. Navigate to [Afghan Cuisine](https://afghan-cuisine.herokuapp.com/)
2. Click Menu from the navbar
3. Click on the read more button on any of the dishes

Expected: 

Desciption, nutrition information and allergen information about the dish is revealed

Actual:

Desciption, nutrition information and allergen information about the dish is revealed

<hr>

**Admin site control**

Description:

Ensure that an admin user can login and find access the site's backend

Steps:
1. Navigate to [Afghan Cuisine](https://afghan-cuisine.herokuapp.com/)
2. login as and admin user
3. Click the account icon on the navbar
4. Click admin page

Expected:

The admin user is redirected to the admin page

Actual:

The admin user is redirected to the admin page

<hr>

Description:

Ensure that an admin user can approve or disapprove reservatoins

Steps:
1. Navigate to [Afghan Cuisine](https://afghan-cuisine.herokuapp.com/) and login as and admin user
2. Click on Reservations table
3. Select a reservation and chose 'delete selected reservations' from the actions

Expected:

The selected reservation deleted from the database

Actual:

The selected reservation deleted from the database

<hr>

Description:

Ensure that the an admin user can performe CRUD functionality on the menu items

Steps:
1. Navigate to [Afghan Cuisine](https://afghan-cuisine.herokuapp.com/) and login as and admin user
2. Click on Dishs table

Expected:

If a dish is selected and the action 'delete selected dish' is chosen, the dish deleted from the database<br>
If clicked 'add dish' and filled the details, the dish added to the database<br>
If clicked on any dish and changed the details, the dish's details upated on the database

Actual:

If a dish is selected and the action 'delete selected dish' is chosen, the dish deleted from the database<br>
If clicked 'add dish' and filled the details, the dish added to the database<br>
If clicked on any dish and changed the details, the dish's details upated on the database

**The same tests were done for the drinks table and the allergens table and they passed**

# Deployment

## Heroku
To deploy my project to Heroku I applied these steps:
- Go to [Heroku.com](https://heroku.com/) and log in or create an account if you don't already have one
- Click the New dropdown and select Create New App.
- Enter a valid name for the project
- Select region and click create app
- Go to settings tab and click reveal config vars
- Add the below config vars:
    * CLOUDINARY_URL = your Cloudinary URL
    * DATABASE_URL = your database URL
    * EMAIL_HOST_USER = the email for receiving submitted contact forms
    * EMAIL_HOST_PASSWORD = email app password
    * SECRET_KEY = your django secret key
    * PORT = 8000
- Navigate to the deploy page
- Connect github account and search for the repository
- Click deploy <br>
The app should now be deployed

## Clone the repository
To clone the repository:
- Navigate to https://github.com/jalalk1244/afghan-cuisine 
- click on the code button at the top of the file
- Choose HTTPS and copy the link
- Navigate to your editors terminal, where git must be installed
- Type git clone URL
- Replace URL with the copied link
- Press enter

# Credits

## Content
- [Allergy icons](https://github.com/Erudus/erudus-icons)
- [Customize allauth forms](https://www.geeksforgeeks.org/python-extending-and-customizing-django-allauth/)
- [Allauth Socialaccount](https://testdriven.io/blog/django-social-auth/)
- [Landing page image](https://foodandnutrition.org/wp-content/uploads/MGT-Afghanistan.jpg)
- [Contact section image](https://www.breadsaltcuisine.com/assets/frontend/images/welcome.jpg)
- [Foodora image](https://upload.wikimedia.org/wikipedia/commons/2/23/Foodora_logo.png)
- [Uber eats image](https://logodownload.org/wp-content/uploads/2019/05/uber-eats-logo.png)
- [Test drink image](https://emuweavinglife.files.wordpress.com/2012/11/dogh-6.jpg?w=584)
- [Crispy Forms](https://django-crispy-forms.readthedocs.io/en/latest/)
- [Django Allauth](https://django-allauth.readthedocs.io/en/latest/installation.html)
- [Sending email with django](https://www.youtube.com/watch?v=xNqnHmXIuzU&t=438s)

