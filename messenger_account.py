# encoding: utf-8
"""
    messenger_account.py
    Authors: Mario Sarmientos, Randy Venegas, Pablo Ruiz 18259 (PingMaster99)
    Version 2.0
    Updated August 31, 2021

    Client that uses XMPP protocol to communicate using network routing algorithms.
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
        self.adjacent_node_weights = self.matrix[self.node_number]
        self.adjacent_names = []
        self.dvr_matrix = []
        self.dvr_min_distances = []

        for i in range(len(self.nodes)):
            self.dvr_matrix.append([0] * len(self.nodes))

        self.dvr_matrix[self.node_number] = self.adjacent_node_weights

        node_index = 0
        for node in self.adjacent_node_weights:
            if node < float('inf') and node != 0:
                self.adjacent_names.append(self.nodes[node_index])
                node_index += 1

        print()


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
            # \ 9 path (convert to list) \ 11 nodes \ 13 message \ 14 algorithm

            if message_data[3] == self.jid:
                print(f"Message received from {message_data[1]}: {message_data[13]}")

            elif message_data[14] == 1:     # DVR
                routing = NetworkAlgorithms()
                self.dvr_matrix[self.nodes.index(message_data[1])] = ast.literal_eval(message_data[13])
                current_min_distances = routing.bellman_ford(self.dvr_matrix, self.node_number)
                if current_min_distances != self.dvr_min_distances:
                    self.dvr_min_distances = current_min_distances
                    print(f"The new minimum distances are:\n{self.dvr_min_distances}")

            elif message_data[14] == 2:                                 # Flooding
                message_data[5] = ast.literal_eval(message_data[5])     # visited nodes
                message_data[9] = ast.literal_eval(message_data[9])     # path
                not_sent_to = [x for x in self.adjacent_names not in message_data[5]]

                if len(not_sent_to) > 0 and message_data[3] in message_data[9]:
                    message_data[9] = [x for x in message_data[9] not in self.adjacent_names]
                    message_data[9] = str(message_data[9])

                    for node in not_sent_to:
                        message_data[5].append(node)
                    message_data[5] = str(message_data[5])
                    message = '/$/'.join(message_data)

                    for node in not_sent_to:
                        self.send_message(node, message, mtype='chat')
                        print(f"Flooding message to {node}")

                message_data[9] = ast.literal_eval(message_data[9])

            elif message_data[14] == 3:                                 # link state routing
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

            elif option == 2:     # Send a message
                try:
                    username = await ainput("Username to send message to\n>> ")
                    message_destinatary = f"{username}{constants.SERVER}"
                    message = await ainput("Message content\n>> ")
                    algorithm = await ainput("Algorithm: \n1. DVR (use option 4 of general menu)"
                                             "\n2. Flooding\n3. Link state routing\n>>"
                                             "routing")
                    path = None
                    if algorithm == '1':    # Distance vector routing
                        # Routes and weights are updated in option number 4.
                        pass
                    elif algorithm == '2':  # Flooding
                        print(self.matrix, self.node_number, message_destinatary)
                        routing = NetworkAlgorithms()
                        path, distance = routing.link_state_routing(self.matrix, self.nodes.index(message_destinatary), self.node_number)
                        message = f"Sender/$/{self.jid}/$/Destinatary/$/{message_destinatary}" \
                                  f"/$/Traversed nodes/$/{self.adjacent_names}/$/Distance/$/N.A/$/Path/$/" \
                                  f"{[x for x in self.nodes if x not in self.adjacent_names]}/$/Nodes/$/{self.nodes}/$/Message/$/{message}/$/2"

                        for i in range(len(self.adjacent_names)):
                            await self.message(self.adjacent_names[i], message, mtype='chat')

                    elif algorithm == '3':  # Link state routing
                        print(self.matrix, self.node_number, message_destinatary)
                        routing = NetworkAlgorithms()
                        path, distance = routing.link_state_routing(self.matrix, self.nodes.index(message_destinatary), self.node_number)
                        message = f"Sender/$/{self.jid}/$/Destinatary/$/{message_destinatary}" \
                                  f"/$/Traversed nodes/$/{[path[0], path[1]]}/$/Distance/$/{distance}/$/Path/$/" \
                                  f"{path[2::]}/$/Nodes/$/{self.nodes}/$/Message/$/{message}/$/3 "
                        print("message payload:\n", message)
                        print(f"Shortest path is: {path} with a total weight of {distance}")
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

            elif option == 3:   # Exit
                self.end_session()

            elif option == 4:   # Send dvr
                for node in self.adjacent_names:
                    message = f"Sender/$/{self.jid}/$/Destinatary/$/{node}" \
                              f"/$/Traversed nodes/$/hi/$/Distance/$/EmptyPayload/$/Path/$/" \
                              f"hi/$/Nodes/$/{self.nodes}/$/Message/$/{self.adjacent_node_weights}/$/3 "

            elif option == 12344321:
                print("Я Коло-бот")

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

    async def add_user_to_contacts(self):
        """
        Adds another user to the current user's contacts.
        :return:
        """
        username = str(await ainput("Username to add as a contact\n>> "))
        self.send_presence_subscription(pto=f"{username}@alumchat.xyz")
