# create sql db with indexed tables

import sqlite3 as sqlite



if __name__ == '__main__':

	db = sqlite.connect('media_dump_db')

	cursor = db.cursor()

	cursor.execute('''
		CREATE TABLE IF NOT EXISTS files(
		id INTEGER UNSIGNED AUTO INCREMENT,
		path VARCHAR(64),
		PRIMARY KEY ('id')
		)
		''')



	cursor.execute('''
		CREATE INDEX path_index ON files (path)
	''')
	cursor.execute('''
		CREATE INDEX id_index ON files (id)
	''')

