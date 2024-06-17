"""
The project does the following:
1) Scrapes Wikipedia 'This Day in History'
2) Grabs the years and events for the day that is input
3) Visit a link for each year grabbed and tries to find an image
4) Connects to Google Sheets and populates a spreadsheet using the format from this website: https://timeline.knightlab.com/#make
5) Creates a timeline using the sheet made through the websiite: https://timeline.knightlab.com/#make
"""

from bs4 import BeautifulSoup
import requests

def get_html(url, path):
    """Requests a webpage and saves the responces into a file"""
    response = requests.get(url)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(response.text)

date = input("Please enter a date in the month_date format, such as October_1: ")
# date = 'October_1'
##Temporary variable for testing
# date = 'June_12'

url = 'https://en.wikipedia.org/wiki/{}'.format(date)
# get_html(url, '../html_docs/on_this_day_{}.html'.format(date)) #Comment after run to avoid doing this multiple times


##Open the file and save the document to a variable
# with open('../html_docs/on_this_day_{}.html'.format(date), 'r', encoding='utf-8') as f:
#     html = f.read()


##URL is called directly
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
# print(soup)

##NEED TO HANDLE A DATE THAT IS NOT VALID, MISPELLED, OR INCORRECTLY FORMATTED
pass

##Get all the information under the 'Events' heading
# events = soup.find_all('span', attrs={'class':"mw-headline"})
# print(events)
events = soup.find_all(['h2', 'h3'])
# print(events)

# for i in events:
#     print(i)
a = soup.find_all(['h2', 'h3'])
events_lst = []
event_lst_cleaned = []
events_lst.extend([a[2], a[3], a[4]])
# print(events_lst[0].next_sibling.next_sibling.find_all('sup'))
# print(events_lst[0].next_sibling.next_sibling)

for i in range(len(events_lst)):
# Remove all <sup> tags (in order to remove the citation reference brackets)
    for sup in events_lst[i].next_sibling.next_sibling.find_all('sup'):
        sup.decompose()

    # Extract and print the text from each <li> tag
    for li in events_lst[i].next_sibling.next_sibling.find_all('li'):
        # print(li)
        a = li.get_text()
        event_lst_cleaned.append(a)

# print(events_lst[0].next_sibling.next_sibling)

def create_event_links():
    # Create a list of links to visit in order to grab an image from corresponding page
    event_links = []
    for i in range(len(events_lst)):
        li_content_list = [li for li in events_lst[i].next_sibling.next_sibling] # Get the list of events
        li_content_list = li_content_list[::2] # Remove blank lines
        # print(li_content_list)
        for i in range(len(li_content_list)): # loop through each event goal is to find some image to associate with the event
            pg_to_visit = li_content_list[i].find_all('a') # find all the links for the event
            if str(pg_to_visit[0].text).isnumeric(): # Check to see if the first link is the year of the event, if it IS, then grab the second link for that event
                # print(pg_to_visit[1].get('href'))
                event_links.append(pg_to_visit[1].get('href'))
            else: # If it is not then grab the first link
                # print(pg_to_visit[0].get('href'))
                event_links.append(pg_to_visit[0].get('href'))

    print(event_links)
    return event_links
# print(event_links[4])

def create_image_collection():
    exclude_matches = ['Semi-protection-shackle', 'Sound-icon', 'Ambox_important', 'red_question_mark', 'Symbol_support_vote',
                       'Pending-protection-shackle', 'Cscr-featured', 'Acap', 'Commons-logo', 'Extended-protection-shackle', 'UI_icon_edit',
                       'Translation_to_english', 'Wikisource-logo', 'Question_book-new', 'Edit-clear']
    event_links = create_event_links()
    img_collection = []
    # Grab the first image in the page of event_links to represent the event in question
    for i in range(len(event_links)):
        pg_to_visit = 'https://en.wikipedia.org' + event_links[i]
        response = requests.get(pg_to_visit)
        pg_to_visit_soup = BeautifulSoup(response.text, 'html.parser')
        first_image = pg_to_visit_soup.find_all('img', attrs={'class':'mw-file-element'})
        try: # Sometimes the page does not have an associated image
            # for exclude in exclude_matches:
            # if any(exclude_matches) in first_image[0].get('src'):
            """We should search through the first 3 images, first_image[i].get('src') on the page for excluded images"""
            if any(e in first_image[0].get('src') for e in exclude_matches):
                if any(e in first_image[1].get('src') for e in exclude_matches):
                    if any(e in first_image[2].get('src') for e in exclude_matches):
                        print('https:' + first_image[3].get('src'), 'djkshfjdsgfjsdgfjkh33')
                        img_collection.append('https:' + first_image[3].get('src'))
                    else:
                        print('https:' + first_image[2].get('src'), 'djkshfjdsgfjsdgfjkh11')
                        img_collection.append('https:' + first_image[2].get('src'))
                else:
                    print('https:' + first_image[1].get('src'), 'djkshfjdsgfjsdgfjkh22')
                    img_collection.append('https:' + first_image[1].get('src'))
            else:
                print('https:' + first_image[0].get('src'))
                img_collection.append('https:' + first_image[0].get('src'))
        except:
            img_collection.append('No image on the page')
            print('No image on the page')

    print(img_collection)
    return img_collection


