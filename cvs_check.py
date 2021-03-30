"""
Published on Mar 30, 2021
@authors: Dimitri Petrakis and Katerina Petrakis
"""
# ----------------------------------------------------------------------------------------------------------------------
"""
  _    _   _____  ______  _____   __      __       _____   _____            ____   _       ______   _____ 
 | |  | | / ____||  ____||  __ \  \ \    / //\    |  __ \ |_   _|    /\    |  _ \ | |     |  ____| / ____|
 | |  | || (___  | |__   | |__) |  \ \  / //  \   | |__) |  | |     /  \   | |_) || |     | |__   | (___  
 | |  | | \___ \ |  __|  |  _  /    \ \/ // /\ \  |  _  /   | |    / /\ \  |  _ < | |     |  __|   \___ \ 
 | |__| | ____) || |____ | | \ \     \  // ____ \ | | \ \  _| |_  / ____ \ | |_) || |____ | |____  ____) |
  \____/ |_____/ |______||_|  \_\     \//_/    \_\|_|  \_\|_____|/_/    \_\|____/ |______||______||_____/ 

"""
# ----------------------------------------------------------------------------------------------------------------------
# User Variables to change

# Input the two-letter state abbreviation into the list; for example, if your state is New York, input 'NY'
STATES = []

# Input city with a CVS location.  Check the cvs website for a list of acceptable cities with a vaccine cvs location
CITIES = []

# Type of email you are sending with (different email types require different protocols to send the email)
# Allowed types = 'gmail', 'outlook', 'yahoo', 'att', 'comcast', and 'verizon'
EMAIL_TYPE = 'gmail'

# Email address to send from ex: 'quackdonut123456789@gmail.com'
SENDER = 'quackdonut123456789@gmail.com'

# Password of the email address you're sending from ex: 'password1234'
PASSWORD = 'password1234'

# Email address to send to/receive from ex: 'quackdonut123456789@gmail.com'
RECEIVER = 'quackdonut123456789@gmail.com'

# How often to refresh the page, in seconds
UPDATE_TIME = 60

# USER INPUT EXAMPLES (everything case IN-sensitive)
# -----------------------
# Search statewide - Searches every city in the state(s) given
# STATES = ['ny', 'MA']
# CITIES = []
# -----------------------
# Search  multiples cities in one state - Searches city/cities in a single state given
# STATES = ['cA']
# CITIES = ['Fresno', 'santa clarita', 'MADERA']
# -----------------------
# Search  multiples cities in multiple states - Cities must match to states in a one to one fashion (can ignore spaces)
# STATES = [   'CA',       'Ny',          'Ca',      'ma']
# CITIES = ['FRESNO', 'New York', 'Santa clarita', 'salem']

"""
Please don't change anything else below unless you know what you're doing.....thanks
"""
# ----------------------------------------------------------------------------------------------------------------------
"""
  _____  __  __  _____    ____   _____  _______   _____          _____  _  __           _____  ______   _____ 
 |_   _||  \/  ||  __ \  / __ \ |  __ \|__   __| |  __ \  /\    / ____|| |/ /    /\    / ____||  ____| / ____|
   | |  | \  / || |__) || |  | || |__) |  | |    | |__) |/  \  | |     | ' /    /  \  | |  __ | |__   | (___  
   | |  | |\/| ||  ___/ | |  | ||  _  /   | |    |  ___// /\ \ | |     |  <    / /\ \ | | |_ ||  __|   \___ \ 
  _| |_ | |  | || |     | |__| || | \ \   | |    | |   / ____ \| |____ | . \  / ____ \| |__| || |____  ____) |
 |_____||_|  |_||_|      \____/ |_|  \_\  |_|    |_|  /_/    \_\ _____||_|\_\/_/    \_\ _____||______||_____/ 
 
"""
# ----------------------------------------------------------------------------------------------------------------------
# Timing
import time

# Emailing
import smtplib

# Email message crafting
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Read dictionary from link
import json

# Used to make copies of the state when zipping cities ans states together
from itertools import cycle

# Page fetching from url
try:
    # Works on python 3+ as of March 30, 2021
    from urllib.request import urlopen
except ImportError:
    # Works on python 2.7
    from urllib2 import urlopen
