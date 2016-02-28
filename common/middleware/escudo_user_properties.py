#!/usr/bin/env python

# -*- coding: utf-8 -*-



import logging

import swiftclient

from keystoneclient.v2_0 import client as kc

import os

import base64

from Crypto.Cipher import AES

from Crypto import Random

from Crypto.PublicKey import RSA

import json

from config import *





# Set cu_logger info to INFO

cu_logger = logging.getLogger(__name__)

cu_logger.setLevel(logging.INFO)

ch = logging.StreamHandler()

ch.setLevel(logging.INFO)

cu_logger.addHandler(ch)



# Size AESKey: 32 bytes = 256 bits, 16 = 128 bits

BLOCK_SIZE = 16





class EscudoMetaUserProperties:



    def __init__(self, name, password, meta_tenant_name, authurl):

        self.name = name

        self.password = password

        self.meta_tenant = meta_tenant_name

        self.authurl = authurl

        self.usrID = self.getUserID()



    def generate_keys(self, force=False):

        """

        Generate a RSA keypair for the new user, then save them locally (TODO: on barbican?)

        The private RSA key must be encrypted before being stored.

        Also store an AES masterkey (TODO: deprecate this point)

        """

        pvtK, pubK = self.gen_keypair(1024)

        pvk_filename = "pvt_%s.key" % self.usrID

        puk_filename = "pub_%s.key" % self.usrID

        mk_filename = "mk_%s.key" % self.usrID



        if not force:

            if (os.path.exists(pvk_filename) or os.path.exists(puk_filename)):

                cu_logger.warning("Warning: User keys already exist")

                return



        # TODO: delete this key

        master_key = os.urandom(BLOCK_SIZE)

        with open(mk_filename, 'w') as mk_file:

            mk_file.write(base64.b64encode(master_key))

            cu_logger.info("Generated and Stored AES MasterKey.")



        # Generate and store RSA keys

        with open(pvk_filename, "w") as pvk_file:

            pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)

            pvtK = pad(pvtK)

            iv = Random.new().read(AES.block_size)

            cipher = AES.new(master_key, AES.MODE_CBC, iv)

            pvk_file.write(base64.b64encode(iv + cipher.encrypt(pvtK)))

        cu_logger.info("Generated and Stored RSA private key.")



        with open(puk_filename, "w") as puk_file:

            puk_file.write(pubK)

        cu_logger.info("Generated and Stored RSA public key.")



        # TODO: store secret in barbican



    

    def create_catalog(self, force=False):

        """

        Generate a personal container .Cat_usr<UserID>

        and an empty catalog $cat_graph<UserID>.json

        Args:

            usrID: user's Keystone ID

            PARAM 'force': force the creation of new keys and reset the catalog

        """

        CatContainer = '.Cat_usr%s' % self.usrID

        CatSource = '$cat_graph%s.json' % self.usrID



        if not force:

            if os.path.exists(CatSource):

                cu_logger.error("ENV_ERR User_props already exists")

                return

        swift_conn = swiftclient.client.Connection(user=ADMIN_USER,

                                                   key=ADMIN_PASS,

                                                   tenant_name=self.meta_tenant,

                                                   authurl=AUTH_URL,

                                                   auth_version='2.0')



        # Create meta-container

        try:

            swift_conn.put_container(CatContainer, headers=None)

            cu_logger.info("Meta-container %s put" % CatContainer)

        except:

            cu_logger.error('Error while putting the meta-container %s' % CatContainer)



        # Add ACL for this user to the meta-container

        cntr_headers = {}

        cntr_headers['x-container-read'] = self.usrID

        cntr_headers['x-container-write'] = self.usrID

        cntr_headers['x-container-meta-acl_label'] = self.usrID

        try:

            swift_conn.post_container(CatContainer, headers=cntr_headers)

            cu_logger.info("Header for meta-container %s set" % CatContainer)

        except:

            cu_logger.error('Error while setting the meta-container %s header' % CatContainer)



        # Create catalog       

        try:

            swift_conn.put_object(CatContainer, CatSource, json.dumps({}, indent=4, sort_keys=True), content_type='application/json')

            cu_logger.info("Catalog %s put in meta-container" % CatSource)

        except:

            cu_logger.error('Error while putting the catalog %s' % CatSource)



        # Post header Label via STD post_object

        obj_headers = {}

        obj_headers['x-container-read'] = self.usrID

        obj_headers['x-container-write'] = self.usrID

        obj_headers['x-object-meta-acl_label'] = self.usrID

        try:

            swift_conn.post_object(CatContainer, CatSource, headers=obj_headers)

            cu_logger.info("Header for catalog %s set" % CatSource)

        except:

            cu_logger.error('Error setting catalog %s header' % CatSource)



        cu_logger.info("Generated and Stored personal catalog.")

        return



    def getUserID(self):

        """

        Get the user's ID from Keystone

        """

        # Requires an admin connection

        kc_conn = kc.Client(username=ADMIN_USER, password=ADMIN_PASS, tenant_name=ADMIN_TENANT, auth_url=AUTH_URL)

        this_user = filter(lambda x: x.username == self.name, kc_conn.users.list())

        return this_user[0].id



    def gen_keypair(self, bits=1024):

        """

        Generate an RSA keypair with an exponent of 65537 in PEM format

        param: bits The key length in bits

        """

        new_key = RSA.generate(bits, e=65537)

        public_key = new_key.publickey().exportKey("PEM")

        private_key = new_key.exportKey("PEM")

        # print private_key

        # print public_key

        return private_key, public_key
