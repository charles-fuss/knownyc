import plotly.graph_objects as go
from getschools_ import * 
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests, re
import pandas as pd
import math, json

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
client = Socrata("data.cityofnewyork.us", 'ZUp9DH0xobMfk9OoRPHREFoIm',
                username='charlesfuss4@gmail.com',
                password='Syntax123!')

# Compiles recent rat reports from the user's neighborhood.
# !!!! TAKES zip AS STRING !!!
def rat_results(zip):
    results = client.get("p937-wjvj")
    results_df = pd.DataFrame.from_records(results)
    try:
        newdf = results_df.loc[(results_df['zip_code'] == zip) & (results_df['inspection_date'] > '2021-07-25T00:00:00.000')]
    # Pull an entry from the freshly generated dataset and extract the user's borough and clean.
        sample = newdf.sample(ignore_index=True)['borough']
        usr_borough = ''.join(char for char in sample if char not in "['")
    # Generate dataset of recent rat inspections in the user's borough.
        comp_df = results_df.loc[(results_df['borough'] == usr_borough) & (results_df['inspection_date'] > '2021-07-25T00:00:00.000')]
    # [edit] Might not respond well to the 2 in round()
        print("Your prospective zipcode constitutes ~",round((newdf.shape[0]/comp_df.shape[0])*100, 2),"% of all rat reports in", usr_borough)
    except:
        print('Your prospective zipcode has had no rat complaints in the past year. Woohoo!')

# DEBUG: filter out data that returns 0 for addy and neighborhood.
def pollution_results(address, neighborhood):
    user_data = find_address(address, False)
    neighborhood = neighborhood.title()
    hospitalizations , deaths, avg_benzene, nox_emissions, pmtoofive_emissions, sotoo_emissions, formaldehyde_conc, borough_avg_benzene, borough_nox_emissions, borough_pmtoofive_emissions, borough_sotoo_emissions, borough_formaldehyde_conc = 0,0,0,0,0,0,0,0,0,0,0,0 
    results = client.get("c3uy-2p5r")
    # Convert to pandas DataFrame
    results_df = pd.DataFrame.from_records(results)
    # Must iterate to avoid KeyError
    for index,row in results_df.iterrows():
        if neighborhood in row['geo_place_name'] and row['start_date'] > '2012-07-25T00:00:00.000':
            #print(row['name'])
            # Accumulate hospitalizations
            if 'Benzene Concentration' in row['name']:
                avg_benzene += float(row['data_value'])
            elif 'NOx Emissions' in row['name']:
                nox_emissions += float(row['data_value'])
            elif 'PM2.5 Emissions' in row['name']:
                pmtoofive_emissions += float(row['data_value'])
            elif 'SO2 Emissions' in row['name']:
                sotoo_emissions += float(row['data_value'])
            elif 'Average Formaldehyde Concentrations' in row['name']:
                formaldehyde_conc += float(row['data_value'])
            if('Hospitalizations' in row['name']):
                hospitalizations+=int(float(row['data_value']))
            # Accumulate deaths
            elif('Deaths' in row['name']):
                deaths+=int(float(row['data_value']))
    # find averages for the borough
    borough = user_data['borough']
    for index,row in results_df.iterrows():
        if borough in row['geo_place_name']:
            if 'Benzene Concentration' in row['name']:
                borough_avg_benzene += float(row['data_value'])
            elif 'NOx Emissions' in row['name']:
                borough_nox_emissions += float(row['data_value'])
            elif 'PM2.5 Emissions' in row['name']:
                borough_pmtoofive_emissions += float(row['data_value'])
            elif 'SO2 Emissions' in row['name']:
                borough_sotoo_emissions += float(row['data_value'])
            elif 'Average Formaldehyde Concentrations' in row['name']:
                borough_formaldehyde_conc += float(row['data_value'])

    print('In',neighborhood,' there have been ', hospitalizations,
    'hospitalizations, and ' , deaths, 'deaths due to air pollution.'
    ,'\n more data... \n PM2.5 emissions:', round(float(pmtoofive_emissions), 2) , 
    'avg:' ,round(float(borough_pmtoofive_emissions), 2),
    '\n benzene concentration:', round(avg_benzene,2), 'avg:' ,
    round(float(borough_avg_benzene),2),'\n NOx emissions:', 
    round(float(nox_emissions),2),'avg:' ,float(borough_pmtoofive_emissions),
     '\n SO2 Emissions: ', round(float(sotoo_emissions),2), 'avg:' ,
     round(float(borough_sotoo_emissions),2),'\n formaldehyde concentrations: ',
    round(float(formaldehyde_conc),2), 'avg:' ,
    round(float(borough_formaldehyde_conc),2),'\n in the last ten years.')