# ----------------------------------------------------------------------------------------------------------------------
"""
   _____  _       ____   ____            _       __      __       _____   _____  ____            _       ______   _____ 
  / ____|| |     / __ \ |  _ \    /\    | |      \ \    / //\    |  __ \ |_   _||  _ \    /\    | |     |  ____| / ____|
 | |  __ | |    | |  | || |_) |  /  \   | |       \ \  / //  \   | |__) |  | |  | |_) |  /  \   | |     | |__   | (___  
 | | |_ || |    | |  | ||  _ <  / /\ \  | |        \ \/ // /\ \  |  _  /   | |  |  _ <  / /\ \  | |     |  __|   \___ \ 
 | |__| || |____| |__| || |_) |/ ____ \ | |____     \  // ____ \ | | \ \  _| |_ | |_) |/ ____ \ | |____ | |____  ____) |
  \_____||______|\____/ |____//_/    \_\|______|     \//_/    \_\|_|  \_\|_____||____//_/    \_\|______||______||_____/ 

"""
# ----------------------------------------------------------------------------------------------------------------------
# Link to all available appointments
LINK="https://www.cvs.com/immunizations/covid-19-vaccine/immunizations/covid-19-vaccine.vaccine-status.json?vaccineinfo"

# Converts user strings to make functions case insensitive
STATES = [state.upper() for state in STATES]
CITIES = [city.upper() for city in CITIES]
EMAIL_TYPE = EMAIL_TYPE.lower()

# If searching for multiple cities in one state
if CITIES and len(STATES) == 1:
    # Zips the cites and states list to a list of tuples [(city1, state1), (city2, state2), ...]
    # Used for verification and indexing into the dictionary of appointments
    MY_CITY_STATES = list(zip(CITIES, cycle(STATES)))

# If the cities list is not empty, the user is searching for specific cities in specific states or
# multiple cities in one state
if CITIES:
    SEARCHING_FOR_SPECIFIC_CITIES = True

# Otherwise searching statewide for availability in all cities, for the given states
else:
    SEARCHING_FOR_SPECIFIC_CITIES = False

# Dictionary to get the server ID and port number for each email type
EMAIL_DICT = {'gmail'  : ('smtp.gmail.com',        587),
              'outlook': ('smtp-mail.outlook.com', 587),
              'yahoo'  : ('smtp.mail.yahoo.com',   587),
              'att'    : ('smpt.mail.att.net',     465),
              'comcast': ('smtp.comcast.net',      587),
              'verizon': ('smtp.verizon.net',      465)}
# ----------------------------------------------------------------------------------------------------------------------
"""
  ______   _    _   _   _    _____   _______   _____    ____    _   _    _____ 
 |  ____| | |  | | | \ | |  / ____| |__   __| |_   _|  / __ \  | \ | |  / ____|
 | |__    | |  | | |  \| | | |         | |      | |   | |  | | |  \| | | (___  
 |  __|   | |  | | | . ` | | |         | |      | |   | |  | | | . ` |  \___ \ 
 | |      | |__| | | |\  | | |____     | |     _| |_  | |__| | | |\  |  ____) |
 |_|       \____/  |_| \_|  \_____|    |_|    |_____|  \____/  |_| \_| |_____/ 

"""
# ----------------------------------------------------------------------------------------------------------------------
def get_dictionary_from_link():
    """
    Given the cvs website link, returns a dictionary with all of the appointment information
    """

    # Get appointments as a single text string from the given link
    text = urlopen(LINK).read().decode("UTF-8")
    # Convert the string into a dictionary to access the bookings
    return json.loads(text)
# ----------------------------------------------------------------------------------------------------------------------
def get_states():
    """
    Gets list of states from the cvs link
    """

    dictionary = get_dictionary_from_link()
    states = dictionary["responsePayloadData"]["data"].keys()
    return sorted(states)
# ----------------------------------------------------------------------------------------------------------------------
def get_cities(list_of_states):
    """
    Gets cities from the array of given states
    """
    all_cities = []
    dictionary = get_dictionary_from_link()

    for state in list_of_states:
        list_O_dicts = dictionary["responsePayloadData"]["data"][state]
        for city_state_status in list_O_dicts:
            all_cities.append(city_state_status["city"])
    return sorted(all_cities)
