#!/usr/bin/python

from flask import Flask
from flask import request, Response
from flask import jsonify

import argparse

import sourcetvRelayServer

configOptions = {
    'dev': {      
    }
}

deploymentOptions = {}

app = Flask(__name__)

#API endpoints
@app.route('/relay/add', methods=['POST'])
def addRelayServer():
    if request.headers['Content-Type'] != 'application/json':
        return Response(status=415)
    data = request.get_json()

    requiredParams = ['sourceTvIP', 'sourceTvPort']

    for param in requiredParams:
        if param not in data:
            return Response(response='{error: "Missing required parameter - %s"}' % (param), status=400)

    sourceTvIP = data['sourceTvIP']
    sourceTvPort = data['sourceTvPort']
    sourceTvPassword = None

    relayServer = sourcetvRelayServer.startRelayServer(sourceTvIP, sourceTvPort, sourceTvPassword)
    if relayServer != None:
        return Response(status=201)

    return Response(status=500)

@app.route('/relays', methods=['GET'])
def listRelays():
    relayServers = sourcetvRelayServer.getActiveRelayServers()

    relays = {}
    for relay in relayServers:
        relays[relay['id']] = relay

    return jsonify(relays)


@app.route('/relays/<relayId>/stop', methods=['POST'])
def stopRelayServer(relayId):
    relay = sourcetvRelayServer.getRelayById(relayId)
    if relay is None:
        return Resonse(status=404)

    if relay["active"] == 0:
        return Response(status=200)

    sourcetvRelayServer.stopRelayServer(relay)

    return Response(status=200)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple web server for listing maps in a given directory')
    parser.add_argument('--config', metavar='config', type=str, nargs=1, help='Which config to use', default=['dev'])
    
    args = parser.parse_args()
    deploymentOptions = configOptions[args.config[0]]

    app.debug = True
    app.run(host='0.0.0.0', port=5001)