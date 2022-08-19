from requests_html import AsyncHTMLSession, HTMLSession
import time
import json
import csv
import re
from collections import OrderedDict
import requests
from bs4 import BeautifulSoup

asession = AsyncHTMLSession()
redfintxt = open('redfindata.txt', 'a', encoding='utf-8')
#last_page = 80

def get_pages(s, e):
    start_page = s
    end_page = e
    url = 'https://www.redfin.com/city/29465/IL/Bolingbrook/filter/property-type=house+condo+townhouse,include=sold-3yr'
    #url = 'https://www.redfin.com/city/29501/IL/Naperville/filter/property-type=house+condo+townhouse,include=sold-3yr/'
    links = []
    while start_page < end_page:
        links.append(url + f'page-{start_page}')
        start_page += 1
    return links


async def get_old_house_links(url):
    listings = []
    r = await asession.get(url)
    await r.html.arender(retries=50, sleep=1, timeout=300)
    r.close()
    container_list = r.html.find('.HomeCardContainer')
    # find home cards
    for container in container_list:
        # find pill symbols
        def_sold_date = container.find('.Pill--sold')
        red_sold_date = container.find('.Pill--red')
        print(def_sold_date)
        print(red_sold_date)
        if len(def_sold_date) + len(red_sold_date) == 0:
            continue
        elif len(def_sold_date) > 0:
            text = def_sold_date[0].text[-4:]
        elif len(red_sold_date) > 0:
            text = red_sold_date[0].text[-4:]
        # convert integer
        text = re.sub('\D', '', text)
        if len(text) > 0:
            text = int(text)
        else:
            continue
        # add old housings
        if text == 2020:
            try:
                home = container.find('a[data-rf-test-name=basic-card-photo]')
                listings.append('redfin.com' + (home[0].get('href')))
            except:
                print('error')
                print(text)
    print(listings)
    return listings


async def get_house_links(page):
    listings = []
    r = await asession.get(page)
    await r.html.arender(retries=50, sleep=1, timeout=300)
    r.close()
    home_list = r.html.find('a[data-rf-test-name=basic-card-photo]')
    for link in home_list:
        listings.append(list(link.absolute_links)[0])
    print(listings)
    return listings


def get_old_house_links_v2(url):
    listings = []
    r = requests.get('http://localhost:8050/render.html', timeout=45, params={'url': url, 'wait': 1})
    soup = BeautifulSoup(r.content, 'html.parser')
    container_list = soup.select('.HomeCardContainer')
    # find home cards
    for container in container_list:
        # find pill symbols
        def_sold_date = container.select('.Pill--sold')
        red_sold_date = container.select('.Pill--red')
        if len(def_sold_date) + len(red_sold_date) == 0:
            continue
        elif len(def_sold_date) > 0:
            text = def_sold_date[0].text[-4:]
        elif len(red_sold_date) > 0:
            text = red_sold_date[0].text[-4:]
        # convert integer
        text = re.sub('\D', '', text)
        if len(text) > 0:
            text = int(text)
        else:
            continue
        # add old housings
        if text == 2020:
            try:
                home = container.select('a[data-rf-test-name=basic-card-photo]')
                listings.append('redfin.com' + (home[0].get('href')))
            except:
                print('error')
                print(text)
    print(listings)
    return listings


def write_csv():
    redfindata = []
    fields = ['Property Type', 'HOA Dues', 'Year Built', 'Community', 'List Price', 'housingprice', 'Est. Mo. Payment',
              '# Of Cars', 'High School', 'address', 'beds', 'baths', 'sqft', 'Heating', 'Cooling',
              '# of Baths (Full)', '# of Baths (1/2)', '# of carpet', '# of hardwood', 'Basement',
              'Basement Description', 'Basement Sq. Ft.', 'Tax Annual Amount', '# of Rooms', 'month', 'yearsold']

    with open('redfindata.txt', 'r', encoding='utf-8') as my_file:
        lines = my_file.readlines()
        '''
        test = lines[26]
        test.rstrip('\n')
        test = str(test).replace("'", '"')
        test = test.replace('Buyer"', "Buyer'")
        print(test)
        '''
        for line in lines:
            line.rstrip('\n')
            res = str(line).replace("'", '"')
            res = res.replace('Buyer"', "Buyer'")
            data = json.loads(res)
            redfindata.append(data)
            if '# of Cars' in data:
                data['# Of Cars'] = data['# of Cars']
                del data['# of Cars']
            if 'Tax' in data:
                data['Tax Annual Amount'] = data['Tax']
                del data['Tax']

    # get rid of housingprice format
    i = 0
    for entry in redfindata:
        try:
            price = entry['housingprice']
            price = re.sub("[\(\[].*?[\)\]]", "", price)
            entry['housingprice'] = price
        except:
            i+=1
            print(i)

    for entry in redfindata:
        try:
            entry['beds'] = float(entry['beds'])
        except:
            print(entry['beds'])

    with open('redfindata.csv', 'w') as my_file:
        d_writer = csv.DictWriter(my_file, fieldnames=fields, extrasaction='ignore')
        d_writer.writeheader()
        for data in redfindata:
            d_writer.writerow(data)