# ----------------------------------------------------------------------------------------------------------------------
def user_input_verification():
    """
    This function checks to confirm that the user input is of the correct form.
    Raises and error exception upon bad input.
    """

    all_states = get_states()
    all_states_set = set(all_states)
    all_cities = get_cities(all_states)

    # If no state is entered
    if not STATES:
        raise ("\nYou must enter at least one state.\n")

    # Checks if all the state inputs are correct
    if not set(STATES).issubset(all_states_set):
        raise ("\nOne or more state inputs are invalid.\n")

    # Checks if all the city inputs are correct
    if not all(city in all_cities for city in CITIES):
        raise ("\nOne or more cities entered are not correct. Please go to "
               "https://www.cvs.com/immunizations/covid-19-vaccine and click "
               "your state to see a list of viable options.\n")

    # In the case in which cities array is not empty, i.e. the search is NOT statewide, further checks are carried out.
    if (CITIES):
        num_cities = len(CITIES)
        num_states = len(STATES)

        # The cities list must either have exactly one state, indicating that all cities being checked are in the same state,
        # OR each city must have a 1:1 match it its state if checking across multiple states.
        if not (num_cities == num_states or num_states == 1):
            raise ("\nCity entry error. If all appointments you are searching are in the same state, "
                   "only enter that one state.  If you are checking in multiple stats, make sure you "
                   "enter the same number of states as you have cities \n")

        if (num_cities == num_states):
            # Confirm that each city is in the corresponding state listed
            for i in range(num_cities):
                if CITIES[i] not in get_cities(STATES):
                    raise ("\nCity entry error. At least 1 City/State pairing is incorrect \n")

        if (num_states == 1):
            # Confirm that each city is in the state listed
            for i in range(num_cities):
                if CITIES[i] not in get_cities(STATES):
                    raise ("\nCity entry error. At least 1 City listed is not in the specified state. \n")

    if not isinstance(UPDATE_TIME, (float, int)):
        raise ("\nUPDATE_TIME variable type must be a number.\n")

    if not (isinstance(SENDER, str) and isinstance(PASSWORD, str) and isinstance(RECEIVER, str)):
        raise ("\nThe sender, password, and receiver fields must all be strings.\n")

    if not ('@' in RECEIVER and '.' in RECEIVER):
        raise ("\nThe receiver must be a proper email containing an '@' character and a '.' character .\n")

    # The sender email must have the same provider as the email_provider
    at_index = SENDER.find('@')
    dot_index = SENDER.find('.')
    sender_suffix = SENDER[at_index + 1: dot_index]
    if not sender_suffix == EMAIL_TYPE:
        raise ("\nThe sender email must come from the same provider as the email_provider variable.\n")
# ----------------------------------------------------------------------------------------------------------------------
def get_available_appointments():
    """
    Gets the set of user specified cities (either specific cities, or all cities given a list of states)
    that have available appointments

    Container type from website = Dict[Str: Dict[Str: Dict[Str: List[Dict[Str: Str]]]]]
    Dict 1 keys = ["responsePayloadData", "responseMetaData"]
    Dict 2 keys = ["currentTime", "data", "isBookingCompleted"]
    Dict 3 keys = ["NY", "CA", "SC", "MA", "FL",  ... all state abbreviations]
    Dict 4 = {"city": "NEW YORK", "state": state abbreviation ex: "NY", "status": either "Available" or "Fully Booked"}
    """

    # Get the dictionary of available appointments
    dictionary = get_dictionary_from_link()

    # Initialize appointments as an empty set
    available_appointments = set()

    # Loop over each user given state
    for state in STATES:
        # Get the list of dicts with city, state, and status
        list_O_dicts = dictionary["responsePayloadData"]["data"][state]

        # Index into the list and add to available appointments (nothing will happen if it's a duplicate)
        for dict4 in list_O_dicts:
            if SEARCHING_FOR_SPECIFIC_CITIES:
                # Add to available appointments if appointment is available and it's the user specified (city, state)
                if (dict4["city"], state) in MY_CITY_STATES and dict4["status"] == "Available":
                    available_appointments.add(dict4["city"])
            # If searching statewide
            else:
                # Add to available appointments only if appointment is available
                if dict4["status"] == "Available":
                    available_appointments.add(dict4["city"])

    return available_appointments
