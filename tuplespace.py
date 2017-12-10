from subprocess import Popen, CREATE_NEW_CONSOLE, CalledProcessError, PIPE
import json
from twisted.internet import defer
from twisted.internet.protocol import Protocol, ClientFactory, ServerFactory


class TupleSpace():

    def __init__(self, port_list, port=10000):
        self.port = port
        self.servers = port_list
        length = len(port_list)
        if length < 1:
            raise "Invalid number of servers"

        for i in range(length):
            try:
                Popen('.\server.py ' + str(i) + ' ' + str(self.servers[i]), stdout=PIPE, stderr=PIPE,
                      shell=True, creationflags=CREATE_NEW_CONSOLE)
            except CalledProcessError:
                raise "Can`t create server"


    def run(self):

        class TSClientProtocol(Protocol):

            def __init__(self, port_list):
                self.ports = port_list


            def dataReceived(self, request):
                self.request = request
                req = json.loads(request)
                if req["op"] not in ["in", "out", "rd"]:
                    raise "Invalid operation"

                if type(req["tup"]) != tuple:
                    raise "Invalid tuple in request"

                from twisted.internet import reactor
                f = TSServerFactory(self)
                # на сервер с каким портом отсылать?
                reactor.connectTCP('localhost', 10000, f)
                self.transport.write(self.respond)


            def connectionLost(self, reason):
                pass


        class TSClientFactory(ServerFactory):

            protocol = TSClientProtocol

            def __init__(self):
                pass

            def clientConnectionFailed(self, connector, reason):
                pass


        class TSServerProtocol(Protocol):

            def __init__(self):
                pass

            def connectionMade(self):
                self.transport.write(self.factory.client.request)

            def dataReceived(self, respond):
                resp = json.loads(respond)
                if resp["res"] not in ["FAIL", "OK"]:
                    raise "Invalid result"
                if type(resp["tup"]) != tuple:
                    raise "Invalid tuple in respond"

                self.factory.client.respond = respond
                self.transport.loseConnection()

            def connectionLost(self, reason):
                pass


        class TSServerFactory(ClientFactory):

            protocol = TSServerProtocol

            def __init__(self, client):
                self.client = client

            def clientConnectionFailed(self, connector, reason):
                pass

        factory = TSClientFactory(self.servers)
        from twisted.internet import reactor
        reactor.listenTCP(self.port, factory, interface='localhost')
        print "TS before run"
        reactor.run()
