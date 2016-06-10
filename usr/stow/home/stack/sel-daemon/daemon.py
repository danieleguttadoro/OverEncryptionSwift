import os,json
import logging

from catalogue import *
from connection import *
from create_user import CreateUser
from Crypto.PublicKey import RSA 

from flask import Flask, request,Response
app = Flask(__name__)
  

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(DAEMON_PORT))


logging.basicConfig(filename='/opt/stack/sel-daemon/logs/event.log',level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route("/update",methods=['PUT'])
def update_req():                                                     
    try:                                                              
        receiver = request.headers['receiver']
        idkey = request.headers['id']
        obj = json.loads(request.data)
        update_catalogue(receiver, idkey, obj)
        logging.info('OK: receiver %s, idkey %s' % (receiver,idkey))
        return Response(status=200)
    except Exception,err:
        logging.warning('Exception: %s' % err)
        return Response(status=304)


@app.route("/create",methods=['GET','PUT'])
def create_req():                                                     
    if request.method == 'GET':
        logging.info('OK: send public_key')
        return Response(staus=200,body=self.get_publickey())
    elif request.method == 'PUT':
        username, password, pub_key = decrypt(request.body)

        CreateUser(username,password,TENANT_NAME,META_TENANT,'Member',AUTH_URL).start()

        suid = self.getUserID(username)
 
        swift_conn = swiftclient.client.Connection(user=ADMIN_USER,
                                                   key=ADMIN_KEY,
                                                   tenant_name=self.meta_tenant,
                                                   authurl=AUTH_URL,
                                                   auth_version='2.0')
        swift_conn.put_object("Keys", suid, pub_key)

        logging.info('OK: create user')
        return Response(status=200, body=suid)
    else:
        logging.warning('ERROR: on create_req function')
        return Response(status=400)

def get_publicKey(userID):    
    """ 
    Get the user's public key
    Returns:
        Public key
    """
    filename = './keys/pub.key'
    with open(filename, 'r') as f:
        public_key = f.read()
    return public_key

def get_privateKey(userID):  
    """
    Get the plain user's private key
    Returns:
        The plain private key
    """
    filename = './keys/pvt.key'
    with open(filename, 'r') as f:
        private_key = f.read()
    return private_key

def getUserID(username):
        """
        Get the user's ID from Keystone
        """
        # Requires an admin connection
        kc_conn = kc.Client(username=ADMIN_USER, password=ADMIN_KEY, tenant_name=TENANT_NAME, auth_url=AUTH_URL)
        this_user = filter(lambda x: x.username == username, kc_conn.users.list())
        return this_user[0].id

def decrypt(secret):
    """
    Decipher the information sent by the client.
    Returns:
        The plain username,password,pub_key
    """
    # RSA decipher
    receiver_priv_key = RSA.importKey(self.get_privateKey())
    return receiver_priv_key.decrypt(secret).split('#')


