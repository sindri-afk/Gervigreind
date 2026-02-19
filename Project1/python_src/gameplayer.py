#!/usr/bin/env python3
"""
Runs a game player server listening on a TCP port (default 4001) for messages from an
environment.
Usage: gameplayer.py [port]
Example: gameplayer.py 4001
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import re
import sys
from agent import *

#########

"""GamePlayer server

A GamePlayer listens on a given port for messages from an
environment and calls appropriate functions (start, next_action,
cleanup) in the associated agent.
"""


class GamePlayer(HTTPServer):

    def __init__(self, agent, port=4001):
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
        msg = self.rfile.read(content_len).decode().lower()
        print("----------------")
        print("received: " + msg)
        try:
            cmd = self.get_command(msg)
            if cmd == "start":
                self.command_start(msg)
                response_string = "ready"
            elif cmd == "play":
                response_string = self.command_play(msg)
            elif cmd == "stop":
                self.command_stop(msg)
                response_string = "done"
            else:
                response_string = "done"
            self.respond(200, response_string)

        except Exception as ex:
            self.respond(400, "error processing command:" + str(ex))
            raise ex

    @staticmethod
    def get_command(msg):
        match = re.search(r'\(\s*(\S+)\s', msg)
        if match:
            cmd = match.group(1)
        else:
            raise Exception("unrecognized message format")
        return cmd

    def command_start(self, msg):
        # msg="(START <MATCH ID> <ROLE> <GAME DESCRIPTION> <STARTCLOCK> <PLAYCLOCK>)"
        match = re.fullmatch(r"""
        \s* \( \s* start
        \s+ (?P<matchid> \S+ )
        \s+ (?P<role> \S+ ) 
        \s* \( (?P<rules> .*) \)
        \s* (?P<start_clock> \d+ )
        \s+ (?P<play_clock> \d+ )
        \s* \) \s* """, msg, flags=re.DOTALL | re.VERBOSE)
        if match:
            role = match.group('role')
            rules = match.group('rules')
            # start_clock = int(match.group('start_clock'))
            play_clock = int(match.group('play_clock'))

            match = re.search(r'\(\s*width\s+(\d+)\s*\)', rules)
            if match:
                width = int(match.group(1))
            else:
                raise RuntimeError("width not found in start message")

            match = re.search(r'\(\s*height\s+(\d+)\s*\)', rules)
            if match:
                height = int(match.group(1))
            else:
                raise RuntimeError("height not found in start message")
                
            white_positions = [tuple(map(int, pos)) for pos in re.findall(r"\(\s*init\s*\(\s*cell\s+(\S+)\s+(\S+)\s+white\s*\)\s*\)", rules)]
            black_positions = [tuple(map(int, pos)) for pos in re.findall(r"\(\s*init\s*\(\s*cell\s+(\S+)\s+(\S+)\s+black\s*\)\s*\)", rules)]
            
        else:
            raise RuntimeError("malformed start message: " + msg)
        self.server.agent.start(role, width, height, play_clock, white_positions, black_positions)

    @staticmethod
    def parse_move(msg):
        # msg="(PLAY <MATCHID> <LASTMOVES>)"
        last_move = None
        match = re.search(r'\(\s*play\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*\)', msg)
        if match:
            last_move = tuple([int(match.group(i)) for i in range(1, 5)])
        return last_move

    def command_play(self, msg):
        return self.server.agent.next_action(self.parse_move(msg))

    def command_stop(self, msg):
        self.server.agent.cleanup(self.parse_move(msg))


#########

def main():
    # TODO: use your own agent here
    agent = RandomAgent()

    # read command line argument(s)
    port = 4001
    if len(sys.argv) == 2:
        try:
            port = int(sys.argv[1])
        except ValueError:
            sys.exit(globals()['__doc__'].strip())
    elif len(sys.argv) != 1:
        sys.exit(globals()['__doc__'].strip())

    # start the game player server
    httpd = GamePlayer(agent, port)
    print(type(agent).__name__ + " is listening on port " + str(port) + " ...")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
