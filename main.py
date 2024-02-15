import requests
import datetime as dt
import smtplib

#sheety headers and  endpoint to access google excel sheet
sheety_headers = {
    'Authorization': 'Basic cmFodWxzaGFybWE6dGhpc2lzcmFodWxzaGFybWE=',
    'username': 'rahulsharma',
    'password': 'thisisrahulsharma'
}
sheety_endpoint = f"https://api.sheety.co/98f599190df98cb70c3c2ab7c0e89530/dataflight/sheet1"

#kiwi headers and  endpoint to access google excel sheet
kiwi_apiKey = "Gds3SVxd1fXd7uvUk0peOOTdJh6E8AwQ"
kiwi_headers = {'apikey': kiwi_apiKey}
FROM_CITY = "mumbai"

#smtp access
to_email = "killbusyness@gmail.com"
email_appPass = "ysrp tvxs edye napz"

#getting sheet data
sheet_data = requests.get(sheety_endpoint, headers=sheety_headers).json()['sheet1']


def formattedDate(date,monthShift):
    return f"{date.day}%2F{date.month+monthShift}%2F{date.year}"

class DataManager: # this class manages the sheet data to edit existing row
    def __init__(self, sheet_data):
        self.sheet_data = sheet_data
    def editRow(self, iataCode, objectID):
        sheety_put_endpoint = f"{sheety_endpoint}/{objectID}"
        sheety_put_parameters = {
            'sheet1': {
            'iataCode': f'{iataCode}',
            }
        }
        requests.put(sheety_put_endpoint, json=sheety_put_parameters, headers=sheety_headers)

class FlightManager: #class to add IATA code ,to search flight
    def __init__(self):
        self.from_city = FROM_CITY
        self.all_cities = {}

    def iataCode(self, cityName): # this accepts city name as parameter and returns IATA code
        try:
            kiwi_search_endpoint = f"https://api.tequila.kiwi.com/locations/query?term={cityName}&locale=en-US&location_types=airport&limit=10&active_only=true"
            request_iata_code = requests.get(url=kiwi_search_endpoint, headers=kiwi_headers)
            return request_iata_code.json()['locations'][0]['id']
        except Exception:
            pass

    def collect_data(self, cityName,  cityData):
        self.all_cities.update({f"{cityName}": cityData})
 
    def searchflight(self, from_iata, to_iata): # This method returns all the data of the flight
        from_date = formattedDate(dt.datetime.now(), 0) # the second parameter here is to add into number of months
        to_date = formattedDate(dt.datetime.now(), 6) # 6 as a second paramtere here checks for flights for 6 months ahead
        #Note here the API end point accepts from IATA ,To IATA ,From date, To date (putting the parameters into dictonary is resulting into and error)
        kiwi_flight_search = f"https://api.tequila.kiwi.com/v2/search?fly_from={from_iata}&fly_ ={to_iata}&date_from={from_date}&date_to={to_date}&curr=INR&vehicle_type=aircraft&limit=100"
        
        new_data = requests.get(url=kiwi_flight_search, headers=kiwi_headers).json()['data']
        flight_data = []
        for flight in new_data:
            new_dict = {}
            new_dict.update({'cityFrom': f"{flight['cityFrom']}"})
            new_dict.update({'cityTo': f"{flight['cityTo']}"})
            new_dict.update({'distance': f"{flight['distance']} KM"})
            new_dict.update({'price': float(flight['price'])})
            new_dict.update({'local_departure': f"{flight['local_departure']}"})
            new_dict.update({'local_arrival': f"{flight['local_arrival']}"})
            flight_data.append(new_dict)
        return flight_data

data_manager = DataManager(sheet_data) #Give the excel sheet to edit the row
flight_manager = FlightManager()


for place_data in data_manager.sheet_data: # This fills the empty cell of IATA code 
    if len(place_data['iataCode']) == 0:
        iata_code = flight_manager.iataCode(place_data['city'])
        data_manager.editRow(iata_code, place_data['id'])


for data in data_manager.sheet_data:
    main_data = flight_manager.all_cities #This stores all the city data like 
    from_city_iata_code = flight_manager.iataCode(FROM_CITY)
    sheet_city_data = flight_manager.searchflight(from_city_iata_code, data['iataCode'])
    print(sheet_city_data)
    flight_manager.collect_data(data['city'], sheet_city_data)

    # for price_data in main_data[data['city']]:
    #     if price_data['price'] <= data['lowestPrice']:
    #         message = f"HURRY UP!!!\nFLIGHT FROM {FROM_CITY}-{from_city_iata_code}---> TO {data['city']}-{data['iataCode']}\n\nPRICE: {price_data['price']} INR\n\nDEPARTURE: {price_data['local_departure']}\nARRIVAL: {price_data['local_arrival']}\n\nDISTANCE: {price_data['distance']}"
    #         mail_connection = smtplib.SMTP("smtp.gmail.com")
    #         mail_connection.starttls()
    #         mail_connection.login(user="killbusyness2@gmail.com", password=email_appPass)
    #         mail_connection.sendmail(from_addr="killbusyness2@gmail.com", to_addrs=to_email, msg=message)
    #         break






