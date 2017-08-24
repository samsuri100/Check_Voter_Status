"""
'Automated Voter Authentication' Program v1.0, Copyright 2017 Sam Suri, all rights reserved. Only use with permission. 

Program checks a csv file to obtain a list of possible voters. Uses current CSV file data. Crosschecks against live
county registration data. Dates in CSV file DO NOT have to be in standardized format. 
"""

from selenium import webdriver
from bs4 import BeautifulSoup
from pandas import DataFrame
from copy import deepcopy
import time
import re

table_list = []
temp_list = []
header = True
# declaring names of columns for CSV file that will output final results
data_frame_columns = ['First Name', 'Last Name', 'Suffix', 'Date of Birth', 'Zip', 'Original Status', 'Notes', 'Verified Status']

class Citizen:
    # URL of Dallas Country Registrar of Voters -- Voter Lookup Page
    base_url = 'http://www.dallascountyvotes.org/voter-lookup/#VoterEligibilitySearch'
    # using FireFox as web driver, specifically geckodriver, and pointing to its path
    ff_driver = webdriver.Firefox(executable_path=r'/Users/Sam/Desktop/geckodriver.exe')

    # initializing object with information needed by web page text fields
    def __init__(self, fname, lname, dob):
        self.fname = fname
        self.lname = lname
        self.dob = dob  # DOB = Date of Birth
        self.status = 'Unknown'  # Status is set to unknown by default, since 'no' implies verification was performed

    # function uses Beautiful Soup to check web page for table attributes
    def check_status(self, source_code):
        soup = BeautifulSoup(source_code, 'xml')  # parsing xml
        table = soup.table  # retrieves table in resulting page

        if table == None:  # for the first verified user, if they are not registered, no table will be present
            self.status = 'No'
            print(self.fname, self.lname, self.dob, self.status)  # allows user to see results as they are found
            return

        table_tag = table.find_all('tr')  # retrieves table rows in resulting page
        searched = re.search('PDF', str(table_tag))  # string 'PDF' is present on pages where someone is not registered

        if bool(searched) == True:  # assigns boolean value to 'PDF' search
            self.status = 'No'
        else:
            self.status = 'Yes'

        print(self.fname, self.lname, self.dob, self.status)  # allows user to see results as they are found

    # function uses selenium to simulate a browser, web page uses javascript
    def get_info_from_county(self):
        driver = self.ff_driver  # referencing earlier defined attributes
        base_url = self.base_url  # referencing earlier defined attributes

        driver.get(base_url)  # goes to website URL

        time.sleep(2)  # lets website load fully

        # navigates to appropriate text box via xpath
        elem = driver.find_element_by_xpath("//input[@id='VOTER_ELIGIBILITY_LOOKUP_FIRST_NAME']")
        elem.clear()
        elem.send_keys(self.fname)  # enters in object attributes

        elem = driver.find_element_by_xpath("//input[@id='VOTER_ELIGIBILITY_LOOKUP_LAST_NAME']")
        elem.clear()
        elem.send_keys(self.lname)

        elem = driver.find_element_by_xpath("//input[@id='VOTER_ELIGIBILITY_LOOKUP_BIRTH_DATE']")
        elem.clear()
        elem.send_keys(self.dob)

        elem = driver.find_element_by_xpath("//input[contains(@class, 'soe_form_button')]")
        elem.click()
        time.sleep(3)  # delay is to allow javascript in page to load

        js_source_code = driver.page_source  # source is saved to allow for parsing
        self.check_status(js_source_code)  # source is passed into check_status function to look for presence of table

        driver.stop_client()  # client is stopped since object function has been completed

# function takes into account difference in date format that EXCEL produces, website only takes 10 digit date style
def format_month(month_string):
    if len(month_string) == 10:  # if date is fine, returns unchanged parameter
        return month_string
    elif len(month_string) == 8:  # ie: 6/8/2014
        return '0' + month_string[0:2] + '0' + month_string[2:]
    elif month_string[1] == '/':  # ie: 6/15/2014
        return '0' + month_string[0:]
    else:  # ie: 10/5/2014
        return month_string[0:3] + '0' + month_string[3:]

# website will only take names that contain ASCII characters, and names cannot be blank, otherwise site will not work
def valid_ascii_text(first_name, last_name):
    if (len(first_name) == 0) or (len(last_name) == 0):  # checks to see if field is blank, if so, automatic 'No'
        prospect.status = 'No'
        print(prospect.fname, prospect.lname, prospect.dob, prospect.status)
        return False

    # iterates over each character in first name and only allows non alphabetical characters '-', ' ', '.', or "'"
    for char in first_name:
        if (char.isalpha() == False) and (char != '-') and (char != ' ') and (char != '.') and (char != "'"):
            prospect.status = 'No'
            print(prospect.fname, prospect.lname, prospect.dob, prospect.status)
            return False

    # iterates over each character in last name and only allows non alphabetical characters '-', ' ', '.', or "'"
    for char in last_name:
        if (char.isalpha() == False) and (char != '-') and (char != ' ') and (char != '.') and (char != "'"):
            prospect.status = 'No'
            print(prospect.fname, prospect.lname, prospect.dob, prospect.status)
            return False

    return True  # returns boolean True if names are valid, to be passed to get_info_from_county function

# function opens CSV file and copies in rows
def get_info_from_csv(header_val):
    with open('/Users/Sam/Desktop/registration_list.csv', 'r') as csv_file:
        for row in csv_file:
            # function disregards header in CSV file, after first row is passed, value set to false, rows are then read
            if header_val != True:
                temp_list = []  # clears temp list
                deliminated = row.split(',')  # creates list, deliminates string with a comma
                for i in range(7):  # function will read more columns than have information, limited to first 7 columns
                    if i == 3:  # 4th column contains date, is reformatted and then reinserted
                        deliminated[3] = format_month(deliminated[3])
                    temp_list.append(deliminated[i])
                    # soft copies by default and since temp_list is cleared, deepcopy is needed
                table_list.append(deepcopy(temp_list))
            header_val = False
    csv_file.close()

# function appends status to nested list in table_list and appends result to DataFrame
def append_to_csv(row, status):
    row.append(status)
    df.loc[len(df)] = row


df = DataFrame(columns=data_frame_columns)  # creates DataFrame with names defined earlier in program
get_info_from_csv(header)  # reads CSV file, appends to table_list

for row in table_list:
    prospect = Citizen(row[0], row[1], row[3])  # creates Class object using first name, last name, Date of Birth
    ascii_bool = valid_ascii_text(prospect.fname, prospect.lname)  # checks to make sure names use ASCII characters
    if ascii_bool == True:
        prospect.get_info_from_county()  # calls object function to check status of individuals on website
    append_to_csv(row, prospect.status)  # appends to pandas DataFrame

# prints DataFrame, sets index to false since EXCEL makes feature redundant
df.to_csv('Verified_County_Results.csv', index=False)
