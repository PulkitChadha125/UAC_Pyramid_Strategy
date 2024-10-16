import AngelIntegration
from datetime import datetime, timedelta
import time
import traceback
import pandas as pd
import Stockdeveloper
import TelegramIntegration as tele


def round_down_to_interval(dt, interval_minutes):
    remainder = dt.minute % interval_minutes
    minutes_to_current_boundary = remainder
    rounded_dt = dt - timedelta(minutes=minutes_to_current_boundary)
    rounded_dt = rounded_dt.replace(second=0, microsecond=0)
    return rounded_dt

def determine_min(minstr):
    min = 0
    if minstr == "1":
        min = 1
    if minstr == "3":
        min = 3
    if minstr == "5":
        min = 5
    if minstr == "15":
        min = 15
    if minstr == "30":
        min = 30

    return min

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

def normalize_current_time(dt, interval_minutes):
    # Remove seconds and microseconds
    dt = dt.replace(second=0, microsecond=0)
    # Normalize to the **previous** interval
    normalized_minute = (dt.minute // interval_minutes) * interval_minutes
    normalized_dt = dt.replace(minute=normalized_minute)
    return normalized_dt


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
                "Calculation": row['Calculation'],"CallTargetVal":None,"PutTargetVal":None,'UpsideTrdeDist':row['UpsideTrdeDist'],
                "UpsideCall":None,"DownsideCall":None,"UpsidePut":None,"DownsidePut":None,"DownsideTradeDist":row['DownsideTradeDist'],'Traded_Qty':None,
                "lotCall":row['lot'],'lotvalueCall':None,"lotPut":row['lot'],'lotvaluePut':None,'StrikeStep':row['StrikeStep'],'BaseSymbol':row['BaseSymbol'],'TradeExpiery':row['TradeExpiery'],
                "Initialcall":None,"InitialPut":None,"UpdatedCall":None,"UpdatedPut":None,"InitialLotsCall":None,"InitialLotsPut":None,
                "UpdatedLotsCall": None, "UpdatedLotsPut": None,"FormatedDate":None,'CandlePercent':row['CandlePercent'],"callltp":None,"putltp":None,"count":0,
                'NoOfAverage':row['NoOfAverage'],'callavgcount':0,'putaveragecount':0,"putaveragetime":datetime.now(),"callaveragetime":datetime.now(),'TFMIN':row['TFMIN'],
                'AverageTargetDist':row['AverageTargetDist'],'ha_close_last_put':None,'ha_open_last_put':None,'ha_high_last_put':None,'ha_low_last_put':None,
                'ha_close_last_call':None,'ha_open_last_call':None,'ha_high_last_call':None,'ha_low_last_call':None,"runtimecall": datetime.now(),"runtimeput": datetime.now(),
                "callcheck": None, "putcheck": None,"StockDevPutSymbol":None,"StockDevCallSymbol":None,"callstrike":None,'putstrike':None,'combinedexitdatetime': None
            }
            result_dict[row['Symbol']] = symbol_dict
        print("result_dict: ", result_dict)
    except Exception as e:
        print("Error happened in fetching symbol", str(e))

def StokDevlogs(message):
    with open('StockDevLog.txt', 'a') as file:  # Open the file in append mode
        file.write(message + '\n')


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
    delete_file_contents("StockDevLog.txt")
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


def is_candle_body_within_percent(open_price, high, low, close, percent):
    candle_length = high - low
    if open_price > close:
        candle_body = open_price - close
    else:
        candle_body = close - open_price
    return candle_body <= (percent / 100) * candle_length

def stock_dev_login_multiclient(client_dict):

    for value, daram in client_dict.items():
        Title = daram['Title']
        if isinstance(Title, str):
            daram['autotrader']=Stockdeveloper.login(daram['Value'])
    print("client_dict: ",client_dict)

stock_dev_login_multiclient(client_dict)

def stockdev_multiclient_orderplacement_buy(basesymbol,client_dict,timestamp,symbol,direction,Stoploss,Target,qty,price, side):
    Orderqty=None
    for value, daram in client_dict.items():
        Title = daram['Title']
        if isinstance(Title, str):
            Orderqty=qty*daram['QtyMultiplier']
            res=Stockdeveloper.regular_order(autotrader=daram["autotrader"],account=daram['Title'], segment="NSE", symbol=symbol,
                                         direction=direction, orderType="MARKET", productType='NORMAL', qty=Orderqty,
                                         price=price)
            print(res)
            orderlog = (
                f"{timestamp} Buy Order executed {side} side {symbol} @  {price},stoploss= {Stoploss}, "
                f"target= {Target} : Account = {daram['Title']} ")
            print(orderlog)
            StokDevlogs(orderlog)

def stockdev_multiclient_orderplacement_exit(basesymbol,client_dict,timestamp,symbol,direction,Stoploss,Target,qty,price,log):
    Orderqty = None
    for value, daram in client_dict.items():
        Title = daram['Title']
        Orderqty=qty*daram['QtyMultiplier']
        Stockdeveloper.regular_order(autotrader=daram["autotrader"],account=daram['Title'], segment="NSE", symbol=symbol,
                                         direction=direction, orderType="MARKET", productType='NORMAL', qty=Orderqty,
                                         price=price)
        orderlog = (
                f"{timestamp} {log} {symbol} @  {price} "
                f"target= {Target} : Account = {daram['Title']} ")
        print(orderlog)
        StokDevlogs(orderlog)



