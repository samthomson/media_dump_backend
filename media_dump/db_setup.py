# create sql db with indexed tables
import sqlite3 as sqlite
import pymongo
from pymongo import MongoClient

if __name__ == '__main__':

	db = sqlite.connect('media_dump_db')

	cursor = db.cursor()


	'''
	files
	'''
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS files(
		id INTEGER NOT NULL,
		path VARCHAR(64),
		PRIMARY KEY (id)
		)
		''')
	cursor.execute('''
		CREATE UNIQUE INDEX IF NOT EXISTS path_index ON files (path)
	''')
	cursor.execute('''
		CREATE INDEX IF NOT EXISTS id_index ON files (id)
	''')

	'''
	log
	'''
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS log(
		id INTEGER NOT NULL,
		system VARCHAR(16),
		action VARCHAR(32),
		value INTEGER UNSIGNED,
		datetime DATETIME,
		PRIMARY KEY (id)
		)
		''')
	cursor.execute('''
		CREATE INDEX IF NOT EXISTS system_index ON log (system)
	''')
	cursor.execute('''
		CREATE INDEX IF NOT EXISTS action_index ON log (action)
	''')
	cursor.execute('''
		CREATE INDEX IF NOT EXISTS date_index ON log (datetime)
	''')


	'''
	queue
	'''
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS queue(
		id INTEGER NOT NULL,
		queue VARCHAR(32),
		file_id INTEGER,
		datetime_from DATETIME,
		active INTEGER DEFAULT 0,
		PRIMARY KEY (id)
		)
		''')
	cursor.execute('''
		CREATE INDEX IF NOT EXISTS id_index ON queue (id)
	''')
	cursor.execute('''
		CREATE INDEX IF NOT EXISTS queue_index ON queue (queue)
	''')
	cursor.execute('''
		CREATE INDEX IF NOT EXISTS file_id_index ON queue (file_id)
	''')
	cursor.execute('''
		CREATE INDEX IF NOT EXISTS datetime_from_index ON queue (datetime_from)
	''')
	cursor.execute('''
		CREATE INDEX IF NOT EXISTS active_index ON queue (active)
	''')


	'''
	tags
	'''
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS tags(
		id INTEGER NOT NULL,
		file_id INTEGER,
		type VARCHAR(32),
		value VARCHAR(64),
		PRIMARY KEY (id)
		)
		''')
	cursor.execute('''
		CREATE INDEX IF NOT EXISTS id_index ON tags (id)
	''')
	cursor.execute('''
		CREATE INDEX IF NOT EXISTS file_id_index ON tags (file_id)
	''')
	cursor.execute('''
		CREATE INDEX IF NOT EXISTS type_index ON tags (type)
	''')
	cursor.execute('''
		CREATE INDEX IF NOT EXISTS value_index ON tags (value)
	''')

	db.close()