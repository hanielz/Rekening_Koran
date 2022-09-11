import config
import phoenixdb

import gssapi 
from requests_gssapi import HTTPSPNEGOAuth , DISABLED, OPTIONAL
import sys

def phoenix_connection_kerberos():
    spnego = gssapi.OID.from_int_seq("1.3.6.1.5.5.2")
    # print(spnego)
    # authobj = HTTPSPNEGOAuth(mutual_authentication=DISABLED,oppo/rtunistic_auth=True,mech=spnego)
    authobj = HTTPSPNEGOAuth(opportunistic_auth=True,mech=spnego)
    phoenixdb_url = config.KRB_PHOENIXDB_URL.split(",")
    principal = config.KRB_PRINCIPAL
    keytab = config.KRB_KEYTAB
    conn = []

    for i in range(len(phoenixdb_url)) :
        conn.append(phoenixdb.connect(
            phoenixdb_url[i] + '{}?authentication={}&principal={}&keytab={}&krb5Conf={}&krb5CredentialsCache={}'.format(
            config.KRB_SCHEMA_NAME, config.KRB_AUTHENTICATION, 
            principal,keytab, 
            config.KRB_KRB5CONF, config.KRB_CREDENTIALS_CACHE)
            , autocommit=True, auth=authobj))
    # print("------------------PHOENIXDB_URL : " + connstring,file=sys.stderr)
    
    # conn = phoenixdb.connect(database_url, autocommit=True, auth=authobj, verify='/etc/ssl/certs/cm-auto-global_cacerts.pem')
    return conn