# ----------------------------------------------------------------------------------------------------------------------
def send_email(message):
    """
    Login via STMP and send email with the given message and with the given email type
    """

    # Get SMTP server ID and port for the given email type
    # SeverID sets which email type to sent from
    # Port used for web protocols, 587 for default web (supports TLS) or 465 for SSL
    serverID, port = EMAIL_DICT[EMAIL_TYPE]

    # Establish SMTP Connection
    s = smtplib.SMTP(host=serverID, port=port)

    # Start SMTP session
    s.starttls()

    # Login using given email ID and password
    s.login(SENDER, PASSWORD)

    # Create email message in proper format
    m = MIMEMultipart()

    # Set email parameters
    m['From'] = SENDER
    m['To'] = RECEIVER
    m['Subject'] = "New Appointment(s) Available! - Looking In: " + collection_2_sentence(set(STATES))

    # Add message to email body (specifying an html string)
    m.attach(MIMEText(message, 'html'))

    # Send the email
    s.sendmail(SENDER, RECEIVER, m.as_string())

    # Terminate the SMTP session
    s.quit()
# ----------------------------------------------------------------------------------------------------------------------
def build_email_message(new_appointments, all_appointments):
    """
    Given the set of new and all appointments, builds an HTML string with the text that will be sent in the
    """

    out = ''  # Initialize empty string
    out += ("<h3>New Appointments:</h3>")  # Adds New Appointments header
    out += collection_2_listed_string(new_appointments) + '\n\n'  # Adds list of new appointments
    out += '\n<br>Go to https://www.cvs.com/immunizations/covid-19-vaccine to book an appointment.' # Gives the link
    out += ("<h3>All Available Appointments:</h3>")  # Adds All Appointments header
    out += collection_2_listed_string(all_appointments) + '\n\n'  # Adds list of all appointments
    return out  # Returns final message
# ----------------------------------------------------------------------------------------------------------------------
def collection_2_listed_string(set_of_cities):
    """
    Given a container of strings,
    returns an HTML string where each city has its own line
    This function will be used to help format and build the email text body in the build_email_message function

    Note: returned cities should be in alphabetical order
    """

    # Early exit if the set is empty
    if not set_of_cities:
        return 'None Available' + '<br>'

    string = ""  # Initialize empty string

    sort = sorted(set_of_cities)  # Sorts the set (converts to a list)

    for city in sort:  # Loop over each city in the set
        string += city + '<br>'  # Append the city to the string

    return string  # Returns the string
# ----------------------------------------------------------------------------------------------------------------------
def collection_2_sentence(list_str):
    """
    Given a container (list or set) of strings with the names of cities, states or any string (elements),
    returns a string where each element is listed in a sentence

    Note: returned objects should be in alphabetical order

    Ex1: {"LIVERPOOL"} -> LIVERPOOL
    Ex2: ["LIVERPOOL", "KINGSTON"] -> KINGSTON and LIVERPOOL
    Ex3: {"BROOKLYN", "LIVERPOOL", "KINGSTON"} -> BROOKLYN, LIVERPOOL, and KINGSTON
    """

    # Sorts the set (converts to a list)
    elements = sorted(list_str)

    # Gets the number of cities in the set
    num_elements = len(list_str)

    # If the set is empty, return None
    if not list_str:
        return 'None Available'
    # If the set has one cities, return the string of the one city
    elif num_elements == 1:
        return elements[0]
    # If the set has two cities, return the two cities as "city1 and city2"
    elif num_elements == 2:
        return elements[0] + ' and ' + elements[1]
    # If the set has three or more cities, return cities like saying a list in a sentence "cityA, ... cityY, and cityZ"
    else:
        string = ""  # Initialize empty string

        for i in range(num_elements - 1):  # Loop over each city in the set except the last one
            string += elements[i] + ', '  # Add the city to the string with a comma and space

        return string + 'and ' + elements[-1]  # Add the final city with an "and" and return string
# ----------------------------------------------------------------------------------------------------------------------
def calculate_appointments(new_set, old_set):
    """
    Calculate different appointment types.  Used for making useful distinctions in the email message
    Ex1: Addition of HONEOYE
    new_set = {'LIVERPOOL', 'BROOKLYN', 'HONEOYE', 'KINGSTON'}
    old_set = {'LIVERPOOL', 'BROOKLYN', 'KINGSTON'}
    returns ->->
    new_appointments = {'HONEOYE'}
    old_appointments = {'LIVERPOOL', 'BROOKLYN', 'KINGSTON'}

    Ex2: No Changes
    new_set = {'LIVERPOOL', 'BROOKLYN', 'HONEOYE', 'KINGSTON'}
    old_set = {'LIVERPOOL', 'BROOKLYN', 'HONEOYE', 'KINGSTON'}
    returns ->->
    new_appointments = set() (empty set)
    old_appointments = {'LIVERPOOL', 'BROOKLYN', 'HONEOYE', 'KINGSTON'}

    """

    new_appointments = new_set.difference(old_set)  # New minus Old
    old_appointments = new_set.intersection(old_set)  # New ∩ Old
    return new_appointments, old_appointments  # Return resulting sets
