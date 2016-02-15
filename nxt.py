import usb
from struct import pack,unpack
from flask import Flask,request
import json


NXT_ID_PRODUCT = 0x2
NXT_ID_VENDOR  = 0x694
NXT_ENDPOINT_READ  = 130
NXT_ENDPOINT_WRITE = 1

class OPCODE:
    GET_DEVICE_INFO = [0X01, 0X9B]

nxts={}
app = Flask(__name__)

@app.route('/')
def list_nxts():
    return json.dumps({'devices':list(nxts.keys())})

@app.route('/<nxt_name>/motor/<action>')
def motor(nxt_name,action):
    try:
        port = request.args.get('port')

        speed = int(request.args.get('speed') or 100)
        direction = int(request.args.get('direction') or 0)
        time = int(request.args.get('time') or 0)
        print(nxts)
        device = nxts[nxt_name]

        run_state = {'run':0x20,'float':0,'break':0x20}[action]
        regulation_mode = (None,0,0x02)[len(port)]
        mode = [None,0x01,0x04][len(port)]
        if action == 'break':
            mode = 0x02

        port = ({'A':0,'B':1,'C':2}[port.upper()]) or 0xff
        print(port)
        payload = pack("BBBbBBbBL",0,4,port,speed,mode,regulation_mode,\
                               direction,run_state,time)
        device.write(NXT_ENDPOINT_WRITE,payload)
        result = device.read(NXT_ENDPOINT_READ,3)
    except Exception as e:
        return json.dumps({"ok":False,"err":str(e)})
    return json.dumps({"ok":True,'in':list(payload),'out':list(result)})

def get_brick_name(device):
    device.write(NXT_ENDPOINT_WRITE,OPCODE.GET_DEVICE_INFO)
    result = device.read(NXT_ENDPOINT_READ,33)[3:17]
    return str(bytes(filter(lambda v:v != 0,result)),encoding='ascii')

def search_nxts():
    nxts = filter(lambda device:device.idProduct == NXT_ID_PRODUCT and \
                         device.idVendor  == NXT_ID_VENDOR ,\
           usb.core.find(find_all=True))
    nxt_index = {}
    for nxt in nxts:
        nxt_index[get_brick_name(nxt)] = nxt
    return nxt_index


if __name__ == '__main__':
    nxts = search_nxts()
    print(nxts)
    # print(nxts)
    # app.debug = True
    app.run('0.0.0.0',5001)