import pandas as pd
import numpy as np
import yfinance as yf
import os
import datetime as dt
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Result:
  final_output = []
  prob_output = []
  higest_pencentage = 0
  high_of_every_year = []

  def print_data(self, begin_month, begin_day, end_month, end_day, code, years, prob):
    writer = pd.ExcelWriter(code + '_output.xlsx', engine='xlsxwriter')
    print('在' + str(begin_month) + '月' + str(begin_day) + '日到' +str(end_month) + '月' + str(end_day) + '日中:')
    print(code + '過往' + str(len(years)) + '年' + str(prob*100) + '%機率出現最高升波幅:' + str(self.higest_pencentage) + '%')
    result_begin_offset = np.where(self.final_output == np.amax(self.final_output))[0][0]
    result_end_offset = np.where(self.final_output == np.amax(self.final_output))[1][0]
    self.result_begin_date = pd.Timestamp(dt.datetime.now().year, begin_month, begin_day) + pd.Timedelta(days=result_begin_offset)
    self.result_end_date = pd.Timestamp(dt.datetime.now().year, begin_month, begin_day) + pd.Timedelta(days=result_end_offset)
    print('出現時段: ' + str(self.result_begin_date.month) + "-" + str(self.result_begin_date.day) + "最低位至" + str(self.result_end_date.month) + "-" + str(self.result_end_date.day))
    final_output_df = pd.DataFrame(self.final_output)
    final_output_df.to_excel(writer, sheet_name='final_ouput') # For backtest
    
    max_vol_of_years = []
    for i in range(len(years)):
      max_vol_of_years.append(self.high_of_every_year[i][0].max())
      pd.DataFrame(self.high_of_every_year[i]).to_excel(writer, sheet_name=str(i))
    writer.save()
    print('輸入時間段在起始日歷年最大升波幅:')
    print(np.sort(max_vol_of_years))

#加back test 今年和過去
def countif(value, seq):
  return sum(1 for item in seq if (value <= item))

def remove_29Feb(s):
  mask = (s.index.year % 4 == 0) & ((s.index.year % 100 != 0) | (s.index.year % 400 == 0)) & (s.index.month == 2) & (s.index.day == 29)
  s = s.loc[~mask]
  return s

def gen_data(data, day_range):
  dayHigh = data['High'].reset_index(drop=True) 
  dayLow = data['Low'].reset_index(drop=True)
  dayClose = data['Close'].reset_index(drop=True)

  rows, cols = (day_range, day_range)
  output = [[0 for i in range(cols)] for j in range(rows)]
  for i in range(day_range):
    for j in range(i + 1, day_range):
      if ( j > i ):
        #理論上應dayHigh[(i+1):(j+1)].max(), 因為無法捕捉當日最低位，或當日最高位出現在最低位前面
        period_highest = (((dayHigh[(i):(j+1)].max())/(dayLow[i])) - 1) * 100
        output[i][j] = period_highest
  output = np.round_(output, decimals = 2)
  #print(output)
  return output

def get_raw_data(code):
  raw_data = pd.read_csv(code + '.csv', index_col='Date')
  raw_data.index = pd.to_datetime(raw_data.index)
  begin_year = raw_data.index.year.min()
  #========begin resample raw data========
  if (pd.to_datetime(str(begin_year) + '-01-01') not in raw_data.index):
    set_begin = pd.DataFrame({},index =[pd.to_datetime(str(begin_year) + '-01-01')])
    raw_data = pd.concat([set_begin, raw_data])
  raw_data = raw_data.resample('1D').bfill()
  ##========end resample raw data========
  raw_data = remove_29Feb(raw_data)
  raw_data = raw_data.fillna(method="ffill").fillna(method="bfill").reset_index()
  raw_data.rename(columns = {'index':'Date'}, inplace=True)
  raw_data[["Year"]] = raw_data["Date"].dt.year
  print(raw_data)
  return raw_data

