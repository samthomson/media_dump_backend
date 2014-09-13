import os, sys
import sqlite3 as sqlite


def get_db_files(db_cursor):
	db_cursor.execute('''SELECT * FROM files''')

	fileList=db_cursor.fetchall()

	return fileList


if __name__ == '__main__':


	db = sqlite.connect('media_dump_db')
	db_cursor = db.cursor()


	sl_db_files = get_db_files(db_cursor)

	print "\n"
	print "%i files in db" % len(sl_db_files)

	for s_db_file in sl_db_files:
		print "file id: %s, path: %s" % (s_db_file[0], s_db_file[1])

	print "\n"