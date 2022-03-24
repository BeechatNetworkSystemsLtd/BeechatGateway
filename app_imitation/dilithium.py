import sys
import base58
from blake3 import blake3
sys.path.append('./')

import pydilithium

# Step 1: Create keys
def createkeys():
    pydilithium.pqcrystals_dilithium2_ref_keypair()
    address = blake3(base58.b58decode(pydilithium.pqcrystals_get_pk())).hexdigest()
    return(pydilithium.pqcrystals_get_sk(),pydilithium.pqcrystals_get_pk(), address)


# Step 2: Sign message
def signmessage(sk,message):
    pydilithium.pqcrystals_set_sk(sk)
    signed_message = pydilithium.pqcrystals_dilithium2_ref(message, len(message))
    return(signed_message)


# Step 3: Check message
def checkmessage(pk,signed_message):
    pydilithium.pqcrystals_set_pk(pk)
    check = pydilithium.pqcrystals_dilithium2_ref_open(signed_message, len(signed_message))
    return(check)
