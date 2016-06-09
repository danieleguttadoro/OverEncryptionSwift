import os,json
from catalogue import *
from connection import *
from flask import Flask, request,Response
app = Flask(__name__)
  
@app.route("/",methods=['PUT'])
def manage_req():                                                     
    try:                                                              
        receiver = request.headers['receiver']
        idkey = request.headers['id']
        obj = json.loads(request.data)
        update_catalogue(receiver, idkey, obj)
        return Response(status=200)
    except Exception,err:
        print Exception,err
        return Response(status=304)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(DAEMON_PORT))