def get_high_low_of_every_year(raw_data, years, begin_month, begin_day, end_month, end_day):
  high_of_every_year = []
  for y in years:
    begin_date = pd.Timestamp(y,begin_month,begin_day)
    end_date = pd.Timestamp(y,end_month,end_day)
    request_data = raw_data.loc[(raw_data["Date"] >= begin_date) & (raw_data["Date"] <= end_date)]
    print('=========處理' + str(y) + '年中==========')
    #print(request_data)
    output = gen_data(request_data, len(request_data))
    high_of_every_year.append(output)
  return high_of_every_year, request_data

#find 90% value
def get_final_output(high_of_every_year, prob, history_years, day_range):
  pos = np.floor((1 - prob) * len(history_years)).astype(int)
  final_output = []
  prob_output = []
  for j in range(day_range):
    final_row = []
    prob_row = []
    for k in range(day_range):
      tmp = []
      for i in range(len(history_years)):
        tmp.append(high_of_every_year[i][j][k])
      tmp = np.sort(tmp)
      target = tmp[pos]
      final_row.insert(k, target)
      prob_row.insert(k, countif(target, tmp)/len(history_years))
    final_output.append(final_row)
    prob_output.append(prob_row)
  return (np.round_(final_output, decimals = 2)), (np.round_(prob_output, decimals = 2)), (np.amax(final_output))

def main():
  #=========begin input value=========
  begin_month = 7
  end_month = 8
  begin_day = 1
  end_day = 30
  prob = 0.90
  code = '^HSI'
  ##=========end input value=========

  '''
  code = input("輸入股票代號(輸入格式如: 0700.HK/MSFT/1234.TW 等): ")
  begin_month = int(input("輸入開始月份(1-12): "))
  begin_day = int(input("輸入開始日期(1-31): "))
  end_month = int(input("輸入結束月份(1-12): "))
  end_day = int(input("輸入結束日期(1-31): "))
  prob = int(input("輸入出現機率%(輸入格式如: 90, 80): ")) / 100
  '''
  yf.download(code, period="max", auto_adjust=True).to_csv(code + '.csv')

  raw_data = get_raw_data(code)
  years = np.sort(raw_data.Year.unique())
  years = [2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019, 2020, 2021] #For testing
  if (len(years) > 1):
    history_years = np.delete(years, len(years) - 1)
  else:
    history_years = years
  result = Result()
  result.high_of_every_year, request_data = get_high_low_of_every_year(raw_data, history_years, begin_month, begin_day, end_month, end_day)
  result.final_output, result.prob_output, result.higest_pencentage = get_final_output(result.high_of_every_year, prob, history_years, len(request_data))
  result.print_data(begin_month, begin_day, end_month, end_day, code, history_years, prob)
  #print('=========歷史矩陣=========')
  #print(final_output)
  #print(prob_output) 

  #=====Begin This Year Result
  high_of_this_year, request_data = get_high_low_of_every_year(raw_data, [dt.datetime.now().year], result.result_begin_date.month, result.result_begin_date.day, result.result_end_date.month, result.result_end_date.day)
  if (request_data.empty):
    print('今年未開始')
  else:
    this_year_period_highest = np.round_((((request_data['High'].reset_index()['High'][0:len(request_data)].max())/(request_data['Low'].reset_index()['Low'][0])) - 1) * 100, decimals = 2)
    this_year_price = request_data['Low'].reset_index()['Low'][0]
    this_year_target_price = np.round_(this_year_price * (result.higest_pencentage/100 + 1), decimals = 2)
    print(str(result.result_begin_date.date()) + ' 最低位置: ' + str(this_year_price))
    print('今年目標價格: ' + str(this_year_target_price))
    if (result.result_end_date < pd.Timestamp(dt.datetime.now().year, dt.datetime.now().month, dt.datetime.now().day)):
      print('今年時段已完結！！！')
    if (this_year_period_highest < result.higest_pencentage):
      print('今年未中，暫時最高升幅: ' + str(this_year_period_highest) + '%')
    else:
      print('今年已中，暫時最高升幅: ' + str(this_year_period_highest) + '%')
  #=====End This Year Result

  #user_input = input("任意鍵退出或r重新開始: ")
  #if (user_input.upper() == 'R'):
  #  main()

if __name__ == "__main__":
  main()