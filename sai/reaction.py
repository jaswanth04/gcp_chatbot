
import logging
from fastapi.logger import logger
import uuid
from google.cloud import bigtable
import datetime
from config import Settings

gunicorn_logger = logging.getLogger('gunicorn.error')

logger.handlers = gunicorn_logger.handlers
logger.setLevel(gunicorn_logger.level)

settings = Settings(_env_file='.env.development', _env_file_encoding='utf-8')

def add_reaction(session_id, transaction_id, reaction):

	project_name = settings.PROJECT_NAME
	instance_name = settings.BIGTABLE_INSTANCE_NAME
	table_name = settings.BIGTABLE_TABLE_NAME


	client = bigtable.Client(project=project_name, admin=True)
	instance = client.instance(instance_name)
	big_table = instance.table(table_name)

	logger.info(f"Saving the response for {session_id} ")
	row = big_table.row(session_id)
	col_family_name = 'transaction'
	timestamp = ""

	read_rows = big_table.read_row(session_id)
	transaction_found = False

	if read_rows is not None:
		transactions = read_rows.cells[col_family_name]['transaction_id'.encode()]
		for t in transactions:
			# print(t)
			if (t.value.decode() == transaction_id):
				timestamp = t.timestamp
				transaction_found = True
	else:
		logger.error(f"session_id {session_id} is not found")
		raise Exception(f"Session id {session_id} not found")


	if not transaction_found:
		logger.error(f'transaction_id {transaction_id} is not found')
		raise Exception(f'Transaction id {transaction_id} is not found')
	
	logger.info(f'Setting reaction as {reaction} for session {session_id} and transaction {transaction_id} ')
	row.set_cell(col_family_name, 'reaction', str(reaction).encode('utf-8'), timestamp)

	row.commit()
	logger.info(f"Successfully Saved the reaction response for {session_id} ")


def main():
	session_id = "95af08ee-ddad-4d22-8635-40815d7b6f26"
	transaction_id = "38d8e415-625f-4ed1-bf6d-a4e0afca3588"

	add_reaction(session_id, transaction_id, 1)

if __name__ == '__main__':
	main()
