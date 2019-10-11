
# ThingPark Activation - Connect to AWS IoT

## Introduction

This guide will direct you through the process of connecting your ThingPark Wireless account with your AWS IoT account, in order to expose your device data directly in AWS IoT core, for all devices activated using ThingPark Activation.

This guide describes the following:

  1.  [Get a ThingPark Activation account](#get-a-partner-account-for-thingPark-activation)
  1.  [Collect the AWS information](#collect-the-aws-information)
  1.  [Provision AWS dataflow in ThingPark Wireless](#provision-aws-dataflow-in-thingpark-wireless)
  1.  [View your device data in AWS IoT core](#view-your-device-data-in-aws-iot-core)


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

You can then provision your device in Network Server and Join Server account. For detailed instructions about ThingPark Activation Provisioning, please refer to [Onboard ThingPark Activation using Microchip Secure Element](https://github.com/actility/Microchip-Getting-Started).

You need to record the ***ASKey*** (or ASTK) from your ThingPark Activation JS account.

## Collect the AWS information
From your AWS console, open your _IAM user menu_ and select _My Security Credentials_

<img src=resource/aws/AwsSecurityCredentials.gif alt="AWS security crendentials UI" width="400"/>

In the menu _Access keys_for CLI_, _SDK_, & _API access_, create an _Access Key_ if you don't already have one.

<img src=resource/aws/AwsCreateAccessKey.gif alt="AWS Create Access Key" width="600"/>

Select _show secret access key_ and record both ***Access key ID*** and ***Secret access key***

Next, go to _Services_->_IoT_Core_ and select _Settings_ from the leftbar menu.
It shows your Customer EndPoint. 

<img src=resource/aws/AwsCustomEndpoint.gif alt="AWS Custom Endpoint" width="600"/>

Record ***accountPrefix*** and ***region***


## Provision AWS dataflow in ThingPark Wireless

### Get DX token
Login in [DX admin API](https://dx-api.thingpark.com/admin/latest/swagger-ui/index.html?shortUrl=tpdx-admin-api-contract.json#!/Token/post_oauth_token) using your ThingPark Wireless NS account.

Input the following parameters in the token request
* ***grant_type***=`client_credentials`
* ***client_id***=`dev1-api/<tpw_login>`
* ***client_secret***=`<tpw_password>`

<img src=resource/aws/DxAdminLogin.gif alt="DX Admin Login UI" width="600"/>

### Declare DX dataflow to AWS account
Next, go to _ThingPark DX Dataflow API_ using top level dropbox (it will keep your DX token set) and input the following parameters in 

_POST_ _/bridgeDataflows_

```
{
    "id": "myRaphaelAWS",
    "name": "Raphael_AWS",
    "bidirectional": true,
    "binder": {
        "classRef": "LRC_HTTP",
        "properties": {
            "deviceEUIList": "*",
            "asKey": <asKey retrieved from TPA account>
        }
    },
    "driver": {
      "classRef": "Raw"
    },
    "connectors": [
        {
            "classRef": "AWSIoT",
            "properties": {
                "connectorVersion": "AWSIoTConnectorV1",
                "sendMetadata": "true",
                "region": <region retrieved from AWS IoT settings>,
                "accountPrefix": <accountPrefix retrieved from AWS IoT settings>,
                "secretAccessKey": <secretAccessKey retrieved from AWS account>,
                "accessKeyId": <accessKeyId retrieved from AWS account>,
                "protocol": "WSS",
                "deviceType": "actilitytestsensor",
                "thingPrefix": "test",
                "downlinkPort": "2"
            }
        }
    ]
}
```

Next, wait for the Dataflow to be activated (it can take 1 or 2 working days). Once it is available, login to your [ThingPark Wireless NS account](https://dev1.thingpark.com/networkManager).
Edit your device, go to _Network_ section in left menubar and click on _Network routing_->_Change_

<img src=resource/aws/DeviceManagerDataflow.gif alt="Device Routing Profile" width="600"/>

Select ***AS routing profile***=`DATAFLOW`

Once this is done, the device is ready to communicate with AWS IoT Core.

### View your device data in AWS IoT core

Thanks to ThingPark X dataflow, no device provisioning is necessary in AWS IoT Core. 
> All devices from your ThingPark Wireless account are automatically provisioned in your AWS IoT Core account.

You can view the device list in AWS IoT leftbar menu _Manage_->_Things_

<img src=resource/aws/AwsManageThings.gif alt="AWS Manage Things" width="600"/>

Data is published via MQTT on topic `aws/things/test/0004A310000AA69D/uplink` where ```test``` is defined in ***thingPrefix*** of the dataflow, and ```0004A310000AA69D``` is the device ***DevEUI***

You can view the data in AWS IoT left menubar _Test_ -> _Subscribe_ and input ***Subscription Topic***=`aws/things/test/0004A310000AA69D/uplink`

<img src=resource/aws/AwsTestTopic.gif alt="AWS Test Topic" width="600"/>

In this example, the data is available in "payload" = `32382E37432F38332E3646` (`28.7C/83.6F` in ASCII).

>  The Dataflow takes care of the AppSKey decryption and Payload decryption to deliver unencrypted payload with end-to-end security to the AWS IoT core account.

## Support
Should you need support or if you have any feedback, please contact Actility support by entering a support case request at partner@actility.com.
