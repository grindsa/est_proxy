#!/usr/bin/python
# -*- coding: utf-8 -*-
""" unittests for openssl_ca_handler """
# pylint: disable=C0415, R0904, W0212
import sys
import os
import unittest
from unittest.mock import patch, mock_open
from OpenSSL import crypto

sys.path.insert(0, '.')
sys.path.insert(1, '..')

class TestACMEHandler(unittest.TestCase):
    """ test class for cgi_handler """

    def setUp(self):
        """ setup unittest """
        import logging
        from examples.ca_handler.openssl_ca_handler import CAhandler
        logging.basicConfig(level=logging.CRITICAL)
        self.logger = logging.getLogger('test_acme2certifier')
        self.cahandler = CAhandler(False, self.logger)
        self.dir_path = os.path.dirname(os.path.realpath(__file__))

    def test_001_default(self):
        """ default test which always passes """
        self.assertEqual('foo', 'foo')

    def test_002_check_config(self):
        """ CAhandler._config_check with an empty config_dict """
        self.cahandler.issuer_dict = {}
        self.assertEqual('issuing_ca_key not specfied in config_file', self.cahandler._config_check())

    @patch('os.path.exists')
    def test_003_check_config(self, mock_file):
        """ CAhandler._config_check with key in config_dict but not existing """
        self.cahandler.issuer_dict = {'issuing_ca_key': 'foo.pem'}
        mock_file.side_effect = [False]
        self.assertEqual('issuing_ca_key foo.pem does not exist', self.cahandler._config_check())

    @patch('os.path.exists')
    def test_004_check_config(self, mock_file):
        """ CAhandler._config_check with key in config_dict key is existing """
        self.cahandler.issuer_dict = {'issuing_ca_key': self.dir_path + '/ca/sub-ca-key.pem'}
        mock_file.side_effect = [True]
        self.assertEqual('issuing_ca_cert must be specified in config file', self.cahandler._config_check())

    @patch('os.path.exists')
    def test_005_check_config(self, mock_file):
        """ CAhandler._config_check with key and cert in config_dict but cert does not exist """
        self.cahandler.issuer_dict = {'issuing_ca_key': self.dir_path + '/ca/sub-ca-key.pem', 'issuing_ca_cert': 'bar'}
        mock_file.side_effect = [True, False]
        self.assertEqual('issuing_ca_cert bar does not exist', self.cahandler._config_check())

    @patch('os.path.exists')
    def test_006_check_config(self, mock_file):
        """ CAhandler._config_check withoutissuing_ca_crl in config_dic """
        self.cahandler.issuer_dict = {'issuing_ca_key': self.dir_path + '/ca/sub-ca-key.pem', 'issuing_ca_cert': self.dir_path + '/ca/sub-ca-cert.pem'}
        mock_file.side_effect = [True, True]
        self.assertEqual('issuing_ca_crl must be specified in config file', self.cahandler._config_check())

    @patch('os.path.exists')
    def test_007_check_config(self, mock_file):
        """ CAhandler._config_check with wrong CRL in config_dic """
        self.cahandler.issuer_dict = {'issuing_ca_key': self.dir_path + '/ca/sub-ca-key.pem', 'issuing_ca_cert': self.dir_path + '/ca/sub-ca-cert.pem', 'issuing_ca_crl': 'foo.pem'}
        mock_file.side_effect = [True, True, False]
        self.assertEqual('issuing_ca_crl foo.pem does not exist', self.cahandler._config_check())

    @patch('os.path.exists')
    def test_008_check_config(self, mock_file):
        """ CAhandler._config_check without cert save path """
        self.cahandler.issuer_dict = {'issuing_ca_key': self.dir_path + '/ca/sub-ca-key.pem', 'issuing_ca_cert': self.dir_path + '/ca/sub-ca-cert.pem', 'issuing_ca_crl': self.dir_path + '/ca/sub-ca-crl.pem'}
        mock_file.side_effect = [True, True, True]
        self.assertEqual('cert_save_path must be specified in config file', self.cahandler._config_check())

    @patch('os.path.exists')
    def test_009_check_config(self, mock_file):
        """ CAhandler._config_check with key and cert in config_dict """
        self.cahandler.issuer_dict = {'issuing_ca_key': self.dir_path + '/ca/sub-ca-key.pem', 'issuing_ca_cert': self.dir_path + '/ca/sub-ca-cert.pem', 'issuing_ca_crl': self.dir_path + '/ca/sub-ca-crl.pem'}
        self.cahandler.cert_save_path = 'foo'
        mock_file.side_effect = [True, True, True, False]
        self.assertEqual('cert_save_path foo does not exist', self.cahandler._config_check())

    @patch('os.path.exists')
    def test_010_check_config(self, mock_file):
        """ CAhandler._config_check with empty ca_chain_list """
        self.cahandler.issuer_dict = {'issuing_ca_key': self.dir_path + '/ca/sub-ca-key.pem', 'issuing_ca_cert': self.dir_path + '/ca/sub-ca-cert.pem', 'issuing_ca_crl': self.dir_path + '/ca/sub-ca-crl.pem'}
        self.cahandler.cert_save_path = self.dir_path + '/ca/certs'
        mock_file.side_effect = [True, True, True, True]
        self.assertEqual('ca_cert_chain_list must be specified in config file', self.cahandler._config_check())

    @patch('os.path.exists')
    def test_011_check_config(self, mock_file):
        """ CAhandler._config_check completed """
        self.cahandler.issuer_dict = {'issuing_ca_key': self.dir_path + '/ca/sub-ca-key.pem', 'issuing_ca_cert': self.dir_path + '/ca/sub-ca-cert.pem', 'issuing_ca_crl': self.dir_path + '/ca/sub-ca-crl.pem'}
        self.cahandler.cert_save_path = self.dir_path + '/ca/certs'
        self.cahandler.ca_cert_chain_list = ['foo', 'bar']
        mock_file.side_effect = [True, True, True, True]
        self.assertFalse(self.cahandler._config_check())

    @patch('os.path.exists')
    def test_012_check_config(self, mock_file):
        """ CAhandler._config_check with wrong openssl.conf """
        self.cahandler.issuer_dict = {'issuing_ca_key': self.dir_path + '/ca/sub-ca-key.pem', 'issuing_ca_cert': self.dir_path + '/ca/sub-ca-cert.pem', 'issuing_ca_crl': self.dir_path + '/ca/sub-ca-crl.pem'}
        self.cahandler.cert_save_path = self.dir_path + '/ca/certs'
        self.cahandler.ca_cert_chain_list = ['foo', 'bar']
        self.cahandler.openssl_conf = 'foo'
        mock_file.side_effect = [True, True, True, True, False]
        self.assertEqual('openssl_conf foo does not exist', self.cahandler._config_check())

    @patch('os.path.exists')
    def test_013_check_config(self, mock_file):
        """ CAhandler._config_check with openssl.conf completed successfully """
        self.cahandler.issuer_dict = {'issuing_ca_key': self.dir_path + '/ca/sub-ca-key.pem', 'issuing_ca_cert': self.dir_path + '/ca/sub-ca-cert.pem', 'issuing_ca_crl': self.dir_path + '/ca/sub-ca-crl.pem'}
        self.cahandler.cert_save_path = self.dir_path + '/ca/certs'
        self.cahandler.ca_cert_chain_list = ['foo', 'bar']
        self.cahandler.openssl_conf = self.dir_path + '/ca/fr1.txt'
        mock_file.side_effect = [True, True, True, True, True]
        self.assertFalse(self.cahandler._config_check())

    def test_014_check_serialagainstcrl(self):
        """ CAhandler._crl_check without specifying a CRL"""
        crl = None
        self.assertFalse(self.cahandler._crl_check(crl, 1))

    def test_015_check_serialagainstcrl(self):
        """ CAhandler._crl_check without specifying a serial number"""
        crl = 'foo'
        self.assertFalse(self.cahandler._crl_check(crl, None))

    def test_016_check_serialagainstcrl(self):
        """ CAhandler._crl_check with a serial number not in CRL"""
        with open(self.dir_path + '/ca/sub-ca-crl.pem', 'r') as fso:
            crl = crypto.load_crl(crypto.FILETYPE_PEM, fso.read())
        self.assertFalse(self.cahandler._crl_check(crl, 2))

    def test_017_check_serialagainstcrl(self):
        """ CAhandler._crl_check with a serial number already in CRL"""
        # crl = crypto.load_crl(crypto.FILETYPE_PEM, open(self.dir_path + '/ca/sub-ca-crl.pem').read())
        with open(self.dir_path + '/ca/sub-ca-crl.pem', 'r') as fso:
            crl = crypto.load_crl(crypto.FILETYPE_PEM, fso.read())
        self.assertTrue(self.cahandler._crl_check(crl, '0BCC30C544EF26A4'))

    def test_018_check_serialagainstcrl(self):
        """ CAhandler._crl_check with a serial number already in CRL"""
        # crl = crypto.load_crl(crypto.FILETYPE_PEM, open(self.dir_path + '/ca/sub-ca-crl.pem').read())
        with open(self.dir_path + '/ca/sub-ca-crl.pem', 'r') as fso:
            crl = crypto.load_crl(crypto.FILETYPE_PEM, fso.read())
        self.assertTrue(self.cahandler._crl_check(crl, '0bcc30c544ef26a4'))

    def test_018_generate_pem_chain(self):
        """ CAhandler._pemcertchain_generate with EE cert but no ca cert"""
        self.assertEqual('ee-cert', self.cahandler._pemcertchain_generate('ee-cert', None))

    def test_019_generate_pem_chain(self):
        """ CAhandler._pemcertchain_generate with EE cert and ca cert"""
        self.assertEqual('ee-certca-cert', self.cahandler._pemcertchain_generate('ee-cert', 'ca-cert'))

    def test_020_generate_pem_chain(self):
        """ CAhandler._pemcertchain_generate with EE cert ca and an invalit entry in cert_cain_list cert"""
        self.cahandler.ca_cert_chain_list = ['foo.pem']
        self.assertEqual('ee-certca-cert', self.cahandler._pemcertchain_generate('ee-cert', 'ca-cert'))

    @patch("builtins.open", mock_open(read_data='_fakeroot-cert-1'), create=True)
    @patch('os.path.exists')
    def test_021_generate_pem_chain(self, mock_file):
        """ CAhandler._pemcertchain_generate with EE cert ca and an valid entry in cert_cain_list cert"""
        self.cahandler.ca_cert_chain_list = [self.dir_path + '/ca/fr1.txt']
        mock_file.return_value = True
        mock_open.return_vlaue = 'foo'
        self.assertEqual('ee-cert_ca-cert_fakeroot-cert-1', self.cahandler._pemcertchain_generate('ee-cert', '_ca-cert'))

    @patch("builtins.open", mock_open(read_data='_fakeroot-cert-1'), create=True)
    @patch('os.path.exists')
    def test_022_generate_pem_chain(self, mock_file):
        """ CAhandler._pemcertchain_generate with EE cert ca and two valid entry in cert_cain_list"""
        self.cahandler.ca_cert_chain_list = [self.dir_path + '/ca/fr1.txt', self.dir_path + '/ca/fr2.txt']
        mock_file.side_effect = [True, True]
        self.assertEqual('ee-cert_ca-cert_fakeroot-cert-1_fakeroot-cert-1', self.cahandler._pemcertchain_generate('ee-cert', '_ca-cert'))

    @patch("builtins.open", mock_open(read_data='_fakeroot-cert-1'), create=True)
    @patch('os.path.exists')
    def test_023_generate_pem_chain(self, mock_file):
        """ CAhandler._pemcertchain_generate with EE cert ca and two valid entry in cert_cain_list and two invalid entriest"""
        self.cahandler.ca_cert_chain_list = [self.dir_path + '/ca/fr1.txt', 'foo1', self.dir_path + '/ca/fr2.txt', 'foo2']
        mock_file.side_effect = [True, False, True, False]
        self.assertEqual('ee-cert_ca-cert_fakeroot-cert-1_fakeroot-cert-1', self.cahandler._pemcertchain_generate('ee-cert', '_ca-cert'))

    def test_024_load_ca_key_cert(self):
        """ CAhandler._ca_load() with empty issuer_dict """
        self.cahandler.issuer_dict = {}
        self.assertEqual((None, None), self.cahandler._ca_load())

    def test_025_load_ca_key_cert(self):
        """ CAhandler._ca_load() with issuer_dict containing invalid key """
        self.cahandler.issuer_dict = {'issuing_ca_key': 'foo.pem'}
        self.assertEqual((None, None), self.cahandler._ca_load())

    @patch("builtins.open", mock_open(read_data='test'), create=True)
    @patch('os.path.exists')
    @patch('OpenSSL.crypto.load_privatekey')
    def test_026_load_ca_key_cert(self, mock_crypto, mock_file):
        """ CAhandler._ca_load() with issuer_dict containing valid key """
        self.cahandler.issuer_dict = {'issuing_ca_key': self.dir_path + '/ca/sub-ca-key.pem'}
        mock_crypto.return_value = 'foo'
        mock_file.return_value = True
        self.assertEqual(('foo', None), self.cahandler._ca_load())

    @patch("builtins.open", mock_open(read_data='test'), create=True)
    @patch('os.path.exists')
    @patch('OpenSSL.crypto.load_certificate')
    @patch('OpenSSL.crypto.load_privatekey')
    def test_027_load_ca_key_cert(self, mock_crypto_key, mock_crypto_cert, mock_file):
        """ CAhandler._ca_load() with issuer_dict containing key and passphrase """
        self.cahandler.issuer_dict = {'issuing_ca_key': self.dir_path + '/ca/sub-ca-key.pem', 'passphrase': 'Test1234'}
        mock_crypto_cert.return_value = 'cert'
        mock_crypto_key.return_value = 'key'
        mock_file.return_value = True
        self.assertEqual(('key', None), self.cahandler._ca_load())

    @patch("builtins.open", mock_open(read_data='test'), create=True)
    @patch('os.path.exists')
    @patch('OpenSSL.crypto.load_certificate')
    @patch('OpenSSL.crypto.load_privatekey')
    def test_028_load_ca_key_cert(self, mock_crypto_key, mock_crypto_cert, mock_file):
        """ CAhandler._ca_load() with issuer_dict containing key and invalid cert """
        self.cahandler.issuer_dict = {'issuing_ca_key': self.dir_path + '/ca/sub-ca-key.pem', 'passphrase': 'Test1234', 'issuing_ca_cert': 'foo.pem'}
        mock_crypto_cert.return_value = None
        mock_crypto_key.return_value = 'key'
        mock_file.return_value = True
        self.assertEqual(('key', None), self.cahandler._ca_load())

    @patch("builtins.open", mock_open(read_data='test'), create=True)
    @patch('os.path.exists')
    @patch('OpenSSL.crypto.load_certificate')
    @patch('OpenSSL.crypto.load_privatekey')
    def test_029_load_ca_key_cert(self, mock_crypto_key, mock_crypto_cert, mock_file):
        """ CAhandler._ca_load() with issuer_dict containing key and invalid cert """
        self.cahandler.issuer_dict = {'issuing_ca_key': self.dir_path + '/ca/sub-ca-key.pem', 'passphrase': 'Test1234', 'issuing_ca_cert': self.dir_path + '/ca/sub-ca-cert.pem'}
        mock_crypto_key.return_value = 'foo'
        mock_crypto_cert.return_value = 'bar'
        mock_file.return_value = True
        self.assertEqual(('foo', 'bar'), self.cahandler._ca_load())

    def test_030_verifycertificatechain(self):
        """ successful verification of one level certificate chain """
        with open(self.dir_path + '/ca/root-ca-client.txt', 'r') as fso:
            cert = fso.read()
        with open(self.dir_path + '/ca/root-ca-cert.pem', 'r') as fso:
            ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, fso.read())
        self.assertFalse(self.cahandler._certificate_chain_verify(cert, ca_cert))

    def test_031_verifycertificatechain(self):
        """ unsuccessful verification of one level certificate chain """
        with open(self.dir_path + '/ca/sub-ca-client.txt', 'r') as fso:
            cert = fso.read()
        with open(self.dir_path + '/ca/root-ca-cert.pem', 'r') as fso:
            ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, fso.read())
        self.assertEqual("[20, 0, 'unable to get local issuer certificate']", self.cahandler._certificate_chain_verify(cert, ca_cert))

    def test_032_verifycertificatechain(self):
        """ unsuccessful verification of two level certificate chain with incomplete chain"""
        with open(self.dir_path + '/ca/sub-ca-client.txt', 'r') as fso:
            cert = fso.read()
        with open(self.dir_path + '/ca/sub-ca-cert.pem', 'r') as fso:
            ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, fso.read())
        self.assertEqual("[2, 1, 'unable to get issuer certificate']", self.cahandler._certificate_chain_verify(cert, ca_cert))

    def test_033_verifycertificatechain(self):
        """ successful verification of two level certificate chain with complete chain"""
        self.cahandler.ca_cert_chain_list = [self.dir_path + '/ca/root-ca-cert.pem']
        with open(self.dir_path + '/ca/sub-ca-client.txt', 'r') as fso:
            cert = fso.read()
        with open(self.dir_path + '/ca/sub-ca-cert.pem', 'r') as fso:
            ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, fso.read())
        self.assertFalse(self.cahandler._certificate_chain_verify(cert, ca_cert))

    def test_034_verifycertificatechain(self):
        """ unsuccessful verification as certificate is damaged"""
        cert = 'foo'
        with open(self.dir_path + '/ca/root-ca-cert.pem', 'r') as fso:
            ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, fso.read())
        self.assertEqual('certificate could not get parsed', (self.cahandler._certificate_chain_verify(cert, ca_cert)))

    def test_035_verifycertificatechain(self):
        """ unsuccessful verification as ca-certificate is damaged"""
        with open(self.dir_path + '/ca/root-ca-client.txt', 'r') as fso:
            cert = fso.read()
        ca_cert = 'foo'
        self.assertEqual('issuing certificate could not be added to trust-store', self.cahandler._certificate_chain_verify(cert, ca_cert))

    def test_036_verifycertificatechain(self):
        """ unsuccessful verification of two level certificate chain as cain cert is damaged"""
        self.cahandler.ca_cert_chain_list = ['ca/root-.pem']
        with open(self.dir_path + '/ca/sub-ca-client.txt', 'r') as fso:
            cert = fso.read()
        with open(self.dir_path + '/ca/sub-ca-cert.pem', 'r') as fso:
            ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, fso.read())
        self.assertEqual('certificate ca/root-.pem could not be added to trust store', self.cahandler._certificate_chain_verify(cert, ca_cert))

    def test_037_revocation(self):
        """ revocation without having a CRL in issuer_dic """
        with open(self.dir_path + '/ca/sub-ca-client.txt', 'r') as fso:
            cert = fso.read()
        self.assertEqual((400, 'urn:ietf:params:acme:error:serverInternal', 'Unsupported operation'), self.cahandler.revoke(cert))

    def test_038_revocation(self):
        """ revocation without having a CRL in issuer_dic but none"""
        self.cahandler.issuer_dict = {'crl' : None}
        with open(self.dir_path + '/ca/sub-ca-client.txt', 'r') as fso:
            cert = fso.read()
        self.assertEqual((400, 'urn:ietf:params:acme:error:serverInternal', 'Unsupported operation'), self.cahandler.revoke(cert))

    # @patch('examples.ca_handler.openssl_ca_handler.CAhandler._certificate_chain_verify')
    # @patch('examples.ca_handler.openssl_ca_handler.CAhandler._ca_load')
    #def test_039_revocation(self, mock_ca_load, mock_vrf):
    #    """ revocation cert validation failed """
    #    with open('ca/sub-ca-client.txt', 'r') as fso:
    #        cert = fso.read()
    #    self.cahandler.issuer_dict = {'issuing_ca_key': 'ca/sub-ca-key.pem', 'passphrase': 'Test1234', 'issuing_ca_cert': 'ca/sub-ca-cert.pem', 'issuing_ca_crl' : 'ca/foo-ca-crl.pem'}
    #    mock_ca_load.return_value = ('ca_key', 'ca_cert')
    #    mock_vrf.return_value = 'test'
    #    self.assertEqual((400, 'urn:ietf:params:acme:error:serverInternal', 'foo'), self.cahandler.revoke(cert))

    @patch('examples.ca_handler.openssl_ca_handler.CAhandler._certificate_chain_verify')
    @patch('examples.ca_handler.openssl_ca_handler.CAhandler._ca_load')
    def test_040_revocation(self, mock_ca_load, mock_vrf):
        """ revocation cert no CA key """
        with open(self.dir_path + '/ca/sub-ca-client.txt', 'r') as fso:
            cert = fso.read()
        self.cahandler.issuer_dict = {'issuing_ca_key': self.dir_path + '/ca/sub-ca-key.pem', 'passphrase': 'Test1234', 'issuing_ca_cert': self.dir_path + '/ca/sub-ca-cert.pem', 'issuing_ca_crl' : self.dir_path + '/ca/foo-ca-crl.pem'}
        mock_ca_load.return_value = (None, 'ca_cert')
        mock_vrf.return_value = None
        self.assertEqual((400, 'urn:ietf:params:acme:error:serverInternal', 'configuration error'), self.cahandler.revoke(cert))

    @patch('examples.ca_handler.openssl_ca_handler.CAhandler._certificate_chain_verify')
    @patch('examples.ca_handler.openssl_ca_handler.CAhandler._ca_load')
    def test_041_revocation(self, mock_ca_load, mock_vrf):
        """ revocation cert no CA cert """
        with open(self.dir_path + '/ca/sub-ca-client.txt', 'r') as fso:
            cert = fso.read()
        self.cahandler.issuer_dict = {'issuing_ca_key': self.dir_path + '/ca/sub-ca-key.pem', 'passphrase': 'Test1234', 'issuing_ca_cert': self.dir_path + '/ca/sub-ca-cert.pem', 'issuing_ca_crl' : self.dir_path + '/ca/foo-ca-crl.pem'}
        mock_ca_load.return_value = ('ca_key', None)
        mock_vrf.return_value = None
        self.assertEqual((400, 'urn:ietf:params:acme:error:serverInternal', 'configuration error'), self.cahandler.revoke(cert))

    @patch('examples.ca_handler.openssl_ca_handler.cert_serial_get')
    @patch('examples.ca_handler.openssl_ca_handler.CAhandler._certificate_chain_verify')
    @patch('examples.ca_handler.openssl_ca_handler.CAhandler._ca_load')
    def test_042_revocation(self, mock_ca_load, mock_vrf, mock_serial):
        """ revocation cert no serial """
        with open(self.dir_path + '/ca/sub-ca-client.txt', 'r') as fso:
            cert = fso.read()
        self.cahandler.issuer_dict = {'issuing_ca_key': self.dir_path + '/ca/sub-ca-key.pem', 'passphrase': 'Test1234', 'issuing_ca_cert': self.dir_path + '/ca/sub-ca-cert.pem', 'issuing_ca_crl' : self.dir_path + '/ca/foo-ca-crl.pem'}
        mock_ca_load.return_value = ('ca_key', 'ca_cert')
        mock_vrf.return_value = None
        mock_serial.return_value = None
        self.assertEqual((400, 'urn:ietf:params:acme:error:serverInternal', 'configuration error'), self.cahandler.revoke(cert))

    @patch('examples.ca_handler.openssl_ca_handler.cert_serial_get')
    @patch('examples.ca_handler.openssl_ca_handler.CAhandler._certificate_chain_verify')
    # @patch('examples.ca_handler.openssl_ca_handler.CAhandler._ca_load')
    def test_043_revocation(self, mock_vrf, mock_serial):
        """ revocation cert """
        with open(self.dir_path + '/ca/sub-ca-client.txt', 'r') as fso:
            cert = fso.read()
        self.cahandler.issuer_dict = {'issuing_ca_key': self.dir_path + '/ca/sub-ca-key.pem', 'passphrase': 'Test1234', 'issuing_ca_cert': self.dir_path + '/ca/sub-ca-cert.pem', 'issuing_ca_crl' : self.dir_path + '/ca/foo-ca-crl.pem'}
        # mock_ca_load.return_value = ('ca_key', 'ca_cert')
        mock_vrf.return_value = None
        mock_serial.return_value = 14
        self.assertEqual((200, None, None), self.cahandler.revoke(cert))

    @patch('examples.ca_handler.openssl_ca_handler.CAhandler._crl_check')
    @patch('examples.ca_handler.openssl_ca_handler.cert_serial_get')
    @patch('examples.ca_handler.openssl_ca_handler.CAhandler._certificate_chain_verify')
    def test_044_revocation(self, mock_vrf, mock_serial, mock_crl):
        """ revocation cert """
        with open(self.dir_path + '/ca/sub-ca-client.txt', 'r') as fso:
            cert = fso.read()
        self.cahandler.issuer_dict = {'issuing_ca_key': self.dir_path + '/ca/sub-ca-key.pem', 'passphrase': 'Test1234', 'issuing_ca_cert': self.dir_path + '/ca/sub-ca-cert.pem', 'issuing_ca_crl' : self.dir_path + '/ca/foo-ca-crl.pem'}
        # mock_ca_load.return_value = ('ca_key', 'ca_cert')
        mock_vrf.return_value = None
        mock_serial.return_value = 14
        mock_crl.return_value = True
        self.assertEqual((400, 'urn:ietf:params:acme:error:alreadyRevoked', 'Certificate has already been revoked'), self.cahandler.revoke(cert))

    def test_044_list_check(self):
        """ CAhandler._list_check failed check as empty entry"""
        list_ = ['bar.foo$', 'foo.bar$']
        entry = None
        self.assertFalse(self.cahandler._list_check(entry, list_))

    def test_045_list_check(self):
        """ CAhandler._list_check check against empty list"""
        list_ = []
        entry = 'host.bar.foo'
        self.assertTrue(self.cahandler._list_check(entry, list_))

    def test_046_list_check(self):
        """ CAhandler._list_check successful check against 1st element of a list"""
        list_ = ['bar.foo$', 'foo.bar$']
        entry = 'host.bar.foo'
        self.assertTrue(self.cahandler._list_check(entry, list_))

    def test_047_list_check(self):
        """ CAhandler._list_check unsuccessful as endcheck failed"""
        list_ = ['bar.foo$', 'foo.bar$']
        entry = 'host.bar.foo.bar_'
        self.assertFalse(self.cahandler._list_check(entry, list_))

    def test_048_list_check(self):
        """ CAhandler._list_check successful without $"""
        list_ = ['bar.foo', 'foo.bar$']
        entry = 'host.bar.foo.bar_'
        self.assertTrue(self.cahandler._list_check(entry, list_))

    def test_049_list_check(self):
        """ CAhandler._list_check wildcard check"""
        list_ = ['bar.foo$', 'foo.bar$']
        entry = '*.bar.foo'
        self.assertTrue(self.cahandler._list_check(entry, list_))

    def test_050_list_check(self):
        """ CAhandler._list_check failed wildcard check"""
        list_ = ['bar.foo$', 'foo.bar$']
        entry = '*.bar.foo_'
        self.assertFalse(self.cahandler._list_check(entry, list_))

    def test_051_list_check(self):
        """ CAhandler._list_check not end check"""
        list_ = ['bar.foo$', 'foo.bar$']
        entry = 'bar.foo gna'
        self.assertFalse(self.cahandler._list_check(entry, list_))

    def test_052_list_check(self):
        """ CAhandler._list_check $ at the end"""
        list_ = ['bar.foo$', 'foo.bar$']
        entry = 'bar.foo$'
        self.assertFalse(self.cahandler._list_check(entry, list_))

    def test_053_list_check(self):
        """ CAhandler._list_check check against empty list flip"""
        list_ = []
        entry = 'host.bar.foo'
        self.assertFalse(self.cahandler._list_check(entry, list_, True))

    def test_054_list_check(self):
        """ CAhandler._list_check flip successful check """
        list_ = ['bar.foo$', 'foo.bar$']
        entry = 'host.bar.foo'
        self.assertFalse(self.cahandler._list_check(entry, list_, True))

    def test_055_list_check(self):
        """ CAhandler._list_check flip unsuccessful check"""
        list_ = ['bar.foo$', 'foo.bar$']
        entry = 'host.bar.foo'
        self.assertFalse(self.cahandler._list_check(entry, list_, True))

    def test_056_list_check(self):
        """ CAhandler._list_check unsuccessful whildcard check"""
        list_ = ['foo.bar$', r'\*.bar.foo']
        entry = 'host.bar.foo'
        self.assertFalse(self.cahandler._list_check(entry, list_))

    def test_057_list_check(self):
        """ CAhandler._list_check successful whildcard check"""
        list_ = ['foo.bar$', r'\*.bar.foo']
        entry = '*.bar.foo'
        self.assertTrue(self.cahandler._list_check(entry, list_))

    def test_056_string_wlbl_check(self):
        """ CAhandler._string_wlbl_check against empty lists"""
        white_list = []
        black_list = []
        entry = 'host.bar.foo'
        self.assertTrue(self.cahandler._string_wlbl_check(entry, white_list, black_list))

    def test_057_string_wlbl_check(self):
        """ CAhandler._string_wlbl_check against empty whitlist but match in blacklist """
        white_list = []
        black_list = ['host.bar.foo$']
        entry = 'host.bar.foo'
        self.assertFalse(self.cahandler._string_wlbl_check(entry, white_list, black_list))

    def test_058_string_wlbl_check(self):
        """ CAhandler._string_wlbl_check against empty whitlist but no match in blacklist """
        white_list = []
        black_list = ['faulty.bar.foo$']
        entry = 'host.bar.foo'
        self.assertTrue(self.cahandler._string_wlbl_check(entry, white_list, black_list))

    def test_060_string_wlbl_check(self):
        """ CAhandler._string_wlbl_check against empty whitlist wildcard check does not hit """
        white_list = []
        black_list = [r'\*.bar.foo$']
        entry = 'host.bar.foo'
        self.assertTrue(self.cahandler._string_wlbl_check(entry, white_list, black_list))

    def test_061_string_wlbl_check(self):
        """ CAhandler._string_wlbl_check against empty whitlist wildcard check hit """
        white_list = []
        black_list = [r'\*.bar.foo$']
        entry = '*.bar.foo'
        self.assertFalse(self.cahandler._string_wlbl_check(entry, white_list, black_list))

    def test_062_string_wlbl_check(self):
        """ CAhandler._string_wlbl_check successful wl check with empty bl"""
        white_list = ['foo.foo', 'bar.foo$']
        black_list = []
        entry = 'host.bar.foo'
        self.assertTrue(self.cahandler._string_wlbl_check(entry, white_list, black_list))

    def test_063_string_wlbl_check(self):
        """ CAhandler._string_wlbl_check unsuccessful empty bl """
        white_list = ['foo.foo$', 'host.bar.foo$']
        black_list = []
        entry = 'host.bar.foo.bar'
        self.assertFalse(self.cahandler._string_wlbl_check(entry, white_list, black_list))

    def test_064_string_wlbl_check(self):
        """ CAhandler._string_wlbl_check unsuccessful host in bl"""
        white_list = ['foo.foo', 'bar.foo$']
        black_list = ['host.bar.foo']
        entry = 'host.bar.foo'
        self.assertFalse(self.cahandler._string_wlbl_check(entry, white_list, black_list))

    def test_065_string_wlbl_check(self):
        """ CAhandler._string_wlbl_check unsuccessful host in bl but not on first position"""
        white_list = ['foo.foo', 'bar.foo$']
        black_list = ['foo.bar$', 'host.bar.foo', 'foo.foo']
        entry = 'host.bar.foo'
        self.assertFalse(self.cahandler._string_wlbl_check(entry, white_list, black_list))

    def test_066_string_wlbl_check(self):
        """ CAhandler._string_wlbl_check successful wildcard in entry not n bl """
        white_list = ['foo.foo', 'bar.foo$']
        black_list = ['host.bar.foo']
        entry = '*.bar.foo'
        self.assertTrue(self.cahandler._string_wlbl_check(entry, white_list, black_list))

    def test_067_string_wlbl_check(self):
        """ CAhandler._string_wlbl_check successful wildcard blacklisting - no match"""
        white_list = ['foo.foo', 'bar.foo$']
        black_list = [r'\*.bar.foo']
        entry = 'host.bar.foo'
        self.assertTrue(self.cahandler._string_wlbl_check(entry, white_list, black_list))

    def test_068_string_wlbl_check(self):
        """ CAhandler._string_wlbl_check  failed wildcard black-listing """
        white_list = ['foo.foo', 'bar.foo$']
        black_list = [r'\*.bar.foo']
        entry = '*.bar.foo'
        self.assertFalse(self.cahandler._string_wlbl_check(entry, white_list, black_list))

    def test_069_string_wlbl_check(self):
        """ CAhandler._string_wlbl_check faked domain"""
        white_list = ['foo.foo', 'bar.foo$']
        black_list = ['google.com.bar.foo']
        entry = 'foo.google.com.bar.foo'
        self.assertFalse(self.cahandler._string_wlbl_check(entry, white_list, black_list))

    def test_070_string_wlbl_check(self):
        """ CAhandler._string_wlbl_check faked wc domain"""
        white_list = ['foo.foo', 'bar.foo$']
        black_list = ['google.com.bar.foo$']
        entry = '*.google.com.bar.foo'
        self.assertFalse(self.cahandler._string_wlbl_check(entry, white_list, black_list))

    def test_071_string_wlbl_check(self):
        """ CAhandler._string_wlbl_check faked domain"""
        white_list = ['foo.foo', 'bar.foo$']
        black_list = ['google.com']
        entry = '*.google.com.bar.foo'
        self.assertFalse(self.cahandler._string_wlbl_check(entry, white_list, black_list))

    def test_072_string_wlbl_check(self):
        """ CAhandler._string_wlbl_check faked hostname and domain"""
        white_list = ['foo.foo', 'bar.foo$']
        black_list = ['google.com']
        entry = 'www.google.com.bar.foo'
        self.assertFalse(self.cahandler._string_wlbl_check(entry, white_list, black_list))

    def test_073_csr_check(self):
        """ CAhandler._check_csr with empty whitelist and blacklists """
        self.cahandler.whitelist = []
        self.cahandler.blacklist = []
        csr = 'csr'
        self.assertTrue(self.cahandler._csr_check(csr))

    @patch('examples.ca_handler.openssl_ca_handler.CAhandler._string_wlbl_check')
    @patch('examples.ca_handler.openssl_ca_handler.csr_cn_get')
    @patch('examples.ca_handler.openssl_ca_handler.csr_san_get')
    def test_074_csr_check(self, mock_san, mock_cn, mock_lcheck):
        """ CAhandler._check_csr with list and failed check """
        self.cahandler.whitelist = ['foo.bar']
        self.cahandler.blacklist = []
        mock_san.return_value = ['DNS:host.foo.bar']
        mock_cn.return_value = 'host2.foo.bar'
        mock_lcheck.side_effect = [True, False]
        csr = 'csr'
        self.assertFalse(self.cahandler._csr_check(csr))

    @patch('examples.ca_handler.openssl_ca_handler.CAhandler._string_wlbl_check')
    @patch('examples.ca_handler.openssl_ca_handler.csr_cn_get')
    @patch('examples.ca_handler.openssl_ca_handler.csr_san_get')
    def test_075_csr_check(self, mock_san, mock_cn, mock_lcheck):
        """ CAhandler._check_csr with list and successful check """
        self.cahandler.whitelist = ['foo.bar']
        self.cahandler.blacklist = []
        mock_san.return_value = ['DNS:host.foo.bar']
        mock_cn.return_value = 'host2.foo.bar'
        mock_lcheck.side_effect = [True, True]
        csr = 'csr'
        self.assertTrue(self.cahandler._csr_check(csr))

    @patch('examples.ca_handler.openssl_ca_handler.CAhandler._string_wlbl_check')
    @patch('examples.ca_handler.openssl_ca_handler.csr_cn_get')
    @patch('examples.ca_handler.openssl_ca_handler.csr_san_get')
    def test_076_csr_check(self, mock_san, mock_cn, mock_lcheck):
        """ CAhandler._check_csr san parsing failed """
        self.cahandler.whitelist = ['foo.bar']
        self.cahandler.blacklist = []
        mock_san.return_value = ['host.google.com']
        mock_cn.return_value = 'host2.foo.bar'
        mock_lcheck.side_effect = [True, True]
        csr = 'csr'
        self.assertFalse(self.cahandler._csr_check(csr))

    @patch('examples.ca_handler.openssl_ca_handler.csr_cn_get')
    @patch('examples.ca_handler.openssl_ca_handler.csr_san_get')
    def test_077_csr_check(self, mock_san, mock_cn):
        """ CAhandler._check_csr san parsing failed """
        self.cahandler.whitelist = ['foo.bar']
        self.cahandler.blacklist = []
        mock_san.return_value = []
        mock_cn.return_value = None
        csr = 'csr'
        self.assertFalse(self.cahandler._csr_check(csr))

if __name__ == '__main__':

    unittest.main()
