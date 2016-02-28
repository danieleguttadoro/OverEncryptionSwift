#!/usr/bin/env python

from config import *
from keystone import SimpleKeystoneClient
from escudo_user_properties import EscudoMetaUserProperties

class CreateUser:

    def __init__(self, user_name, user_password, user_tenant, meta_tenant, user_role, authurl):
        # Simple Keystone Client
        self.client = SimpleKeystoneClient(ADMIN_U, ADMIN_K, ADMIN_TEN, authurl)
        self.user = user_name
        self.password = user_password
        self.tenant = user_tenant
        self.meta_tenant = meta_tenant
        self.role = user_role
        self.url = authurl

    def start(self):
        admin_role = self.client.ks_client.roles.find(name="admin")
        # Get user role
        us_role = self.client.ks_client.roles.find(name=self.role)
        # Create meta-tenant
        meta_tenant = self.client.create_tenant(name=self.meta_tenant)
        # Create user tenant
        tenant = self.client.create_tenant(name=self.tenant)
        # Create user
        user = self.client.create_user(self.user, self.password, self.tenant)
        # Set role to the user
        self.client.add_user_role(user, us_role, tenant)
        # Add admin users to the meta-tenant
        if us_role == admin_role:
            self.client.add_user_role(user, us_role, meta_tenant)

        # Escudo Meta-User Properties
        # Generate the catalogs
        self.emup = EscudoMetaUserProperties(name=self.user, password=self.password,
                                             meta_tenant_name=self.meta_tenant, authurl=self.url)
        self.emup.generate_keys()
        self.emup.create_catalog()