def get_token(symbol):
    df= pd.read_csv("Instrument.csv")
    row = df.loc[df['symbol'] == symbol]
    if not row.empty:
        token = row.iloc[0]['token']
        return token

tradedictcall={}
tradedictput={}
TradeQtyPriceDict={}


def normalize_to_lower_5_min(time):
    normalized_minute = (time.minute // 5) * 5
    return time.replace(minute=normalized_minute, second=0, microsecond=0)


def add_and_normalize_time(minutes_to_add):
    current_time = datetime.now()
    new_time = current_time + timedelta(minutes=minutes_to_add)
    normalized_time = normalize_to_lower_5_min(new_time)
    return new_time, normalized_time

def main_strategy():
    print("Main strategy running ")
    global result_dict,tradedictcall,tradedictput
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

                ExitTime = params['ExitTime']
                ExitTime = datetime.strptime(ExitTime, "%H:%M").time()

                ExitDate = params['ExitDate']
                ExitDate = datetime.strptime(ExitDate, "%d-%b-%y")
                combined_exit_datetime = datetime.combine(ExitDate, ExitTime)

                print("EntryDate: ", EntryDate)
                print("EntryTime: ", EntryTime)
                print("ExitTime: ",ExitTime)
                print("ExitDate: ", ExitDate)
                print("Current time: ",datetime.now())
                params['combinedexitdatetime'] =combined_exit_datetime
                print("combined_exit_datetime: ", params['combinedexitdatetime'])



                current_date = datetime.now().date()
                current_time = datetime.now().time()
                print(
                    f"{timestamp} InitialTrade: {params['InitialTrade']}, Initialcall: {params['Initialcall']}, InitialPut: {params['InitialPut']},"
                    f"UpsideCall: {params['UpsideCall']},UpsidePut: {params['UpsidePut']},DownsideCall: {params['DownsideCall']},DownsidePut: {params['DownsidePut']},"
                    f" Call ltp : {params['callltp']}, PutLtp: {params['putltp']}")

                if current_date >= EntryDate.date() and current_time.strftime("%H:%M") >= EntryTime.strftime("%H:%M"):
                    try:
                        ltp=AngelIntegration.get_ltp(segment="NFO", symbol=params['Symbol'],
                                                            token=get_token(params['Symbol']))

                    except Exception as e:
                        print("Error happened in fetching spot ltp : ", str(e))
                        time.sleep(1)
                        ltp = AngelIntegration.get_ltp(segment="NFO", symbol=params['Symbol'],
                                                       token=get_token(params['Symbol']))


                    rounded_price=round_to_nearest(number=ltp, nearest=params['StrikeStep'])
                    print("Ltp rounded_price: ",rounded_price)

                    if params['OptionType']=="ATM":
                        selectedstrikecall= rounded_price
                        selectedstrikeput = rounded_price
                    if params['OptionType']=="OTM":
                        selectedstrikecall= rounded_price+ int(params["StrikeDistance"])
                        selectedstrikeput = rounded_price- int(params["StrikeDistance"])
                    if params['OptionType']=="ITM":
                        selectedstrikecall= rounded_price - int(params["StrikeDistance"])
                        selectedstrikeput = rounded_price+ int(params["StrikeDistance"])

                if current_date == EntryDate.date() and current_time.strftime("%H:%M") == EntryTime.strftime("%H:%M") :
                    date_obj = datetime.strptime(params["TradeExpiery"], "%d-%b-%y")
                    formatted_date = date_obj.strftime("%d%b%y").upper()
                    params["FormatedDate"]= formatted_date
                    print(formatted_date)


                    if params["InitialTrade"]==None:
                        params["callstrike"]= selectedstrikecall
                        params['putstrike']= selectedstrikeput
                        params["Initialcall"] = f"{params['BaseSymbol']}{params['FormatedDate']}{selectedstrikecall}CE"
                        params["InitialPut"] = f"{params['BaseSymbol']}{params['FormatedDate']}{selectedstrikeput}PE"
                        print("InitialPut: ",params["InitialPut"])
                        print("Initialcall: ", params["Initialcall"])
                        try:
                            params["callltp"] = AngelIntegration.get_ltp(segment="NFO", symbol=params["Initialcall"],
                                                           token=get_token(params["Initialcall"]))
                        except Exception as e:
                            print("Error happened in fetching call ltp : ", str(e))
                            time.sleep(1)
                            params["callltp"] = AngelIntegration.get_ltp(segment="NFO", symbol=params["Initialcall"],
                                                                         token=get_token(params["Initialcall"]))

                        try:
                            params["putltp"] = AngelIntegration.get_ltp(segment="NFO", symbol=params["InitialPut"],
                                                          token=get_token(params["InitialPut"]))

                        except Exception as e:
                            print("Error happened in fetching put ltp : ", str(e))
                            time.sleep(1)
                            params["putltp"] = AngelIntegration.get_ltp(segment="NFO", symbol=params["InitialPut"],
                                                                        token=get_token(params["InitialPut"]))

                        print("callltp: ",params["callltp"])
                        print("putltp: ",params["putltp"])

                        params["InitialTrade"]="BUY"

                        if params["Calculation"]=="POINT":

                            params["UpsideCall"]=params["callltp"] + params["UpsideTrdeDist"]
                            params["UpsidePut"] = params["putltp"] + params["UpsideTrdeDist"]

                            params["DownsideCall"] = params["callltp"]-params["DownsideTradeDist"]
                            params["DownsidePut"] = params["putltp"] - params["DownsideTradeDist"]

                        if params["Calculation"]=="PERCENTAGE":

                            params["UpsideCall"]=params["callltp"]* params["UpsideTrdeDist"]*0.01
                            params["UpsideCall"]=params["UpsideCall"]+params["callltp"]

                            params["UpsidePut"] = params["putltp"]* params["UpsideTrdeDist"]*0.01
                            params["UpsidePut"]=params["UpsidePut"]+params["putltp"]

                            params["DownsideCall"] = params["callltp"]* params["DownsideTradeDist"]*0.01
                            params["DownsideCall"]=params["callltp"]-params["DownsideCall"]

                            params["DownsidePut"] = params["putltp"] * params["DownsideTradeDist"]*0.01
                            params["DownsidePut"] = params["putltp"] - params["DownsidePut"]

                        params["lotvalueCall"]=params["lotCall"]
                        params["lotvaluePut"] = params["lotPut"]

                        params["InitialLotsPut"] = params["Quantity"]
                        params["InitialLotsCall"] = params["Quantity"]
                        params["UpdatedLotsCall"] = params["Quantity"]
                        params["UpdatedLotsPut"] = params["Quantity"]
                        # "lotCall": row['lot'], 'lotvalueCall': None, "lotPut": row['lot'], 'lotvaluePut': None
                        params["StockDevPutSymbol"] = f"{params['BaseSymbol']}_{Stockdeveloper.convert_date(params['TradeExpiery'])}_PE_{params['putstrike']}"
                        params["StockDevCallSymbol"] = f"{params['BaseSymbol']}_{Stockdeveloper.convert_date(params['TradeExpiery'])}_CE_{params['callstrike']}"
                        tradedictcall[f"trade_{len(tradedictcall) + 1}"] = {
                            "tradeltp": params["callltp"],
                            "Lots": params["lotvalueCall"],
                            "Moneyinvested": params["lotvalueCall"] * params["callltp"],
                            "StockDevSymbol":params["StockDevCallSymbol"],
                            "StockDevQty": params['UpdatedLotsCall'],
                        }
                        tradedictput[f"trade_{len(tradedictput) + 1}"] = {
                            "tradeltp": params["putltp"],
                            "Lots": params["lotvaluePut"],
                            "Moneyinvested": params["lotvaluePut"] * params["putltp"],
                            "StockDevSymbol": params["StockDevPutSymbol"],
                            "StockDevQty": params['UpdatedLotsPut'],
                        }
                        new_time, params["putaveragetime"] = add_and_normalize_time(10)
                        new_time, params["callaveragetime"] = add_and_normalize_time(10)
                        params["count"]=params["count"]+1
                        OrderLog=(f"{timestamp} Initial buy trade executed @ {symbol_value}, CallSymbol{params['Initialcall']},"
                                  f" CallLtp= {params['callltp']}, CallUpsideTarget={params['UpsideCall']},CalldownsideAverage: {params['DownsideCall']}, lots={params['UpdatedLotsCall'] },callaveragetime: {params['callaveragetime']}")
                        print(OrderLog)
                        write_to_order_logs(OrderLog)
                        OrderLog = (f"{timestamp} Initial buy trade executed @ {symbol_value}, PutSymbol{params['InitialPut']},"
                                    f" putLtp= {params['putltp']}, PutUpsideTarget={params['UpsidePut']},PutdownsideAverage:{params['DownsidePut']}, lots={params['UpdatedLotsPut']}, putaveragetime: {params['putaveragetime']}")
                        print(OrderLog)
                        write_to_order_logs(OrderLog)
                        params["callstrike"] = selectedstrikecall
                        params['putstrike'] = selectedstrikeput

                        stockdev_multiclient_orderplacement_buy(basesymbol=params['BaseSymbol'], client_dict=client_dict,
                                                        timestamp=timestamp, symbol=params["StockDevPutSymbol"],
                                                        direction="BUY", Stoploss=0,Target=0,qty=params["Quantity"], price=params["putltp"], side="PUT")

                        stockdev_multiclient_orderplacement_buy(basesymbol=params['BaseSymbol'],
                                                                client_dict=client_dict,timestamp=timestamp, symbol=params["StockDevCallSymbol"],
                                                                direction="BUY", Stoploss=0,Target=0,qty=params["Quantity"], price=params["callltp"],
                                                                side="CALL")

                if params["InitialTrade"]=="BUY":
                    #  call ka calculation
                    print("InitialPut: ", params["InitialPut"])
                    print("Initialcall: ", params["Initialcall"])
                    try:
                        params["callltp"] = AngelIntegration.get_ltp(segment="NFO", symbol=params["Initialcall"],
                                                               token=get_token(params["Initialcall"]))
                    except Exception as e:
                        print("Error happened in fetching call ltp : ", str(e))
                        time.sleep(1)
                        params["callltp"] = AngelIntegration.get_ltp(segment="NFO", symbol=params["Initialcall"],
                                                                     token=get_token(params["Initialcall"]))

                    try:
                        params["putltp"] = AngelIntegration.get_ltp(segment="NFO", symbol=params["InitialPut"],
                                                          token=get_token(params["InitialPut"]))

                    except Exception as e:
                        print("Error happened in fetching put ltp : ", str(e))
                        time.sleep(1)
                        params["putltp"] = AngelIntegration.get_ltp(segment="NFO", symbol=params["InitialPut"],
                                                                    token=get_token(params["InitialPut"]))

                    print("callltp trade buy: ", params["callltp"])
                    print("UpsideCall: ", params["UpsideCall"])
                    print("UpsideCall: ", params["UpsideCall"])
                    print("putltp trade buy: ", params["putltp"])
                    print("callltp trade buy: ", params["callltp"])

                    if datetime.now() >= params["runtimecall"]:
                        try:

                            time.sleep(1)
                            data_call = AngelIntegration.get_historical_data(segment="NFO", symbol=params["Initialcall"],
                                                                        token=get_token(params["Initialcall"]),
                                                                        timeframe=params["Timeframe"])
                        except Exception as e:
                            print("Error happened in fetching call historical data : ", str(e))
                            time.sleep(1)
                            data_call = AngelIntegration.get_historical_data(segment="NFO", symbol=params["Initialcall"],
                                                                             token=get_token(params["Initialcall"]),
                                                                             timeframe=params["Timeframe"])

                        last_row_call = data_call.iloc[-1]
                        last_rowtime = last_row_call['date']  # Assuming this is a pandas Timestamp

                        given_time = last_rowtime.time()

                        curr_time = normalize_current_time(datetime.now(), params['TFMIN'])
                        time.sleep(1)
                        if curr_time.hour == given_time.hour and curr_time.minute == given_time.minute:
                            last_row_call = data_call.iloc[-2]
                            print("Previous call contract row : ",last_row_call)
                            params["callcheck"]= last_row_call['date']
                            params['ha_close_last_call'] = last_row_call['HA_close']
                            params['ha_open_last_call'] = last_row_call['HA_open']
                            params['ha_high_last_call'] = last_row_call['HA_high']
                            params['ha_low_last_call'] = last_row_call['HA_low']
                        else:

                            last_row_call = data_call.iloc[-1]
                            params["callcheck"] = last_row_call['date']
                            print("last_row_call: ",last_row_call)
                            params['ha_close_last_call'] = last_row_call['HA_close']
                            params['ha_open_last_call'] = last_row_call['HA_open']
                            params['ha_high_last_call'] = last_row_call['HA_high']
                            params['ha_low_last_call'] = last_row_call['HA_low']
                            next_specific_part_time = datetime.now() + timedelta(
                                seconds=determine_min(str(params["TFMIN"])) * 60)
                            next_specific_part_time = round_down_to_interval(next_specific_part_time,
                                                                             determine_min(str(params["TFMIN"])))
                            print("Next datafetch time = ", next_specific_part_time)
                            params['runtimecall'] = next_specific_part_time


                        if datetime.now() >= params["runtimeput"]:

                            try:

                                time.sleep(2)
                                data_put = AngelIntegration.get_historical_data(segment="NFO", symbol=params["InitialPut"],
                                                                                     token=get_token(params["InitialPut"]),
                                                                                     timeframe=params["Timeframe"])
                            except Exception as e:
                                print("Error happened in fetching put historical data : ", str(e))
                                time.sleep(1)
                                data_put = AngelIntegration.get_historical_data(segment="NFO", symbol=params["InitialPut"],
                                                                                token=get_token(params["InitialPut"]),
                                                                                timeframe=params["Timeframe"])
                            last_row_put = data_put.iloc[-1]
                            last_rowtime = last_row_put['date']  # Assuming this is a pandas Timestamp

                            given_time = last_rowtime.time()

                            curr_time = normalize_current_time(datetime.now(), params['TFMIN'])
                            time.sleep(1)
                            if curr_time.hour == given_time.hour and curr_time.minute == given_time.minute:
                                last_row_put = data_put.iloc[-2]
                                print("last_row_put: ",last_row_put)
                                params["putcheck"]= last_row_put['date']
                                params['ha_close_last_put'] = last_row_put['HA_close']
                                params['ha_open_last_put']= last_row_put['HA_open']
                                params['ha_high_last_put']= last_row_put['HA_high']
                                params['ha_low_last_put']= last_row_put['HA_low']
                            else:

                                last_row_put = data_put.iloc[-1]
                                print("last_row_put: ",last_row_put)
                                params["putcheck"] = last_row_put['date']
                                params['ha_close_last_put'] = last_row_put['HA_close']
                                params['ha_open_last_put'] = last_row_put['HA_open']
                                params['ha_high_last_put'] = last_row_put['HA_high']
                                params['ha_low_last_put'] = last_row_put['HA_low']

                            next_specific_part_time = datetime.now() + timedelta(
                                seconds=determine_min(str(params["TFMIN"])) * 60)
                            next_specific_part_time = round_down_to_interval(next_specific_part_time,
                                                                             determine_min(str(params["TFMIN"])))
                            print("Next datafetch time = ", next_specific_part_time)
                            params['runtimeput'] = next_specific_part_time



                    # print("Callaveragetime :", params["callaveragetime"])
                    # print("putaverage time :", params["putaveragetime"])
                    # print("///////////////////////////////////////")
                    # print("CallPreviouscandletime :",params["callcheck"])
                    # print("putPreviouscandletime :",params["putcheck"])
                    # print("///////////////////////////////////////")
                    # print("hahigh call:", params['ha_high_last_call'])
                    # print("halow call:", params['ha_low_last_call'])
                    # print("haclose call:", params['ha_close_last_call'])
                    # print("haopen call:", params['ha_open_last_call'])

                    print("Ha condition call : ", is_candle_body_within_percent(close=params['ha_close_last_call'],
                                                                                open_price=params[
                                                                                    'ha_open_last_call'],
                                                                                high=params['ha_high_last_call'],
                                                                                low=params['ha_low_last_call'],
                                                                                percent=params['CandlePercent']))

                    print("hahigh put:", params['ha_high_last_put'])
                    print("halow put:", params['ha_low_last_put'])
                    print("haclose put:", params['ha_close_last_put'])
                    print("haopen put:", params['ha_open_last_put'])

                    print("Ha condition put : ", is_candle_body_within_percent(close=params['ha_close_last_put'],
                                                                                open_price=params[
                                                                                    'ha_open_last_put'],
                                                                                high=params['ha_high_last_put'],
                                                                                low=params['ha_low_last_put'],
                                                                                percent=params['CandlePercent']))


                    if params["putltp"]>=params["UpsidePut"] and params["UpsidePut"] is not None:
                        total_stock_dev_qty = sum(trade["StockDevQty"] for trade in tradedictput.values())
                        stockdev_multiclient_orderplacement_exit(
                                basesymbol=params['BaseSymbol'],  # Basesymbol from params
                                client_dict=client_dict,  # Assuming client_dict is defined elsewhere
                                timestamp=timestamp,  # Assuming timestamp is defined elsewhere
                                symbol=next(iter(tradedictput.values()))['StockDevSymbol'],  # Symbol from tradedictput
                                direction="SELL",  # Direction is "SELL"
                                Stoploss=0,  # Stoploss is 0 as per your example
                                Target=0,  # Target is 0 as per your example
                                qty=total_stock_dev_qty,  # Quantity from tradedictput
                                price=params["callltp"],  # LTP (Last Traded Price) from tradedictput
                                log=f"UpsidePut executed exiting put trade {next(iter(tradedictput.values()))['StockDevSymbol']} @ "  # Log message includes the key
                            )

                        tradedictput.clear()
                        params["putaveragetime"]=None

                        if datetime.now() <= params['combinedexitdatetime']:
                            new_time, params["putaveragetime"] = add_and_normalize_time(10)
                            params['putaveragecount']=0
                            exitprice = params["putltp"]


                            try:
                                ltp = AngelIntegration.get_ltp(segment="NFO", symbol=params['Symbol'],
                                                               token=get_token(params['Symbol']))

                            except Exception as e:
                                print("Error happened in fetching spot ltp : ", str(e))
                                time.sleep(1)
                                ltp = AngelIntegration.get_ltp(segment="NFO", symbol=params['Symbol'],
                                                               token=get_token(params['Symbol']))
                            rounded_price = round_to_nearest(number=ltp, nearest=params['StrikeStep'])
                            print("rounded_price: ", rounded_price)


                            if params['OptionType'] == "ATM":
                                selectedstrikecall = rounded_price
                                selectedstrikeput = rounded_price
                            if params['OptionType'] == "OTM":
                                selectedstrikecall = rounded_price + int(params["StrikeDistance"])
                                selectedstrikeput = rounded_price - int(params["StrikeDistance"])
                            if params['OptionType'] == "ITM":
                                selectedstrikecall = rounded_price - int(params["StrikeDistance"])
                                selectedstrikeput = rounded_price + int(params["StrikeDistance"])


                            params['putstrike'] = selectedstrikeput
                            params["StockDevPutSymbol"] = f"{params['BaseSymbol']}_{Stockdeveloper.convert_date(params['TradeExpiery'])}_PE_{params['putstrike']}"

                            params["UpdatedPut"] = f"{params['BaseSymbol']}{params['FormatedDate']}{selectedstrikeput}PE"
                            params["putltp"]=AngelIntegration.get_ltp(segment='NFO', symbol=params['UpdatedPut'],token=get_token(params['UpdatedPut']))
                            params["lotvaluePut"] = params["lotPut"]
                            params["count"] = 1
                            params["InitialLotsPut"] = params["Quantity"]
                            params["UpdatedLotsPut"] = params["InitialLotsPut"]
                            tradedictput[f"trade_{len(tradedictput) + 1}"] = {
                                "tradeltp": params["putltp"],
                                "Lots": params["lotvaluePut"],
                                "Moneyinvested": params["lotvaluePut"] * params["putltp"],
                                "StockDevSymbol": params["StockDevPutSymbol"],
                                "StockDevQty": params['Quantity'],
                            }

                            if params["Calculation"] == "POINT":
                                params["UpsidePut"] = params["putltp"] + params["UpsideTrdeDist"]
                                params["DownsidePut"] = params["putltp"] - params["DownsideTradeDist"]
                            if params["Calculation"] == "PERCENTAGE":
                                params["UpsidePut"] = params["putltp"] * params["UpsideTrdeDist"]*0.01
                                params["UpsidePut"] = params["UpsidePut"] + params["putltp"]
                                params["DownsidePut"] = params["putltp"] * params["DownsideTradeDist"]*0.01
                                params["DownsidePut"] = params["putltp"] - params["DownsidePut"]


                            OrderLog = (f"{timestamp} UpsidePut: Previous buy put exited {params['InitialPut']} @ exitprice= {exitprice} opening new buy trade  put@ "
                                            f"{params['UpdatedPut']} @ {params['putltp']},  "
                                        f"  Put Upside target : {params['UpsidePut']},"
                                            f"Put downside Average  Val: {params['DownsidePut']}, put aversge check time : {params['putaveragetime'] }")
                            print(OrderLog)
                            write_to_order_logs(OrderLog)
                            params["InitialPut"] = params["UpdatedPut"]
                            stockdev_multiclient_orderplacement_buy(basesymbol=params['BaseSymbol'],
                                                                    client_dict=client_dict,
                                                                    timestamp=timestamp, symbol=params["StockDevPutSymbol"],
                                                                    direction="BUY", Stoploss=0,
                                                                    Target=0,
                                                                    qty=params["Quantity"], price=params["putltp"],
                                                                    side="PUT")

                    if params["callltp"] >= params["UpsideCall"] and params["UpsideCall"] is not None:
                        total_stock_dev_qty = sum(trade["StockDevQty"] for trade in tradedictcall.values())
                        stockdev_multiclient_orderplacement_exit(
                                basesymbol=params['BaseSymbol'],  # Basesymbol from params
                                client_dict=client_dict,  # Assuming client_dict is defined elsewhere
                                timestamp=timestamp,  # Assuming timestamp is defined elsewhere
                                symbol=next(iter(tradedictcall.values()))["StockDevSymbol"],  # Symbol from tradedictput
                                direction="SELL",  # Direction is "SELL"
                                Stoploss=0,  # Stoploss is 0 as per your example
                                Target=0,  # Target is 0 as per your example
                                qty=total_stock_dev_qty,  # Quantity from tradedictput
                                price=params["callltp"],  # LTP (Last Traded Price) from tradedictput
                                log=f"UpsideCall executed previous call exited {next(iter(tradedictcall.values()))['StockDevSymbol']} @ "  # Log message includes the key
                            )

                        tradedictcall.clear()
                        params["callaveragetime"]=None
                        if datetime.now() <= params['combinedexitdatetime']:
                            new_time, params["callaveragetime"] = add_and_normalize_time(10)
                            params['callavgcount']=0
                            exitprice=params["callltp"]


                            try:
                                ltp = AngelIntegration.get_ltp(segment="NFO", symbol=params['Symbol'],
                                                                   token=get_token(params['Symbol']))

                            except Exception as e:
                                print("Error happened in fetching spot ltp : ", str(e))
                                time.sleep(1)
                                ltp = AngelIntegration.get_ltp(segment="NFO", symbol=params['Symbol'],
                                                               token=get_token(params['Symbol']))

                            rounded_price = round_to_nearest(number=ltp, nearest=params['StrikeStep'])
                            print("rounded_price: ", rounded_price)
                            if params['OptionType'] == "ATM":
                                selectedstrikecall = rounded_price
                                selectedstrikeput = rounded_price
                            if params['OptionType'] == "OTM":
                                selectedstrikecall = rounded_price + int(params["StrikeDistance"])
                                selectedstrikeput = rounded_price - int(params["StrikeDistance"])
                            if params['OptionType'] == "ITM":
                                selectedstrikecall = rounded_price - int(params["StrikeDistance"])
                                selectedstrikeput = rounded_price + int(params["StrikeDistance"])

                            params["callstrike"] = selectedstrikecall
                            params["StockDevCallSymbol"] = f"{params['BaseSymbol']}_{Stockdeveloper.convert_date(params['TradeExpiery'])}_CE_{params['callstrike']}"
                            params["UpdatedCall"] = f"{params['BaseSymbol']}{params['FormatedDate']}{selectedstrikecall}CE"
                            params["callltp"]=AngelIntegration.get_ltp(segment='NFO', symbol=params['UpdatedCall'],token=get_token(params['UpdatedCall']))
                            params["lotvalueCall"] = params["lotCall"]
                            params["count"] = 1
                            params["InitialLotsCall"] = params["Quantity"]
                            params["UpdatedLotsCall"] = params["InitialLotsCall"]
                            tradedictcall[f"trade_{len(tradedictcall) + 1}"] = {
                                "tradeltp": params["callltp"],
                                "Lots": params["lotvalueCall"],
                                "Moneyinvested": params["lotvalueCall"] * params["callltp"],
                                "StockDevSymbol": params["StockDevCallSymbol"],
                                "StockDevQty": params['Quantity'],
                            }
                            if params["Calculation"] == "POINT":
                                params["UpsideCall"] = params["callltp"] + params["UpsideTrdeDist"]
                                params["DownsideCall"] = params["callltp"] - params["DownsideTradeDist"]


                            if params["Calculation"] == "PERCENTAGE":
                                params["UpsideCall"] = params["callltp"] * params["UpsideTrdeDist"]*0.01
                                params["UpsideCall"] = params["UpsideCall"] + params["callltp"]
                                params["DownsideCall"] = params["callltp"] * params["DownsideTradeDist"]*0.01
                                params["DownsideCall"] = params["callltp"] - params["DownsideCall"]


                            OrderLog = (f"{timestamp} UpsideCall: Previous buy call exited {params['Initialcall']}@ {exitprice} opening new buy trade  call @"
                                            f" {params['UpdatedCall']} @ {params['callltp']}, Call upside target Val : {params['UpsideCall'] },Call downside average Val: {params['DownsideCall']}"
                                        f", call aversge check time : {params['callaveragetime'] }"
                                            )
                            print(OrderLog)
                            write_to_order_logs(OrderLog)
                            params["Initialcall"] = params["UpdatedCall"]
                            stockdev_multiclient_orderplacement_buy(basesymbol=params['BaseSymbol'],
                                                                    client_dict=client_dict,
                                                                    timestamp=timestamp,
                                                                    symbol=params["StockDevCallSymbol"],
                                                                    direction="BUY", Stoploss=0,
                                                                    Target=0,
                                                                    qty=params["Quantity"], price=params["callltp"],
                                                                    side="CALL")



                    normalized_now = normalize_current_time(datetime.now(), params['TFMIN'])
                    print("normalized_now :", normalized_now)

                    if (params['putaveragecount'] < params['NoOfAverage'] and
                            normalized_now >= params["putaveragetime"] and
                            params["putaveragetime"] is not None and
                            params["DownsidePut"] is not None and
                            params['ha_close_last_put'] < params["DownsidePut"] and
                            is_candle_body_within_percent(
                                close=params['ha_close_last_put'],
                                open_price=params['ha_open_last_put'],
                                high=params['ha_high_last_put'],
                                low=params['ha_low_last_put'],
                                percent=params['CandlePercent']
                            )==True and datetime.now() <= params['combinedexitdatetime']):
                        # params["putaveragetime"] = datetime.now() + timedelta(minutes=params['TFMIN'])
                        new_time, params["putaveragetime"] = add_and_normalize_time(params['TFMIN'])

                        OrderLog = (
                            f"{timestamp} Initiateing downside trade put @ {symbol_value} next put average time : {params['putaveragetime']}, normalised time= {normalized_now}, check time put ={params['runtimeput']}")
                        print(OrderLog)
                        write_to_order_logs(OrderLog)
                        print("InitialLotsPut: ",params["lotvaluePut"])
                        print("putltp: ", params["putltp"])
                        params["UpdatedLotsPut"] = int(params["UpdatedLotsPut"] * 2)
                        params["lotvaluePut"] = params["lotvaluePut"] * 2
                        tradedictput[f"trade_{len(tradedictput) + 1}"] = {
                            "tradeltp": params["putltp"],
                            "Lots": params["lotvaluePut"],
                            "Moneyinvested": params["lotvaluePut"] * params["putltp"],
                            "StockDevSymbol": params["StockDevPutSymbol"],
                            "StockDevQty": params['UpdatedLotsPut'],
                        }
                        print("tradedictput: ", tradedictput)
                        write_to_order_logs(f"tradedictput: {tradedictput}")

                        total_money_invested_put = sum(trade["Moneyinvested"] for trade in tradedictput.values())
                        average_money_invested_put = total_money_invested_put / sum(
                            trade["Lots"] for trade in tradedictput.values())

                        print("total_money_invested_put: ", total_money_invested_put)
                        write_to_order_logs(f"total_money_invested_put: {total_money_invested_put}")
                        print("average_money_invested_put: ", average_money_invested_put)
                        write_to_order_logs(f"average_money_invested_put: {average_money_invested_put}")

                        params["count"] = params["count"] + 1
                        if params["Calculation"] == "POINT":
                            params["DownsidePut"] = params["putltp"] - params["DownsideTradeDist"]
                            params["UpsidePut"] = average_money_invested_put + params["AverageTargetDist"]

                        if params["Calculation"] == "PERCENTAGE":
                            params["UpsidePut"] = average_money_invested_put * params["AverageTargetDist"] * 0.01
                            params["UpsidePut"] = params["UpsidePut"] + average_money_invested_put

                            params["DownsidePut"] = params["putltp"] * params["DownsideTradeDist"] * 0.01
                            params["DownsidePut"] = params["putltp"] - params["DownsidePut"]

                        OrderLog = (
                                f"{timestamp} {symbol_value} DownsidePut level reached:  {params['InitialPut']} @ {params['putltp']} previous heikenashi close= {params['ha_close_last_put']} opening double lotsize put: {params['UpdatedLotsPut']},"
                                f",updated put upside target: {params['UpsidePut']}, put downside average: {params['DownsidePut']}")
                        print(OrderLog)
                        write_to_order_logs(OrderLog)
                        params["StockDevPutSymbol"] = f"{params['BaseSymbol']}_{Stockdeveloper.convert_date(params['TradeExpiery'])}_PE_{params['putstrike']}"
                        params['putaveragecount'] = params['putaveragecount'] + 1
                        stockdev_multiclient_orderplacement_buy(basesymbol=params['BaseSymbol'],
                                                                client_dict=client_dict,
                                                                timestamp=timestamp, symbol=params["StockDevPutSymbol"],
                                                                direction="BUY", Stoploss=0,
                                                                Target=0,
                                                                qty=params['UpdatedLotsPut'], price=params["putltp"],
                                                                side="PUT")


                    if (params['callavgcount'] < params['NoOfAverage'] and
                            normalized_now >= params["callaveragetime"] and
                            params["callaveragetime"] is not None and
                            params["DownsideCall"] is not None and
                            params['ha_close_last_call'] < params["DownsideCall"] and
                            is_candle_body_within_percent(
                                close=params['ha_close_last_call'],
                                open_price=params['ha_open_last_call'],
                                high=params['ha_high_last_call'],
                                low=params['ha_low_last_call'],
                                percent=params['CandlePercent']
                            )==True and datetime.now() <= params['combinedexitdatetime']):
                        # =datetime.now() + timedelta(minutes=params['TFMIN'])

                        new_time, params["callaveragetime"] = add_and_normalize_time(params['TFMIN'])

                        OrderLog = (
                            f"{timestamp} Initiateing downside trade call @ {symbol_value} next downtrend call time : {params['callaveragetime']}, normalised time= {normalized_now}, check time call ={params['runtimecall']}")
                        print(OrderLog)
                        write_to_order_logs(OrderLog)
                        # if params["count"]>1:
                        params["UpdatedLotsCall"] = int(params["UpdatedLotsCall"]*2)
                        params["lotvalueCall"] = params["lotvalueCall"] * 2

                        tradedictcall[f"trade_{len(tradedictcall) + 1}"] = {
                            "tradeltp": params["callltp"],
                            "Lots": params["lotvalueCall"],
                            "Moneyinvested": params["lotvalueCall"] * params["callltp"],
                            "StockDevSymbol": params["StockDevCallSymbol"],
                            "StockDevQty": params['UpdatedLotsCall'],
                        }
                        print("tradedictcall: ", tradedictcall)
                        write_to_order_logs(f"tradedictcall: {tradedictcall}")
                        total_money_invested_call = sum(trade["Moneyinvested"] for trade in tradedictcall.values())
                        average_money_invested_call = total_money_invested_call / sum(
                            trade["Lots"] for trade in tradedictcall.values())

                        print("total_money_invested_call: ", total_money_invested_call)
                        write_to_order_logs(f"total_money_invested_call: {total_money_invested_call}")
                        print("average_money_invested_call: ", average_money_invested_call)
                        write_to_order_logs(f"average_money_invested_call: {average_money_invested_call}")
                        params["count"] = params["count"] + 1
                        if params["Calculation"] == "POINT":
                            params["DownsideCall"] = params["callltp"] - params["DownsideTradeDist"]
                            params["UpsideCall"] = average_money_invested_call + params["AverageTargetDist"]

                        if params["Calculation"] == "PERCENTAGE":
                            params["DownsideCall"] = params["callltp"] * params["DownsideTradeDist"] * 0.01
                            params["DownsideCall"] = params["callltp"] - params["DownsideCall"]

                            params["UpsideCall"] = average_money_invested_call * params["AverageTargetDist"] * 0.01
                            params["UpsideCall"] = params["UpsideCall"] + average_money_invested_call

                        OrderLog = (f"{timestamp} {symbol_value} DownsideCall level reached :  {params['Initialcall']} @ {params['callltp']} previous heikenashi close= {params['ha_close_last_call']} opening double lotsize call: {params['UpdatedLotsCall']},"
                                        f" updated call upside target: {params['UpsideCall']}, call downside average: {params['DownsideCall']}")
                        print(OrderLog)
                        write_to_order_logs(OrderLog)
                        params["StockDevCallSymbol"] = f"{params['BaseSymbol']}_{Stockdeveloper.convert_date(params['TradeExpiery'])}_CE_{params['callstrike']}"
                        params['callavgcount']=params['callavgcount']+1
                        stockdev_multiclient_orderplacement_buy(basesymbol=params['BaseSymbol'],
                                                                client_dict=client_dict,
                                                                timestamp=timestamp,
                                                                symbol=params["StockDevCallSymbol"],
                                                                direction="BUY", Stoploss=0,
                                                                Target=0,
                                                                qty=params['UpdatedLotsCall'], price=params["callltp"],
                                                                side="CALL")




    except Exception as e:
        print("Error happened in Main strategy loop: ", str(e))
        traceback.print_exc()

def repeat_every_day():
    AngelIntegration.login(api_key=api_key, username=username, pwd=pwd, totp_string=totp_string)
    AngelIntegration.symbolmpping()

next_run_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
if datetime.now() >= next_run_time:
    next_run_time += timedelta(days=1)

while True:
    current_time = datetime.now()
    print("strategy run initiated")
    start_time = current_time.replace(hour=9, minute=14, second=0, microsecond=0)
    end_time = current_time.replace(hour=15, minute=45, second=0, microsecond=0)
    if current_time >= next_run_time:
        repeat_every_day()
        # Schedule for the next day at 9 AM
        next_run_time += timedelta(days=1)

    if start_time < current_time <= end_time:
        main_strategy()
        time.sleep(3)

