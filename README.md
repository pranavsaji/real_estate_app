# Run the following

## Navigate to backend folder
pip install -r requirements.txt

## Create a .env file inside bakend folder with content below:
FLASK_APP=app.py
FLASK_ENV=development
OPENAI_API_KEY="Open AI key"

## now go to frontend
npm install

## Now in one terminal, run the backend using the following command after navigating to backend folder:

python app.py

## Now in another terminal, run the frontend using the following command after navigating to frontend folder:
npm start
