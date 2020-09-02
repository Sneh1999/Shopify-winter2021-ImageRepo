const loginButton = document.getElementById("login_btn"); 

loginButton.addEventListener('click', login);


function login(){
   console.log('Hello')
}

const uploadButton = document.getElementById("UploadImage"); 

uploadButton.addEventListener('click', upload_images);




function upload_images() {
    console.log('I am here')
    var selected_files = document.getElementById("filesToUpload").files;
    var images_to_upload = new Array();

    for (let i = 0; i < selected_files.length; i++) {

        var fileReader = new FileReader();
        fileReader.onload = function (event) {
            images_to_upload.push(event.target.result);

            if (i == selected_files.length - 1) {

                console.log('Hello')
                post_data_to_api(images_to_upload);
            }
        };

        fileReader.readAsDataURL(selected_files[i]);
    }
}

function post_data_to_api(images_to_upload) {
    console.log(JSON.stringify(images_to_upload));
    data = {
        "images_data":JSON.stringify(images_to_upload) ,
        };
      url = "http://0.0.0.0:5000/api/uploadmultipleimg=";
      $.ajax({
        type: "POST",
        url: url,
        data:data,
        success: function(result){
          console.log(result);
        },
        failure: function(errMsg) {
           console.log(errMsg);
        }
        });

    // CALL API
}