from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use a secure key in production

# Dummy user storage for demonstration
users = {}

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return "User already exists!"
        users[username] = password  # Store user info (hashed in production)
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('home'))
        return "Invalid credentials!"
    return render_template('login.html')

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)

###################################################
from flask import Flask, render_template, request, jsonify
from final_predicting import get_future_price, historical_data_func, get_corr
import json
import yfinance as yf


app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def home_page():
    return render_template('index.html')

@app.route('/process_selection', methods=['GET','POST'])
def process_selection():
    timeframe = request.form.get("timeframe")
    cryptocoin = request.form.get("crypto")
    date = request.form.get("date")
    cryptocoin_RMSE_scores = {"DOGE":"0.005280370371151401",
"BNB":"7.227682898466721",
"BTC" :"3633.319348318641",
"ETH":"19.364336351504054",
"USDT" :"0.004571586921625304"}
    
    RMSE_SCORE = cryptocoin_RMSE_scores[cryptocoin]

    if timeframe == 'None':
        predicted_price, dates, prices=get_future_price(Input_Date=str(date), tickers=cryptocoin)
    else:
        dates, prices = historical_data_func(tickers=cryptocoin, period_tag=timeframe)
    response_data = {
        'dates': dates,
        'prices': prices,
        "rmse":RMSE_SCORE
    }

    json_data = json.dumps(response_data)

    return jsonify(json_data)

@app.route('/calculate_profit_loss', methods=['POST'])
def calculate_profit_loss():
    btc = request.form.get('btc')
    buying_price = request.form.get('price')
    crypto = request.form.get('crypto_selection')

    cryptocoin_dict = {'DOGE':'DOGE-GBP', 'BNB':'BNB-GBP', 'BTC':'BTC-GBP', 'ETH':'ETH-GBP', 'USDT':'USDT-GBP'}
    data = yf.download([cryptocoin_dict[crypto]], period='1mo')
    data.drop("Adj Close", inplace=True, axis=1)
    data.drop("Volume", inplace=True, axis=1)
    data.drop("Open", inplace=True, axis=1)
    data.drop("High", inplace=True, axis=1)
    data.drop("Low", inplace=True, axis=1)
    data.reset_index(inplace=True)
    current_price = float(data['Close'].iloc[-1])

    buying_price = float(buying_price)
    btc = float(btc)
    Profit = (current_price - buying_price)*btc 
    if Profit < 0:
       response_data={
            'profit':Profit
            }
       json_data = json.dumps(response_data)
       return jsonify(json_data)
    else:
        response_data={
            'profit': abs(Profit)
            }
        json_data = json.dumps(response_data)
        return jsonify(json_data)


@app.route('/get_correlated_cryptos', methods=['POST'])
def get_corr_func():
    chosenCrypto = request.form.get('chosenCrypto')

    cryptocoin_dict={"BTC":"BTC-GBP","ETH":"ETH-GBP","XRP":"XRP-GBP","USDT":"USDT-GBP","USDC":"USDC-GBP","DOGE":"DOGE-GBP","XTZ":"XTZ-GBP","SOL":"SOL-GBP","TUSD":"TUSD-GBP"}

    pos, neg = get_corr(chosen_crypto = cryptocoin_dict[chosenCrypto])

    return jsonify({'positive_cryptos': pos, 'negative_cryptos': neg})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