# DEBUG: maybe use different dataset? or filter idm
def demographics(zip):
    results = client.get("kku6-nxdu", limit=2000)
    results_df = pd.DataFrame.from_records(results)
    newdf = results_df.loc[(results_df['jurisdiction_name'] == zip)]
    try:
        pacific_islander = ''.join(char for char in newdf.sample(ignore_index=True)['percent_pacific_islander'] if char not in "['")
        latinx = ''.join(char for char in newdf.sample(ignore_index=True)['percent_hispanic_latino'] if char not in "['")  
        white =  ''.join(char for char in newdf.sample(ignore_index=True)['percent_white_non_hispanic'] if char not in "['")  
        black = ''.join(char for char in newdf.sample(ignore_index=True)['percent_black_non_hispanic'] if char not in "['")   
        asian = ''.join(char for char in newdf.sample(ignore_index=True)['count_asian_non_hispanic'] if char not in "['")
        naitive = ''.join(char for char in newdf.sample(ignore_index=True)['percent_american_indian'] if char not in "['")      
        unknown = ''.join(char for char in newdf.sample(ignore_index=True)['percent_ethnicity_unknown'] if char not in "['")   
    except:
        print('threw NaN')
        return
    if pacific_islander == '0' and latinx == '0' and white == '0' and 'black' == '0' and asian == '0' and naitive == '0':
        return('demographics unavailable for your zip code')
    print(
    '\npercent pacific islander: ', pacific_islander, 
    '\n percent hispanic latinx: ', latinx, 
    '\n percent cracker: ' , white, 
    '\n percent black: ', black,
    '\n percent naitive american', naitive,
    '\n percent asian', asian,
    '\n percent unknown: ', unknown)

people = {1: {'name': 'John', 'age': '27', 'sex': 'Male'},
          2: {'name': 'Marie', 'age': '22', 'sex': 'Female'}}

people[3] = {}

people[3]['name'] = 'Luna'
people[3]['age'] = '24'
people[3]['sex'] = 'Female'
people[3]['married'] = 'No'


# filters out uptown/downtown 
#loads fast asl
# bar chart the different subway lines, show each station and its distance
def subways(address):
    f = open("demofile2.txt", "a")
    sub_list = {}
    hold_error = True
    user_data = find_address(address, False)
    json = requests.get('https://data.cityofnewyork.us/api/views/he7q-3hwy/rows.json?accessType=DOWNLOAD')
    json_response = json.json()
    #from json response, find each address instance and analyze each one, checking
    # each one's distance from the user coords
    for dict in json_response['data']:
        train_address = str(dict[len(dict)-3])
        line = str(dict[-1])
        # Yes, the dataset had the coordinates backwards... stripping text here...
        backwards_coords = eval(str(dict[-2]).strip(' POINT ()').replace(' ', ', '))
        coords = (backwards_coords[1], backwards_coords[0])
        sub_list[train_address] = {}
        sub_list[train_address]['line'] = str(line)
        sub_list[train_address]['coords'] = coords
    # Iterate through nested dict and calculate distance in O(n)
    remove_dups = set()
    valid_addresses = set()
    for key in sub_list:
        dist = round(geodesic(sub_list[key]['coords'], user_data['coords']).mi, 2)
        if dist < .5:
                if key[0:len(key)-9] not in remove_dups:
                    remove_dups.add(key[0:len(key)-9])
                    valid_addresses.add('The '+ key[0:len(key)-12] + 'station is close to you!')
    for i in valid_addresses:
        print(i)
    return valid_addresses


def parks(address):
    clear_json('parks_json.json')
    clear_json('user_data.json')
    f = open('parks_json.json', 'w')
    u = open('user_data.json', 'w')
    user_data = find_address(address, False)
    u.write(json.dumps(find_address(address, False), indent=4))
    u.close()
    if user_data['borough'] == 'The Bronx':
        user_data['borough'] = 'Bronx'
    results = client.get("hv9n-xgy4", limit=100000)
    results_df = pd.DataFrame.from_records(results)
    newdf = results_df.loc[(results_df['borough'] == user_data['borough'][0].upper())]
    filterrows = set()
    parks = {}
    nearby_parks = {}
    print(newdf)
    for index,row in newdf.iterrows():
        if row['propertyname'] not in filterrows:
           # print(row['propertyname'], ': ', row['point']['coordinates'])
            filterrows.add(row['propertyname'])
            parks[row['propertyname']] = {}
            parks[row['propertyname']]['coords'] = eval('(' + str(row['point']['coordinates'][1]) + ', ' + str(row['point']['coordinates'][0]) + ')')
            parks[row['propertyname']]['hours'] = str(row['hours'])
    print('successfully filtered df')
    for key in parks:
        dist = round(geodesic(parks[key]['coords'], user_data['coords']).mi, 2)
        if dist < .5:
            print('found nearby park')
            # Filter out NaNs with a neat trick
            nearby_parks[key] = {}
            nearby_parks[key]['distance'] = dist
            nearby_parks[key]['coords'] = parks[key]['coords']
            if parks[key]['hours'] != parks[key]['hours']:
                nearby_parks[key]['hours'] = parks[key]['hours']
                parks[key]['dist'] = dist
                print(key, 'is ', parks[key]['dist'], 'miles away from you! \nHours: ' , parks[key]['hours'])
            else:
                print(key, 'is ', round(dist,2), 'miles away from you!')
    f.write(json.dumps(nearby_parks, indent = 4))
    f.close()
    return parks
    #return park_events(parks, user_data)

