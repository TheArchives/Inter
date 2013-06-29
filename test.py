# coding=utf-8
import psycopg2

conn = psycopg2.connect("dbname=inter user=inter password=inter")

cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS player_players      (id serial PRIMARY KEY, username varchar UNIQUE);")
cur.execute("CREATE TABLE IF NOT EXISTS player_data         (pid serial, last_server varchar, last_online time, "
            "points integer);")
cur.execute("CREATE TABLE IF NOT EXISTS player_login_logout (pid serial, action bool, time time);")
cur.execute("CREATE TABLE IF NOT EXISTS player_points       (pid serial, change integer);")

cur.execute("INSERT INTO player_players (username) VALUES (%s);", ("arbot",))

cur.execute("SELECT id FROM player_players WHERE username = (%s)", ("arbot",))
player_id = cur.fetchone()[0]

print "ID: %s" % player_id

conn.commit()