import types_pb2 as types

def request():
    return types.Request()

def request_echo(msg):
    req = request()
    req.echo.message = msg
    return req

def request_flush():
    req = request()
    req.flush.CopyFrom(types.RequestFlush())
    return req

def request_info():
    req = request()
    req.info.CopyFrom(types.RequestInfo())
    return req

def request_set_option(key, val):
    req = request()
    req.set_option.key = key
    req.set_option.value = val
    return req

def request_deliver_tx(tx_bytes):
    req = request()
    req.deliver_tx.tx = tx_bytes
    return req

def request_check_tx(tx_bytes):
    req = request()
    req.check_tx.tx = tx_bytes
    return req

def request_commit():
    req = request()
    req.commit.CopyFrom(types.RequestCommit())
    return req

def request_query():
    req = request()
    req.query.CopyFrom(types.RequestQuery())
    return req

def request_init_chain(validators):
    req = request()
    req.init_chain.validators = validators
    return req

def request_begin_block(hash, header):
    req = request()
    req.begin_block.hash = hash
    req.begin_block.header = header
    return req

def request_end_block(height):
    req = request()
    req.end_block.height = height
    return req

def response():
    return types.Response()

def response_exception(err_str):
    resp = response()
    resp.exception.error = err_str
    return resp

def response_echo(msg):
    resp = response()
    resp.echo.message = msg
    return resp

def response_flush():
    resp = response()
    resp.flush.CopyFrom(types.ResponseFlush())
    return resp

def response_info():
    resp = response()
    resp.info.CopyFrom(types.ResponseInfo())
    return resp

def response_set_option(log):
    resp = response()
    resp.set_option.log = log
    return resp

def response_deliver_tx(code, data, log):
    resp = response()
    resp.deliver_tx.code = code
    resp.deliver_tx.data = data
    resp.deliver_tx.log = log
    return resp

def response_check_tx(code, data, log):
    resp = response()
    resp.check_tx.code = code
    resp.check_tx.data = data
    resp.check_tx.log = log
    return resp

def response_commit(code, data, log):
    resp = response()
    resp.commit.code = code
    resp.commit.data = data
    resp.commit.log = log
    return resp

def response_query():
    resp = response()
    resp.query.CopyFrom(types.ResponseQuery())
    return resp

def response_init_chain():
    resp = response()
    resp.init_chain.CopyFrom(types.ResponseInitChain())
    return resp

def response_begin_block():
    resp = response()
    resp.begin_block.CopyFrom(types.ResponseBeginBlock())
    return resp

def response_end_block():
    resp = response()
    resp.end_block.CopyFrom(types.ResponseEndBlock())
    return resp

def write(w, msg):
    b = msg.SerializeToString()
    l = len(b)
    ll = 0
    while l:
        l >>= 8
        ll += 1
    b = ll.to_bytes(1, byteorder='big') + len(b).to_bytes(ll, byteorder='big') + b
    w.write(b)

def read(r, msg):
    ll = int.from_bytes(r.read(1), byteorder='big')
    l = int.from_bytes(r.read(ll), byteorder='big')
    b = r.read(l)
    msg.ParseFromString(b)
