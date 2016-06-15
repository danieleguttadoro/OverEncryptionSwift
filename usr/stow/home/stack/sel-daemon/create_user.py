#!/usr/bin/env python

from connection import *
from simplekeystone import SimpleKeystoneClient

class CreateUser:

    def __init__(self, user_name, user_password, user_tenant, meta_tenant, user_role, authurl):
        # Simple Keystone Client
        self.client = SimpleKeystoneClient(ADMIN_USER, ADMIN_KEY, TENANT_NAME, authurl)
        self.user = user_name
        self.password = user_password
        self.tenant = user_tenant
        self.meta_tenant = meta_tenant
        self.role = user_role
        self.url = authurl

    def start(self):
        admin_role = self.client.ks_client.roles.find(name="admin")
        us_role = self.client.ks_client.roles.find(name=self.role)

        ##TO EXECUTE DURING THE DAEMON CREATION
        # Create meta-tenant
        meta_tenant = self.client.create_tenant(name=self.meta_tenant)
        # Create user tenant
        tenant = self.client.create_tenant(name=self.tenant)
        ##

        # Create user
        user = self.client.create_user(self.user, self.password, self.tenant)
        
        # Set role to the user
        self.client.add_user_role(user, us_role, tenant)
        self.client.add_user_role(user, us_role, meta_tenant)