async def get_data(url):
    r = await asession.get(url)
    val = await r.html.arender(retries=50, timeout=300)
    r.close()
    details = []
    garage_list = []

    # find the first section of info
    key_details_list = r.html.find('.keyDetail')

    # filter through first section and add all data entries
    for detail_list in key_details_list:
        span_list = detail_list.find('span')
        for span in span_list:
            details.append(span.text)

    # remove duplicates in details list
    details = list(OrderedDict.fromkeys(details))

    # form dictionary from first section
    counter = 0
    details_dict = {}
    while counter < len(details) - 1:
        details_dict[details[counter]] = details[counter + 1]
        counter += 2

    # finding the rest of the information
    super_group_content = r.html.find('.super-group-content')

    # filtering through each section of the remaining information
    keyattrs = ["Cars", "High School:", "Heating:", "Cooling:", "# of Rooms", "# of Baths",
                "Carpet", "Hardwood", "Basement:",
                "Basement Description:", "Basement Sq. Ft.:", "Tax Annual Amount:"]
    carpet = 0
    hardwood = 0
    for group_content in super_group_content:
        span_list = group_content.find('span')
        for span in span_list:
            for attr in keyattrs:
                if attr in span.text:
                    floor = False
                    if attr == "Carpet":
                        floor = True
                        carpet += 1
                    if attr == "Hardwood":
                        floor = True
                        hardwood += 1
                    if floor is False:
                        garage_list.append(span.text)
    garage_list.append(str(f"# of carpet: {carpet}"))
    garage_list.append(str(f"# of hardwood: {hardwood}"))

    # adding selected data to dictionary
    for data in garage_list:
        garage_string = data.split(":")
        details_dict[garage_string[0]] = garage_string[1]

    # adding the address
    split = (url.split('/'))
    split = (split[5].split('-'))
    details_dict['address'] = ' '.join(split)

    # finding top stats
    stats_values = r.html.find('.statsValue')

    # adding stats to dictionary
    details_dict['beds'] = stats_values[1].text
    details_dict['baths'] = stats_values[2].text
    details_dict['sqft'] = stats_values[3].text

    try:
        price_cols = r.html.find('.secondary-info')[0].text
        sentence = price_cols.split()
        for word in sentence:
            if '$' in word:
                details_dict['housingprice'] = word  # old listings
            else:
                details_dict['housingprice'] = stats_values[0].text
    except IndexError:
        details_dict['housingprice'] = stats_values[0].text  # live listings
    except:
        print(url)

    months = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6, 'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}

    try:
        date = r.html.find('.Pill--sold')[0].text
        for key in months:
            if key in date:
                details_dict['month'] = months[key]
        year = date[-4:]
        details_dict['yearsold'] = year
        #details_dict['selldate'] = date
    except:
        print(url)
    #print(date)

    redfintxt.write(str(details_dict))
    redfintxt.write('\n')
    return val


def run_get_house_links(old):
    lambdas = []
    links = []

    if old is False:
        for i in get_pages(1, last_page):
            lambdas.append(lambda url=i: get_house_links(url))
    if old is True:
        for i in get_pages(1, last_page):
            lambdas.append(lambda url=i: get_old_house_links(url))

    for i in lambdas:
        links = asession.run(i)[0] + links

    return links


def run_get_data():
    list_of_lambdas = []
    count = 0
    for i in main_link_list:
        if count == 10: break
        list_of_lambdas.append(lambda url=i: get_data(url))
        count += 1

    for i in list_of_lambdas:
        asession.run(i)


#this below will get commented out a lot
main_link_list = run_get_house_links(old=True)
print(main_link_list)
#----------------------------------------------------------------------------------------
# main_link_list = []
# listings_list = get_pages(0, X)
# for listing in listings_list:
#     main_link_list += get_old_house_links_v2(listing)
# main_link_list = set(main_link_list)
# main_link_list = list(main_link_list)
# for i in range(len(main_link_list)):
#     main_link_list[i] = 'https://' + main_link_list[i]  # set a new value
# print(main_link_list)


# while len(main_link_list) > 0:
#     print("---------------------" + str(len(main_link_list)))
#     run_get_data()
#     main_link_list = main_link_list[10:]


#write_csv()

#filter out - — — � *