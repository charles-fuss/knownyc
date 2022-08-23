import requests, concurrent, time, re, math, json
from threading import Thread
from zipfile import ZIP_MAX_COMMENT
from geopy.geocoders import Nominatim
import requests, re
import pandas as pd
from sodapy import Socrata

# Comments
    # Only data from BK/MN


pd.options.mode.chained_assignment = None  # default='warn'


# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
client = Socrata("data.cityofnewyork.us", 'ZUp9DH0xobMfk9OoRPHREFoIm',
                username='charlesfuss4@gmail.com',
                password='Syntax123!')

def addr_to_ordinal(address):
    ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
    string_list = address.split()
    for index, word in enumerate(string_list):
        # Transform to ordinal form, but also checking the word is not already in ordinal form/has special characters.
        try:
            if re.findall(r'\d+', word) and word[len(word)-2:] != 'st' and word[len(word)-2:] != 'nd' and word[len(word)-2:] != 'rd' and word[len(word)-2:] != 'th' and word[len(word)-2:] != 'ST' and word[len(word)-2:] != 'ND' and word[len(word)-2:] != 'RD' and word[len(word)-2:] != 'TH' and '-,`~.' not in word and len(word) < 7:
                string_list[index] = ordinal(int(word))
            else:
                string_list[index] = word
        # catch any odd addresses that slip through validation
        except:
            return address
    string_list = ' '.join(string_list)
    return string_list



# Uses Google's Geocoder API to locate addresses and return a postal code + borough.
def find_address(address, flag):
    API_KEY = 'AIzaSyApeNsbncrLyjKJw3itJHXyYLLdgBAi-Z4'
    #address = addr_to_ordinal(address)
    # Ensures that only street addresses are put in ordinal structure
    #if(len(address) !=5):
    stripped_school_address = re.sub(r"\s+", '%', address)
    # Prepares the API query
    params = { 'key' : API_KEY, 'address' : stripped_school_address}
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
    try:
        json_data = requests.get(base_url, params=params).json()
    except:
        return 'Request failed'
    # We now have the API response! We can now parse the json response and return the borough/zip. 
    results = {'borough': 'nil', 'zip': 'nil', 'coords':'nil', 'address':'nil'}
    try:
        results['coords'] = (json_data['results'][0]['geometry']['location']['lat'], json_data['results'][0]['geometry']['location']['lng'])
        results['address'] = address
    except:
        x=1
        #print('could not fetch coordinates')
        
    try:
        for key in json_data['results'][0]['address_components']:
            if key['long_name'] == 'Brooklyn':
                results['borough'] = 'Brooklyn'
            elif key['long_name'] =='Manhattan':
                results['borough'] = 'Manhattan'
            elif key['long_name']=='Queens':
                results['borough'] = 'Queens'
            elif key['long_name']=='The Bronx' :
                results['borough'] = 'The Bronx'
            elif key['long_name']=='Staten Island':
                results['borough'] = 'Staten Island'
            # Find zip
            elif 'postal_code' == key['types'][0]:
                results['zip'] = key['short_name']
    except:
        if(flag == True):
            #print('Dead address...')
            return results
        #print('Query does not contain address_components. Trying with ordinal:')
        find_address(addr_to_ordinal(address), True)
    '''if(flag == True):
        print('Everybody deserves a second chance. Success!')'''
    #print(results)
    print('got address')
    return results


# Finds nearby schools according to NYC's 2019 - 2020 School Locations
def generate_nearby_schools_table(zip, borough, public_school):
    bbl = ''
    if(borough == 'Manhattan'):
        bbl = '1'
    elif(borough == 'The Bronx'):
        bbl = '2'
    elif borough == 'Brooklyn':
        bbl = '3'
    elif borough == 'Queens':
        bbl = '4'
    elif borough == 'Staten Island':
        bbl = '5'
    else:
        return 'Invalid borough. (How did this slip through find_address ?)'
    school_list = []
    results = client.get("wg9x-4ke6", limit=1000)
    results_df = pd.DataFrame.from_records(results)
    # In order to increase efficiency and limit API queries, we will filter the dataset according to the 
    # user's borough. 
    bbl_df = results_df.iloc[0:0]
    #print('fetched bbl_df')
    for index,row in results_df.iterrows():
        #print('iterating results_df')
        if row['borough_block_lot'][0] == bbl:
            bbl_df.loc[len(bbl_df.index)] = row
    return school_entry(bbl_df, zip, public_school)



# Passing in a table of schools in user borough, pass in a single entry's address and figure out proximity
# to user.

def school_entry(df, zip, public_schools):
    print('dataframe in user boroguh:\n',df)
    results = {'schools' : 'nil'}
    resultsXI = []
    print('parsing schools')
    for index,row in df.iterrows():
        if public_schools == True:
            x = find_address(row['primary_address_line_1'], False)
            try:
                if x['zip'] == str(zip):
                    print(str(row['location_name']) , ' is in your zip!')
                    results['schools'] = (str(row['location_name']))
                    resultsXI.append(str(row['location_name'])) 
            except:
                x = 0  # error with geolocation return vals
        else:
            if 'P.S.' not in row['location_name']:
                 x = find_address(row['primary_address_line_1'], False)
            try:
                if x['zip'] == str(zip):
                    print(str(row['location_name']) , ' is in your zip!')
                    results['schools'] = (str(row['location_name']))
                    resultsXI.append(str(row['location_name'])) 
            except:
                x = 0  # error with geolocation return vals
            else:
                x=0 # don't count public schools
    return resultsXI



#DEBUG: make faster (threading), filter out some BS school entires
def master(zip, public_school):
    dict = find_address(str(zip), False)
    results = generate_nearby_schools_table(dict['zip'], dict['borough'], public_school)
    print('Final results:' , results)
