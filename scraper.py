
import requests
from bs4 import BeautifulSoup
import json
import urllib.request
import pyshorteners
import smtplib
from email.message import EmailMessage

#Global Variables
dictionary = {}
temp_dictionary = {}
found = False
keywords = ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5", "keyword6", "keyword7"]

#saved urls
URL = "https://www.websitelink.com"
file_URL = "https://www.linktospecificfileonthewebsite.com"


#checks if the website is up
def websiteUp(host=URL):
        try:
                urllib.request.urlopen(host)
                return True
        except:
                return False


#reads a json file with entries from last time
def readJSON():
        global dictionary
        print("Reading data from JSON file...", end='')
        with open("data.json", "r") as openfile:
                dictionary = json.load(openfile)
                print("SUCCESSFUL!")

def writeJSON():
        global dictionary
        print("Writing new data to JSON file...", end='')
        with open("data.json", "w") as writefile:
                json.dump(dictionary, writefile)
                print("SUCCESSFUL!")


#main scraping function
def scrape():
        print(f"SCRAPER: Scraping {URL}")
        found = False
        #checks the website for html
        webpage = requests.get(URL)
        soup = BeautifulSoup(webpage.content, "html.parser")
        #saves only the divs with a specific class name or specific id
        results = soup.find_all("div", {"class": "classname"})

        #checks for all results
        for x in results:
                #stores the title
                key = x.h3.get_text()
                

                #check if key contains any keyword
                if any(substring in str(key).lower() for substring in keywords):
                        #checks if this result was already checked
                        if dictionary.get(key) == None:
                                #gets file link and adds the second part, which was just scraped
                                temp = x.find("a")
                                #concats the href to website link
                                long_url = file_URL + temp.get('href')
                                #shortenes the link to tiny.url
                                type_tiny = pyshorteners.Shortener()
                                tiny_url = type_tiny.tinyurl.short(long_url)
                                #stores them in a dictionary
                                dictionary[key] = tiny_url
                                #stores it in the temporary for alerting the user (only new entries)
                                temp_dictionary[key] = tiny_url
                                found = True
                
        #if there is a new one found, it alerts over email
        if(found == True):
                print("SCRAPER: "+ str(len(temp_dictionary)) + " new entries found. Sending email...", end='')
                alertViaEMail()
                #deletes all temp stored values that have been alerted
                temp_dictionary.clear()
                #sets found to false because user is alerted
                found = False
                writeJSON()
        else:
                #no new changes
                print("SCRAPER: Scraping done: no new entries found.")

             
        
def alertViaEMail():
        #counter for list items in email
        listcount = 1

        #counter for new items
        count = len(temp_dictionary)
        #email variables - sender, receiverm subject, body...
        sender_email = "youremail@domain.com"
        receiver_email = "receiveremail@domain.com"
        valueforauth = "one time code or password goes here"
        email_subject = f"New entries ({count})"
        message_body = "Here is a list of all new entries found:\n\n"
        for key, value in temp_dictionary.items():
                message_body += f"{listcount}. {key}; Link to the file: {value} \n"
                listcount = listcount+1
        smtp_link = "smtp.gmail.com"
        smtp_port = 587

        #building a message
        mail = EmailMessage()
        mail.set_content(message_body)
        mail['Subject'] = email_subject
        mail['From'] = sender_email
        mail['To'] = receiver_email

        #starting tls connection, loging in and sending a message
        with smtplib.SMTP(smtp_link, smtp_port) as smtp:
                smtp.starttls()
                smtp.login(sender_email, valueforauth)
                smtp.send_message(mail)

        listcount = 1
        print("DONE!")
        print(f"MAILER: Email sent to {receiver_email}")


#main program
print("\n---------------------------------Welcome to SCRAPER V1.0!---------------------------------")
print(f"Checking connection to: {URL} ... ", end='')
if(websiteUp()):
        print("CONNECTED!")
        print("------------------------------------------------------------------------------------------")
        readJSON()
        print("SCRAPER: Starting...")
        scrape()
        print("SCRAPER: Exiting...")
        print("------------------------------------------------------------------------------------------")
        
else:
        print("OFFLINE!")
        print("\n---------------------------------------------------------------------------------------------------------------------\n")
        print(f"ERROR OCCURRED: No connection to website: {URL}\n                Please check your connection!          \n ")
        print("----------------------------------------------------------------------------------------------------------------------\n")