"""Utilize the functions above"""
##Create a list for the year of the event
year_of_occurence = []
event_description = []
img_links = []
# print(event_lst_cleaned)
for i in range(len(event_lst_cleaned)):
    year = event_lst_cleaned[i][:event_lst_cleaned[i].find('–')-1]
    if 'BC' not in year: # If the year is not BC just add it to the list
        year_of_occurence.append(year)
    else: # If the year is BC, drop BC and make year negative
        year = year[:year.find('B')-1]
        year = str(int(year)*-1)
        year_of_occurence.append(year)
    # Add the event text to a list for the current year in the loop
    event_descr = event_lst_cleaned[i][event_lst_cleaned[i].find('–') + 1:].strip()
    event_description.append(event_descr)

img_links = create_image_collection() #Grab links to images - returns a list

print(year_of_occurence)
print(event_description)
# print(len(year_of_occurence), len(event_description)) # should be the same number


# Write all data to a Pandas dataframe
# df = pd.DataFrame() # Create the df object
#
# df['year'] = year_of_occurence
# df['event'] = event_description
# df['image'] = create_image_collection()
# df.to_excel('timeline.xlsx', index = False)


"""Write the data to the Google Sheet for timeline creation"""
from oauth2client.service_account import ServiceAccountCredentials
import gspread

def parse_headline():
    month_parsed = date[0:date.find('_')]
    day_parsed = date[date.find('_')+1:]
    head_line_text = f'This timeline shows key events across history that have occured on {month_parsed} {day_parsed}. ' \
                     f'The data is scraped from Wikipedia using Python.'
    return ["A Day in History" +' - ' + month_parsed + ' ' + day_parsed, head_line_text]


# headline = parse_headline()
# print(headline)

def write_to_google_sheet():
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    credentials = ServiceAccountCredentials.from_json_keyfile_name("timeline.json", scopes)  # access the json key you downloaded earlier
    file = gspread.authorize(credentials)  # authenticate the JSON key with gspread
    sheet = file.open("Copy of Official TimelineJS3 Template")  # open sheet
    sheet = sheet.sheet1  # replace sheet_name with the name that corresponds to yours, e.g, it can be sheet1

    # Set the desired number of rows and columns
    num_rows = len(year_of_occurence)+2
    num_columns = 18

    # Resize the sheet
    sheet.resize(rows=num_rows, cols=num_columns)

    """Write the data"""
    # for i in range(len(year_of_occurence)):
    #     sheet.update_cell(i+3, 1, year_of_occurence[i]) # Year of occurence
    #     sheet.update_cell(i+3, 11, event_description[i]) #Event text

    #Update the year
    cell_list = sheet.range(f'A3:A{num_rows}')
    for i, cell in enumerate(cell_list):
        cell.value = year_of_occurence[i]

    # Update the cells in batch
    sheet.update_cells(cell_list)

    #Update the event
    cell_list = sheet.range(f'K3:K{num_rows}')
    for i, cell in enumerate(cell_list):
        cell.value = event_description[i]

    # Update the cells in batch
    sheet.update_cells(cell_list)

    cell_list = sheet.range(f'L3:L{num_rows}')
    for i, cell in enumerate(cell_list):
        cell.value = img_links[i]

    # Update the cells in batch
    sheet.update_cells(cell_list)

    sheet.update_acell('J2', parse_headline()[0])
    sheet.update_acell('K2', parse_headline()[1])

write_to_google_sheet()


######old code #############
# create_image_collection()

# print(event_lst_cleaned)
# timeline = {}

# for i in range(len(event_lst_cleaned)):
#     a = event_lst_cleaned[i][:event_lst_cleaned[i].find('–')-1]
#     timeline[a] = event_lst_cleaned[i][event_lst_cleaned[i].find('–') + 1:].strip()
#
#
# print(timeline)

# #Save the dictionary as a string to a file in order to build a timeline
# with open('day_in_history.txt', 'w', encoding='utf-8') as f:
#     f.write(date + '\n')
#     f.write(str(timeline)) #use eval() function to convert back into dictionary when opening