const loginForm = document.getElementById("login-form")
const failureMessage = document.getElementsByClassName("failure-message")[0]
let count = 0

/**
 * Sends user credentials to the server in order to perform user auth
 * @param  {{email: String, password: String}} data authentication data to verify on the server
 */
const checkCredentials = (data) => {
    // package data in a JSON object
    

    // SEND DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/processlogin",
        data: data,
        type: "POST",
        success:function(returned_data){
            returned_data = JSON.parse(returned_data);
            if ('failure' in returned_data){
                count += 1
                failureMessage.firstElementChild.textContent = count
                failureMessage.classList.remove('hidden')
            }
            else{
                window.location.href = "/home";
            }           
                
            }
    });
}

// on form submit starts the authetication process
loginForm.addEventListener("submit", e => {
    e.preventDefault()
    const formData = new FormData(e.target)
    checkCredentials(Object.fromEntries(formData.entries()))
})