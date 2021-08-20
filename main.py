"""
    main.py
    Author: Pablo Ruiz 18259 (PingMaster99)
    Version 1.0
    Updated August 12, 2021

    Main file to run the XMPP client
"""

from messenger_account import MessengerAccount
import logging
import constants
from registration import Registration

if constants.LOGGING:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')


def main():
    """
    Main loop for the program functionality
    """
    running = True
    while running:
        option = input(constants.APP_MENU)

        try:
            option = int(option)
        except ValueError:
            print("Incorrect option")
            continue

        if option == 1:     # Register
            jid = input("Username: ")
            password = input("Password: ")
            if constants.SERVER not in jid:
                jid += constants.SERVER

            xmpp = Registration(jid, password)
            xmpp.register_plugin('xep_0030')  # Service Discovery
            xmpp.register_plugin('xep_0004')  # Data forms
            xmpp.register_plugin('xep_0066')  # Out-of-band Data
            xmpp.register_plugin('xep_0077')  # In-band Registration
            xmpp['xep_0077'].force_registration = True
            xmpp.connect()
            xmpp.process(forever=False)

        elif option == 2:   # Login
            jid = input("Username: ")
            password = input("Password: ")
            if constants.SERVER not in jid:
                jid += constants.SERVER

            xmpp = MessengerAccount(jid, password)
            xmpp['feature_mechanisms'].unencrypted_plain = True
            xmpp.register_plugin('xep_0199')
            xmpp.connect()
            print("Connected!")
            xmpp.process(forever=False)
            xmpp.disconnect()

        elif option == 3:   # Exit
            print("Thank you for using the XMPP secret chat")
            exit()


if __name__ == '__main__':
    main()
