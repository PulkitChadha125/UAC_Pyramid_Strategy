import AngelIntegration
from datetime import datetime, timedelta
import time
import traceback
import pandas as pd
import Stockdeveloper
import TelegramIntegration as tele

print(f"Strategy developed by Programetix visit link for more development requirements : {'https://programetix.com/'} ")

client_dict={}

def get_client_detail():
    global client_dict
    try:
        csv_path = 'clientdetails.csv'
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()


        for index, row in df.iterrows():
            # Create a nested dictionary for each symbol
            symbol_dict = {
                'Title': row['Title'],
                'Value': row['Value'],
                'QtyMultiplier': row['QtyMultiplier'],
                'autotrader': None,
            }
            client_dict[row['Title']] = symbol_dict
        # print("client_dict: ", client_dict)
    except Exception as e:
        print("Error happened in fetching symbol", str(e))


get_client_detail()
def round_to_nearest(number, nearest):
    return round(number / nearest) * nearest

def get_user_settings():
    global result_dict
    # Symbol, Quantity, Segment, OptionType, StrikeDistance, EntryDate, EntryTime, ExitDate, ExitTime
    try:
        csv_path = 'TradeSettings.csv'
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        result_dict = {}
        # Symbol,EMA1,EMA2,EMA3,EMA4,lotsize,Stoploss,Target,Tsl
        for index, row in df.iterrows():
            # Create a nested dictionary for each symbol
            # StepNumberBUYCE	StepNumberSELLCE	StepNumberBUYPE	StepNumberSELLPE	SellPremium_CE	SellPremium_PE	BuyPremium_PE	BuyPremium_CE
            symbol_dict = {
                'Symbol': row['Symbol'],"Quantity":row['Quantity'],"Segment":row['Segment'],"OptionType":row['OptionType'],
                "StrikeDistance": row['StrikeDistance'],"EntryDate": row['EntryDate'],"EntryTime": row['EntryTime'],
                "ExitDate": row['ExitDate'],"ExitTime": row['ExitTime'],"InitialTrade":None,'Timeframe':row['Timeframe'],
                "Calculation": row['Calculation'], "Target": row['Target'], "Stoploss": row['Stoploss'],"TargetVal":None,
                "StoplossVal":None,"Upside":None,"Downside":None,"DownsideTradeDist":row['DownsideTradeDist'],'Traded_Qty':None,
                "lot":row['Calculation'],'lotvalue':None
            }
            result_dict[row['Symbol']] = symbol_dict
        print("result_dict: ", result_dict)
    except Exception as e:
        print("Error happened in fetching symbol", str(e))

def write_to_order_logs(message):
    with open('OrderLog.txt', 'a') as file:  # Open the file in append mode
        file.write(message + '\n')

