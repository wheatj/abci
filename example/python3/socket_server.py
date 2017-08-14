from conn import ConnReader, ConnWriter
import logging
import messages
import queue
import socket
import threading
import time

class SocketServer():

    def __init__(self, addr, app):

        self.host, port = addr.split(':')
        self.port = int(port)

        self.app = app
        self.app_lock = threading.RLock()

        self.conns = {}
        self.conns_lock = threading.RLock()

        self.next_id = 0

        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.setblocking(False)

    def on_start(self):
        self.listener.bind((self.host, self.port))
        self.listener.listen(1)
        self.accept_connections()

    def on_stop(self):
        self.listener.close()
        with self.conns_lock:
            for conn_id, conn in self.conns.items():
                conn.close()
                del self.conns[conn_id]

    def add_conn(self, conn):
        with self.conns_lock:
            self.conns[self.next_id] = conn
            self.next_id += 1
            return self.next_id - 1

    def rm_conn(self, conn_id):
        with self.conns_lock:
            self.conns[conn_id].close()
            del self.conns[conn_id]

    def accept_connections(self):
        while True:
            print('Waiting for a new connection...')
            try:
                conn, addr = self.listener.accept()
                print('Accepted a new connection')
                conn_id = self.add_conn(conn)
                responses = queue.Queue()
                thread = threading.Thread(target=self.handle_responses, args=(conn, conn_id, responses))
                thread.start()
                thread = threading.Thread(target=self.handle_requests, args=(conn, conn_id, responses))
                thread.start()
            except BlockingIOError:
                time.sleep(1) ## how long to sleep?
            except Exception as e:
                logging.exception('Failed to accept connection: ' + str(e))

    def handle_requests(self, conn, conn_id, responses):
        count = 0
        r = ConnReader(conn)
        while True:
            req = messages.request()
            try:
                messages.read(r, req)
            except (BlockingIOError, IOError):
                time.sleep(1) ## how long to sleep?
                continue
            except Exception as e:
                logging.exception('Error reading message: ' + str(e))
                self.rm_conn(conn_id)
            with self.app_lock:
                count += 1
                self.handle_request(req, responses)

    def handle_responses(self, conn, conn_id, responses):
        count = 0
        w = ConnWriter(conn)
        while True:
            resp = responses.get(block=True)
            try:
                messages.write(w, resp)
            except Exception as e:
                logging.exception('Error writing message: ' + str(e))
                self.rm_conn(conn_id)
            if resp.WhichOneof('value') == 'flush':
                w.flush()
            count += 1

    def handle_request(self, req, responses):
        val = req.WhichOneof('value')
        if val == 'echo':
            resp = messages.response_echo(req.echo.message)
        elif val == 'flush':
            resp = messages.response_flush()
        elif val == 'info':
            resp = self.app.info()
        elif val == 'set_option':
            so = req.set_option
            log = self.app.set_option(so.key, so.value)
            resp = messages.response_set_option(log)
        elif val == 'deliver_tx':
            res = self.app.deliver_tx(req.deliver_tx.tx)
            resp = messages.response_deliver_tx(res.code, res.data, res.log)
        elif val == 'check_tx':
            res = self.app.check_tx(req.check_tx.tx)
            resp = messages.response_check_tx(res.code, res.data, res.log)
        elif val == 'commit':
            res = self.app.commit()
            resp = messages.response_commit(res.code, res.data, res.log)
        elif val == 'query':
            resp = self.app.query(req.query)
        elif val == 'init_chain':
            self.app.init_chain(req.init_chain.validators)
            resp = messages.response_init_chain()
        elif val == 'begin_block':
            bb = req.begin_block
            self.app.begin_block(bb.hash, bb.header)
            resp = messages.response_begin_block()
        elif val == 'end_block':
            res = self.app.end_block(req.end_block.height)
            resp = messages.response_end_block(res)
        else:
            resp = messages.response_exception('Unknown request')

        responses.put(resp)
