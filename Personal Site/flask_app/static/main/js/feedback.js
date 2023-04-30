const feedbackButton = document.getElementsByClassName("feedback-banner")[0]
const feedbackWindow = document.getElementsByClassName("feedback-modal")[0]
const exitButton = document.getElementsByClassName("exit-button")[0]
/**
 * Sets up the feedback button to display the feedback form window
 */
const setUpFeedbackButton = () => {
    feedbackButton.addEventListener('click', () => {
        feedbackButton.classList.add('hidden')
        feedbackWindow.showModal()
    })
}
/**
 * Sets up an event listener to the feedback window to show the feedback button once window is closed
 * Prevents keystrokes from triggering events outside of the feedback window
 */
const setUpFeedbackWindow = () => {
    feedbackWindow.addEventListener('close', () => {
        feedbackButton.classList.remove('hidden')})

    feedbackWindow.addEventListener('keydown', (event) => {
        event.stopImmediatePropagation()
    })

    feedbackWindow.addEventListener('keyup', (event) => {
        event.stopImmediatePropagation()
    })
}
/**
 * Adds event listener to the feedback window X Button to close the window on click event
 */
const setUpExitButton = () => {
    exitButton.addEventListener('click', () => {
        feedbackWindow.close()
    })
}




setUpFeedbackButton()
setUpExitButton()
setUpFeedbackWindow()