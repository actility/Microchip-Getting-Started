# ThingPark Activation Getting Started

RaphaelApfeldorfer-Actility edited this page on Sep 20th, 2019

# ATECC608A-TNGACT Pre-Provisioned secure element with ThingPark Activation Getting Started Guide

## Introduction

This guide will direct you through the process of getting started with developing a secure LoRa end device product using Microchip Technology's Pre-provisioned ATECC608A secure element along with ThingPark Activation service from Actility.

This guide describes the following:

  1.  [Get a ThingPark Activation account](#get-a-partner-account-for-thingPark-activation)
  1.  [Collect the Device identifiers](#collect-the-device-identifiers)
  1.  [Provision device in ThingPark Activation](#provision-device-in-thingpark-activation)
  1.  [Provision/Activate device in ThingPark Wireless](#provisionactivate-device-in-thingpark-wireless)


## Get a partner account for ThingPark Activation
To request an account on ThingPark Activation and ThingPark Wireless, post the following email
```
To: partner-activation@actility.com
Subject: ThingPark Activation evaluation
Mail: Please provide me a free test account for ThingPark Activation.
Account Name: Paul Smith
Company:      Acme
Login email:  paul.smith@acme.com
Project:      Gas meter in Europe
Timeline:     Mass production end of 2020
URL:          https://www.acme.com/products/gasmeter.html
```
Please anticipate your request as it may requires a few days to be processed.
(Note: login email should be a separate email from any existing DEV1 account)

You will receive 2 onboarding emails (one for Network Server, one for Join Server), please activate accounts using both emails.

## Collect the Device identifiers
In order to pre-commission a device using ATECC608A secure element in ThingPark Activation, the following idenfiers are required:
* DevEUI: LoRaWAN device 64-bit unique identifier assigned by the Device manufacturer (or using Secure Element default value)
* JoinEUI: LoRaWAN JS 64-bit unique identifier of the Join Server on which AppKey of the device is stored
* TKM Info: ATECC608A secure element identifier allowing ThingPark Activation to retrieve secure element AppKey

Connect to the Microchip ATSAMR34 Xplained Pro evaluation kit with serial port at 115200 bps and reboot the board.
It prints the following content:
```
Microchip LoRaWAN Stack MLS_SDK_1_0_P_1

Init - Successful
----------------------------

DEVEUI: 0x0123d345666e2dbd
JOINEUI: 0xF03D29AC71010001
TKM INFO: 0x31110123d345666e2dbd
```
## Provision device in ThingPark Activation
### Open Key Manager
Key Manager application allows Device Manufacturers to safely import the AppKeys of their devices into ThingPark Activation (Note: this is usually done via API but we will present the GUI here for simplicity)
When using Microchip's Secure Element on their devices, the on-boarding doesn't require them to know the `AppKey`: they can provide `TKM_INFO` instead.

Login your ThingPark Activation account and open [Key Manager](https://js.labs.thingpark.com/keyManager)

<img src=resource/KeyManager.gif alt="Key Manager UI" width="600"/>

### Define an AS Transport Key
ThingPark Activation is a secure service which provides End-to-End security so it delivers encrypted payload and encrypted AppSKey to the Application Servers.
The user can select an AS Transport Key (ASTK) to encrypt the AppSKey for each device (which can be the same for all devices or unique per device)

To retrieve ASTK secretly, you can use an RSA2048 key pair. It is generated with the following commands, else you can use the one generate by below example [mykey-private.key](resource/mykey-private.key) and [mykey-public.pem](resource/mykey-public.pem).
```
> openssl genrsa -des3 -out mykey-private.key 2048
Enter pass phrase for mykey-private.key: 1234
Verifying - Enter pass phrase for mykey-private.key: 1234
> openssl rsa -in mykey-private.key -outform PEM -pubout -out mykey-public.pem
Enter pass phrase for mykey-private.key: 1234
writing RSA key
```

To create ASTK, go to ASTK Menu and Press Create button

<img src=resource/ASTK.gif alt="Create ASTK" width="600"/>

Select `HSM Group` = `HSM_LABS_PROD` for ECC608A production parts and copy paste your RSA Public key `mykey-public.pem` as text

<img src=resource/CreateASTK.gif alt="Input RSA Public Key" width="600"/>

 Copy the output in `encryptedASKey.txt` file and retrieve the plaintext ASTK with the following command 
 ```
> cat encryptedASKey.txt | xxd -r -p | openssl rsautl -decrypt -inkey mykey-private.key | xxd -p
Enter pass phrase for mykey-private.key: 1234
4c65f2fc5eedb0ed0ede1f5dea2c3aed
 ``` 
 
### Provision device in Join Server
Click on Add Device -> Create

<img src=resource/Device.gif alt="Create Device" width="600"/>

Select `Secure Element` = `Yes` and your `LoRaWAN version`
Select `HSM Group` = `HSM_LABS_PROD` for ECC608A production parts and copy paste your identifier retrieve from ECC608A previously into `DevEUI`/`AppEUI`/`TKM info` input boxes.
`Home NS NetID` = `000002` for Actility development platform DEV1
Select the `ASTK` created previously

<img src=resource/CreateDevice.gif alt="Device creation fields" width="600"/>

 Once you device appears in Key Manager, it is ready for activation.
 However, it must also be provisioned in Network Server before being able to transmit on the radio.

## Provision/Activate device in ThingPark Wireless

### Create Application Server and routing profile
 
To create a new Application Server routing profile, first create a local Application Server. Click on Application Servers, Add Application servers -> Create and select type `HTTP Application Server (LoRaWAN)`

<img src=resource/CreateAS.gif alt="Create AS" width="600"/>

Select `Content Type` according to your Application Server requirement, but note that the Application Server **must** support end-to-end encryption (see #activate-device).
Then add the destination route by clicking Route -> Add.

<img src=resource/CreateASroute.gif alt="Create AS route" width="600"/>

Once the Application Server is created, create an Application Server routing profile. Click on AS routing profiles -> Create and select type `Local application server`.

<img src=resource/CreateASRP.gif alt="Create AS routing profile" width="600"/>

### Provision device in Network Server

Login your ThingPark DEV1 partner account and open [Device Manager](https://dev1.thingpark.com/deviceManager)

The device is provisioned as usual on ThingPark Wireless, except no `AppKey` needs to be provided to the Network Server.

Click on Add Device -> Create

<img src=resource/DeviceDM.gif alt="Create Device" width="600"/>

Select `Manufacturer` = `Generic` and you `LoRaWAN device profile`, `Activation type` and fill in the `DevEUI`/`AppEUI` retrieved previously.

<img src=resource/CreateDeviceDM.gif alt="Device creation fields" width="600"/>

Note that it is mandatory to select a Connectivity Plan and an Application Server routing Profile for your device to be fully provisioned and ready to be activated. 

### Activate device 
The device is now ready to be activated
LoRaWAN data can be monitored using [Wireless Logger](https://dev1.thingpark.com/wLogger)

Note however it is shown encrypted in Wireless Logger as the service delivers end-to-end security so the payload delivered to the Application Server is encrypted with the ASTK.

If your Application Server does not support end-to-end security, you can decode payload manually. To decode applicative payload sent over the tunnel interface, first decode `<AppSKey>` metadata using `ASKey`:
```
echo $AppSKey | xxd -r -p | openssl enc -d -aes-128-cbc -nosalt -iv 0 -K $ASKey -nopad | xxd -p
```
Then, decrypt the `<payload_hex>` as specified in LoRaWAN using clear text `AppSKey`

## Support
Should you need support or if you have any feedback, please contact Actility support by entering a support case request at partner@actility.com.
