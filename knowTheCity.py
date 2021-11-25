# -*- coding: utf-8 -*-
"""
Created on Thu Nov 25 07:28:55 2021

@author: Apsara
"""



from amadeus import Client, ResponseError
from flask import Flask, render_template
import json
from pymongo import MongoClient
import requests
app = Flask(__name__)
amadeus = Client(
    client_id='nlvN6SoJb4Bfj2CXqaMJrmq4hj5mPqd0',
    client_secret='0Ho7B9A92u3ONLMG'
    )


items=[]

@app.route("/")
def home():
    return render_template('HomePage.html')

@app.route("/about/<city>")
def about(city):
    return render_template('about1.html', cityname=city)

@app.route("/KnowTheCity/CountryDetails/<city>")
def countryDetailsHTML(city):
    return render_template('countryPg.html',cityname=city)

@app.route("/KnowTheCity/CityActivities/<city>")
def cityActivitiesHTML(city):
    return render_template('about1.html',cityname=city)

@app.route("/KnowTheCity/CovidInfo/<city>")
def covidInfoHTML(city):
    return render_template('covidinfo.html',cityname=city )

@app.route("/KnowTheCity/WeatherReport/<city>")
def weatherReportHTML(city):
    return render_template('WeatherPage.html',cityname=city)

@app.route("/KnowTheCity/NoInfo")
def noInfoHTML():
    return render_template('NoInfoPage.html')

@app.route("/ws/CountryDetail/<city>", methods=['GET','POST'])
def countryDetails(city):
    country = cityfromcountry(city)
    #country = "Chennai"
    st='https://travelbriefing.org/'+country+'?format=json'
    api_result = requests.get(st)
    print("result")
    print(api_result.status_code)
    api_response = api_result.json()
    
    list_languages=api_response["language"]
    languages=[]
    for i in list_languages:
        languages.append(i["language"])
        
    list_neighbors=api_response["neighbors"]
    neighbors=[]
    for i in list_neighbors:
        neighbors.append(i["name"])

    electricity_details=api_response["electricity"]
    
    telephonedetails=api_response["telephone"]

    currency_details=api_response["currency"]
    
    countrydetails={
            'country' : country,
            'currency_code':currency_details["code"],
            'languages':languages,
            'neighbors':neighbors,
            'calling_code':telephonedetails["calling_code"],
            'police':telephonedetails["police"],
            'ambulance':telephonedetails["ambulance"],
            'fire':telephonedetails["fire"],
            'voltage':electricity_details["voltage"],
            'frequency':electricity_details["frequency"],
            'plugs':electricity_details["plugs"]
            }
    result = json.dumps(countrydetails)
    print(result)
    
    return result

@app.route("/ws/CityActivities/<city>")
def activitiesCity(city):
    try:
        res = amadeus.get('/v1/reference-data/locations',subType='CITY',keyword=str(city))
        dt = res.data[0]
        lat = dt['geoCode']['latitude']
        lon = dt['geoCode']['longitude']
        #print(lat,lon)
        response = amadeus.shopping.activities.get(
            latitude=str(lat),
            longitude=str(lon),
            radius=20)
        d = response.body
        data = json.loads(d)
        if(len(data['data']) == 0):
            resu = {}
            return json.dumps(resu)
        #print(data)
        #print(data['data'][0])
        activities={}
        cnt = 0
        print("Status code" , response.status_code)
        if(response.status_code == 200):
            for d in data['data']:
                
                item = {
                'Type' : d['type'],
                'Name' : d['name'],
                'Description' : d['shortDescription'],
                #'Rating' : d['rating'],
                'Pictures' : d['pictures'],
                'Booking_link' : d['bookingLink'],
                'Currency_code' : d['price']['currencyCode'],
                'Amount' : d['price']['amount']
                }
                #items.append(item)
                cnt = cnt+1
                if(cnt == 6):
                    break
                activities[str(cnt)] = item
            result = json.dumps(activities, indent = 4) 
            return result
        else:
            resu = {}
            return json.dumps(resu)
        
    except ResponseError as error:
        print(error)

    

@app.route("/ws/CovidInfo/<city>")
def covidInfoCity(city):
    try:
        res = amadeus.get('/v1/reference-data/locations',subType='CITY',keyword=str(city))
        
        dt = res.data[0]
        ctyCode = dt['iataCode']
        cntyCode = dt['address']['countryCode']
        response = amadeus.get('/v1/duty-of-care/diseases/covid19-area-report', countryCode=str(cntyCode),cityCode=str(ctyCode))
        print(response)
        print("Status code")
        print(response.status_code)
        d = response.data
        #print("data",d)
        if(response.status_code == 200):
            print("Inside")
            info = {
                    'Area' : d['area'],
                    'Sub ' : d['subAreas'][0]['area'],
                    'Summary' : d['subAreas'][0]['summary'],
                    'Risk level' : d['subAreas'][0]['diseaseRiskLevel'],
                    'Disease infection' : d['diseaseInfection'],
                    'level':d['diseaseInfection']['level'],
                    'rate':d['diseaseInfection']['rate'],
                    'Disease cases' : d['diseaseCases'],
                    'deaths':d['diseaseCases']['deaths'],
                    'confirmed':d['diseaseCases']['confirmed'],
                    'Disease testing' : d['areaAccessRestriction']['diseaseTesting'],
                    'Instruction': d['areaAccessRestriction']['diseaseTesting']["text"],
                    'testingRequestion':d['areaAccessRestriction']['diseaseTesting']["isRequired"],
                    'Tracing_application' : d['areaAccessRestriction']['tracingApplication']['text'],
                    'Ios url' : d['areaAccessRestriction']['tracingApplication']['iosUrl'],
                    'Android url' : d['areaAccessRestriction']['tracingApplication']['androidUrl'],
                    'Mask' : d['areaAccessRestriction']['mask']['text'],
                    'Exit' : d['areaAccessRestriction']['exit']['text'],
                    'Vaccinated' : d['areaVaccinated'][0]['percentage']
                    }
            result = json.dumps(info, indent = 4)
            return result
        else:
            res = {}
            result = json.dumps(res)
            return result
        return json.dumps(result)
    except ResponseError as error:
        print(error)
        return error

