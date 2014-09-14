


import os, sys



'''
create index
'''
from whoosh.fields import Schema, TEXT

schema = Schema(title=TEXT, content=TEXT)

schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
ix = create_in("../index", schema)





'''
write to index
'''