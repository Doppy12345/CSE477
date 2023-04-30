const loginForm = document.getElementById("login-form")
const failureMessage = document.getElementsByClassName("failure-message")[0]
/**
 * creates a new user in the server database
 * @param  {{email: String, password: String}} data
 */
const createUser = (data) => {
    // package data in a JSON object
    

    // SEND DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/createUser",
        data: data,
        type: "POST",
        success:function(returned_data){
            returned_data = JSON.parse(returned_data);
            if ('failure' in returned_data){
                failureMessage.classList.remove('hidden')
            }
            else{
                console.log(data)
                jQuery.ajax({
                    url: "/processlogin",
                    data: data,
                    type: "POST",
                    success:function(returned_data){
                        window.location.href = "/home";
                    }
                })
            }           
                
            }
    });
}

// creates new user from the login form on form submit
loginForm.addEventListener("submit", e => {
    e.preventDefault()
    const formData = new FormData(e.target)
    createUser(Object.fromEntries(formData.entries()))
})