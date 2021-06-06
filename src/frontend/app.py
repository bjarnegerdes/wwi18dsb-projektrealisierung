from flask import Flask, url_for, request, render_template, redirect
from sqlalchemy import create_engine
import pandas as pd
import time
from datetime import datetime

# Connect to database
PGHOST='h2933354.stratoserver.net'
PGDATABASE='admin'
PGUSER='admin'
PGPASSWORD='password'
PGPORT='3000'

connection_string = 'postgresql://'+PGUSER+':'+PGPASSWORD+'@'+PGHOST+':'+PGPORT+'/'+PGDATABASE
engine = create_engine(connection_string)


# app = Flask(__name__) creates an instance of the Flask class called app. 
# The first argument is the name of the module or package (in this case Flask). 
# We are passing the argument __name__ to the constructor as the name of the application package. 
# It is used by Flask to find static assets, templates and so on.
app = Flask(__name__)

# As the pictures are changing after each classification, the caching of this app must be disabled
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# We set the Track Modifications to True so thatFlask-SQLAlchemy will track modifications of objects and emit signals. 
# The default is None, which enables tracking but issues a warning that it will be disabled by default in the future. 
# This requires extra memory and should be disabled if not needed.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# CREATING ROUTES
# We use Routes to associate a URL to a view function. A view function is simply a function which responds to the request. 

# This code registers the index() view function as a handler for the root URL of the application. 
# Everytime the application receives a request where the path is "/" the index() function will be invoked and the return the index.html template.
@app.route("/")
def index():
    return render_template('index.html')

# This function returns the preferences.html page which is used to input a text which should be analyzed.
@app.route("/preferences")
def preferences():
    return render_template('preferences.html')

# This function is used to pass the text input to the machine learning classification model and calculate the results if we are only using the clustering based on text features. 
@app.route("/preferences_end", methods=['GET', 'POST'])
def preferences_end():
    if request.method == 'POST':

        # Get the text input and save it globally as we will need it in another function
        global text
        text = "bla"

        # Get the taget variable
        global targetvariable

        targetvariable = "No"

        # If no target variable for an improved classification was submitted, then redirect directly to the result

        if targetvariable=='No':

            return redirect(url_for('dashboard'))
        
        # Otherwise ask for the other variables

        else:

            return redirect(url_for('variableinput'))

# This function returns the variableinput.html page which is used to input the values of the additional variables.
@app.route("/variableinput")
def variableinput():

    # We are definig all possible target variables and removing the choosen one to ask for the others in the frontend.
    neededvariables = ['Age', 'Gender', 'Topic', 'Sign']
    neededvariables.remove(targetvariable)

    return render_template('variableinput.html', targetvariable=targetvariable, neededvariables=neededvariables)

# This function is used to pass the text input and the other submitted variables to the machine learning classification model and calculate the results. 
@app.route("/variableinput_end", methods=['GET', 'POST'])
def variableinput_end():
    if request.method == 'POST':

        # Define the labels as global as we need them in another function.
        global age, gender, topic, sign, clustering
        
        # Ask for the variables whech need to be presubmitted
        try:
            age = int(request.form['age'])
        except:
            age = 0

        try:
            gender = request.form['gender']
        except:
            gender = '0'

        try:
            topic = request.form['topic']
        except:
            topic = '0'

        try:
            sign = request.form['sign']
        except:
            sign = '0'

        # Now we are starting the text analyzation and produce a result.
        #age, gender, sign, topic, clustering = randomModel(text, numerical=True, input=[age, gender, sign, topic], target=targetvariable) #Model for stacked prediction

        # On the Website we use pictures for the result of age which is created now.
        #center_text(str(age), 'age')
        return redirect(url_for('dashboard'))

# This function returns the calculated labels to the html templates. 
# If someone opens this site bfore inserting a text he will get autatically redirected to the textinput. 
@app.route("/dashboard")
def dashboard():
    try:
        company='EBAY'
        sql_data = pd.read_sql(f"SELECT created_utc as time, sentiment FROM redditposts WHERE ticker = '{company}' AND passed_filter_checks = true ORDER BY 1", con=engine).dropna()
        #data = ["{"+f"x: {int(time.mktime(row[1]['time'].to_pydatetime().timetuple()))*1000}, y: {str(row[1]['sentiment'])}"+"}, " for row in data.iterrows()]
        data = [float(row[1]['sentiment']) for row in sql_data.iterrows()]
        labels = [int(time.mktime(row[1]['time'].to_pydatetime().timetuple()))*1000 for row in sql_data.iterrows()]
        return render_template('dashboard.html', data=data, labels=labels, company=company)
    except NameError:
        return render_template('preferences.html')

# This function returns the team.html page containing the information details from our team.
@app.route("/team")
def team():
    return render_template('team.html')

# Python assigns the name "__main__" to the script when the script is executed. 
# If the script is imported from another script, the script keeps it given name (e.g. app.py). 
# In our case we are executing the script. Therefore, __name__ will be equal to "__main__". 
# That means the if conditional statement is satisfied and the app.run() method will be executed.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)