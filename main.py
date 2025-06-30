api_key = "uqlV0YfO7c"
# EVDS API KEY


from evds import evdsAPI
evds = evdsAPI(api_key)
json = evds.get_data(['TP.DK.USD.A.YTL','TP.DK.EUR.A.YTL'], startdate="01-01-2019", enddate="01-01-2020")

print(json.head())







