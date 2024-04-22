# Ranking social

The ranking system for all user content posted on social networks is based on the user's behavior toward that post. From there, come up with a solution to recommend appropriate content to users.

👉 Using python and django for this project

## ✴️Features

- Calculate ranking
- Filter ranking by location
- Schedule ranking daily, weekly

## 🔧Installation

#### 1. Setup python enviroment, python version 3.11 up

You can download python at link https://www.python.org/downloads/

After installation you can check, open terminal

```bash
  python --version
```

If result is 3.11 or up sucessfully

#### 2. Install library

Open terminal inside folder ranking_social (The root folder is cloned from git)

```bash
  python install -r requirements.txt
```

After running this command the libraries will be installed

## ✔️Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`MYSQL_USER`
`MYSQL_DATABASE`
`MYSQL_ROOT_PASSWORD`
`MYSQL_PASSWORD`
`DJANGO_SECRET_KEY`

Above is variables relation your database and secret key for run this app.

## 🌏Run Locally

#### ❗❗ You need to create a db in mysql whose name must match `MYSQL_DATABASE` in the .env file

#### Need migrate change database to your db

```bash
  python manage.py migrate
```

#### 📜After migrate using need import data from excel to database

Open terminal, using cli:

```bash
  python manage.py import_data
```

If successfully, in console will be log `Data imported successfully`

To run server you run cli:

```bash
  python manage.py runserver
```

Development server running at `http://127.0.0.1:8000/`

⏰ If you want run schedule reset ranking, you can open new terminal and run:

```bash
  python manage.py cronloop
```