# ----------------------------------------------------------------------------------------------------------------------
"""
  __  __              _____   _   _     ______   _    _   _   _    _____   _______   _____    ____    _   _ 
 |  \/  |     /\     |_   _| | \ | |   |  ____| | |  | | | \ | |  / ____| |__   __| |_   _|  / __ \  | \ | |
 | \  / |    /  \      | |   |  \| |   | |__    | |  | | |  \| | | |         | |      | |   | |  | | |  \| |
 | |\/| |   / /\ \     | |   | . ` |   |  __|   | |  | | | . ` | | |         | |      | |   | |  | | | . ` |
 | |  | |  / ____ \   _| |_  | |\  |   | |      | |__| | | |\  | | |____     | |     _| |_  | |__| | | |\  |
 |_|  |_| /_/    \_\ |_____| |_| \_|   |_|       \____/  |_| \_|  \_____|    |_|    |_____|  \____/  |_| \_|

"""
# ----------------------------------------------------------------------------------------------------------------------
def check_cvs(previous_appointments):
    """
    This function repeatedly reads the CVS website, and if any appointments are available in your state, it emails you.

    Terminology definitions:
    previous_appointments = set of available cites from previous check / empty set (if first time running program)
    fresh_appointments = set of available cities after checking the link
    new_appointments = set of cities available that are available now but not in the previous check
    old_appointments = set of cities available that are available now but were also available in the previous check

    Note: old_appointments is currently not used in any meaningful way but is there for further customization
    """

    # Useful information to print to the terminal for some visuals
    print("Looking for appointments in " + collection_2_sentence(set(STATES))
          + " at " + str(time.strftime('%H:%M:%S', time.localtime())))

    # Get all available appointments from the CVS website
    fresh_appointments = get_available_appointments()

    # Calculate different appointment types.  Used for making useful distinctions in the email message
    new_appointments, old_appointments = calculate_appointments(fresh_appointments, previous_appointments)

    # Used for testing but also can print all cities on each check of the function if desired
    print("New Appointments:              " + collection_2_sentence(new_appointments))
    # print("Old Appointments:              " + collection_2_sentence(old_appointments))
    print("All Available Appointments:    " + collection_2_sentence(fresh_appointments) + '\n')

    # Sets the email as an HTML string to sent to the user
    email_message = build_email_message(new_appointments, fresh_appointments)

    # If there is a new city with appointments available that wasn't available in the last check, sends an email
    if new_appointments:
        print("Found an appointment!!! \n")  # Pretty visual for the terminal

        # Send email to user with given message
        send_email(email_message)

    # Returns updated set of appointments to be inputted as previous_appointments in the next function run
    return fresh_appointments
# ----------------------------------------------------------------------------------------------------------------------
"""
  _____    _    _   _   _     ______   _    _   _   _    _____   _______   _____    ____    _   _ 
 |  __ \  | |  | | | \ | |   |  ____| | |  | | | \ | |  / ____| |__   __| |_   _|  / __ \  | \ | |
 | |__) | | |  | | |  \| |   | |__    | |  | | |  \| | | |         | |      | |   | |  | | |  \| |
 |  _  /  | |  | | | . ` |   |  __|   | |  | | | . ` | | |         | |      | |   | |  | | | . ` |
 | | \ \  | |__| | | |\  |   | |      | |__| | | |\  | | |____     | |     _| |_  | |__| | | |\  |
 |_|  \_\  \____/  |_| \_|   |_|       \____/  |_| \_|  \_____|    |_|    |_____|  \____/  |_| \_|

"""
# ----------------------------------------------------------------------------------------------------------------------
def main():
    # Verifies the user's inputs
    user_input_verification()

    # Make the initial set of available appointments an empty set
    previous_appointments = set()

    # Runs Forever
    while True:
        try:
            # Repeatedly checks CVS every minute or amount of time specified
            previous_appointments = check_cvs(previous_appointments)
            time.sleep(UPDATE_TIME)

        # Quits the program if you click Control/Command C
        except KeyboardInterrupt:
            break
# ----------------------------------------------------------------------------------------------------------------------
# Actually runs the function when called
if __name__ == '__main__':
    main()