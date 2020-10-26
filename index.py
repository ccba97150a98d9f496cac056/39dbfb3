# -*- coding: utf-8 -*-
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
from dateutil import tz
import time
import sys
import os
import json

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""" API  """""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

BUY_OPERATION = 'call'
SELL_OPERATION = 'put'


class IQ:
    def __init__(self):
        self.api = IQ_Option(os.environ["IQU"], os.environ["IQP"])
        self.api.connect()
        self.api.change_balance(sys.argv[1])  # REAL | PRACTICE
        self.currency = sys.argv[2]

        while True:
            if self.api.check_connect() == False:
                print('Erro ao conectar')
                self.api.connect
            else:
                print('Conectado com Sucesso')
                break
            time.sleep(3)

    def getCurrency(self):
        return self.currency

    def getBalance(self):
        return self.api.get_balance()

    def getEnterValue(self):
        return 2.0

        # valor_entrada = bancaFloor() if int(banca()) > 20 else 2
        #
        # divided_by = 36
        # banca_balance = banca()
        # if (banca_balance > divided_by * 2):
        #     return float(int(banca()) // divided_by);

        # return float(int(banca()) // (divided_by / 3));
        # Limited to $USD 2

    def getServerDatetime(self):
        serverTime = self.api.get_server_timestamp()
        hora = datetime.strptime(datetime.utcfromtimestamp(
            serverTime).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        return hora.replace(tzinfo=tz.gettz('GMT'))

    def getCandles(self, rangeTime=60, quant=10):
        return self.api.get_candles(self.currency, rangeTime, quant, self.api.get_server_timestamp())

    def buyDigitalSpot(self, direction):
        return self.api.buy_digital_spot(self.currency, self.getEnterValue(), direction, 1)

    def checkResult(self, id):
        return self.api.check_win_digital_v2(id)

    def shouldEntry(self):
        serverTime = self.getServerDatetime()
        # minutes = float(serverTime.strftime('%M.%S')[1:])
        # return True if (minutes >= 4.58 and minutes <= 5) or minutes >= 9.58 else False
        seconds = int(serverTime.strftime('%S'))

        if seconds < 20:
            time.sleep(20)
        elif seconds < 30:
            time.sleep(10)

        goTrade = True if (seconds >= 48 and seconds <=
                           50) or seconds >= 58 else False
        if goTrade == False:
            time.sleep(1)

        return goTrade


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""     CANDLES HELPERS    """""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

candleGREEN = 'g'
candleRED = 'r'
candleNule = '-'


def getCandleTotalVolumeFinal(candles):
    v = 0
    for candle in candles:
        v = float(candle['close']) - float(candle['open'])
    return v


def getAverageCandleVolume(candles):
    v = 0
    for candle in candles:
        close = candle['close']
        open = candle['open']
        v += close - open if (close > open) else open - close
    return v / 10


def whatTheCandleIs(vela):
    return candleGREEN if vela['open'] < vela['close'] else candleRED if vela['open'] > vela['close'] else candleNule


def getCandleSequence(candles):
    return [
        whatTheCandleIs(candles[0]),
        whatTheCandleIs(candles[1]),
        whatTheCandleIs(candles[2]),
        whatTheCandleIs(candles[3]),
        whatTheCandleIs(candles[4]),
        whatTheCandleIs(candles[5]),
        whatTheCandleIs(candles[6]),
        whatTheCandleIs(candles[7]),
        whatTheCandleIs(candles[8]),
        whatTheCandleIs(candles[9])
    ]


def getCandleSequenceString(candles):
    candlesList = getCandleSequence(candles)
    return " ".join(candlesList)


def extractResultData(candlesSequence, candleOrigin, direction, enterValue, resultValue, date):
    return {
        "result": "gain" if resultValue > 0 else "lose",
        "entrada": enterValue,
        "value": round(resultValue, 2),
        "sequencia": candlesSequence,
        "candles": candleOrigin,
        "direction": direction,
        "date": "{}".format(date)
    }


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""     FOR JSON FILES     """""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def readJSONFile(path):
    f = open(path, "r")
    return json.loads(f.read())


def saveJSONFile(path, obj):
    with open(path, 'w') as outfile:
        json.dump(obj, outfile)


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""   THE REAL OPERATION   """""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
RESULTS = {"GAIN": 0, "LOST": 0, "TOTAL": 0}

TRADE = IQ()

print('Valor da Banca é {} - Trade atual é {}, com valor de entrada definido em {} '.format(
    TRADE.getBalance(), TRADE.getCurrency(), TRADE.getEnterValue()))

NO_ACTION_TAKE_COUNTER = 0

while True:
    if RESULTS["TOTAL"] > 20:
        print("20 operations has been made. Now is time to analytics!")

    if TRADE.shouldEntry():
        print('--------')
        print("Trade {} - {}".format(TRADE.getCurrency(), TRADE.getServerDatetime()))

        direction = False  # rename to buyOrSell

        candles = TRADE.getCandles()

        candleVolume = getCandleTotalVolumeFinal(candles)
        candleSequence = getCandleSequenceString(candles)
        greens = candleSequence.count(candleGREEN)
        reds = candleSequence.count(candleRED)

        GR = "g{}_r{}".format(greens, reds)

        isG9R1 = True if GR == 'g8_r2' else False  # 80%
        isG8R2 = True if GR == 'g8_r2' else False  # 70%
        if isG9R1 or isG8R2:
            print("{} and the volume is {}, so {}".format(
                isG9R1 if isG9R1 else isG8R2, candleVolume, direction))
            direction = BUY_OPERATION

        isG1R9 = True if GR == 'g8_r2' else False  # 80%
        isG2R8 = True if GR == 'g8_r2' else False  # 70%
        if isG1R9 or isG2R8:
            print("{} and the volume is {}, so {}".format(
                isG1R9 if isG1R9 else isG2R8, candleVolume, direction))
            direction = SELL_OPERATION

        isG7R3 = True if GR == 'g7_r3' else False  # 70%
        if (isG7R3):
            direction = BUY_OPERATION if candleVolume > 0 else SELL_OPERATION
            print("isG7R3 and the volume is {}, so {}".format(
                round(candleVolume, 6), direction))

        isG3R7 = True if GR == 'g3_r7' else False  # 70%
        if (isG3R7):
            direction = SELL_OPERATION if candleVolume < 0 else BUY_OPERATION
            print("isG3R7 and the volume is {}, so {}".format(
                round(candleVolume, 6), direction))
        
        print("candles is 0.0 something? ", True if candleVolume > -1 and candleVolume < 1 else False)
        if candleVolume > -1 and candleVolume < 1:
            direction == False
            print("Candles volume not increase/descrease too much")

        if direction == False:
            NO_ACTION_TAKE_COUNTER += 1

            if NO_ACTION_TAKE_COUNTER > 60:
                print("Active is Ending because NO_ACTION_TAKE_COUNTER is {}!".format(
                    NO_ACTION_TAKE_COUNTER))
                sys.exit()
            else:
                print("No take action because directions can variate")

            time.sleep(5)
            entrar = False

        else:

            NO_ACTION_TAKE_COUNTER -= 1

            enterValue = TRADE.getEnterValue()
            tradeTime = TRADE.getServerDatetime()

            spotSTATUS, spotID = TRADE.buyDigitalSpot(direction)

            if type(spotID) != int:
                if 'message' in spotID:
                    print(spotID['message'])
                    sys.exit()

            print("SPOT#{} -  {} @ {}".format(spotID,
                                              'UP' if direction == BUY_OPERATION else 'DOWN', GR))

            if spotSTATUS:
                while True:
                    checkSTATUS, checkValuevalor = TRADE.checkResult(spotID)

                    if checkSTATUS:
                        resultValue = checkValuevalor if checkValuevalor > 0 else float(
                            '-' + str(abs(enterValue)))
                        roundedValue = round(resultValue, 2)

                        if resultValue > 0:
                            RESULTS["GAIN"] = RESULTS["GAIN"] + 1
                            RESULTS["TOTAL"] = float(
                                RESULTS["TOTAL"] + roundedValue)

                            print("{} 🎉 +1 de {} - Resultados: {} 💰 e {} 💸  === 🤖 {}".format(
                                GR, roundedValue, RESULTS["GAIN"], RESULTS["LOST"], RESULTS["TOTAL"]))
                        else:
                            RESULTS["LOST"] = RESULTS["LOST"] + 1
                            RESULTS["TOTAL"] = float(
                                RESULTS["TOTAL"] + roundedValue)
                            print("{} 💩 -1 de {} - Resultados: {} 💰 e {} 💸  === 🤖 {}".format(
                                GR, roundedValue, RESULTS["GAIN"], RESULTS["LOST"], RESULTS["TOTAL"]))

                        LOGS = extractResultData(
                            candleSequence, candles, direction, enterValue, resultValue, tradeTime)

                        saveJSONFile(
                            "./logs/v3.{}.{}.json".format(TRADE.getCurrency(), tradeTime), LOGS)

                        break

            else:
                print('ERRO AO REALIZAR ORDEM')
