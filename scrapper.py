import os
import json
import yfinance as yf
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials

# 🔹 Ambil credentials dari GitHub Secrets
credentials_json = os.getenv("GOOGLE_CREDENTIALS")

# 🔹 Simpan credentials sebagai file sementara
with open("credentials.json", "w") as f:
    f.write(credentials_json)

# 🔹 Load credentials dari file JSON
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
gc = gspread.authorize(credentials)

# 🔹 Buka Google Sheets
spreadsheet = gc.open("Saham Indonesia")  # Ganti dengan nama Google Sheet Anda
worksheet_name = "tabelincome"  # Worksheet yang akan digunakan

# 🔹 Cek apakah worksheet ada, jika tidak buat baru
try:
    worksheet = spreadsheet.worksheet(worksheet_name)
except:
    worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows="100", cols="10")

# 🔹 Daftar saham yang akan diambil
tickers = ["AMRT.JK", "ITMG.JK", "ADRO.JK", "ASII.JK"]

# 🔹 Ambil Data Keuangan dari Yahoo Finance
data_list = []
for ticker in tickers:
    stock = yf.Ticker(ticker)
    financials = stock.financials  # Laporan keuangan

    if financials.empty:
        print(f"Tidak bisa mengambil data untuk {ticker}")
        continue

    # Ambil 2 tahun terakhir
    years = list(financials.columns)
    if len(years) < 2:
        print(f"Data kurang dari 2 tahun untuk {ticker}")
        continue

    current_year = years[0].year
    previous_year = years[1].year

    revenue_current = financials.loc["Total Revenue", years[0]] if "Total Revenue" in financials.index else "N/A"
    revenue_previous = financials.loc["Total Revenue", years[1]] if "Total Revenue" in financials.index else "N/A"
    net_income_current = financials.loc["Net Income", years[0]] if "Net Income" in financials.index else "N/A"
    net_income_previous = financials.loc["Net Income", years[1]] if "Net Income" in financials.index else "N/A"

    data_list.append([ticker, revenue_previous, revenue_current, net_income_previous, net_income_current])

# 🔹 Buat DataFrame
df = pd.DataFrame(data_list, columns=["Ticker", "Revenue Previous Year", "Revenue Current Year", 
                                      "Net Income Previous Year", "Net Income Current Year"])

# 🔹 Simpan ke Google Sheets
worksheet.clear()  # Hapus data lama sebelum menulis data baru
set_with_dataframe(worksheet, df)

print("✅ Data berhasil dikirim ke Google Sheets pada worksheet 'tabelincome'!")

