import argparse
import json
from twisted.internet.protocol import Protocol, ServerFactory


tuple_space = []
server_id = 0
server_port = 2048


class TSService(object):

    @staticmethod
    def find(tp):
        tup_id = -1
        for i, tup in enumerate(tuple_space):
            tup_id = i
            if len(tup) == len(tp):
                for t1, t2 in zip(tp, tup):
                    if t1 == '_':
                        continue
                    elif t1 != t2:
                        tup_id = -1
                        break
                if tup_id == i:
                    break
            else:
                tup_id = -1
        return tup_id

    @staticmethod
    def out(tp):
        print "put %s" % tp
        tuple_space.append(tp)
        return tp

    @staticmethod
    def inp(tp):
        print "pop %s" % tp
        tup_id = TSService.find(tp)
        if tup_id != -1:
            return tuple_space.pop(tup_id)
        return None

    @staticmethod
    def rdp(tp):
        print "get %s" % tp
        tup_id = TSService.find(tp)
        if tup_id != -1:
            return tuple_space[tup_id]
        return None


class TSProtocol(Protocol):

    def __init__(self):
        self.respond = {}

    def connectionMade(self):
        print 'connected'
        # self.transport.write(self.factory.poem)
        # self.transport.loseConnection()

    def dataReceived(self, request):
        req = json.loads(request)
        self.respond = {'res': 'FAIL', 'tup': None}
        res_tp = self.factory.apply_operation(req['op'], req['tup'])

        if res_tp is not None:
            self.respond['res'] = 'OK'
            self.respond['tup'] = res_tp

        self.transport.write(json.dumps(self.respond))
        self.transport.loseConnection()

    def connectionLost(self, reason):
        pass


class TSFactory(ServerFactory):

    protocol = TSProtocol

    def __init__(self, service):
        self.service = service

    def apply_operation(self, operation, tp):
        op = getattr(self, '_%s' % (operation,), None)

        if op is None:
            return None

        try:
            return op(tp)
        except:
            return None

    def _out(self, tp):
        return self.service.out(tp)

    def _in(self, tp):
        return self.service.inp(tp)

    def _rd(self, tp):
        return self.service.rdp(tp)


def parser():
    p = argparse.ArgumentParser()
    p.add_argument('id', type=int)
    p.add_argument('port', type=int)
    return p


def main():
    global server_id, server_port
    # tuple_space = open(ts_file).read()
    pars = parser()
    args = pars.parse_args()
    server_id, server_port = args.id, args.port
    service = TSService()
    factory = TSFactory(service)

    from twisted.internet import reactor
    reactor.listenTCP(server_port, factory, interface='localhost')
    print 'before run'
    reactor.run()


if __name__ == '__main__':
    main()
