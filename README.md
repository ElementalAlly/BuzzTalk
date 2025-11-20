# Technologies

In this, I use:
 - **Python** as my language of choice
 - **MySQL** as the database
 - **Pymysql** as the database API for python
 - **Pydantic** for type verification
 - **FastAPI** as the website backend
 - **Uvicorn** as the website listener

# Setup

Clone this repository to a folder of your choosing. In the folder, make a python venv, and run these two commands:

```
pip install fastapi "uvicorn[standard]"
pip install pymysql
pip install pydantic
```

Download and install MySQL, and run the queries in buzztalkdb_init.sql. Establish a root user with some password. Put the following in a .env file in the directory of the repository:

```
user="root"
password="{insert password here, no braces}"
```

# Todo

 - Make different servers, with different tables (registry, messages) for every server.
 - Make profiles for RAs and separate admins
 - Make admin tools, editing and stuff
 - Develop the profile pages.
 - Add restricted servers/channels
 - Add media links and pages.
 - Use a proper templating engine like Jinja for html pages instead of crappy txt files in html lol
 - Make this mobile-friendly

## far future

 - Develop it into a more discord-like server explore maybe?
 - Develop app that could be a glorified browser
 - Publish app
 - Ask RAs and GATech to adopt the app
 - Look for funding for admins maybe?