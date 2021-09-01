# Lab3
CLI client that supports the XMPP protocol. Includes routing algorithms to send messages.
Connects to the server: ```alumchat.xyz```

#### NOTE: You can also test the program locally by changing ```SERVER = <Your IPv4>``` in the constants.py file.  
This project has been proven to work locally with a Spark client and Openfire Server running on alumchat.xyz with a custom DNS to your local IPv4 address. 
To configure a local server, type in:

```<Your IPv4 alumchat.xyz>``` inside the hosts file located in: C:/Windows/System32/drivers/etc. 

## Requirements
- asyncio
- aiconsole
- slixmpp
- logging
- Python 3.7+

## Installation
1. Clone this repository: ```git clone https://github.com/PingMaster99/NetworksLab3```
2. Run the command: ```python main.py``` in a command window on the folder location
3. Follow on screen instructions
4. To edit the logging configuration, set LOGGING to True in constants.py

## Functionalities
### Account administration
- Register a new account
- Log in
- Log off
- Delete an account

### Communication
- Show all users
- Add a user to contacts
- Show contact details of users
- Send a message to a user/contact
- Participate in group chats
- Define presence message
- Notifications
- Files
