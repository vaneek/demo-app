#!/usr/bin/env python
import logging
import json
import time
from optparse import OptionParser
import requests
import boto3
from cfnresponse import send, SUCCESS, FAILED


logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

class bootstrap(object):
    reason = None
    response_data = None

    def __init__(self, event, context):
        self.event = event
        self.context = context
        logger.info("Event: %s" % self.event)
        logger.info("Context: %s" % self.context)
        if self.context != None:
            self.s3 = boto3.session.Session().client('s3')
        else:
            self.s3 = boto3.session.Session(profile_name=event['ResourceProperties']['Profile']).client('s3')
        try:
            self.api_id = event['ResourceProperties']['ApiId']
            self.s3_bucket = event['ResourceProperties']['S3Bucket']
            self.region = event['ResourceProperties']['Region']
        except KeyError as e:
            self.reason = "Missing required property %s" % e
            logger.error(self.reason)
            if self.context:
                send(event, self.context, FAILED)
            return

    def create(self, updating=False):
        try:
            #Force a delay to wait for API deployment as "DependsOn" statements
            # are not reliable with API deployments.
            time.sleep(10)

            #PUT dummy records
            url = "https://" + self.event['ResourceProperties']['ApiId'] + ".execute-api." + self.event['ResourceProperties']['Region'] + ".amazonaws.com/Prod/resource"

            resource1 = "8888"
            data1 = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
            url1 = url + "/" + resource1
            response = self.do_put(url1, data1)
            logger.info("URL: %s" % url1 )
            logger.info("Response: %s" % response)

            resource2 = "random"
            data2 = "{Name: hostname, Value: server1}"
            url2 = url + "/" + resource2
            response = self.do_put(url2, data2)
            logger.info("URL: %s" % url2 )
            logger.info("Response: %s" % response)

            #Create index.html
            button1 = "<form action=\"" + url1 + "\"><input type=\"submit\" value=\"Data1\"></form>"
            button2 = "<form action=\"" + url2 + "\"><input type=\"submit\" value=\"Data2\"></form>"

            file = open("/tmp/index.html", "w")
            file.write(button1)
            file.write(button2)
            file.close()

            response = self.s3.upload_file(
                '/tmp/index.html', self.s3_bucket, 'index.html', ExtraArgs={'ACL': "public-read", 'ContentType': 'text/html'}
            )

            send(self.event, self.context, SUCCESS)
        except Exception as e:
            logger.info("Exception: %s" % e)
            pass

    def delete(self):
        print self.event
        send(self.event, self.context, SUCCESS)

    def update(self):
        print self.event
        send(self.event, self.context, SUCCESS)

    def do_put(self, url, payload):
        headers = {'Access-Control-Allow-Origin' : '*',
                   'Access-Control-Allow-Headers':'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                   'Access-Control-Allow-Credentials' : 'true',
                   'Content-Type': 'application/json'}
        response = requests.put(url, data=payload, headers=headers)
        return response

def lambda_handler(event, context):
    website = bootstrap(event, context)
    if event['RequestType'] == 'Delete':
        website.delete()
        return
    if event['RequestType'] == 'Create':
        website.create()
        return
    if event['RequestType'] == 'Update':
        website.update()
        return
    logger.info("Received event: " + json.dumps(event, indent=2))
    if context:
        send(event, context, FAILED, reason="Unknown Request Type %s" % event['RequestType'])

if __name__ == "__main__":
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-r","--region", help="Region in which to run.")
    parser.add_option("-a","--api", help="API Id.")
    parser.add_option("-s","--hosted_website", help="S3 bucket hosting website.")
    parser.add_option("-p","--profile", help="Profile name to use when connecting to aws.", default="default")
    parser.add_option("-x","--execute", help="Execute an update create or delete.", default="Create")
    (opts, args) = parser.parse_args()

    options_broken = False
    if not opts.api:
        logger.error("Must Specify API endpoint")
        options_broken = True
    if not opts.hosted_website:
        logger.error("Must Specify S3 Bucket hosting website")
        options_broken = True
    if options_broken:
        parser.print_help()
        exit(1)
    if opts.execute != 'Update':
        event = { 'RequestType': opts.execute, 'ResourceProperties': { 'ApiId': opts.api, 'S3Bucket': opts.hosted_website, 'Profile': opts.profile, 'Region': opts.region } }
    else:
        event = { 'RequestType': opts.execute, 'ResourceProperties': { 'HostedZoneId': opts.hosted_zone_id, 'VpcId': opts.vpc_id, 'Profile': opts.profile, 'Region': opts.region }, 'OldResourceProperties': { 'HostedZoneId': opts.old_hosted_zone_id, 'VpcId': opts.old_vpc_id, 'Profile': opts.profile, 'Region': opts.region } }
    lambda_handler(event, None)
