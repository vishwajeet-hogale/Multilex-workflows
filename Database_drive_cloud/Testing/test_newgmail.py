import os
import sys
database = os.path.abspath(os.path.join(os.path.realpath(__file__), "..", ".."))

sys.path.append(database)
from Modules.gmail import get_mails,get_mail_messages
sys.path.remove(database)
import pprint
received_from = 'karthicknathan.l@exchange-data.in'
sent_to = 'techmultilex.gmail.com'
after_date = '1/5/2023'
before_date = '10/5/2023'
dict_file = get_mails(sent_to,received_from,after_date,before_date)
pprint.pprint(dict_file)