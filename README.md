# **Project Foodgram:**

_Yours assistant in the world of cooking_

**Description:**

This project is yours easy way to create your own culinary blog.

It includes:

- Secure authentication system with OAuth 2.0.
- A feed of recipes from you, for you and for all your friends.
- A Subscription system that will allow you always see the latest recipes from your colleagues in the culinary arts.
- A Favorites system that will allow you easy manage your favorite recipes.
- Shopping Cart system easy add all ingredients of recipes, what you decide to cook today to Shopping List.
- Preloaded database with many ingredients

Example of project you can see [here](https://foodgram-serhioth.ddns.net/).


**Technologies:**

- Python
- Bash
- Django
- Django Rest Framework
- Djoser
- Docker
- Docker-compose
- Gunicorn
- Nginx
- PostgreSQL
- CI\CD

**How to set up project on your own server:**

1. Install Docker and Docker-compose to yours server (instructions [here](https://docs.docker.com/engine/install/))
2. Clone the repository to yours server
3. Into directory foodgram-project-react/backend/ you will find run\_app.sh
4. This is script for preconfiguring of backend container, it premading default superuser, don't forget to change its data to desired
5. In foodgram-project-react/backend/infra/ you will find .env.example file rename it to .env, change it to desired settings
6. Now copy docker-compose.production.yml, nginx.conf and .env to foodgram-project-react directory from infra directory
7. Run command "sudo docker-compose –f docker-compose.production.yml up –d"
8. If you configured all in a right way – your site will be available at yours desired URL