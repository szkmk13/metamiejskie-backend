# migrate.sh
#python3 -m venv venv
# activate the virtual environment
#source venv/bin/activate
python3 -m ensurepip --upgrade
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py collectstatic --noinput
