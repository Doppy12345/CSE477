const createBoardButton = document.getElementsByClassName('new-board')[0]
const newBoardWindow = document.getElementsByClassName('create-board-modal')[0]
const exitButton = document.getElementsByClassName('exit-button')[0]
const createBoardForm = document.getElementById('create-board-form')

/**
 * set up modal window listerners for the create a board modal
 */
const setUpNewBoardWindow = () => {
    newBoardWindow.addEventListener('keydown', (event) => {
        event.stopImmediatePropagation()
    })
    newBoardWindow.addEventListener('keyup', (event) => {
        event.stopImmediatePropagation()
    })
    createBoardForm.addEventListener('submit', () => {
        newBoardWindow.classList.remove('show')
    })
}
/**
 * Sets up the exit button to close the modal
 */
const setUpExitButton = () => {
    exitButton.addEventListener('click', () => {
        newBoardWindow.close()
    })
}
/**
 * Sets up the newBoard button to reveal the modal
 */
const setUpNewBoardButton = () => {
    createBoardButton.addEventListener('click', () => {
        newBoardWindow.showModal()
    })
}
/**
 * Checks to see if this is the first time this user has sign up to prompt them to make a board
 */
const checkFirstSignup = () => {
    if (newBoardWindow.classList.contains('show')){
        newBoardWindow.classList.remove('show')
        newBoardWindow.showModal()
    }
}

setUpNewBoardButton()
setUpNewBoardWindow()
setUpExitButton()
checkFirstSignup()