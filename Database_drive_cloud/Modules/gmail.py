import os
import sys

database = os.path.abspath(os.path.join(os.path.realpath(__file__), "..", ".."))

sys.path.append(database)

from Luigi_Workflow.db import Update_token_gmail

sys.path.remove(database)

update_token = Update_token_gmail()
update_token.run()