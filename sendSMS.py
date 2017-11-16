import boto3
import os

def sendMessage(message):
   # Create an SNS client
    myKeyEnv=os.environ.get('AWS_KEY')
    mySecKeyEnv=os.environ.get('AWS_SECKEY')
    phone_number=os.environ.get('PHONE_NUMBER')

    client = boto3.client(
        "sns",
        aws_access_key_id=myKeyEnv,
        aws_secret_access_key=mySecKeyEnv,
        region_name="ap-southeast-1"
    )

 
    client.publish(PhoneNumber=phone_number, Message=message)
    print
    print "*************************"
    print "Sent SMS: " + message
    print "*************************"

