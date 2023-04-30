const mobileNavbar = document.getElementById('mobile-nav')
const menuButton = document.getElementsByClassName('menubar')[0]

/**
 * Sets up nav bar menu button to trigger mobile nav bar show and hide functionality
 */
const setupMenuButton = () =>{
    menuButton.addEventListener('click', () => {
        mobileNavbar.classList.toggle('hidden')
        setTimeout(mobileNavbar.classList.toggle('show'), 50)
    })
}

setupMenuButton()