#!/usr/bin/env python

from simplekeystone import SimpleKeystoneClient
import swiftclient
from middleware.connection import *
from daemon import *


kc = SimpleKeystoneClient(ADMIN_USER,ADMIN_KEY,TENANT_NAME,AUTH_URL)
# find 'admin' and 'Member' roles
admin_role = kc.ks_client.roles.find(name="admin")
member_role = kc.ks_client.roles.find(name="Member")
# Create meta-tenant
meta_tenant = kc.create_tenant(name=META_TENANT)
# Create user tenant
#tenant = self.client.create_tenant(name=TENANT_NAME) <-- already exist!
admin_user = kc.ks_client.users.find(name=ADMIN_USER)
swift_user = kc.ks_client.users.find(name=SWIFT_USER)

kc.add_user_role(admin_user, admin_role, meta_tenant)
kc.add_user_role(swift_user, member_role, meta_tenant)

swift_conn = swiftclient.client.Connection(user=ADMIN_USER,
                                           key=ADMIN_KEY,
                                           tenant_name=META_TENANT,
                                           authurl=AUTH_URL,
                                           auth_version='2.0')

headers = {}
headers['x-container-read'] = '*'
headers['x-container-write'] = getUserID(ADMIN_USER)
swift_conn.put_container("Keys", headers)
create_catalog(swift_user.id,admin_user.id)
generate_swiftKeys()

filename = '/opt/stack/swift/swift/common/middleware/pub.key'
with open(filename, 'r') as f:
    swift_pubKey = f.read()
swift_conn.put_object("Keys", getUserID('swift'), swift_pubKey)

filename = '/opt/stack/swift/swift/common/middleware/vk.key'
with open(filename, 'r') as f:
    swift_vkKey = f.read()
swift_conn.put_object("Keys", 'vk_%s' % getUserID('swift'), swift_vkKey)
