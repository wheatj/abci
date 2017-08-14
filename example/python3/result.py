import types_pb2 as types

class Result():
    def __init__(self, code, data, log):
        self.code = code
        self.data = data
        self.log = log

    def is_ok():
        return self.code == types.OK

    def is_err():
        return self.code != types.OK

    def is_same_code(compare):
        return self.code == compare.code

    def error():
        return 'ABCI{code:%i, data:%X, log:%s}' % (self.code, self.data, self.log)

    def string():
        return 'ABCI{code:%i, data:%X, log:%s}' % (self.code, self.data, self.log)

    def prepend_log(log):
        self.log = log + self.log

    def append_log(log):
        self.log += log

    def set_log(log):
        self.log = log

    def set_data(data):
        self.data = data

class ResultOK(Result):
    def __init__(self, data=bytes(), log=''):
        super().__init__(types.OK, data, log)

def result(resp):
    return Result(resp.code, resp.Data, resp.Log)

def result_query(resp):
    return {
        'Code': resp.code,
        'Height': resp.height,
        'Index': resp.index,
        'Log': resp.log,
        'Key': resp.key,
        'Proof': resp.proof,
        'Value': resp.value
    }
