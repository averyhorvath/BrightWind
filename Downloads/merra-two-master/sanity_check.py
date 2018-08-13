"""
Sanity check to see connection to databases are working with simple queries
"""

from __future__ import absolute_import
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

auth_provider = PlainTextAuthProvider(username='username', password='pwd')
session = Cluster(['52.16.60.214'], port = 9042, auth_provider=auth_provider).connect()
                                                                    
query = "SELECT * FROM merra_two.reanalysis WHERE locationid=361460 AND readingdtm>='2017-06-28' AND readingdtm<'2017-06-29' LIMIT 10"
rows = session.execute(query)

for row in rows: print(row.readingdtm)