def delete_file_contents(file_name):
    try:
        # Open the file in write mode, which truncates it (deletes contents)
        with open(file_name, 'w') as file:
            file.truncate(0)
        print(f"Contents of {file_name} have been deleted.")
    except FileNotFoundError:
        print(f"File {file_name} not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
result_dict={}

def get_api_credentials():
    credentials = {}
    delete_file_contents("OrderLog.txt")
    try:
        df = pd.read_csv('Credentials.csv')
        for index, row in df.iterrows():
            title = row['Title']
            value = row['Value']
            credentials[title] = value
    except pd.errors.EmptyDataError:
        print("The CSV file is empty or has no data.")
    except FileNotFoundError:
        print("The CSV file was not found.")
    except Exception as e:
        print("An error occurred while reading the CSV file:", str(e))

    return credentials
get_user_settings()
credentials_dict = get_api_credentials()
stockdevaccount=credentials_dict.get('stockdevaccount')
api_key=credentials_dict.get('apikey')
username=credentials_dict.get('USERNAME')
pwd=credentials_dict.get('pin')
totp_string=credentials_dict.get('totp_string')
AngelIntegration.login(api_key=api_key,username=username,pwd=pwd,totp_string=totp_string)
AngelIntegration.symbolmpping()



def stock_dev_login_multiclient(client_dict):

    for value, daram in client_dict.items():
        Title = daram['Title']
        if isinstance(Title, str):
            daram['autotrader']=Stockdeveloper.login(daram['Value'])
    print("client_dict: ",client_dict)

stock_dev_login_multiclient(client_dict)

def stockdev_multiclient_orderplacement_sell(basesymbol,client_dict,timestamp,symbol,direction,Stoploss,Target,qty,price, side):
    Orderqty=None
    for value, daram in client_dict.items():
        Title = daram['Title']
        if isinstance(Title, str):

            Orderqty=qty*daram['QtyMultiplier']
            res=Stockdeveloper.regular_order(autotrader=daram["autotrader"],account=daram['Title'], segment="NSE", symbol=symbol,
                                         direction=direction
                                         , orderType="LIMIT", productType='DELIVERY', qty=Orderqty,
                                         price=price)
            print(res)
            orderlog = (
                f"{timestamp} Sell Order executed {side} side {symbol} @  {price},stoploss= {Stoploss}, "
                f"target= {Target} : Account = {daram['Title']} ")
            print(orderlog)
            write_to_order_logs(orderlog)
def stockdev_multiclient_orderplacement_buy(basesymbol,client_dict,timestamp,symbol,direction,Stoploss,Target,qty,price, side):
    Orderqty=None
    for value, daram in client_dict.items():
        Title = daram['Title']
        if isinstance(Title, str):
            Orderqty=qty*daram['QtyMultiplier']
            res=Stockdeveloper.regular_order(autotrader=daram["autotrader"],account=daram['Title'], segment="NSE", symbol=symbol,
                                         direction=direction
                                         , orderType="LIMIT", productType='DELIVERY', qty=Orderqty,
                                         price=price)
            print(res)
            orderlog = (
                f"{timestamp} Buy Order executed {side} side {symbol} @  {price},stoploss= {Stoploss}, "
                f"target= {Target} : Account = {daram['Title']} ")
            print(orderlog)
            write_to_order_logs(orderlog)

def get_token(symbol):
    df= pd.read_csv("Instrument.csv")
    row = df.loc[df['symbol'] == symbol]
    if not row.empty:
        token = row.iloc[0]['token']
        return token

TradeQtyPriceDict={}
def main_strategy():
    global result_dict
    ltp=0
    ha_close_last=0
    ha_open_last=0
    try:
        for symbol, params in result_dict.items():
            symbol_value = params['Symbol']
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
            if isinstance(symbol_value, str):
                EntryTime = params['EntryTime']
                EntryTime = datetime.strptime(EntryTime, "%H:%M").time()
                EntryDate = params['EntryDate']
                EntryDate = datetime.strptime(EntryDate, "%d-%b-%y")

                current_date = datetime.now().date()
                current_time = datetime.now().time()
                if current_date >= EntryDate.date() and current_time.strftime("%H:%M") >= EntryTime.strftime("%H:%M"):
                    data = AngelIntegration.get_historical_data(segment="NFO", symbol=params['Symbol'],
                                                            token=get_token(params['Symbol']),
                                                            timeframe=params["Timeframe"])


                    last_row = data.iloc[-1]
                    ha_close_last = last_row['HA_close']
                    ha_open_last = last_row['HA_open']

                    print("HA_close (last row):", ha_close_last)
                    print("HA_open (last row):", ha_open_last)
                    ltp=AngelIntegration.get_ltp(segment="NFO", symbol=params['Symbol'],
                                                            token=get_token(params['Symbol']))
                    print("ltp: ",ltp)
                if current_date == EntryDate.date() and current_time.strftime("%H:%M") == EntryTime.strftime("%H:%M") :


                    if params["InitialTrade"]==None:
                        params["InitialTrade"]="BUY"
                        if params["Calculation"]=="POINT":
                            params["TargetVal"]=ltp+params["Target"]
                            params["Upside"]=ltp+params["Target"]
                            params["Downside"] = ltp-params["DownsideTradeDist"]

                        if params["Calculation"]=="PERCENTAGE":
                            params["TargetVal"]=ltp*params["Target"]
                            params["TargetVal"]=params["TargetVal"]+ltp
                            params["Upside"]=ltp+params["TargetVal"]
                            params["Downside"] = ltp-params["DownsideTradeDist"]

                        params["lotvalue"]=params["lot"]
                        trade_price = ltp  # Assuming ltp is the trade price, adjust if needed
                          # Assuming params contains Quantity, adjust if needed
                        TradeQtyPriceDict[symbol_value] = {
                            "trade_price": trade_price,
                            "lot": params["lot"],
                            "lot_value":params["lotvalue"],
                            "amount_invested":trade_price* params["lotvalue"]
                        }

                        OrderLog=f"{timestamp} Initial buy trade executed @ {symbol_value}, Target : {params['TargetVal']},Buy trade Val: {params['Upside']},Sell Trade Val: {params['Downside']}"
                        print(OrderLog)

                    if params["InitialTrade"]=="BUY":
                        if ltp>=params['TargetVal'] and params['TargetVal']is not None :
                            TradeQtyPriceDict.clear()

                            params["InitialTrade"]=None
                            OrderLog = f"{timestamp} Target Executed @ {symbol_value}, Target : {params['TargetVal']},Buy trade Val: {params['Upside']},Sell Trade Val: {params['Downside']}"
                            print(OrderLog)

                        if ltp >= params["Upside"] and params["Upside"] is not None:
                            if params["Calculation"] == "POINT":
                                params["TargetVal"] = ltp + params["Target"]
                                params["Upside"] = ltp + params["Target"]
                                params["Downside"] = ltp - params["DownsideTradeDist"]

                            if params["Calculation"] == "PERCENTAGE":
                                params["TargetVal"] = ltp * params["Target"]
                                params["TargetVal"] = params["TargetVal"] + ltp
                                params["Upside"] = ltp + params["TargetVal"]
                                params["Downside"] = ltp - params["DownsideTradeDist"]

                            params["lotvalue"] = params["lot"]
                            trade_price = ltp
                            TradeQtyPriceDict[symbol_value] = {
                                "trade_price": trade_price,
                                "lot": params["lot"],
                                "lot_value": params["lotvalue"],
                                "amount_invested": trade_price * params["lotvalue"]
                            }

                            OrderLog = f"{timestamp} Previous buy exited opening new buy trade  @ {symbol_value}, Target : {params['TargetVal']},Buy trade Val: {params['Upside']},Sell Trade Val: {params['Downside']}"
                            print(OrderLog)

                        if ltp <= params["Downside"] and params["Downside"] is not None and ha_close_last==ha_open_last :

                            params["lotvalue"] = params["lot"]*2
                            trade_price = ltp
                            TradeQtyPriceDict[symbol_value] = {
                                "trade_price": trade_price,
                                "lot": params["lot"],
                                "lot_value": params["lotvalue"],
                                "amount_invested": trade_price * params["lotvalue"]
                            }

                            if params["Calculation"] == "POINT":
                                total_amount_invested = sum(
                                    item["amount_invested"] for item in TradeQtyPriceDict.values())
                                totallottaken=sum(
                                    item["lot_value"] for item in TradeQtyPriceDict.values())
                                avgerage=total_amount_invested/totallottaken
                                params["TargetVal"] = avgerage + params["Target"]
                                params["Upside"] = None
                                params["Downside"] = ltp - params["DownsideTradeDist"]

                            if params["Calculation"] == "PERCENTAGE":
                                total_amount_invested = sum(
                                    item["amount_invested"] for item in TradeQtyPriceDict.values())
                                totallottaken = sum(
                                    item["lot_value"] for item in TradeQtyPriceDict.values())
                                avgerage = total_amount_invested / totallottaken
                                params["TargetVal"] = avgerage * params["Target"]
                                params["TargetVal"] = params["TargetVal"] + ltp
                                params["Upside"] = None
                                params["Downside"] = ltp - params["DownsideTradeDist"]


                            OrderLog = (f"{timestamp} {symbol_value}  opening the double lotsize buy {params['Quantity'] } updated target value : {params['TargetVal'] }")
                            print(OrderLog)






    except Exception as e:
        print("Error happened in Main strategy loop: ", str(e))
        traceback.print_exc()


while True:
    main_strategy()
    time.sleep(2)

