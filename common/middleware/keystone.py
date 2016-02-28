#!/usr/bin/env python

from keystoneclient.exceptions import NotFound, Conflict
import keystoneclient.v2_0.client as kc
import logging

# set logger info to INFO
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

class SimpleKeystoneClient:

    def __init__(self, admin_user, admin_pass, admin_tenant, auth_url):
        self.ks_client = kc.Client(username=admin_user, password=admin_pass,
                                   tenant_name=admin_tenant, auth_url=auth_url)

    def create_tenant(self, name, **kwargs):
        try:
            tenant = self.ks_client.tenants.find(name=name)
            logger.info('Tenant %s exists [id: %s].' % (name, tenant.id))
        except NotFound:
            tenant = self.ks_client.tenants.create(tenant_name=name, **kwargs)
            logger.info('Tenant %s created [id: %s].' % (name, tenant.id))
        return tenant

    def create_user(self, name, password, tenant_name, **kwargs):
        try:
            user = self.ks_client.users.find(name=name)
            logger.warning('User %s exists (password unchanged).' % name)
        except NotFound:
            tenant = self.create_tenant(tenant_name)
            user = self.ks_client.users.create(name=name, password=password,
                                               tenant_id=tenant.id, **kwargs)
            logger.info('User %s created.' % name)
        return user

    def create_role(self, role_name, **kwargs):
        try:
            role = self.ks_client.roles.find(name=role_name)
            logger.info('Role %s exists.' % role_name)
        except NotFound:
            role = self.ks_client.roles.create(role_name, **kwargs)
            logger.info('Role %s created.' % role_name)
        return role

    def add_user_role(self, user, role, tenant, **kwargs):
        try:
            self.ks_client.roles.add_user_role(user, role, tenant, **kwargs)
            logger.info('Role given to user.')
        except Conflict:
            logger.info('User already has the requested role.')

