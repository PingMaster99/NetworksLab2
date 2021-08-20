"""
    registration.py
    Author: Pablo Ruiz 18259 (PingMaster99)
    Version 1.0
    Updated August 12, 2021

    Client that uses XMPP protocol to communicate.
    Base reference for slixmpp implementation: https://groups.google.com/g/sleekxmpp-discussion/c/iAFJGcpH-Ps
"""


from slixmpp import ClientXMPP, exceptions


class Registration(ClientXMPP):
    """
    Registers a new user
    """
    def __init__(self, jid, password):
        """
        Initializes the registration class
        :param jid: jid of the new account
        :param password: password of the new account
        """
        ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("register", self.register)

    async def session_start(self, event):
        """
        Starts the registration bot
        :param event: event to handle
        """
        self.send_presence()
        await self.get_roster()
        await self.disconnect()

    async def register(self, event):
        """
        Registers a new user
        :param event: event to handle
        """
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password

        try:
            await resp.send()
            print(f"{self.boundjid}'s account has been created!")
        except exceptions.IqError as e:
            if e.iq['error']['code'] == '409':
                print(f"There is already an account with the username: {resp['register']['username']}")
            else:
                print("Account could not be registered")
            await self.disconnect()
        except exceptions.IqTimeout as e:
            print("Timeout error, please try again")
            await self.disconnect()
