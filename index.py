# -*- coding: utf-8 -*-
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
from dateutil import tz
import time
import sys
import os
import json
import math
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""   PARAMS   """""""""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""" 
ENVS: 
[1] = ["REAL" | "PRACTICE"] -> Balance
[2] = ["USDJPY | ...] -> Currency

"""
ARG_BALANCE = sys.argv[1]
ARG_CURRENCY = sys.argv[2]
ARG_DURATION = int(sys.argv[3])

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""" API  """""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

BUY_OPERATION = 'call'
SELL_OPERATION = 'put'


class IQ:
    def __init__(self):
        self.api = IQ_Option(os.environ["IQU"], os.environ["IQP"])
        self.api.connect()
        self.api.change_balance(ARG_BALANCE)
        self.currency = ARG_CURRENCY

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
        banca = self.getBalance()
        bancaFloor = math.floor(banca / 40)
        return bancaFloor if int(banca) > 40 else 2.0
        # Limited to $USD 2

    def getServerDatetime(self):
        serverTime = self.api.get_server_timestamp()
        hora = datetime.strptime(datetime.utcfromtimestamp(
            serverTime).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        return hora.replace(tzinfo=tz.gettz('GMT'))
    
    def getCandles(self, rangeTime=60, quant=10):
        return self.api.get_candles(self.currency, rangeTime, quant, self.api.get_server_timestamp())

    def buyDigital(self, direction):
        return self.api.buy_digital_spot(self.currency, self.getEnterValue(), direction, ARG_DURATION)

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
        substract = float(candle['close'] - candle['open'])
        v += substract
    return v


def getAverageCandleVolume(candles):
    v = 0
    for candle in candles:
        close = candle['close']
        open = candle['open']
        v += close - open if (close > open) else open - close
    return v / 10


def whatTheCandleIs(candle, variante):
    open = candle['open']
    close = candle['close']

    volume = float(close - open) * 1000

    if volume > (-(variante)) and volume < variante:
        return candleNule

    if volume > 0:
        return candleGREEN

    return candleRED


def getCandleSequence(candles):
    return [
        whatTheCandleIs(candles[0], 0.5),
        whatTheCandleIs(candles[1], 0.5),
        whatTheCandleIs(candles[2], 0.5),
        whatTheCandleIs(candles[3], 0.5),
        whatTheCandleIs(candles[4], 0.5),
        whatTheCandleIs(candles[5], 0.5),
        whatTheCandleIs(candles[6], 0.5),
        whatTheCandleIs(candles[7], 0.5),
        whatTheCandleIs(candles[8], 0.5),
        whatTheCandleIs(candles[9], 0.5)
    ]


def getCandleSequenceString(candles):
    candlesList = getCandleSequence(candles)
    return " ".join(candlesList)


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
RESULTS = {"GAIN": 0, "LOST": 0, "BALANCE": 0}

TRADE = IQ()

print('Valor da Banca é {} - Trade atual é {}, com valor de entrada definido em {}'.format(
    TRADE.getBalance(), TRADE.getCurrency(), TRADE.getEnterValue()))

NO_ACTION_TAKE_COUNTER = 0

while True:
    if RESULTS['LOST'] > 1:
        print("Maximum loss is 2 gaming")
        break
    
    if RESULTS["GAIN"] > 10:
        print("Concept proved. Time to analytics!")
        break

    if TRADE.shouldEntry():
        print('--------')
        print("Trade {} - {}".format(TRADE.getCurrency(), TRADE.getServerDatetime()))

        direction = False  # rename to buyOrSell

        candles = TRADE.getCandles()

        candleVolumeTotal = getCandleTotalVolumeFinal(candles)
        candleSequence = getCandleSequenceString(candles)
        greens = candleSequence.count(candleGREEN)
        reds = candleSequence.count(candleRED)

        GR = "g{}_r{}".format(greens, reds)

        isG9R1 = True if GR == 'g8_r2' else False  # 80%
        isG8R2 = True if GR == 'g8_r2' else False  # 70%
        if isG9R1 or isG8R2:
            print("{} and the volume is {}, so {}".format(
                isG9R1 if isG9R1 else isG8R2, candleVolumeTotal, direction))
            direction = BUY_OPERATION

        isG1R9 = True if GR == 'g8_r2' else False  # 80%
        isG2R8 = True if GR == 'g8_r2' else False  # 70%
        if isG1R9 or isG2R8:
            print("{} and the volume is {}, so {}".format(
                isG1R9 if isG1R9 else isG2R8, candleVolumeTotal, direction))
            direction = SELL_OPERATION

        isG7R3 = True if GR == 'g7_r3' else False  # 70%
        if (isG7R3):
            direction = BUY_OPERATION if candleVolumeTotal > 0 else SELL_OPERATION
            print("isG7R3 and the volume is {}, so {}".format(
                round(candleVolumeTotal, 6), direction))

        isG3R7 = True if GR == 'g3_r7' else False  # 70%
        if (isG3R7):
            direction = SELL_OPERATION if candleVolumeTotal < 0 else BUY_OPERATION
            print("isG3R7 and the volume is {}, so {}".format(
                round(candleVolumeTotal, 6), direction))

        nuleCandlesCount = candleSequence.count(candleNule)
        if nuleCandlesCount > 1:
            direction = False
            print("{} nule candles".format(nuleCandlesCount))

        """ 
        Multiply to 1000, to eliminate good porcentage from both,
        by the previus analytics, the total of 66% are loses
        """
        calcVolumeWorth = candleVolumeTotal * 1000
        print("{} with volume {} on {}".format(direction, calcVolumeWorth, GR))
        if calcVolumeWorth > -1 and calcVolumeWorth < 1:
            direction = False
            print("Accuracy is too low - {}".format(calcVolumeWorth))

        if direction == False:
            NO_ACTION_TAKE_COUNTER += 1

            if NO_ACTION_TAKE_COUNTER > 100:
                print("Active is Ending because NO_ACTION_TAKE_COUNTER is {}!".format(
                    NO_ACTION_TAKE_COUNTER))
                sys.exit()
            else:
                print("No take action")

            time.sleep(5)
            entrar = False

        else:

            NO_ACTION_TAKE_COUNTER -= 1

            enterValue = TRADE.getEnterValue()
            tradeTime = TRADE.getServerDatetime()

            spotSTATUS, spotID = TRADE.buyDigital(direction)

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
                            RESULTS["GAIN"] += 1
                            RESULTS["BALANCE"] = float(
                                RESULTS["BALANCE"] + roundedValue)

                            print("{} 🎉 +1 de {} - Resultados: {} 💰 e {} 💸  === 🤖 {}".format(
                                GR, roundedValue, RESULTS["GAIN"], RESULTS["LOST"], RESULTS["BALANCE"]))
                        else:
                            RESULTS["LOST"] += 1
                            RESULTS["BALANCE"] = float(
                                RESULTS["BALANCE"] + roundedValue)

                            print("{} 💩 -1 de {} - Resultados: {} 💰 e {} 💸  === 🤖 {}".format(
                                GR, roundedValue, RESULTS["GAIN"], RESULTS["LOST"], RESULTS["BALANCE"]))

                        LOGS = {
                            "result": "gain" if resultValue > 0 else "lose",
                            "entrada": enterValue,
                            "value": round(resultValue, 2),
                            "sequencia": candleSequence,
                            "candles": candles,
                            "direction": direction,
                            "volumeTotal": candleVolumeTotal,
                            "date": "{}".format(tradeTime)
                        }

                        timeStr = "{}".format(tradeTime)
                        timeStr = timeStr.replace(":", "_")
                        timeStr = timeStr.replace("+", "_")
                        timeStr = timeStr.replace(" ", "-")
                        saveJSONFile(
                            "./logs/v3.{}.{}.json".format(TRADE.getCurrency(), timeStr), LOGS)

                        break

            else:
                print('ERRO AO REALIZAR ORDEM')
