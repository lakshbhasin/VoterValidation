# Overview

A voter validation tool for petition gathering. This uses a raw txt voter file
with a specified schema, as mentioned in update_voters.py. Voters are stored in
a database, and fuzzy search can be used to search petition signers and mark
them as valid. The voter file itself is stored as MVF\_YYYY\_MM\_DD.tsv.

This tool can allow grassroots campaigns to run low-cost petition validation
software on Heroku to validate petition signatures against a voter file,
without having to pay for proprietary software. It has features like fuzzy
search and a simple search ranking algorithm using trigram similarity and exact
text match, with some speed optimizations.

A lot of this was developed for the San Francisco voter file, and is only
designed to work with a single jurisdiction's voter file. Typical users for
this kind of tool would be campaign staff and volunteers looking to validate
signatures to qualify a ballot measure.

DISCLAIMER: It is illegal to use signatures on an initiative petition in California for
a purpose other than qualification of the proposed measure for the ballot.
Petitions cannot be used to create or add to mailing lists or similar lists
for any purpose, including fundraising or requests for support. Any such misuse
constitutes a crime. Handle your data carefully, and only keep it for as long
as absolutely necessary for validation purposes.

# GitHub / Heroku Setup

The steps below should get you set up on an Arch Linux computer. If you have
issues, contact the author.

If you don't already have git:

```
sudo apt-get install git
```

To pull down the repository:

```
git clone https://github.com/lakshbhasin/VoterValidation.git
```

Get the Heroku command line tools and login.

```
yaourt -S heroku-cli
heroku login
```

To add the production Heroku remote:

```
git remote add heroku https://git.heroku.com/sf-voter-validation.git
```

And you should be all set up to push to production (if you have been given
push access).

# Local Runbook

Note: The following instructions assume you have Python 3.8.2+, which is
referred to as just "python". If "python" points to "python2" on your computer,
please take note of this key difference!

## Installing Non-Python Requirements
Install postgresql and dev headers from your package manager, and
configure it. If you don't already have them, also grab the the python3
dev headers and virtualenv.

On Arch Linux:
```
pacman -S postgresql python redis flake8
```

## Configuring PostgreSQL

To configure PostgreSQL to work with the local version of this website (see
backend/settings.py for the latest authentication info), follow these steps:

```
sudo -u postgres psql template1

# The following lines are run in psql, where "template1=#" is the prompt
template1=# CREATE USER voter_validation_test WITH PASSWORD 'voter_validation_test_pass';
template1=# CREATE DATABASE voter_validation_test_db;
template1=# GRANT ALL PRIVILEGES ON DATABASE voter_validation_test_db TO voter_validation_test;
template1=# \connect voter_validation_test_db
You are now connected to database "voter_validation_test_db" as user "postgres".
voter_validation_test_db=# CREATE EXTENSION pg_trgm;
voter_validation_test_db=# \q
```

The last few lines connect to the DB so we can install the Postgres trigram
similarity extension, which supports fuzzy search. You can also run `\dx` in
`psql` after installing the extension, to check it is installed.

On Arch Linux, you will have to run `chmod og+X /home /home/$USER` and
follow the instructions on https://wiki.archlinux.org/index.php/PostgreSQL#Installing_PostgreSQL
(through starting the service with systemctl) before trying the above commands.

## Installing Python Requirements
Install all of the Python requirements inside a virtualenv, in the root
directory of the project:

```
python3.8 -m pip install --user virtualenv
python3.8 -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

Note that, in every new terminal window where you want to run the server, you
will first have to source the virtualenv (as above). It might be useful to
create an alias that "cd"s into the repo directory and sources the virtualenv,
to make development easier.

## Local Website Setup
If any environment variables can't be found, you can source the .env file 
and export all of its variables:
```
set -a
source .env
set +a
```
A helpful alias for development and opening new terminal windows (change 
~/Documents/code/VoterValidation to your repo location):
```
alias voterval='cd ~/Documents/code/VoterValidation && set -a && source .env && set +a && source venv/bin/activate'
```

You then need to migrate any DB changes as follows:

```
python manage.py migrate
```

Next, create a superuser for your local copy:

```
python manage.py createsuperuser
# Follow the prompts to set up your local account
# Do this for as many users as you need for testing
```

Create UserProfiles for each of your users as well:
```
python manage.py create_user <username>
```

## Local testing
To run locally:

```
heroku local
```

The web server will run at localhost:5000.

## Lint
Run `flake8` to lint and correct style issues.

## Updating Voter File

You can use the `update_voters` script to update the voter file in an atomic
transaction, with confirmation required before finalizing changes.
```
python manage.py update_voters <mvf_tsv_url> [--dry_run]
```

Where `mvf_tsv_url` is a URL holding the Master Voter File as a TSV.

# Troubleshooting

## PostgreSQL Not Running on Port 5432

This can happen after a PostgreSQL update on Arch Linux. The error for this
looks like:
```
could not connect to server: Connection refused
	Is the server running on host "localhost" (::1) and accepting
	TCP/IP connections on port 5432?
```

To resolve this, follow the update instructions in
https://wiki.archlinux.org/index.php/PostgreSQL#Quick_guide. Once the database
has been upgraded, run `sudo systemctl start postgresql.service` and `sudo
systemctl enable postgresql.service`. Then rerun `heroku local`.
