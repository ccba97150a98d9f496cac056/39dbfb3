# -*- coding: utf-8 -*-
from iqoptionapi.stable_api import IQ_Option
import time
import json
from datetime import datetime
from dateutil import tz
import sys
import json
import os


"""
TO RUN:

python run.py PRACTICE EURUSD

"""
API = IQ_Option(os.environ["IQU"], os.environ["IQU"])  # Entrar Login e Senha
API.connect()
# API.change_balance('REAL') #Real ou Practice
API.change_balance(sys.argv[1])

CURRENCY = sys.argv[2]

GREEN = 'g'
RED = 'r'
STAY = '-'

BUY_OB = 'call'
SELL_OB = 'put'

RESULTS = {
    "GAIN": 0,
    "LOST": 0,
    "TOTAL": 0
}

LOGS = []

INCONSIVE_SEQUENCE = 0

def stop(lucro, gain, loss):
    if lucro <= float('-' + str(abs(loss))):
        print('Stop Loss batido!')
        sys.exit()

    if lucro >= float(abs(gain)):
        print('Stop Gain Batido!')
        sys.exit()

while True:
    if API.check_connect() == False:
        print('Erro ao conectar')
        API.connect
    else:
        print('Conectado com Sucesso')
        break
    time.sleep(3)


def readFile(path):
    f = open(path, "r")
    return json.loads(f.read())

