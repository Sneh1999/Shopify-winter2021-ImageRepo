# Shopify-winter2021- Backend Developer Intern Challenge
Built an image repository which allows the user to register,login,upload new images,delete images,download images and share access of  images with there friends


### Deployed the Api, Access the Swagger UI on the given url
-  [Image Repository](https://imagerepo-shopify.herokuapp.com/ui/)

# Table of Contents
- [Authentication](#authentication)
- [User](#user)
- [Images](#images)
- [Permission](#permissions)
- [Future Features](#future-features)
- [Note For Shopify Developers](##note-for-shopify-developers)
- [Contact Me](#contact-met)

## Features

<p align="center">
    <u><h2 align="center">Authentication</h2></u>
</p>

-  I chose JWT based authentication. The server generates a JWT token that verifies the user identity and sends  back to the client. 
- I have created an admin  which has access to all the functionalities in the Image Repository and can function as the root to get the details of other users.By default the first user created is the admin user.

    ```
        username : admin
        password: admin
    ```

-  <b>Create a new user</b>: Post {/users} -  Pass in the first name,last name,email and password in the request body.These details get stored in the user.db table.The password is first encypted using  pbkdf2_sha256 and then stored in the database for safety.

    -  Curl request for creating a new user
        ```
        curl -X POST "https://imagerepo-shopify.herokuapp.com/users" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"email\":\"string\",\"fname\":\"string\",\"lname\":\"string\",\"password\":\"string\"}"
        ```

    - The Swagger UI interface
        ![createuser](https://user-images.githubusercontent.com/35871990/92342777-e4553380-f08f-11ea-9698-d6f6dfed10e6.png)

    - Sample Response Body
        ```
        {
            "email": "string",
            "fname": "string",
            "id": 3,
            "images": [],
            "lname": "string",
            "timestamp": "2020-09-06T00:12:45.076698"
        }
        ```

-  <b>Login for an existing user</b>: Post {/login} - Provide the email and password of the user created above in the login endpoint. This function returns back a JWT token based on details verified agaisnt the details in the user.db.The password is verified by creating a hash and then checking if the hash matches the hash in the db.

    - CURL REQUEST for login
        ```
        curl -X POST "https://imagerepo-shopify.herokuapp.com/login" -H  "accept: text/plain" -H  "Content-Type: application/json" -d "{\"email\":\"string\",\"password\":\"string\"}"
        ```
    - The Swagger UI interface
        ![loginimage](https://github.com/Sneh1999/Shopify-winter2021-private/blob/master/ImageRepo/static/images/login.png?raw=true)

    -  Example response is a JWT token
        ```
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOm51bGwsImlhdCI6MTU5OTM1MzI3MiwiZXhwIjoxNTk5MzU5MjcyLCJzdWIiOiIyIn0.tWo9C46sw4_JSPFS-uRBKvYFdVvFduFVBAuDKG8dEzs
        ```

- <b> To further access any other feature in Swagger UI paste the JWT token by clicking the Authorize button </b>
    ![authorizeButton](https://user-images.githubusercontent.com/35871990/92342926-5f1e4e80-f090-11ea-950a-dbadfe4e8a01.png)
    ![authorizebuttonmodel](https://user-images.githubusercontent.com/35871990/92342937-680f2000-f090-11ea-8cb7-da25821417ff.png)



<p align="center">
    <u><h2 align="center">User</h2></u>
</p>

- The image repository has a user which has an email,first name,last name,email,password and a list of images to which he has  authorization.

    - Get all the users: GET {/users}
        - This function is only allowed to be accessed only by the admin. Use the admin username and password provided above. This is to make sure that no  user other than the admin has access to other user's details.You need to login  as the admin to access this endpoint.
    
        - Curl Request:
            ```
                curl -X GET "https://imagerepo-shopify.herokuapp.com/users" -H  "accept: application/json" -H  "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOm51bGwsImlhdCI6MTU5OTM1NDY5OCwiZXhwIjoxNTk5MzYwNjk4LCJzdWIiOiIxIn0.hCr8FgUZBB4aRvx8ITb10-rIuaoT7F6HVirbMRBH4sU"
            ```
        - Swagger UI interface
            ![login](https://user-images.githubusercontent.com/35871990/92342787-ed460500-f08f-11ea-819d-fef7bf6f7afc.png)
        - Example Response body:
            ```
                [
                    {
                        "email": "string",
                        "fname": "string",
                        "id": 2,
                        "images": [],
                        "lname": "string",
                        "timestamp": "2020-09-06T01:12:05.280970"
                    },
                    {
                        "email": "admin",
                        "fname": "admin",
                        "id": 1,
                        "images": [],
                        "lname": "admin",
                        "timestamp": "2020-09-06T00:37:30.702541"
                    }
                ]
            ```
    - To get a particular user: Get /users/{user_id}
        - Curl request 
            ```
            curl -X GET "https://imagerepo-shopify.herokuapp.com/users/2" -H  "accept: application/json" -H  "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOm51bGwsImlhdCI6MTU5OTM1MzI3MiwiZXhwIjoxNTk5MzU5MjcyLCJzdWIiOiIyIn0.tWo9C46sw4_JSPFS-uRBKvYFdVvFduFVBAuDKG8dEzs"
            ```

        - Swagger UI interface
            ![getuser](https://user-images.githubusercontent.com/35871990/92342804-f8009a00-f08f-11ea-8bbe-47038e48ee6c.png)
        - Example Response is a user object
            ```
            {
                "email": "string",
                "fname": "string",
                "id": 2,
                "images": [],
                "lname": "string",
                "timestamp": "2020-09-06T00:47:49.073446"
            }
            ```

    - To ammend a particular user: Put /users/{user_id}
        - Curl request 
            ```
                curl -X PUT "https://imagerepo-shopify.herokuapp.com/users/2" -H  "accept: application/json" -H  "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOm51bGwsImlhdCI6MTU5OTM1MzI3MiwiZXhwIjoxNTk5MzU5MjcyLCJzdWIiOiIyIn0.tWo9C46sw4_JSPFS-uRBKvYFdVvFduFVBAuDKG8dEzs" -H  "Content-Type: application/json" -d "{\"email\":\"str\",\"fname\":\"string\",\"lname\":\"string\"}"
            ```
        
        - Swagger UI interface
            ![ammenduser](https://user-images.githubusercontent.com/35871990/92342826-08187980-f090-11ea-9dcc-8cf083efd2bc.png)

        - Example Response:
            ```
            {
                "email": "str",
                "fname": "string",
                "id": 2,
                "images": [],
                "lname": "string",
                "timestamp": "2020-09-06T01:03:03.674621"
            }
            ```

    - To delete a particular user: Delete {/users/{user_id}}

        - Curl Request:
            ```
                curl -X DELETE "https://imagerepo-shopify.herokuapp.com/users/2" -H  "accept: */*" -H  "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOm51bGwsImlhdCI6MTU5OTM1MzI3MiwiZXhwIjoxNTk5MzU5MjcyLCJzdWIiOiIyIn0.tWo9C46sw4_JSPFS-uRBKvYFdVvFduFVBAuDKG8dEzs"
            ```
        - Swagger UI interface
            ![deleteuser](https://user-images.githubusercontent.com/35871990/92342912-52015f80-f090-11ea-9ebb-fa30e9d183a1.png)

        - Example Response: 
            ```	
                 204, Successfully deleted a user
            ```
    
 <p align="center">
    <u><h2 align="center">Images</h2></u>
</p>   
        
- Images can be uploaded,downloaded and deleted. One user can have multiple images and Images can be shared between users.

    - Upload an image :
        - <b>Storage of an image</b>: 
            - The storage of the image is done in Firebase cloud storage and not in the database because of multiple reasons relating to security, costs and backups
            -  Image.db only contains the hash of the image name(Name of the file is hashed because of security reasons)
            - Firebase Cloud Storage has restrictive write permissions,Only allowing admin to upload the images for security reasons.
        - <b>To ensure secure uploading of an image</B> :
            - File names are hashed and then stored in the database
            - File names have a limit on how many characters they can contain
            - Only Specific types of image types are supported
            - There is a restriction on the file size
        -  <b> Ensure Bulk Images are uploaded </b>:
            - Only allowing one image to be uploaded at a time : Reason is to allow parallel uploading instead of sequential to prevent malicious attacks and increase speed of the response.
            - Planning on deploying multiple instances of the app in the future and using a load balancer to balance the load to increase the upload speed of bulk images.
        - Upload an Image: Post {{/users/{user_id}/images}}
            - Curl request
                ```
                curl -X POST "https://imagerepo-shopify.herokuapp.com/users/2/images" -H  "accept: application/json" -H  "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOm51bGwsImlhdCI6MTU5OTM2NzM2MiwiZXhwIjoxNTk5MzczMzYyLCJzdWIiOiIyIn0.QEzICcnOVNPtewgTdfnQK_ZvZ96QVuiq-bEi05jbDHw" -H  "Content-Type: multipart/form-data" -F "filename=@2k9lib (1).jpg;type=image/jpeg"
                ```
            - Swagger Ui interface:
                <img width="1426" alt="uploadimage" src="https://user-images.githubusercontent.com/35871990/92342842-16669580-f090-11ea-83ba-23843b1e4385.png">
            - Sample Request Body:
                ```
                {
                    "download_token": "af961ba0-f204-4236-b3ef-b56b5103deb2",
                    "id": 1,
                    "image": "e68cd5001de84539fe4ef8b99c63e515b852ad956a1470b78d028ac21599367402",
                    "timestamp": "2020-09-06T04:43:22.618393",
                    "user": [
                        2
                    ]
                }
                ```
    - Downloading an image:
        - Download : The file's download url is generated using firebase
        - Security during download:
            - The download url is an unique url generated by firebase
            - Only admin has access on the read and can generate the url
            - Only users with permission for the image can download the image
        - Ensure Bulk Imgaes are deleted : Following a parallel model(As in the case of upload),only allowing one image to be deleted at a time to prevent malicious attacks and increase speed of the response.
        - Download an Image: Get {{/users/{user_id}/images/{image_id}}}
            - Curl request:
                ```
                    curl -X GET "https://imagerepo-shopify.herokuapp.com/users/2/images/1" -H  "accept: text/plain" -H  "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOm51bGwsImlhdCI6MTU5OTQzNTMzMCwiZXhwIjoxNTk5NDQxMzMwLCJzdWIiOiIyIn0.GAyDLi1mrjf-zs2jNQ_wKxMSqe1kMP_2axR7o9Bx9EI"
                ```
            - Swagger UI interface
                ![downloadimage](https://user-images.githubusercontent.com/35871990/92342857-23838480-f090-11ea-940f-e1cadee73a35.png)
            - Sample response body:
                ```
                    https://firebasestorage.googleapis.com/v0/b/shopify-d7101.appspot.com/o/e68cd5001de84539fe4ef8b99c63e515b852ad956a1470b78d028ac21599435395?alt=media&token=c8bbf46d-fe8e-45a6-8170-89862a965b46
                ```
    - Reading a list of images: Get {{/users/{user_id}/imagesß}}
        -  This endpoint helps in reading all the images related to a user.Only an authorized user and  admin can access this.
        - Curl request:
            ```
            curl -X GET "https://imagerepo-shopify.herokuapp.com/users/2/images" -H  "accept: application/json" -H  "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOm51bGwsImlhdCI6MTU5OTQzNTMzMCwiZXhwIjoxNTk5NDQxMzMwLCJzdWIiOiIyIn0.GAyDLi1mrjf-zs2jNQ_wKxMSqe1kMP_2axR7o9Bx9EI"
            ```
        - Swagger UI interface:
            ![readingimages](https://user-images.githubusercontent.com/35871990/92342895-47df6100-f090-11ea-88c1-e201fce1762c.png)
        - Sample response body:
            ```
                [
                    {
                        "download_token": "c8bbf46d-fe8e-45a6-8170-89862a965b46",
                        "id": 1,
                        "image": "e68cd5001de84539fe4ef8b99c63e515b852ad956a1470b78d028ac21599435395",
                        "timestamp": "2020-09-06T23:36:35.870114",
                        "user": [
                        2
                        ]
                    }
                ]
            ```
    - Deleting an image for the user:
        - <b>Secure Deletion of the image </b>: 
            - This function is used to delete a permission of a user for an image from the permission.db table. The image gets deleted from firebase only when no user is left with the permission for the given image 
            - Only an authorized user and admin can delete permission for the image
            - Firebase is configured to only allow admin credentials to delete the image
        - <b>Ensuring bulk deletion of the images</b>: Only one image is allowed to be deleted at a time to follow a parallel model instead of a sequential model to prevent malicious attacks and increase speed of the response
        - Delete an image : Delete {{/users/{user_id}/images/{image_id}}}
            - Curl request
                ```
                    curl -X DELETE "https://imagerepo-shopify.herokuapp.com/users/2/images/1" -H  "accept: */*" -H  "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOm51bGwsImlhdCI6MTU5OTQzNTMzMCwiZXhwIjoxNTk5NDQxMzMwLCJzdWIiOiIyIn0.GAyDLi1mrjf-zs2jNQ_wKxMSqe1kMP_2axR7o9Bx9EI"
                ```
            - Swagger UI interface:
                ![deleteimage](https://user-images.githubusercontent.com/35871990/92342870-30a07380-f090-11ea-8ff5-43d13a17fb7e.png)
            - Sample response :
                ```
                204: Successfully deleted access to an image
                ```
<p align="center">
    <u><h2 align="center">Permissions</h2></u>
</p>

- Have you ever used google photos ? Wanna share your photos with your friends ? Here you go :) . Permissions allows a user to give another user permission for his image.Just provide the email of the user in the request body to give him permission for your image.Cool right :) 
    - Sample Curl request:
        ```
        curl -X POST "https://imagerepo-shopify.herokuapp.com/users/2/images/1/access" -H  "accept: application/json" -H  "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOm51bGwsImlhdCI6MTU5OTQzNTM2NywiZXhwIjoxNTk5NDQxMzY3LCJzdWIiOiIyIn0.6uVzJyem-FhQpUoiht3S1TWqmATpnE4nHGsp2mtgjSY" -H  "Content-Type: application/json" -d "{\"email\":\"str\"}"
        ```
    - Swagger ui interface
        ![access](https://user-images.githubusercontent.com/35871990/92342882-38f8ae80-f090-11ea-9fb8-7371cebb5a98.png)
    - Sample response body:
        ```
        {
            "download_token": "9ee0e29a-75a4-4572-92d4-f5e8957ef0cf",
            "id": 1,
            "image": "e68cd5001de84539fe4ef8b99c63e515b852ad956a1470b78d028ac21599437761",
            "timestamp": "2020-09-07T00:16:02.367533",
            "user": [
                2,
                3
            ]
        }
        ```

<p align="center">
    <u><h2 align="center">Future Features</h2></u>
</p>

- Making multiple instances of my app and running a load balancer to balance the load between various instances so that the bulk images get uploaded faster 
- Make the UI interface for the app
- Have the  ability to revoke access to an image for another user
- Building health checks for the instances 

<p align="center">
    <u><h2 align="center">Note for Shopify Developers</h2></u>
</p>

- As I am using a free version of heroku it has a problem of [Heroku](https://devcenter.heroku.com/articles/sqlite3)
```
Heroku’s Cedar stack has an ephemeral filesystem. You can write to it, and you can read from it, but the contents will be cleared periodically.
```
- Best way to test if the data is getting stored properly is to open two tabs and see that its working correctly 
- I will migrate to aws or gcp in the future releases.
- Thankyou  for your time :) 

<p align="center">
    <u><h2 align="center">Contact Me</h2></u>
</p>

Email : s2koul@uwaterloo.ca