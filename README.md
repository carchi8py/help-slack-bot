# help-slack-bot
#setup
## Slack Set up
### Create App
Go to https://api.slack.com/apps and click on “create new app”
### App Scopes
Click on OAuth & Permissions
Add the following Bot Token Scopes
* channels:history
* channels:read
* chat:write
* commands
* groups:history
* im:history
* im:read
* im:write

## AWS Set up
Set up a free account
### Lambda
Go to Lambda Services
Click on create function and author from scratch
Runtime should be python (3.8)
#### Add Trigger
Select API gateway, and make sure it a HTTPS 

## Back to Slack
### Event Subscription
Paste APi endpoint link from AWS in request URL

### Subscribe to bot events
These are the event that be sent to the lambda function
* message.channels -- any message in a channel this bot is part of
* message.groups -- any message in a group chat this bot is part of
* message.im -- any message sent to the bot

### Basic Information
Install your app in to your workspace

### Oauth & Permissions
Copy Bot User Oauth Token for later step

## Back to AWS
### Code
Copy Lambda_function.py in to code 

### Configuration
#### Environment Variables
Create a new vairable called `BOT_TOKEN` add the cot user oauth token from slack

#Monitoring the app
At this point you should have a running app
##monitor
Every time Slack generates an Event, it will appear in the Monitor section of Lambda with a link to the logStream in CloudWatch