# Função para converter timestamp
def timestamp_converter(x):
    hora = datetime.strptime(datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    hora = hora.replace(tzinfo=tz.gettz('GMT'))

    return hora

# Pega o valor da banca
def banca():
    return API.get_balance()

# Calcula o valor da banca e quando é possível investir
def bancaFloor():
    return 2.0
    # divided_by = 36
    # banca_balance = banca()
    # if (banca_balance > divided_by * 2):
    #     return float(int(banca()) // divided_by);
    
    # return float(int(banca()) // (divided_by / 3));
    # Limited to $USD 2

# def isGoodToGo():
#     ALL_PROFITS = API.get_all_profit()
#     profit = ALL_PROFITS[CURRENCY]
#     print("Percent of Profit", profit)


valor_entrada = bancaFloor() if int(banca()) > 20 else 2

print('Valor da Banca é {} - Trade atual é {}, com valor de entrada definido em {} '.format(banca(), CURRENCY, valor_entrada))

# martingale = int(1)
# martingale += 1

stop_loss = float(int(banca()) // 5)
stop_gain = float(int(banca()) // 2)
print("Stop Loss -> {} == {} <- stop_gain".format(stop_loss, stop_gain))

lucro = 0
valor = 0

def progress(minutos):
    sys.stdout.write("\r{}".format(minutos))
    sys.stdout.flush()

def textConsole(text):
    sys.stdout.write("\r{}".format(text))
    sys.stdout.flush()

def saveLog(obj):
    with open("./logs/{}.v2.{}.json".format(CURRENCY,API.get_server_timestamp()), 'w') as outfile:
        json.dump(obj, outfile)

def calcVela(vela):
    return GREEN if vela['open'] < vela['close'] else RED if vela['open'] > vela['close'] else STAY

def getCandles(timeRange, quant ):
    
    
    return velas

# getPayout()

while True:
    timeServer = timestamp_converter(API.get_server_timestamp())
          
    # every =  minutos = float(timeServer.strftime('%M.%S')[2:])
    # entrar = True if (every > 0.45 and every < 0.5) else False
    # textConsole("{} - {} - {}".format(timeServer, every, entrar))
        
        
    minutos = float(timeServer.strftime('%M.%S')[1:])
    entrar = True if (minutos >= 4.57 and minutos <= 5) or minutos >= 9.57 else False
    # progress("{}".format(minutos))
    
    
    if entrar:
        # getPayout()
        print('--------')
        print("Iniciando Trade {} - {}".format(CURRENCY, str(timeServer)[:-6]))
        
        direcaoGraph = False

        candleOrigin = API.get_candles(CURRENCY, 60, 10, API.get_server_timestamp())
        
        velas = []
        
        C0 = calcVela(candleOrigin[0])
        C1 = calcVela(candleOrigin[1])
        C2 = calcVela(candleOrigin[2])
        C3 = calcVela(candleOrigin[3])
        C4 = calcVela(candleOrigin[4])
        C5 = calcVela(candleOrigin[5])
        C6 = calcVela(candleOrigin[6])
        C7 = calcVela(candleOrigin[7])
        C8 = calcVela(candleOrigin[8])
        C9 = calcVela(candleOrigin[9])
        
        # Check One
        candles_0_1_2_3_4 = "{} {} {} {} {}".format(C0,C1,C2,C3,C4)
        clandle_7_8_9 = "{} {} {}".format(C7,C8,C9)
        
        ALLCANDLES = "{} {} {} {} {} {}".format(candles_0_1_2_3_4,C5,C6,C7,C8,C9)
        allGreen = ALLCANDLES.count(GREEN)
        allRed = ALLCANDLES.count(RED)
        GR = "g{}_r{}".format(ALLCANDLES.count(GREEN),ALLCANDLES.count(RED))
        
        # Call
        isG9R1 = True if GR == 'g8_r2' else False # 80%
        isG8R2 = True if GR == 'g8_r2' else False # 70%
        isG7R3 = True if GR == 'g7_r3' else False # 70%
        if isG9R1 or isG8R2 or isG7R3:
            direcaoGraph = BUY_OB
        
        # Put
        isG1R9 = True if GR == 'g8_r2' else False # 80%
        isG2R8 = True if GR == 'g8_r2' else False # 70%
        isG3R7 = True if GR == 'g3_r7' else False # 70%
        if isG1R9 or isG2R8 or isG3R7:
            direcaoGraph = SELL_OB
        
        negativeList = readFile('./negative-sequence.json')
        
        if direcaoGraph == False:
            print("CANCEL because the {}".format(GR))
        
        print("negative tem {} itens".format(len(negativeList)))
        if ALLCANDLES in negativeList:
            direcaoGraph = False
            print("This sequence is on negative list - '{}'".format(ALLCANDLES))
        
        # if direcaoGraph == False:
        #     if allGreen > 7:
        #         direcaoGraph = BUY_OB
        #         # inverte = False
        #     elif allRed > 7:
        #         direcaoGraph = SELL_OB
                
        
        
        if direcaoGraph:
            INCONSIVE_SEQUENCE = 0
            status, id = API.buy_digital_spot(CURRENCY, valor_entrada, direcaoGraph, 1)
            print("BuyID {} para {} em {}".format(id, 'cima' if direcaoGraph == BUY_OB else 'baixo', GR))
            
            if type(id) != int:    
                if 'message' in id:
                    print(id['message'])
                    sys.exit()
            
            if status:
                while True:
                    status, valor = API.check_win_digital_v2(id)

                    if status:
                        valor = valor if valor > 0 else float('-' + str(abs(valor_entrada)))
                        value_rounded = round(valor, 2)
                        lucro += value_rounded
                        
                        if valor > 0:
                            RESULTS["GAIN"] = RESULTS["GAIN"] + 1
                            RESULTS["TOTAL"] = float(RESULTS["TOTAL"] + value_rounded)
                            
                            print("{} 🎉 +1 de {} - Resultados: {} 💰 e {} 💸  === 🤖 {}".format(GR, value_rounded, RESULTS["GAIN"],RESULTS["LOST"], RESULTS["TOTAL"]))
                        else:
                            RESULTS["LOST"] = RESULTS["LOST"] + 1
                            RESULTS["TOTAL"] = float(RESULTS["TOTAL"] + value_rounded)
                            print("{} 💩 -1 de {} - Resultados: {} 💰 e {} 💸  === 🤖 {}".format(GR, value_rounded, RESULTS["GAIN"],RESULTS["LOST"], RESULTS["TOTAL"]))
                        
                        LOGS.append({
                            "result": "gain" if valor > 0 else "lose",
                            "entrada": valor_entrada,
                            "value": value_rounded,
                            "velas": ALLCANDLES.split(' '),
                            "candleOrigin":candleOrigin,
                            "direction": direcaoGraph,
                            "1quad": candles_0_1_2_3_4,
                            "2quad": clandle_7_8_9,
                            "candle": "{}|{}".format(C5, C6),
                            "date": "{}".format(timeServer)
                        })
                        saveLog(LOGS);

                        stop(lucro, stop_gain, stop_loss)

                        break;
                    
            else:
                print('ERRO AO REALIZAR ORDEM')
                
        else:
            INCONSIVE_SEQUENCE = INCONSIVE_SEQUENCE + 1
            if INCONSIVE_SEQUENCE > 9:
                print("Atividade suspensa por inconclusividade - 10 seguidas!")
                sys.exit()
            time.sleep(5)
            entrar = False
