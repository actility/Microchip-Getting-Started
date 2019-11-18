#!/usr/bin/env python3
# author: <raphael.apfeldorfer@actility.com>
# date: Tue September 24 16:37:21 CET 2019
'''
se_microchip.py manifest.xml
   where manifest.xml is the Microchip manifest file
'''
import sys, argparse, re
import json, base64
from pyasn1.codec.der import decoder 
try:
    import pyThingPark.dxMaker as dxMaker
    isProvisionPossible = True
except ImportError as e:
    print("pyThingPark is not available: MicrochipSEManifest.provision is not available")
    #HINT: Add pyThingPark to PYTHONPATH if it is installed in another directory
    print(e)
    isProvisionPossible = False

class MicrochipSEManifest:
    def __init__(self, json_data):
        self.seList  = []
        print('\nProcessing {} entry:'.format(len(json_data)))
        for signed_se in json_data:
            protected = json.loads(base64.b64decode(signed_se['protected'].encode('ascii')))
            payload = json.loads(base64.b64decode((signed_se['payload'] + '=' * (-len(signed_se['payload']) % 4)).encode('ascii')))
            assert(payload["model"] == "ATECC608A")
            assert(payload["partNumber"] == "ATECC608A-MAHAL")
            assert(payload["provisioner"]['organizationName'] == "Microchip Technology Inc")
            assert(payload['uniqueId'].lower() == signed_se['header']['uniqueId'].lower())
            dev_cert = base64.b64decode(payload['publicKeySet']['keys'][0]['x5c'][0])
            (der, leftover) = decoder.decode(dev_cert)
            (uniqueId, devEUI) = re.search("(?P<uniqueId>[\w\d]+)\s(?P<devEUI>[\w\d]+)\sATECC",str(der)).groups()
            assert(payload['uniqueId'].lower() == uniqueId.lower())
            se = MicrochipSE(devEUI, "3121", uniqueId[:-2])
            print(se)
            self.seList.append(se)
    def provision(self, bearerToken):
        dx = dxMaker.DxMaker(bearerToken)
        for se in self.seList:
            dev = dxMaker.FactoryDevice(DevEUI=se.devEUI, JoinEUI=se.joinEUI, TkmInfo=se.tkmInfo)
            try:
                dx.postFactoryDevice(dev)
            except: 
                print("Error: could not provision {0}".format(dev))
    def deprovision(self, bearerToken):
        dx = dxMaker.DxMaker(bearerToken)
        for se in self.seList:
            try:
                dx.deleteFactoryDevice(se.devEUI)
            except: 
                print("Error: could not deprovision DevEUI {0}".format(se.devEUI))
    def __repr__(self):
        return str(self.seList)
        

class MicrochipSE:
    def __init__(self, devEUI, seInfo, seId):
        assert(type(seInfo) is str and len(seInfo)==4)
        assert(type(devEUI) is str and len(seId)==16)
        assert(type(seId) is str and len(seId)==16)
        self.devEUI = devEUI
        self.joinEUI = "f03d29ac71010001"
        self.tkmInfo = seInfo + seId
    def __repr__(self):
        return "Microchip ATECC608A: DevEUI={0} JoinEUI={1} TkmInfo={2}".format(self.devEUI, self.joinEUI, self.tkmInfo)
    
def main(argv):
    # Parse arguments
    parser = argparse.ArgumentParser(description='Provision ECC608A from Microchip manifest in ThingPark Activation')
    parser.add_argument(
        'manifest',
        help='ECC608A manifest file')
    parser.add_argument(
        '--delete',
        help='Delete devices in manifest instead of provision them',
        action="store_true", required=False)
    parser.add_argument(
        '--user',
        help='DX login on js-labs-api',
        type=str, required=isProvisionPossible, metavar='login' )
    parser.add_argument(
        '--password',
        help='DX password on js-labs-api',
        type=str, required=isProvisionPossible, metavar='pwd' )
    parser.add_argument(
        '--cert',
        help='Verification certificate file in PEM format',
        nargs=1, type=str, required=False, metavar='file' )
    args = parser.parse_args(argv)
    
    # Load manifest as JSON
    with open(args.manifest, 'r') as f:
        manifest = MicrochipSEManifest(json.load(f))
    if not isProvisionPossible: sys.exit(1)
    
    # DX login (relies on pyThingPark.dxMaker)
    try:
        dx = dxMaker.DxAdmin(args.user, args.password)
    except Exception as e:
        print(e)
        sys.exit(3)
    bearerToken = dx.getBearerToken()
    # Provision all ECC608A in manifest into account
    if not args.delete:
        print("\nProvision {0} devices in ThingPark Activation".format(len(manifest.seList)))
        manifest.provision(bearerToken)
    else:
        print("\nDe-provision {0} devices in ThingPark Activation".format(len(manifest.seList)))
        manifest.deprovision(bearerToken)
        

if __name__ == "__main__":
    main(sys.argv[1:])
    sys.exit(0)