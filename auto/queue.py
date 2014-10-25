import time
import sqlite3 as sqlite



def queue_file(s_file_id, s_queue, s_datetime_from = time.strftime('%Y-%m-%d %H:%M:%S')):
	db_cursor.execute('''INSERT INTO queue (queue, file_id, datetime_from) VALUES (?,?,?)''', (s_queue, s_file_id, s_datetime_from,))