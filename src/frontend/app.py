from flask import Flask, url_for, request, render_template, redirect
import pandas as pd
import datetime
from sqlalchemy.orm import Session
from finviz.screener import Screener
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import Boolean, Column, DateTime, Float, String, create_engine, and_
from pathlib import Path
import os
from statistics import mean

# create dataclass for redditpostes
Base = automap_base()
metadata = Base.metadata

class Redditpost(Base):
    __tablename__ = 'redditposts'

    ticker = Column(String, primary_key=True, nullable=False)
    created_utc = Column(DateTime, primary_key=True, nullable=False)
    comment = Column(String, nullable=False)
    passed_filter_checks = Column(Boolean)
    sentiment = Column(Float(53))

# connect to database
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


# app = Flask(__name__) creates an instance of the Flask class called app. 
# the first argument is the name of the module or package (in this case Flask). 
# we are passing the argument __name__ to the constructor as the name of the application package. 
# it is used by Flask to find static assets, templates and so on.
app = Flask(__name__)

# we set the Track Modifications to True so thatFlask-SQLAlchemy will track modifications of objects and emit signals. 
# the default is None, which enables tracking but issues a warning that it will be disabled by default in the future. 
# this requires extra memory and should be disabled if not needed.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# CREATING ROUTES
# we use Routes to associate a URL to a view function. A view function is simply a function which responds to the request. 

# this code registers the index() view function as a handler for the root URL of the application. 
# everytime the application receives a request where the path is "/" the index() function will be invoked and the return the index.html template.
@app.route("/")
def index():
    return render_template('index.html')

# this function returns the preferences.html page which is used to input get the customer preferences regarding sector, risk und return.
@app.route("/preferences")
def preferences():

    global df_data

    # update metadata if it is older than 24 hours
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

    return render_template('preferences.html', sectors=sorted(list(set(df_data['Sector']))), hint=False)

# this function is used to receive the customer preferences 
@app.route("/preferences_end", methods=['GET', 'POST'])
def preferences_end():
    if request.method == 'POST':

        # read the sector preferences and apply the right format
        global sectors
        sectors = [sector.replace("_"," ") for sector in request.form.getlist("sector")]

        # read the risk preferences
        global risk_aversity
        risk_aversity = float(request.form.getlist("risk")[0])

        # read the minimal return and transform it to a decimal number
        global min_return
        min_return = float(request.form.getlist("min_return")[0])/100

        return redirect(url_for('dashboard'))

