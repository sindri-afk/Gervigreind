#!/usr/bin/env python
"""
Runs a game player server listening on a TCP port (default 4001) for messages from an
environment.
Usage: gameplayer.py [port]
Example: gameplayer.py 4001
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import re
import sys
import random
from agent import *
from search import *

#########

"""GamePlayer server

A GamePlayer listens on a given port for messages from an
environment and calls appropriate functions (start, next_action,
cleanup) in the associated agent.
"""
class GamePlayer(HTTPServer):

  def __init__(self, agent, port = 4001):
    self.agent = agent
    super().__init__(('', port), GGPRequestHandler)
    return

#########

"""HTTP Request handler for the GamePlayer"""
class GGPRequestHandler(BaseHTTPRequestHandler):

  def respond(self, code, message):
    self.send_response_only(code)
    self.send_header('Server', self.version_string())
    self.send_header('Date', self.date_time_string())
    self.send_header('Content-type', 'text/acl')
    self.end_headers()
    self.wfile.write(message.encode())
    print("sending: " + str(code) + " - " + message)

  def do_GET(self):
  	self.respond(400, "Only POST requests are supported!")
    
  def do_PUT(self):
  	self.respond(400, "Only POST requests are supported!")

  def do_POST(self):
    # Reads post request body
    content_len = int(self.headers['Content-Length'])
    msg = self.rfile.read(content_len).decode()
    print("----------------")
    print("received: " + msg)
    try:
      cmd = self.get_command(msg)
      if cmd == "START":
        self.command_start(msg)
        response_string = "READY"
      elif cmd == "PLAY":
        response_string = self.command_play(msg)
      elif cmd == "STOP":
        self.command_stop(msg)
        response_string = "DONE"
      self.respond(200, response_string)

    except Exception as ex:
      self.respond(400, "error processing command:" + str(ex))
      raise ex

  def get_command(self, msg):
    cmd = ""
    match = re.search(r'\(\s*([^\s]*)\s', msg)
    if match:
      cmd = match.group(1)
    else:
      raise Exception("unrecognized message format")
    cmd = cmd.upper()
    return cmd

  def get_percepts(self, msg):
    # only works for atomic percepts and actions so far
    if msg.endswith("NIL)"):
      return []
    else:
      percept_string = ""
      open_idx = msg.rindex("(")
      close_idx = msg.index(")", open_idx)
      percept_string = msg[open_idx+1:close_idx]
      return re.findall(r'[^\s]+', percept_string)

  def get_initial_state(self, msg):
      matches = re.findall(r'\(INIT\s*([^\s)]*|\((AT|ORIENTATION|HOME)[^)]*\))\s*\)', msg)
      result = [match[0] for match in matches]
      match = re.search(r'\(SIZE\s+([0-9]+)\s+([0-9]+)\s*\)', msg)
      if match:
        result.append(match.group(0))
      return result;

  def command_start(self, msg):
    percepts = self.get_initial_state(msg)
    self.server.agent.start(percepts)

  def command_play(self, msg):
    percepts = self.get_percepts(msg)
    return self.server.agent.next_action(percepts)

  def command_stop(self, msg):
    percepts = self.get_percepts(msg)
    self.server.agent.cleanup(percepts)

#########

def main():
  # TODO: use your own agent here
  search = AStarSearch(SimpleHeuristics())
  agent = VacuumCleanerAgent(search)

  # read command line argument(s)
  port = 4001
  if len(sys.argv) == 2:
    try:
      port = int(sys.argv[1])
    except ValueError as e:
      sys.exit(globals()['__doc__'].strip())
  elif len(sys.argv) != 1:
    sys.exit(globals()['__doc__'].strip())

  # start the game player server
  httpd = GamePlayer(agent, port)
  print(type(agent).__name__ + " is listening on port " + str(port) + " ...")
  httpd.serve_forever()

if __name__ == "__main__":
  main()
