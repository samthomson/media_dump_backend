# create sql db with indexed tables

import sqlite3 as sqlite



if __name__ == '__main__':

	db = sqlite.connect('media_dump_db')

	cursor = db.cursor()


	'''
	file table
	'''
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS files(
		id INTEGER NOT NULL,
		path VARCHAR(64),
		PRIMARY KEY (id)
		)
		''')
	cursor.execute('''
		CREATE UNIQUE INDEX path_index ON files (path)
	''')
	cursor.execute('''
		CREATE INDEX id_index ON files (id)
	''')

	'''
	log table
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
		CREATE INDEX system_index ON log (system)
	''')
	cursor.execute('''
		CREATE INDEX action_index ON log (action)
	''')
	cursor.execute('''
		CREATE INDEX date_index ON log (datetime)
	''')

	db.close()
