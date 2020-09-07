# Shopify-winter2021-private
Image repo challenge


### Deploed the Api, Access the swagger ui 
-  [Image Repository](https://imagerepo-shopify.herokuapp.com/ui/)



## Features

<p align="center">
    <u><h2 align="center">Authentication</h2></u>
</p>

-  I chose JWT based authentication. The server generates a JWT token that verifies the user identity and sends it to the back to the client. 
- I have created an admin which can be used to access which has access to all the functionalities in the Image Repository and can function as the root to access the details of other users
    ```
        username : admin
        password: admin
    ```
-  <b>Create a new user</b>: Pass in the first name,last name,email and password in the request body.These details get stored in the user.db table.The password is first encypted using  pbkdf2_sha256 and then stored in the database for safety.

    -  CURL REQUEST for creating a new user
        ```
        curl -X POST "https://imagerepo-shopify.herokuapp.com/users" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"email\":\"string\",\"fname\":\"string\",\"lname\":\"string\",\"password\":\"string\"}"
        ```

    - The Swagger UI interface

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

-  <b>Login for an existing user</b>: Provide the email and password of the user created above in the login endpoint. This function returns back a JWT token based on details verified agaisnt the details in the user.db.The password is verified by creating a hash and then checking if the hash matches the hash in the db.

    - CURL REQUEST for login
        ```
        curl -X POST "https://imagerepo-shopify.herokuapp.com/login" -H  "accept: text/plain" -H  "Content-Type: application/json" -d "{\"email\":\"string\",\"password\":\"string\"}"
        ```
    - The Swagger UI interface

    -  Example response is a JWT token
        ```
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOm51bGwsImlhdCI6MTU5OTM1MzI3MiwiZXhwIjoxNTk5MzU5MjcyLCJzdWIiOiIyIn0.tWo9C46sw4_JSPFS-uRBKvYFdVvFduFVBAuDKG8dEzs
        ```

- <b> To further access any other feature in Swagger UI paste the JWT token by clicking the Authorize button </b>




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


        - Example Response: Empty Response
    
 <p align="center">
    <u><h2 align="center">Images</h2></u>
</p>   
        
- Images can be uploaded,downloaded and deleted.One user can have multiple images and Images can be shared between users.

    - Upload an image :
        - <b>Storage of an image</b>: 
            - The storage of the image is done in Firebase cloud storage and not in the database because of multiple reasons realating to security, costs and backups
            -  Image.db only contains the hash of the image name(Name of the file is hashed because of security reasons)
            - Firebase Cloud Storage has restrictive write permissions,Only allowing admin to upload the images for security reasons.
        - <b>To ensure secure uploading of an image</B> :
            - File names are hashed and then stored in the database
            - File names have a limit on how many characters they can contain
            - Only Specific types of image types are supported
            - There is a restriction on the file size
        -  <b> Ensure Bulk Images are uploaded </b>:
            - Only allowing one image to be uploaded at a time : Reason for that being if multiple images are uploaded together, if one image is malicious the whole request fails and its better to follow a parallel model than a sequential one.
            - Planning on deploying multiple instances of the app in the future and using a load balancer to balance the load to support bulk image support in parallel.
        - Upload an Image: Post {{/users/{user_id}/images}}
            - Curl request
                ```
                curl -X POST "https://imagerepo-shopify.herokuapp.com/users/2/images" -H  "accept: application/json" -H  "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOm51bGwsImlhdCI6MTU5OTM2NzM2MiwiZXhwIjoxNTk5MzczMzYyLCJzdWIiOiIyIn0.QEzICcnOVNPtewgTdfnQK_ZvZ96QVuiq-bEi05jbDHw" -H  "Content-Type: multipart/form-data" -F "filename=@2k9lib (1).jpg;type=image/jpeg"
                ```
            - Swagger Ui interface:

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
        - Ensure Bulk Imgaes are deleted : Following a parallel model(As in the case of upload),only allowing one image to be deleted at a time
        - Download an Image: Get {{/users/{user_id}/images/{image_id}}}
            - Curl request:
                ```
                    curl -X GET "https://imagerepo-shopify.herokuapp.com/users/2/images/1" -H  "accept: text/plain" -H  "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOm51bGwsImlhdCI6MTU5OTQzNTMzMCwiZXhwIjoxNTk5NDQxMzMwLCJzdWIiOiIyIn0.GAyDLi1mrjf-zs2jNQ_wKxMSqe1kMP_2axR7o9Bx9EI"
                ```
            - Swagger UI interface

            - Sample response body:
                ```
                    https://firebasestorage.googleapis.com/v0/b/shopify-d7101.appspot.com/o/e68cd5001de84539fe4ef8b99c63e515b852ad956a1470b78d028ac21599435395?alt=media&token=c8bbf46d-fe8e-45a6-8170-89862a965b46
                ```
    - Reading a list of images:
        -  This endpoint helps in reading all the images realted to a user.Only an authorized user and the admin can access this.
        - Curl request:
            ```
            curl -X GET "https://imagerepo-shopify.herokuapp.com/users/2/images" -H  "accept: application/json" -H  "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOm51bGwsImlhdCI6MTU5OTQzNTMzMCwiZXhwIjoxNTk5NDQxMzMwLCJzdWIiOiIyIn0.GAyDLi1mrjf-zs2jNQ_wKxMSqe1kMP_2axR7o9Bx9EI"
            ```
        - Swagger UI interface:

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
            - Firebase is coonfigured to only allow admin credentiaks to delete the image
        - <b>Ensuring bulk deletion of the images</b>: Only one image is allowed to be deleted at a time to follow a parallel model instead of a sequential model to prevent malicious attacks and speed of the response
        - Delete an image : Delete {{/users/{user_id}/images/{image_id}}}
            - Curl request
                ```
                    curl -X DELETE "https://imagerepo-shopify.herokuapp.com/users/2/images/1" -H  "accept: */*" -H  "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOm51bGwsImlhdCI6MTU5OTQzNTMzMCwiZXhwIjoxNTk5NDQxMzMwLCJzdWIiOiIyIn0.GAyDLi1mrjf-zs2jNQ_wKxMSqe1kMP_2axR7o9Bx9EI"
                ```
            - Swagger UI interface:

            - Sample response :
                ```
                204: Successfully deleted access to an image
                ```
<p align="center">
    <u><h2 align="center">Permissions</h2></u>
</p>