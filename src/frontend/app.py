from flask import Flask, url_for, request, render_template, redirect
import pandas as pd
import time
import datetime
from sqlalchemy.orm import Session
from finviz.screener import Screener
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import Boolean, Column, DateTime, Float, String, create_engine, or_, and_
from pathlib import Path
import os

#Create Dataclass for Redditpostes
Base = automap_base()
metadata = Base.metadata

class Redditpost(Base):
    __tablename__ = 'redditposts'

    ticker = Column(String, primary_key=True, nullable=False)
    created_utc = Column(DateTime, primary_key=True, nullable=False)
    comment = Column(String, nullable=False)
    passed_filter_checks = Column(Boolean)
    sentiment = Column(Float(53))

# Connect to database
PGHOST='h2933354.stratoserver.net'
PGDATABASE='admin'
PGUSER='admin'
PGPASSWORD='password'
PGPORT='3000'

engine = create_engine('postgresql://'+PGUSER+':'+PGPASSWORD+'@'+PGHOST+':'+PGPORT+'/'+PGDATABASE)
conn = engine.connect()

Base.prepare(engine, reflect=True)
Base.metadata.create_all(bind=engine)
session = Session(engine)

# Extrahieren aller Ticker in der DB um mit diesen später zu filtern
ticker_obj = session.query(Redditpost.ticker).distinct().all()
ticker = [ticker[0] for ticker in ticker_obj]

# Update metadata if it is older than 24 hours
delta = datetime.datetime.utcnow() - datetime.datetime.strptime(str(list(Path(".").rglob("metadata_*.csv"))[0])[-30:-4], '%Y-%m-%d %H:%M:%S.%f')
if delta.days == 0:
    df_data = pd.read_csv(str(list(Path(".").rglob("metadata_*.csv"))[0]), index_col=False)
else:
    stock_list_performance = Screener(table='Performance', order='price', filters = ['cap_midover', 'ipodate_more1', 'exch_nasd'])
    stock_list_overview = Screener(table='Overview', order='price', filters = ['cap_midover', 'ipodate_more1', 'exch_nasd'])
    # Daten lesen als Dataframe und mergen
    df_performance = pd.DataFrame(stock_list_performance.data)
    df_overview = pd.DataFrame(stock_list_overview.data)

    difference_cols = list(df_performance.columns.difference(df_overview.columns))
    difference_cols.append("Ticker")

    df_data = df_overview.merge(df_performance[difference_cols], left_on="Ticker", right_on="Ticker", how="outer")

    os.remove(str(list(Path(".").rglob("metadata_*.csv"))[0]))
    df_data.to_csv(f"metadata_{datetime.datetime.utcnow()}.csv", index=False)


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
    return render_template('preferences.html', sectors=sorted(list(set(df_data['Sector']))))

# This function is used to pass the text input to the machine learning classification model and calculate the results if we are only using the clustering based on text features. 
@app.route("/preferences_end", methods=['GET', 'POST'])
def preferences_end():
    if request.method == 'POST':

        global sectors
        sectors = [sector.replace("_"," ") for sector in request.form.getlist("sector")]

        return redirect(url_for('dashboard'))