@app.route("/ws/AllCountries")
def getAllCountries():
    url = "https://www.universal-tutorial.com/api/countries"
    headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7InVzZXJfZW1haWwiOiJhaXNod2FyeWEuYWRhaWtrYWxhdmFuQGdtYWlsLmNvbSIsImFwaV90b2tlbiI6InpScXM0R1VjV0xRMnBxOTlFRUdycmxmamctMDloOXFaN1ppUl91NjF4Y1FadmlhbU9fNTVSR3F3OXJrczluTEZ2bjgifSwiZXhwIjoxNjM0OTE1NDg0fQ.Ih8rezLOJ79QajGuIUeKKCsbpbSE0LUUn2zS4ONHFOs"}
    resp = requests.get(url, headers=headers)
    result=resp.json()
    countries_list={}
    cnt=0
    for r in result:
        country_info = {
                'Country Name' : r['country_name'],
                'Country Phone Code' : r['country_phone_code']}
        cnt = cnt+1
        countries_list[str(cnt)] = country_info
    result = json.dumps(countries_list, indent = 4)
    return result


@app.route("/ws/AllCities/<country>")
def getallcities(country):
    CONNECTION_STRING = "mongodb+srv://AishwaryaA:Shirdisaibaba_0601@cluster0.i3b39.mongodb.net/test"
    client = MongoClient(CONNECTION_STRING)
    db = client["countries"]
    mycol = db["cities"]

    mydoc=mycol.find( {"name":country} )
    l=[]
    citiesname=[]
    for x in mydoc:
        l=x['cities']
        for i in l:    
            citiesname.append(i['name'])
            
    #print(citiesname)
    result = json.dumps(citiesname, indent = 4)
    return result
    
@app.route("/ws/WeatherReport/<city>")
def getweather(city):
    url = "https://community-open-weather-map.p.rapidapi.com/weather"

    querystring = {"q":city,"lat":"0","lon":"0","callback":"test","id":"2172797","lang":"null","units":"imperial","mode":"xml"}
    
    headers = {
        'x-rapidapi-host': "community-open-weather-map.p.rapidapi.com",
        'x-rapidapi-key': "d33b90aeeamsh31fd6e5f0211c66p1bec37jsn5b515deae7f0"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    print("status code",response.status_code)   
    if (response.status_code == 200):
        res=response.text
        res=res.replace("test","")
        
        res=res.replace("(","")
        res=res.replace(")","")
        
        data=json.loads(res)
        #print(data)
        #print(s['weather'][0])
        maindetails=data['main']
        winddetails=data['wind']
        
        weatherdetails={
                'shortd':data['weather'][0]['main'],
                'description':data['weather'][0]['description'],
                'temp':maindetails['temp'],
                'feels_like':maindetails['feels_like'],
                'temp_min':maindetails['temp_min'],
                'temp_max':maindetails['temp_max'],
                'pressure':maindetails['pressure'],
                'humidity':maindetails['humidity'],
                'windspeed':winddetails['speed'],
                'winddegree':winddetails['deg']
                }
        
        result = json.dumps(weatherdetails, indent = 4)
        print(result)
        return result
    
    else:
        resu = {}
        return json.dumps(resu)


#@app.route("/ws/Upsert/<cityname>")
def upsert(cityname):
    CONNECTION_STRING = "mongodb+srv://AishwaryaA:Shirdisaibaba_0601@cluster0.i3b39.mongodb.net/test"
    client = MongoClient(CONNECTION_STRING)
    db = client['myDB']
    coll = db['cities']
    val=1
    cv=None
    freq=0
    if coll.count_documents({"city":cityname}) >0:
        print(coll.find({"city":cityname}))
        print("Yes")
        for doc1 in coll.find({"city":cityname}):
            cv=doc1
            freq=doc1['frequency']
            freq=freq+1
        coll.update_one(cv,{"$set":{"frequency":freq}})
    else:
        coll.insert_one({"city":cityname,"frequency":val})
       
        
    for doc2 in coll.find():
       print(doc2)

@app.route("/ws/FrequentSearches")       
def frequentlysearched():
    myclient = MongoClient("mongodb://localhost:27017/")
    db = myclient["myDB"]
    mycol = db["cities"]

    mydoc=mycol.find( {},{ "city": 1 } ).sort("frequency",-1).limit(3)
    for x in mydoc:
        print(x)
    return "Hello"

def cityfromcountry(city):
    CONNECTION_STRING = "mongodb+srv://AishwaryaA:Shirdisaibaba_0601@cluster0.i3b39.mongodb.net/test"
    client = MongoClient(CONNECTION_STRING)
    db = client["Webservice"]
    mycol = db["CountryAndCities"]
    mydoc=mycol.find({
    "cities.name" : city
    
    });

    #mydoc = mycol.find(myquery)

    for x in mydoc:
        countryname = x['name']
    return countryname
    
        
        
if __name__ == "__main__":
    app.run()
    

    