# this function returns the calculated recommandations and the data for the dashboard
# if someone opens this site before inserting setting the preferences he will get automatically redirected to the preferences input. 
@app.route("/dashboard")
def dashboard():
    try:
        # retrieve all tickers which are relevant for the customer sector preferences
        relevant_tickers = df_data[(df_data["Sector"].isin(sectors))]["Ticker"]

        # read the relevant tickers from the SQL database
        tickerdata = pd.DataFrame(session.query(Redditpost.ticker, Redditpost.created_utc, Redditpost.sentiment).filter(and_(Redditpost.ticker.in_(relevant_tickers), Redditpost.sentiment != None)).all(),\
                  columns=["Ticker", "created_utc", "sentiment"]).sort_values("created_utc")

        # join the tickers with the metadata
        tickerdata = pd.merge(tickerdata, df_data, on=["Ticker", "Ticker"], how="left", indicator=True
            ).query('_merge=="both"')[["Ticker", "created_utc", "sentiment", "Company", "Sector", "Industry", "Country", "Price", "Perf YTD", "Volatility M"]]
        
        # aggregate the data for each ticker
        series_collection = []
        for company in sorted(list(set(tickerdata["Ticker"]))):

            # extract the data for each each ticker
            df = tickerdata[tickerdata['Ticker'] == company]

            # read the matadata of the ticker
            name_variable = list(df_data[(df_data["Ticker"] == company)]["Company"])[0]
            sector_variable = list(df_data[(df_data["Ticker"] == company)]["Sector"])[0]
            industry_variable = list(df_data[(df_data["Ticker"] == company)]["Industry"])[0]
            country_variable = list(df_data[(df_data["Ticker"] == company)]["Country"])[0]
            price_variable = list(df_data[(df_data["Ticker"] == company)]["Price"])[0]
            return_variable = list(df_data[(df_data["Ticker"] == company)]["Perf YTD"])[0]
            risk_variable = list(df_data[(df_data["Ticker"] == company)]["Volatility M"])[0]

            # add a current timestamp with sentiment 0 to ensure that the time series of every ticker has same length
            df = df.append(pd.DataFrame({'Ticker':[company],'created_utc':[datetime.datetime.utcnow()],'sentiment':[0], 'Company':[name_variable], 'Sector':[sector_variable], 'Industry':[industry_variable], 'Country':[country_variable], 'Price':[price_variable], 'Perf YTD':[return_variable], 'Volatility':[risk_variable]}), ignore_index=False)

            # calculate average sentiment per 6 hours and calculate the rolling average based on the 6-hour-average
            resampled_ticker = df.resample('6h', on='created_utc').sentiment.mean().fillna(0).rolling('24h').mean()

            # safe each ticker
            series_collection.append({"sentiments":list(resampled_ticker)[-125:], "ticker": company, "company": name_variable, "sector": sector_variable, "industry": industry_variable, "country": country_variable, "price": price_variable, "return": return_variable, "risk": risk_variable})

        # remove all tickers which dont hold the minimum return constraint
        series_collection = [series for series in series_collection if float(series["return"].strip("%"))/100 >= min_return]  

        # calculate sentiment and risk scores
        sentiment_ranking = {}
        risk_ranking = {}
        for index in range(len(series_collection)):
            series_collection[index]["sentiment_score"] = mean(series_collection[index]["sentiments"])
            
            sentiment_ranking[series_collection[index]["ticker"]] = series_collection[index]["sentiment_score"]
            risk_ranking[series_collection[index]["ticker"]] = float(series_collection[index]["risk"].strip("%"))

        # calculate sentiment ranking
        sorted(sentiment_ranking, key=sentiment_ranking.get, reverse=True)
        sentiment_ranking = {key: rank for rank, key in enumerate(sorted(sentiment_ranking, key=sentiment_ranking.get, reverse=True), 1)}

        # calculate risk ranking
        sorted(risk_ranking, key=risk_ranking.get, reverse=False)
        risk_ranking = {key: rank for rank, key in enumerate(sorted(risk_ranking, key=risk_ranking.get, reverse=False), 1)}

        # safe the the sentiment and risk renking and calculate, save the weighted average of them based on the risk-aversity
        total_ranking = {}
        for index in range(len(series_collection)):
            sentiment_rank = sentiment_ranking[series_collection[index]["ticker"]]
            risk_rank = risk_ranking[series_collection[index]["ticker"]]
            
            series_collection[index]["sentiment_rank"] = sentiment_rank
            series_collection[index]["risk_rank"] = risk_rank
            total_ranking[series_collection[index]["ticker"]] = (risk_aversity * risk_rank + (1 - risk_aversity) * sentiment_rank)

        # calculate total ranking
        sorted(total_ranking, key=total_ranking.get, reverse=False)
        total_ranking = {key: rank for rank, key in enumerate(sorted(total_ranking, key=total_ranking.get, reverse=False), 1)}

        # add total rank to the tickers
        for index in range(len(series_collection)):
            total_rank = total_ranking[series_collection[index]["ticker"]]
            
            series_collection[index]["total_rank"] = total_rank

        # keep only 10 best ranked tickers
        series_collection_best = [series for series in series_collection if series["total_rank"] <= 10]  

        # sort the remaining tickers based on the ranking
        def sort_on_rank(element):
            return element["total_rank"]

        series_collection_best = sorted(series_collection_best, key=sort_on_rank)

        # round the sentiment score
        for index in range(len(series_collection_best)):
            series_collection_best[index]["sentiment_score"] = round(series_collection[index]["sentiment_score"], 3)

        # define colors used in the dashboard
        rgb=["rgba(152, 176, 155, 0.8)", "rgba(8, 103, 131, 0.8)", "rgba(146, 140, 138, 0.8)", "rgba(192, 192, 153, 0.8)", "rgba(59, 60, 59, 0.8)", "rgba(71, 173, 207, 0.8)", "rgba(99, 136, 104, 0.8)", "rgba(8, 75, 96, 0.8)", "rgba(8, 50, 62, 0.8)", "rgba(192, 226, 238, 0.8)"]      

        # assign colors to the tickers
        for index in range(len(series_collection_best)):
            series_collection_best[index]["color"] = rgb[index]
        
        # preparing the risk and return data (the visualisation program demands different data-structures for the two graphs inthe dashboard)
        risk_return_data = {"tickers": [data["ticker"] for data in series_collection_best], "risks": [float(data["risk"].strip("%")) for data in series_collection_best], "returns": [float(data["return"].strip("%")) for data in series_collection_best], "borderColors": [data["color"] for data in series_collection_best], "backgroundColors": [data["color"].replace("0.8", "0.7") for data in series_collection_best]}

        # combining the time stamps with the sentiment data
        sentiment_data = [[int(date/1000000) for date in resampled_ticker.index.values.tolist()][-125:], series_collection_best]
        
        # if filter constraints lead to no data: redirect to preferences page
        if len(sentiment_data[1]) == 0:
            return render_template('preferences.html', sectors=sorted(list(set(df_data['Sector']))), hint="Please ease your constraints. Your preferences excluded all stocks.")
        
        return render_template('dashboard.html', sentiment_data=sentiment_data, risk_return_data=risk_return_data)
    
    # return to the preferences input if they were not set before
    except NameError:
        return render_template('preferences.html', sectors=sorted(list(set(df_data['Sector']))), hint=False)

# this function returns the team.html page containing the information details from our team.
@app.route("/team")
def team():
    return render_template('team.html')

# python assigns the name "__main__" to the script when the script is executed. 
# if the script is imported from another script, the script keeps it given name (e.g. app.py). 
# in our case we are executing the script. Therefore, __name__ will be equal to "__main__". 
# that means the if conditional statement is satisfied and the app.run() method will be executed.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)