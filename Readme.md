Install requirement

`pip install -r requirements.txt`

Run

`gunicorn -w 1 -b 0.0.0.0:5000 --worker-class eventlet app:app --reload`

