const impsumGen = document.getElementsByClassName('ipsum-gen')[0]
const impsumText = document.getElementsByClassName('ipsum')[0]

/**
 * adds click event listener to show ipsum text
 */
const setupIpsumGen = () => {
    impsumGen.addEventListener('click', () => {
        impsumText.classList.toggle('hidden')
    })
}




setupIpsumGen() 
