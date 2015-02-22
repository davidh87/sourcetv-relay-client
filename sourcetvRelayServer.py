#!/usr/bin/python

import time
import sqlite3
import subprocess

DATABASE_FILE = 'relays.db'

def setupDatabase():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS relays (
        id integer primary key,
        sourceTvIP text, 
        sourceTvPort integer, 
        sourceTvPassword text, 
        localPort integer,
        startTime integer,
        active integer,
        processId integer
        ) """)
    conn.commit()

"""
Get a relay server by its ID

Returns the relay server, or None if no server found with the given ID
"""
def getRelayById(relayId):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT id, sourceTvIP, sourceTvPort, sourceTvPassword, localPort, startTime, active, processId
        FROM relays 
        WHERE id = ?
        """, (relayId, ))
    row = c.fetchone()
    if row is None:
        return None
    return {
            "id": row[0],
            "sourceTvIP": row[1],
            "sourceTvPort": row[2],
            "sourceTvPassword": row[3],
            "localPort": row[4],
            "startTime": row[5],
            "active": row[6],
            "processId": row[7]
        }

def getActiveRelayServers():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT id, sourceTvIP, sourceTvPort, sourceTvPassword, localPort, startTime, active, processId
        FROM relays 
        WHERE active = 1
        """)

    relays = []
    for row in c:
        relay = {
            "id": row[0],
            "sourceTvIP": row[1],
            "sourceTvPort": row[2],
            "sourceTvPassword": row[3],
            "localPort": row[4],
            "startTime": row[5],
            "active": row[6],
            "processId": row[7]
        }

        relays.append(relay)

    return relays


"""
Starts a STV relay server.

Returns the server details, or False in case of error
"""
def startRelayServer(sourceTvIP, sourceTvPort, sourceTvPassword):
    #TODO: actually start a STV relay
    if sourceTvPort != 12345:
        return False

    localPort = getLocalPort()
    startTime = int(time.time())

    pid = subprocess.Popen(["nohup", "/Users/davidh/Documents/tf2center/relays/srcds_run", "-game", "tf", "-console", 
        "+tv_enable", "\"1\"", "+tv_port", "%s" % (localPort), "+tv_relay", 
        "%s:%s" % (sourceTvIP, sourceTvPort)]).pid

    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO relays (sourceTvIP, sourceTvPort, sourceTvPassword, localPort, startTime, active, processId)
        VALUES (?, ?, ?, ?, ?, 1, ?)
        """, 
        (
            sourceTvIP,
            sourceTvPort,
            sourceTvPassword,
            localPort,
            startTime,
            pid
        ))

    relayId = c.lastrowid
    conn.commit()

    print relayId

    return getRelayById(relayId)

"""
Get a free local port to use.

Returns the port, or None if no available ports found
"""
def getLocalPort():
    return 27025

"""
Stops a relay server

Returns True if stopped, or False if an error occurred
"""
def stopRelayServer(relayServer):
    #TODO actually stop the STV relay
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("""
        UPDATE relays
        SET active=0, processId=NULL
        WHERE id = ?
        """, (relayServer['id'],))
    conn.commit()

    return True

def init():
    setupDatabase()