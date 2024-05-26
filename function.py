import csv
from tradingview_ta import TA_Handler, Interval
from config import SHORT_ACTIONS, top_20_tickers, crypto_tickers


def get_changes_as_string():
    handlers = []
    for ticker in top_20_tickers + crypto_tickers:
        if ticker in ['MA', 'PG', 'BRK.A', 'BRK.B', 'DIS', 'UNH', 'BAC/PE', 'HD', 'V', 'JPM', 'JNJ']:
            try:
                handler = TA_Handler(
                    symbol=ticker,
                    exchange="NYSE" if ticker in top_20_tickers else "BINANCE",
                    screener="crypto" if ticker in crypto_tickers else "america",
                    interval=Interval.INTERVAL_1_MINUTE
                )
                handlers.append(handler)
            except Exception as e:
                print(f"Ошибка при инициализации для {ticker}: {e}")
        else:
            try:
                handler = TA_Handler(
                    symbol=ticker,
                    exchange="NASDAQ" if ticker in top_20_tickers else "BINANCE",
                    screener="crypto" if ticker in crypto_tickers else "america",
                    interval=Interval.INTERVAL_1_MINUTE
                )
                handlers.append(handler)
            except Exception as e:
                print(f"Ошибка при инициализации для {ticker}: {e}")

    tickers = {}
    for handler in handlers:
        try:
            handler.get_analysis().summary
            tickers[handler.symbol] = [handler.get_analysis().indicators["open"], handler.get_analysis().indicators["RSI"]]
        except Exception as e:
            print(f"Ошибка при получении котировки для {handler.symbol}: {e}")

    old_data = {}
    try:
        with open('old.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Пропускаем заголовок
            for row in reader:
                if row[1]:  # Проверяем, что строка не пустая
                    ticker, price_str, rsi_str = row
                    old_data[ticker] = [float(price_str), float(rsi_str)]
    except FileNotFoundError:
        pass

    changes = []
    for ticker, info in tickers.items():
        price = info[0]
        rsi = info[1]
        if ticker in old_data:
            old_price = old_data[ticker][0]
            changep = (price - old_price) / old_price * 100
            if abs(changep) >= 0.01:
                flag = 'PRICE CHANGE'
                changes.append((ticker, changep, flag))
        if ticker in old_data:
            old_rsi = old_data[ticker][1]
            changer = (rsi - old_rsi) / old_rsi * 100
            if abs(changer) >= 5:
                flag = 'RSI CHANGE'
                changes.append((ticker, changer, flag))
    changes_slovar = {}
    for ticker, change, flag in changes:
        active = ticker[:-4] if 'USDT' in ticker else SHORT_ACTIONS[ticker]
        changes_slovar[active] = f"""<b>{active}</b>: изменение {'цены' if flag == 'PRICE CHANGE' else 'RSI'} на {round(change, 3)} % """

    # Запись новых данных в старый файл
    with open('old.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Ticker', 'Price', 'RSI'])
        for ticker, info in tickers.items():
            writer.writerow([ticker, info[0], info[1]])

    return changes_slovar