# This function returns the calculated labels to the html templates. 
# If someone opens this site bfore inserting a text he will get autatically redirected to the textinput. 
@app.route("/dashboard")
def dashboard():
    try:
        #Retrieve all tickers which are relevant for the customer sector preferences
        relevant_tickers = df_data[(df_data["Sector"].isin(sectors))]["Ticker"]

        #Read the relevant tickers from the SQL database
        tickerdata = pd.DataFrame(session.query(Redditpost.ticker, Redditpost.created_utc, Redditpost.sentiment).filter(and_(Redditpost.ticker.in_(relevant_tickers), Redditpost.sentiment != None)).all(),\
                  columns=["Ticker", "created_utc", "sentiment"]).sort_values("created_utc")

        #Join the tickers with the metadata
        tickerdata = pd.merge(tickerdata, df_data, on=["Ticker", "Ticker"], how="left", indicator=True
            ).query('_merge=="both"')[["Ticker", "created_utc", "sentiment", "Company", "Sector", "Industry", "Country", "Price", "Perf YTD", "Volatility M"]]
        
        #Define colors used in the dashboard
        rgb=["rgba(152, 176, 155, 0.8)", "rgba(8, 103, 131, 0.8)", "rgba(146, 140, 138, 0.8)", "rgba(192, 192, 153, 0.8)", "rgba(59, 60, 59, 0.8)", "rgba(71, 173, 207, 0.8)", "rgba(99, 136, 104, 0.8)", "rgba(8, 75, 96, 0.8)", "rgba(8, 50, 62, 0.8)", "rgba(192, 226, 238, 0.8)"]      
        
        #Aggregate data per ticker
        series_collection = []
        counter = 0
        for company in sorted(list(set(tickerdata["Ticker"]))):

            # Extract the data for each each ticker
            df = tickerdata[tickerdata['Ticker'] == company]

            # Read the matadata of the ticker
            name_variable = list(df_data[(df_data["Ticker"] == company)]["Company"])[0]
            sector_variable = list(df_data[(df_data["Ticker"] == company)]["Sector"])[0]
            industry_variable = list(df_data[(df_data["Ticker"] == company)]["Industry"])[0]
            country_variable = list(df_data[(df_data["Ticker"] == company)]["Country"])[0]
            price_variable = list(df_data[(df_data["Ticker"] == company)]["Price"])[0]
            return_variable = list(df_data[(df_data["Ticker"] == company)]["Perf YTD"])[0]
            risk_variable = list(df_data[(df_data["Ticker"] == company)]["Volatility M"])[0]

            # Add a current timestamp with sentiment 0 to ensure that the time series of every ticker has same length
            df = df.append(pd.DataFrame({'Ticker':[company],'created_utc':[datetime.datetime.utcnow()],'sentiment':[0], 'Company':[name_variable], 'Sector':[sector_variable], 'Industry':[industry_variable], 'Country':[country_variable], 'Price':[price_variable], 'Perf YTD':[return_variable], 'Volatility':[risk_variable]}), ignore_index=False)

            # Calculate average sentiment per 6 hours and calculate the rolling average based on the 6-hour-average
            resampled_ticker = df.resample('6h', on='created_utc').sentiment.mean().fillna(0).rolling('24h').mean()

            # Safe for each ticker: (newest 125 sentiment 6-hour-time-series-intervalls, comany and sector, used line color)
            series_collection.append((list(resampled_ticker)[-125:], company, name_variable, sector_variable, industry_variable, country_variable, price_variable, return_variable, risk_variable, rgb[counter]))

            #Allows repaeting the colors (we use 10 different colors)
            counter +=1
            if counter == 10:
                counter = 0


        #resampled_ticker = tickerdata.resample('6H', on='created_utc', offset='0Min0s').sentiment.mean().fillna(method='ffill')
        #tickerdata = tickerdata.set_index("created_utc").sort_index()
        

        # Combining the time stamps with the sentiment data
        sentiment_data = [[int(date/1000000) for date in resampled_ticker.index.values.tolist()][-125:], series_collection]
        #sentiment_data = [[int(date/1000000) for date in tickerdata.index.values.tolist()], list(tickerdata["sentiment"].rolling('24h').mean())]
        
        risk_data = [[data[1] for data in sentiment_data[1]]]
        risk_data.append([float(data[8].strip("%")) for data in sentiment_data[1]])
        risk_data.append([data[9] for data in sentiment_data[1]])
        risk_data.append([data[9].replace("0.8", "0.7") for data in sentiment_data[1]])
        risk_data.append([float(data[7].strip("%")) for data in sentiment_data[1]])

        return render_template('dashboard.html', sentiment_data=sentiment_data, risk_data=risk_data)
    except NameError:
        return render_template('preferences.html', sectors=sorted(list(set(df_data['Sector']))))

# This function returns the team.html page containing the information details from our team.
@app.route("/team")
def team():
    return render_template('team.html')

# Python assigns the name "__main__" to the script when the script is executed. 
# If the script is imported from another script, the script keeps it given name (e.g. app.py). 
# In our case we are executing the script. Therefore, __name__ will be equal to "__main__". 
# That means the if conditional statement is satisfied and the app.run() method will be executed.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=500, debug=True)