#import thu vien
import ccxt
import pandas
import time
import sys
import numpy
import datetime
import tulipy
import yaml
import os
from datetime import datetime
import telebot
#Ham get config
def get_config():
        if os.path.isfile('config.yml'):
            with open('config.yml', 'r') as config_file:
                user_config = yaml.full_load(config_file)
        else:
            user_config = dict()
        return user_config
        
#ham get gia
def get_price(exchange, symbol, timeframe, limits):
    data_ohlc = exchange.fetch_ohlcv(symbol, timeframe, limit = limits)
    dataframe = pandas.DataFrame(data_ohlc)
    dataframe.transpose()

    dataframe.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    dataframe['datetime'] = dataframe.timestamp.apply(
        lambda x: pandas.to_datetime(datetime.fromtimestamp(x / 1000).strftime('%c'))
        )

    dataframe.set_index('datetime', inplace=True, drop=True)
    dataframe.drop('timestamp', axis=1, inplace=True)

    return dataframe
     
#ham tinh toan
#Ham tinh MA
def sma(data_ohlc, period_count ):
     close_data = numpy.array(data_ohlc['close'])
     sma_data = tulipy.sma(close_data,period_count)
     return sma_data
#ham tính rsi
def rsi_adv(data_ohlc, period_count = 10):
    point_rsi = 0
    msg = ""
    close_data = numpy.array(data_ohlc['close'])
    rsi_data = tulipy.rsi(close_data,period_count)
    ma_rsi2  = tulipy.sma(rsi_data, 2)
    ma_rsi7 = tulipy.sma(rsi_data, 7)
    #case Long - rsi2 cat rsi7
    if ma_rsi2[-1] > ma_rsi7[-1]:
        if ma_rsi2[-2] < ma_rsi7[-2]:
            point_rsi = point_rsi + 0.5
            msg = msg + "\n 🟢 MA2_RSI cắt lên MA7_RSI"
    #case Long - rsi2 tang
        if (ma_rsi2[-1] - min(ma_rsi2[-2],ma_rsi2[-3])) > 6.8:
            point_rsi = point_rsi + 0.5
            msg = msg + "\n 🟢 MA2_RSI tăng: " + str(ma_rsi2[-1] - min(ma_rsi2[-2],ma_rsi2[-3]))
    #Case Short - rsi2 cat rsi7
    elif ma_rsi2[-1] < ma_rsi7[-1]:
        #Case Short - rsi2 cat rsi7
        if ma_rsi2[-2] > ma_rsi7[-2]:
            point_rsi = point_rsi - 0.5
            msg = msg + "\n 🔴 MA2_RSI cắt xuống MA7_RSI"
        #case Short - rsi2 tang
        if (max(ma_rsi2[-2],ma_rsi2[-3]) - ma_rsi2[-1]) > 6.8:
            point_rsi = point_rsi - 0.5
            msg = msg + "\n 🔴 MA2_RSI giảm: " + str(max(ma_rsi2[-2],ma_rsi2[-3]) - ma_rsi2[-1])

    return [point_rsi, msg]
    
 
    return ma_rsi7
#ham tinh ema
def ema(data_ohlc, period_count ):
     close_data = numpy.array(data_ohlc['close'])
     ema_data = tulipy.ema(close_data,period_count)
     return ema_data
#ham xet ema
def ema_adv(data_ohlc):
    point_ema = 0
    msg_ema = ""
    ema_89 = ema(data_ohlc, 89)
    ema_200 = ema(data_ohlc, 200)
    #Xet ema 89
    price_close = data_ohlc.iloc[-1]['close']
    price_open = data_ohlc.iloc[-1]['close']
    # Cắt lên ema 89 - Long
    if price_open < ema_89[-1] < price_close:
        point_ema = point_ema + 0.5
        msg_ema = msg_ema + "\n 🟢 Giá căt EMA 89: " + str(ema_89[-1])
    #Giá cắt xuống ema89 - SHort
    if price_close < ema_89[-1] < price_open:
        point_ema = point_ema - 0.5
        msg_ema = msg_ema + "\n 🔴 Giá căt xuống EMA 89: " + str(ema_89[-1])
    # Cắt lên ema 200 - Long
    if price_open < ema_200[-1] < price_close:
        point_ema = point_ema + 0.5
        msg_ema = msg_ema + "\n 🟢 Giá căt EMA 89: " + str(ema_200[-1])
    #Giá cắt xuống ema200 - SHort
    if price_close < ema_200[-1] < price_open:
        point_ema = point_ema - 0.5
        msg_ema = msg_ema + "\n 🔴 Giá căt xuống EMA 89: " + str(ema_200[-1])
    return [point_ema, msg_ema]
#hàm send noti        
def send_noti(message, conf):
    tb = telebot.TeleBot(conf['token'])
    tb.send_message(conf['chat_id'], message)
def main():
    conf = get_config()
    binance = ccxt.binance()
    while True:
        for market_pairs in conf['market_pairs']:
            data_ohlc = get_price(binance, market_pairs, "15m", 210)
            point_rsi, msg_rsi = rsi_adv(data_ohlc)
            point_ema, msg_ema = ema_adv(data_ohlc)
            point = point_rsi + point_ema
            price = data_ohlc.iloc[-1]['close']
            if point > 1:
                msg = market_pairs + "- Point: " + str(point) + "- Price: " + str(price) + msg_rsi + msg_ema
                send_noti(msg)
            elif point < -1:
                msg = market_pairs + "- Point: " + str(point) + "- Price: " + str(price) + msg_rsi + msg_ema
                send_noti(msg,conf['telegram'])
        print("Sleeping for 60 seconds")
        time.sleep(300)
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)



#data = get_price(binance, "BTCUSDT", "1m", 210)
#sma200 = rsi_adv(data, 10)
#print(sma200)
#print(len(data))
#conf = get_config()
#send_noti("Test",conf['telegram'] )
#print(conf['telegram']['token'])

