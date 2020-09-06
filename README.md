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
        


