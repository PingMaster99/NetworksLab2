# encoding: utf-8
"""
    messenger_account.py
    Author: Pablo Ruiz 18259 (PingMaster99)
    Version 1.0
    Updated August 12, 2021

    Client that uses XMPP protocol to communicate.
    Base reference for slixmpp implementations: https://lab.louiz.org/poezio/slixmpp/-/tree/master/examples
"""

import ast
import asyncio
import constants
from aioconsole import ainput
from slixmpp import ClientXMPP, exceptions
from topology_reader import TopologyReader
from routing_algorithms import NetworkAlgorithms

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class MessengerAccount(ClientXMPP):
    """
    Client that uses the XMPP protocol to communicate
    """
    def __init__(self, jid, password):
        """
        Initializes the client
        :param jid: jid of the user
        :param password: password to log in
        """
        super().__init__(jid, password)
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0199')  # XMPP Ping
        self.register_plugin('xep_0059')  # Result set management
        self.register_plugin('xep_0060')  # Publish-subscribe
        self.register_plugin('xep_0077')  # In-Band Registration
        self.register_plugin('xep_0045')  # Multi-User Chat
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("session_start", self.messaging_app)
        self.add_event_handler("failed_auth", self.failed_auth)
        self.add_event_handler("message", self.get_notification)
        self.add_event_handler("changed_status", self.wait_for_presences)
        self.add_event_handler("roster_subscription_request", self.get_notification)
        self.add_event_handler("groupchat_invite", self.group_chat_invite)
        self.received = set()
        self.presences_received = asyncio.Event()

        topology_reader = TopologyReader()
        self.nodes = topology_reader.nodes
        self.matrix = topology_reader.adjacency_matrix
        self.node_number = self.nodes.index(self.jid)
        self.adjacent_nodes = self.matrix[self.node_number]

        self.routing_algorithm = NetworkAlgorithms()

    def get_notification(self, event):
        """
        Prints a notification according to the event received
        :param event: event received
        """
        print(event['type'])
        if event['type'] in ('chat', 'normal'):
            message_data = event['body'].split('/$/')
            # 1 sender jid \ 3 Destinatary jid \ 5 visited nodes(convert to list) \ 7 distance
            # \ 9 path (convert to list) \ 11 nodes \ 13 message

            if message_data[0] == self.jid:
                print(f"Message received from {message_data[1]}: {message_data[13]}")
            else:
                print(f"Message in transit received")
                message_data[5] = ast.literal_eval(message_data[5])     # visited_nodes
                message_data[9] = ast.literal_eval(message_data[9])     # path
                message_destinatary_index = message_data[9].pop(0)
                message_data[5].append(message_destinatary_index)
                message_destinatary = self.nodes[message_destinatary_index]

                message_data[5] = str(message_data[5])
                message_data[9] = str(message_data[9])

                message = '/$/'.join(message_data)

                self.send_message(message_destinatary, message, mtype='chat')

                print(f"Forwarding message to node {message_destinatary}")

        elif event['type'] == 'groupchat':
            print(f"New message from group {event['from']}: {event['body']}")
        elif event['type'] == 'headline':
            print(f"Headline received: {event['body']}")
        elif event['type'] == 'error':
            print(f"An error has occurred: {event['body']}")
        elif event['type'] == 'subscribe':
            print(f"New subscription received from: {event['from'].username}")

    @staticmethod
    def group_chat_invite(event):
        """
        Prints a notification for group chat invites
        :param event: group chat invite
        """
        print(f"New groupchat invite. Room: {event['from']}")

    async def session_start(self, event):
        """
        Starts the session
        :param event: start
        """
        try:
            await self.get_roster()
        except exceptions.IqTimeout:
            print("Request timed out")

        self.send_presence()

    @staticmethod
    def failed_auth(event):
        """
        Prints a message when login fails
        :param event: failed credentials
        """
        print("Could not log in with the specified credentials")

    async def messaging_app(self, event):
        """
        Handles the main functionalities of the client
        :param event: event to start the app (session start)
        """
        running = True
        while running:
            try:
                option = int(await ainput(constants.MAIN_MENU))
            except ValueError:
                print("Invalid option")
                continue

            if option == 1:     # Log out
                print("logged out")
                await self.disconnect()
                break

            elif option == 2:   # Delete account
                await self.delete_account()
                break

            elif option == 3:     # Show contacts
                await self.show_users_and_contacts()
                continue

            elif option == 4:     # Add contact
                await self.add_user_to_contacts()
                continue

            elif option == 5:     # Send a message
                try:
                    username = await ainput("Username to send message to\n>> ")
                    message_destinatary = f"{username}@alumchat.xyz"
                    message = await ainput("Message content\n>> ")
                    algorithm = await ainput("Algorithm: \n1. Flooding\n2. Distance vector routing\n3. Link state "
                                             "routing")
                    path = None
                    if algorithm == '1':    # Flooding
                        pass
                    elif algorithm == '2':  # Distance vector routing
                        pass
                    elif algorithm == '3':  # Link state routing
                        path, distance = self.routing_algorithm.link_state_routing(self.matrix, self.nodes.index(message_destinatary), self.node_number)
                        message = f"Sender/$/{self.jid}/$/Destinatary/$/{message_destinatary}" \
                                  f"/$/Traversed nodes/$/{[path[0], path[1]]}/$/Distance/$/{distance}/$/Path/$/" \
                                  f"{path[2::]}/$/Nodes/$/{self.nodes}/$/Message/$/{message} "

                    else:
                        print("Algorithm wasn't correct")
                        continue
                    if path is not None and len(path) > 1:
                        await self.message(self.nodes[path[1]], message, mtype='chat')
                    else:
                        await self.message(message_destinatary, message, mtype='chat')
                    print(f"Sent: {message} > {username}")
                except AttributeError:
                    print("El usuario no es correcto")
                continue
            elif option == 6:     # Group message
                room_name = str(await ainput("Introduce the room name:\n>> "))
                room_name = f"{room_name}@conference.alumchat.xyz"
                self.plugin['xep_0045'].join_muc(room_name, self.username)

                message = str(await ainput("Message to send:\n>> "))
                self.send_message(room_name, message, mtype='groupchat')
                continue

            elif option == 7:     # Change status message
                await self.change_presence_message()
                print("Status message changed")

            elif option == 8:   # Send file
                await self.send_file()

            elif option == 9:   # Particular contact details
                user = str(await ainput("Contact to show details\n>> "))
                await self.show_users_and_contacts(user)
                continue

            elif option == 10:   # Exit
                self.end_session()

            elif option == 12344321:
                print("Я Коло-бот")
            elif option == 11: 
                
                
                """
                read txt file with network topology
                """
                fil = open("topology.txt","r")

                #---------------------------------------
                """
                send message
                """
                
                print("hello world")
                try:
                    username = await ainput("Username to send message to\n>> ")
                    message_destinatary = f"{username}@alumchat.xyz"
                    message = await ainput("Message content\n>> ")
                    await self.message(message_destinatary, message, mtype='chat')
                    print(f"Sent: {message} > {username}")
                except AttributeError:
                    print("El usuario no es correcto")
                continue
        
            else:
                print("Invalid option")

    async def message(self, message_destinatary, message, mtype='chat'):
        """
        Sends a message to another user
        :param message_destinatary: other user
        :param message: content
        :param mtype: message type, defaults to chat
        :return: True
        """
        self.send_message(message_destinatary, message, mtype=mtype)
        return True

    def end_session(self):
        """
        Logs out of the client
        """
        self.disconnect()

    async def show_users_and_contacts(self, username=None):
        """
        Shows the users and contacts with their availability and statuses
        """
        print('Roster for %s' % self.boundjid.bare)
        groups = self.client_roster.groups()
        for group in groups:
            print('\n%s' % group)
            print('-' * 72)
            for jid in groups[group]:
                sub = self.client_roster[jid]['subscription']
                name = self.client_roster[jid]['name']
                if username is not None:
                    if username != self.client_roster[jid]['name']:
                        if f"{username}@alumchat.xyz" != jid:
                            continue
                if self.client_roster[jid]['name']:
                    print(' %s (%s) [%s]' % (name, jid, sub))
                else:
                    print(' %s [%s]' % (jid, sub))

                connections = self.client_roster.presence(jid)
                for res, pres in connections.items():
                    show = 'available'
                    if pres['show']:
                        show = pres['show']
                    print('   - %s (%s)' % (res, show))
                    if pres['status']:
                        print('       %s' % pres['status'])

    def wait_for_presences(self, pres):
        """
        Tracks how many roster entries have received presence updates.
        :param pres: prescence event
        """
        self.received.add(pres['from'].bare)
        if len(self.received) >= len(self.client_roster.keys()):
            self.presences_received.set()
        else:
            self.presences_received.clear()

    async def change_presence_message(self):
        """
        Changes the availability, nickname, and status of a user.
        """
        status = str(await ainput("Insert your new availability (hint: away/dnd/chat/xa)\n>> "))
        status_message = str(await ainput("Type your new status message\n>> "))
        nickname = str(await ainput("Type in your new nickname\n>> "))

        self.send_presence(pshow=status, pstatus=status_message, pnick=nickname)

    async def add_user_to_contacts(self):
        """
        Adds another user to the current user's contacts.
        :return:
        """
        username = str(await ainput("Username to add as a contact\n>> "))
        self.send_presence_subscription(pto=f"{username}@alumchat.xyz")

    def start_conversation(self):
        """
        Send a message to another user
        """
        username = input("Username to send message to\n>> ")
        message = input("Message content\n>> ")
        self.send_message(f"{username}@alumchat.xyz", message, mtype='chat')

    async def delete_account(self):
        """
        Deletes the current account.
        """
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['remove'] = True

        try:
            await resp.send()
            print(f"{self.boundjid}'s account has been removed")
        except exceptions.IqError as e:
            if e.iq['error']['code'] == '409':
                print(f"Could not delete account: {resp['register']['username']}")
            else:
                print("Account could not be deleted")
            await self.disconnect()
        except exceptions.IqTimeout as e:
            print("Timeout error, please try again")
            await self.disconnect()

    async def send_file(self):
        """
        Sends a file to another user
        """
        filename = str(await(ainput("Introduce the name of the file to send with extension\n>> ")))
        recipient = str(await(ainput("Recipient's username\n>> ")))
        recipient += "@alumchat.xyz"
        try:
            url = await self.plugin['xep_0363'].upload_file(
                filename, domain='alumchat.xyz', timeout=10)
        except exceptions.IqTimeout:
            raise TimeoutError('Could not send message in time')

        html = (
            f'<body xmlns="http://www.w3.org/1999/xhtml">'
            f'<a href="{url}">{url}</a></body>'
        )
        message = self.make_message(mto=recipient, mbody=url, mhtml=html)
        print("Message sent")
        message['oob']['url'] = url
        message.send()


my_list = "[1, 'mycar', 3, 4, 5, 6]"
my_list = ast.literal_eval(my_list)
my_list = [str(number) for number in my_list]
my_list = my_list[0::]
my_list.append(str([2,3]))
my_list = '/$/'.join(my_list)

print(my_list, "This is the list")

