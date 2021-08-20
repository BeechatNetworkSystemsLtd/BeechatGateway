import sys
import os
cwd = os.getcwd()
sys.path.append('./')
sys.path.append(cwd)

from myapp.main import pykyber;

# Step 1:
# Alice
def createkeys():
	pykyber.pqcrystals_kyber512_ref_keypair()
	pk = pykyber.pqcrystals_get_pk()
	sk = pykyber.pqcrystals_get_sk()
	return(sk,pk)

# Step 2:
# Bob
def encapsulate(pk):
	pykyber.pqcrystals_kyber512_ref_enc("", pk)
	skey = pykyber.pqcrystals_get_skey()
	ciphertext = pykyber.pqcrystals_get_ct()
	return(ciphertext,skey)

# Step 3:
# Alice
def decapsulate(ct,sk):
	pykyber.pqcrystals_kyber512_ref_dec(ct, sk)
	skey = pykyber.pqcrystals_get_skey()
	return skey