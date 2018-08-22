import requests
import json
from secrets import url
from secrets import key

# this grabs the list of test contacts created and returns the list id and the list name
def getTestList():
    querystring = {"api_action":"list_list","api_output":"json","ids":"all", "api_key": key}
    headers = {
        'Cache-Control': "no-cache",
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.text)
    if data["result_code"] != 1:
        print(data["result_message"])
        return
    return (data["0"]["id"], data["0"]["name"])

# this returns a list of all contact emails
def getContacts():
    querystring = {"api_action":"contact_list","api_output":"json","ids":"all","api_key":key}
    headers = {
        'Cache-Control': "no-cache",
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.text)
    if data["result_code"] != 1:
        print(data["result_message"])
        return
    contacts = []
    for k, v in data.items():
        try:
            k = int(k)
        except ValueError:
            pass
        if type(k) == int:
            contacts.append(v["email"])
    return contacts

# this creates a basic email message using static data and returns the id for the message
def createMessage():
    listID, listName = getTestList()
    querystring = {"api_action":"message_add","api_output":"json","api_key": key}
    payload = {
        "format": "text",
        "subject": "Hello!",
        "fromemail": "snoopy@dogs.com",
        "fromname": "snoopy",
        "reply2": "snoopy@dogs.com",
        "priority": 5,
        "charset": "utf-8",
        "encoding": "quoted-printable",
        "htmlconstructor": "htmlfetch",
        "html": "<strong>ActiveCampaign Rocks!</strong>",
        "htmlfetch": "http://somedomain.com/somepage.html",
        "htmlfetchwhen": "send",
        "textconstructor": "textfetch",
        "text": "ActiveCampaign Rocks!",
        "textfetch": "http://somedomain.com/somepage.txt",
        "textfetchwhen": "send",
        "p[" + listID + "]": listID,
    }
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "no-cache",
        }
    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
    data = json.loads(response.text)
    if data["result_code"] != 1:
        print(data["result_message"])
        return
    print(f'A new message was created with the subject "{payload["subject"]}" for {listName}')
    return data["id"]

# this creates a campaign with the name of the provided argument
def createAndScheduleCampaign(name):
    message = createMessage()
    listID, listName = getTestList()
    querystring = {"api_action":"campaign_create","api_output":"json","api_key": key}
    payload = {
        "type": "single",
        "name":  name,
        "sdate": "2018-11-05 08:40:00",
        "status": "public",
        "tracklinks": "all",
        "p[" + listID + "]": listID,
        "m[" + message + "]": 100,
    }
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "no-cache",
        }
    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
    data = json.loads(response.text)
    if data["result_code"] != 1:
        print(data["result_message"])
        return
    print(f'A new campaign called "{payload["name"]}" has been created for {listName}')
    scheduleCampaign(data["id"], "2018-08-25 09:00:00")
    sendCampaign(data["id"])

# I am using this function solely to grab the campaign name for logging purposes
def getCampaignName(campaignID):
    querystring = {"api_action":"campaign_list","api_output":"json","ids": campaignID,"api_key": key}
    headers = {
        'Cache-Control': "no-cache",
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.text)
    if data["result_code"] != 1:
        print(data["result_message"])
        return
    return data["0"]["name"]

# this schedules a campaign for the specified campaign id and date arguments
def scheduleCampaign(campaignID, date):
    campaignName = getCampaignName(campaignID)
    querystring = {"api_action":"campaign_status","api_output":"json","id":campaignID,"status":"1","sdate":date,"api_key": key}
    headers = {
        'Cache-Control': "no-cache",
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.text)
    if data["result_code"] != 1:
        print(data["result_message"])
        return
    print(f'The campaign "{campaignName}" has been successfully scheduled for {date}')

# this sends a campaign for the specified campaign id to every contact
def sendCampaign(campaignID):
    campaignName = getCampaignName(campaignID)
    contacts = getContacts()
    for contact in contacts:
        querystring = {"api_action":"campaign_send","api_output":"json","email":contact,"campaignid":campaignID,"type":"text","action":"send","api_key": key}
        headers = {
            'Cache-Control': "no-cache",
            }
        response = requests.request("GET", url, headers=headers, params=querystring)
        data = json.loads(response.text)
        if data["result_code"] != 1:
            print(data["result_message"])
            return
        print(f'The campaign "{campaignName}" has been sent to {contact}')

createAndScheduleCampaign("Dogs")