# locvation, event_name
# this finna b slow
def park_events(parks, user_data):
    x=set()
    results = client.get("6v4b-5gp4", limit=100000)
    results_df = pd.DataFrame.from_records(results)
    for key in parks:
        try:
            for index, rows in results_df.iterrows():
                if key in str(rows['location']) and str(rows['event_name']) not in x and key==key:
                    x.add(rows['event_name'])
                    print('at ', key, 'you can see/do', rows['event_name'], '!')
        except:
            print('throws Nan')
    print(x)



    

# visualize: https://kb.tableau.com/articles/howto/plotting-geographic-data-using-custom-longitude-and-latitude
def crime(address):
    # most popular crimes, diffrent types of crimes (felony, misdemenor)
    # First, we need user lat/long
    # categories: violent, sex crimes, fraud, misdemeanors, automobile theft/tampering
    sex_crimes, violent_crimes, fraudluent_crimes, auto_crimes, misc_crimes, theft_crimes = 0,0,0,0,0,0    
    user_data = find_address(address, False)
    results = client.get("qgea-i56i", limit=100000)
    results_df = pd.DataFrame.from_records(results)
    if user_data['borough'] == 'The Bronx':
        user_data['borough'] = 'Bronx'
    #filter rpt date but figure out how with floating timestamp, 
    #print(user_data['borough'])
    results_df = results_df.loc[(results_df['boro_nm'] == user_data['borough'].upper()) & (results_df['rpt_dt'] > '2010-07-25T00:00:00.000')]
    for index, row in results_df.iterrows():
        try:
            row_coord_tuple = (row['lat_lon']['latitude'] , row['lat_lon']['longitude'])
            if(geodesic(user_data['coords'], row_coord_tuple).mi) <= .5:
                # Sort crimes into categories for later visualization
                if 'SEX' in row['ofns_desc'] or 'RAPE' in row['ofns_desc']:
                    sex_crimes+= 1
                elif 'ASSAULT' in row['ofns_desc'] or 'HARRASSMENT' in row['ofns_desc']:
                    violent_crimes+= 1
                elif 'FORGERY' in row['ofns_desc'] or 'FRAUD' in row['ofns_desc']:
                    fraudluent_crimes += 1
                elif 'VEHICLE' in row['ofns_desc'] or 'AUTO' in row['ofns_desc'] or 'MOTOR' in row['ofns_desc']:
                    auto_crimes+= 1
                elif 'BURGLARY' in row['ofns_desc'] or 'LARCENY' in row['ofns_desc']:
                    theft_crimes+=1
                else:
                    # drugs, disturbing the peace
                    misc_crimes+= 1
        except:
            print('throws NaN')
    if user_data['borough'] == 'Bronx':
        user_data['borough'] == 'The Bronx'
    nearby_crime = {'sex_crimes':sex_crimes, 'violent_crimes':violent_crimes, 'fraud_crimes': fraudluent_crimes, 'auto_crimes': auto_crimes, 'misc_crimes':misc_crimes}
    print('Within .5 miles of your address, ' , address , '...\n\nsex crimes:' , sex_crimes , '\nviolent crimes:' , 
    violent_crimes, '\nfraudulent crimes:', fraudluent_crimes, 
    '\nauto crimes:', auto_crimes, '\ntheft crimes:', theft_crimes,
     '\nmisc crimes:' , misc_crimes)
    
    f = open('nearby_crime', 'w')
    f.write(json.dumps(nearby_crime, indent = 4))
    f.close()
    return nearby_crime

def clear_json(file):
    open(file, 'w').close()


def main():
    # 30 Malcolm X Blvd #402,New York, NY 10026 -- harlem(mn)
    # 72 Richardson St #10, Brooklyn, NY 11211 -- williamsburg(bk)
    # 228 Bushwick Ave APT 5C, Brooklyn, NY 11206 -- williamsburg
    # 100 Luten Ave, Staten Island, NY 10312 -- tottenville(si)
    # 102-30 66th Rd, Forest Hills, NY 11375 -- forest hills (queens)
    # 700 oakland place bronx ny 10457 -- tremont(bx)

    # using soql queries in url requests may be significantly faster than
    # doing it yourself... comb thru
    # write api requests to a file and save $

    addy = input('this is a test. input your street address   ')
    zip = input('please input your zip  ')
    neighborhood = input('this is a test. please input your neighborhood \n ex.) gramercy, fordham, williamsburg, etc   ')
    parks(addy)
    '''pollution_results(addy, neighborhood)
    demographics(zip)
    print(crime(addy))
    rat_results(zip)'''

main()
# Why not just take the data structure, convert it to JSON, and then write a .js file that your .html file includes that is simply var data = { json: "object here" };
# https://docs.mapbox.com/mapbox-gl-js/example/
# for illustrating data
# https://plotly.com/python/