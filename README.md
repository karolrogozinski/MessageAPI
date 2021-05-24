# MessageAPI

API for saving, returning and editing short messages (max 160 characters), created with python FastAPI and SQL database, deployed on Heroku.




## Possible ulrs

Presented urls are linked with docs for easiest testing (methods like DELETE can't be reached otherwise)


### /messages
```
https://message-api-practise.herokuapp.com/docs#/default/messages_messages_get
```
Method to display all messages in format:
```
{
  "id": message_id,
  "owner": "message_owner_email_address",
  "title": "message_title"
}
```
Doesn't require any authentication.


### /messages/{message_id}
```
https://message-api-practise.herokuapp.com/docs#/default/get_message_messages__message_id__get
```
Method to display message specified in ```message_id``` in  format:
```
{
  "owner": "message_owner_email_address",
  "title:": "message_title",
  "text": "message_text",
  "counter": counter_of_dispaly_times
}
```
Doesn't require any authentication. After displaying message, counter is increased by 1. Possible exception:
* ``` 404, "Not_found" ``` - message with given id doesn't exist


### /send_secrets/{email}
```
https://message-api-practise.herokuapp.com/docs#/default/send_secrets_send_secrets__email__get
```
Method to send mail with generated one-time password to given ```email```. After that, there is redirection to ```/login```, where you have to type email and received password to authenticate user. 
Caution! Sometimes there is an error with redirecting. If that happens, you need to try to send password once again.
Methods below are only avaible for authenticate users:

### /messages/new
```
https://message-api-practise.herokuapp.com/docs#/default/create_message_messages_new_post
```
Post method to create new message. You have to post message in format:
```
{
  "owner":  "message_owner_email_address",
  "title": "message_title",
  "text": "message_text"
}
```
You have to be logged as same user as specified in ```owner```. Possible exceptions:
* ``` 403, "Unauthorized" ``` - You are not logged in
* ``` 402, "All parameters have to be specified" ``` - Not all parrameters was given
* ``` 402, "Your message is to long" ``` -  ```text```  is longer than 160 characters
* ``` 403, "You do not have access to create message as this user" ``` - Logged as different user than specified in ```owner```

### /messages/edit
```
https://message-api-practise.herokuapp.com/docs#/default/edit_message_messages_edit_post
```
Post method to edit existing message. You have to post message in format:
```
{
  "message_id": id_message_to_change,
  "text": "text_to_overrite"
}
```
To change message text you have to be owner of choosen message. After that ```counter``` is set to 0.  Possible exceptions:
* ``` 403, "Unauthorized" ``` - You are not logged in
* ``` 404, "Not found" ``` - Message with given ```id``` not found
* ``` 402, "Incorrect message text" ``` -  ```text```  is longer than 160 characters or not given

### /messages/{message_id}/delete
```
https://message-api-practise.herokuapp.com/docs#/default/delete_message_messages__message_id__delete_delete
```
Delete method to remove message with given ```message_id```. Possible exceptions:
* ``` 403, "Unauthorized" ``` - You are not logged in
* ``` 404, "Not found" ``` - Message with given ```id``` not found
* ``` 403, "You are not the owner" ``` - Logged as different user than message owner

## License
This project is licensed under the terms of the MIT license.
