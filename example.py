# If you DO have the WhatsApp Desktop app installed

from alright import WhatsApp

msg = "E ai mano"
wpp = WhatsApp()
wpp.find_by_username('Ryan')
wpp.send_message(msg)
