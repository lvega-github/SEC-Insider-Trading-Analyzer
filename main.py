from ClassTradingData import TradingData
from ClassForm4 import Form4
from multiprocessing import Pool
from functools import partial
import time


def extract_trading_data(cik, start_date=None, end_date=None, days_range=0):
    tradingData = TradingData(
        cik, start_date, end_date, days_range)
    return tradingData


def parallel_extract_trading_data(ciks, start_date=None, end_date=None, days_range=0, parallel_exc=2):
    if parallel_exc > 1:
        batch_delay = 1/parallel_exc
        # create a pool of processes
        with Pool(processes=parallel_exc) as pool:
            # create a partial function with the start_date and end_date arguments fixed
            create_data_pool = partial(
                extract_trading_data, start_date=start_date, end_date=end_date, days_range=days_range)
            # call the create_data_pool function on the first half of the cik values in parallel using the pool.map method with a time delay between each process
            for i, cik in enumerate(ciks[:len(ciks)//2]):
                if i != 0:
                    time.sleep(batch_delay)
                pool.apply_async(create_data_pool, args=(cik,))
            pool.map(create_data_pool, ciks[len(ciks)//2:])
            # close the pool of processes and wait for all processes to finish
            pool.close()
            pool.join()
    else:
        print("The parameter 'parallel_exc' must be higher than 0")


def extract_form4(cik, start_date=None, end_date=None, days_range=0):
    form4Data = Form4(
        cik, start_date, end_date, days_range)
    return form4Data


def parallel_extract_form4_data(ciks, start_date=None, end_date=None, days_range=0, parallel_exc=2):
    if parallel_exc > 1:
        batch_delay = 1/parallel_exc
        # create a pool of processes
        with Pool(processes=parallel_exc) as pool:
            # create a partial function with the start_date and end_date arguments fixed
            create_data_pool = partial(
                extract_form4, start_date=start_date, end_date=end_date, days_range=days_range)
            # call the create_data_pool function on the first half of the cik values in parallel using the pool.map method with a time delay between each process
            for i, cik in enumerate(ciks[:len(ciks)//2]):
                if i != 0:
                    time.sleep(batch_delay)
                pool.apply_async(create_data_pool, args=(cik,))
            pool.map(create_data_pool, ciks[len(ciks)//2:])
            # close the pool of processes and wait for all processes to finish
            pool.close()
            pool.join()


if __name__ == '__main__':
    start_time = time.time()
    start_date = '2021-01-01'
    end_date = '2021-12-31'
    days_range = 0

    ciks = ['1318605', '320193', '1045810', '1018724', '789019', '1326801', '1652044', '1682852', '1647639', '1535527', '1818874', '1783879', '1633917', '1559720', '2488', '0000320193', '0001018724', '0001288776', '0001652044', '0000789019', '0001318605', '0001372612', '0000072903', '0000919087', '0001054374', '0000789019', '0001108524', '0001588308', '0001045810', '0001403161', '0001114446', '0000108772', '0001029800', '0001657041', '0001122976', '0000707389', '0001364742', '0001318605', '0001439404', '0001075531', '0001608552',
            '0001583803', '0001166126', '0001090872', '0001512673', '0001090872', '0001580052', '0001160308', '0001101239', '0000815094', '0000922689', '0001006432', '0001326801', '0001335197', '0000789019', '0001018724', '0001015739', '0000850462', '0001326801', '0001030865', '0001526520', '0001588308', '0001271024', '0001086222', '0001114128', '0000934549', '0001280452', '0001114446']
    ciks = ciks[0:15]
    parallel_extract_form4_data(
        ciks, start_date, end_date, days_range, parallel_exc=2)
    parallel_extract_trading_data(
        ciks, start_date, end_date, days_range, parallel_exc=2)
    end_time = time.time()
    print(f'Execution time: {round(end_time - start_time)} seconds.')
