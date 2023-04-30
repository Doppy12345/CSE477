const sound = {65:"http://carolinegabriel.com/demo/js-keyboard/sounds/040.wav",
                87:"http://carolinegabriel.com/demo/js-keyboard/sounds/041.wav",
                83:"http://carolinegabriel.com/demo/js-keyboard/sounds/042.wav",
                69:"http://carolinegabriel.com/demo/js-keyboard/sounds/043.wav",
                68:"http://carolinegabriel.com/demo/js-keyboard/sounds/044.wav",
                70:"http://carolinegabriel.com/demo/js-keyboard/sounds/045.wav",
                84:"http://carolinegabriel.com/demo/js-keyboard/sounds/046.wav",
                71:"http://carolinegabriel.com/demo/js-keyboard/sounds/047.wav",
                89:"http://carolinegabriel.com/demo/js-keyboard/sounds/048.wav",
                72:"http://carolinegabriel.com/demo/js-keyboard/sounds/049.wav",
                85:"http://carolinegabriel.com/demo/js-keyboard/sounds/050.wav",
                74:"http://carolinegabriel.com/demo/js-keyboard/sounds/051.wav",
                75:"http://carolinegabriel.com/demo/js-keyboard/sounds/052.wav",
                79:"http://carolinegabriel.com/demo/js-keyboard/sounds/053.wav",
                76:"http://carolinegabriel.com/demo/js-keyboard/sounds/054.wav",
                80:"http://carolinegabriel.com/demo/js-keyboard/sounds/055.wav",
                59:"http://carolinegabriel.com/demo/js-keyboard/sounds/056.wav"};


/** 
* Class representing a Piano Key Object that contains the html to the key and its sound
*/
class PianoKey{
    /**
     * @param  {HTMLElement} html the html element visually respresenting this key
     * @param  {HTMLAudioElement} sound the sound to play when this key is triggered
     */
    constructor(html, sound){
        this.html = html;
        this.sound = sound;
        this.note = new Audio(sound)
    }
    /**
     * Plays the note corresponding to the current Piano Key
     */
    playNote(){
        this.note.pause()
        this.note.currentTime = 0
        this.note.play()
    }

}

/** 
* Class representing a stack using a string as the underlying data type
*/
class StringStack{
    /**
     * @param  {String} pattern the pattern contrast the current string stack with
     * @param  {Number} size the size of the string stack i.e. how many characters is the string
     */
    constructor(pattern, size){
        this.size = size
        this.pattern = pattern
        this.string = ''
    }
    /**
     * Pushes a single character to the stack
     * @param  {String} val the character to push
     */
    push(val){
        if (this.string.length === this.size){
            this.string = this.string.substr(1)
        }
       
        this.string += val
    }
    /**
     * Checks if the current stack matches the pattern
     */
    isMatch(){
        return this.string == this.pattern
    }

}


const pianoKeys = {}
const lastPlayed = new StringStack('weseeyou', 8)



/**
 * Setup event listeners and creates a PianoKey for each of the html keys 
 */
function setupPianoAudio(){
    const Keys = Array.from(document.getElementsByClassName('key'))
    Keys.forEach(key => {
        let currPianoKey = new PianoKey(key, sound[key.dataset.keycode])
        pianoKeys[key.dataset.keycode] = currPianoKey
    });
}

/**
 * Event handler for when a keyboard key is pressed down
 * @param  {KeyboardEvent} event the Keyboard event captured by the event listener
 */
function handleKeyDown(event){
    try {
        let pressedKey = pianoKeys[event.keyCode]
        pressedKey.html.classList.add('pressed')
        pressedKey.playNote()
        lastPlayed.push(event.key)
    } catch (error) {
        
    }
}

/**
 * Event handler for when a keyboard key is released
 * @param  {KeyboardEvent} event the Keyboard event captured by the event listener
 */
function handleKeyUp(event){
    try{
        let pressedKey = pianoKeys[event.keyCode]
        pressedKey.html.classList.remove('pressed')
        if (lastPlayed.isMatch()){
            revealTheOldOne()
        }
    }
    catch(error){
        
    }
}

/**
 * Setup and add event handler and listeners to the window
 */
function setUpKeypressListeners(){    
    window.addEventListener('keydown', handleKeyDown)
    window.addEventListener('keyup', handleKeyUp)
}
/**
 * removes event listeners to the window
 */
function removeKeypressListeners(){
    window.removeEventListener('keydown', handleKeyDown)
    window.removeEventListener('keyup', handleKeyUp)
}
/**
 * replaces the Piano with a picture of the Great Old One
 */
function revealTheOldOne(){
    const Piano = document.getElementById('piano')
    const revealSound = new Audio('https://orangefreesounds.com/wp-content/uploads/2020/09/Creepy-piano-sound-effect.mp3?_=1')
    removeKeypressListeners()
    revealSound.play()

    Piano.querySelector('p').innerText = 'I have awoken'
    setTimeout(() => Piano.classList.add('awoken'), 20)
    Piano.querySelector('img').classList.remove('hidden')


}

/**
 * The main function
 */
function main(){
    setupPianoAudio()
    setUpKeypressListeners()
}

main()