#!/usr/bin/env python

from simplekeystone import SimpleKeystoneClient
import swiftclient

kc = SimpleKeystoneClient(ADMIN_USER,ADMIN_KEY,TENANT_NAME,AUTH_URL)

admin_role = kc.ks_client.roles.fin(name="admin")

# Create meta-tenant
meta_tenant = self.client.create_tenant(name=META_TENANT)
# Create user tenant
#tenant = self.client.create_tenant(name=TENANT_NAME) <-- already exist!

kc.add_user_role(ADMIN_USER, admin_role, meta_tenant)

swift_conn = swiftclient.client.Connection(user=ADMIN_USER,
                                           key=ADMIN_KEY,
                                           tenant_name=META_TENANT,
                                           authurl=AUTH_URL,
                                           auth_version='2.0')

headers = {}
headers['x-container-read'] = '*'
headers['x-container-write'] = getUserID(ADMIN_USER)

swift_conn.put_container("Keys", headers)

filename = '/opt/stack/swift/swift/common/middleware/pub.key'
with open(filename, 'r') as f:
    swift_pubKey = f.read()

swift_conn.put_object("Keys", getUserID('swift'), swift_pubKey)

def getUserID(username):

    # Requires an admin connection
    kc_conn = kc.Client(username=ADMIN_USER, password=ADMIN_KEY, tenant_name=TENANT_NAME, auth_url=A
    this_user = filter(lambda x: x.username == username, kc_conn.users.list())
    return this_user[0].id
