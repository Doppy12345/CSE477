const chatForm = document.getElementById("chat-form")
const newTaskButton = document.getElementsByClassName('new-task')[0]
const newTaskWindow = document.getElementsByClassName('new-task-modal')[0]
const newTaskForm = document.getElementById('new-task-form')
const exitButton = document.getElementsByClassName('exit-button')[0]
const todoList = document.getElementsByClassName('todo')[0]
const doingList = document.getElementsByClassName('doing')[0]
const completeList = document.getElementsByClassName('complete')[0]

let tasks = []

let socket = io.connect('https://' + document.domain + ':' + location.port + '/chat');
const currUser = chatForm.dataset.current_user


// Emits a message when ever the chat message form is submitted
chatForm.addEventListener("submit", e => {
    e.preventDefault()
    const formData = new FormData(e.target)
    const data = Object.fromEntries(formData.entries())
    socket.emit('sendMessage', data, chatForm.dataset.board_id)
    chatForm.reset()
})
/**
 * utility function to remove all child elements from an HTML element
 * @param  {HTMLElement} parent
 */
const removeAllChildNodes = (parent) => {
    while (parent.firstChild){
        parent.removeChild(parent.firstChild)
    }
}

// Sets up all the socket event listeners on page load
$(document).ready(function(){
    
    
    socket.on('connect', function() {
        socket.emit('joinChat', {} ,chatForm.dataset.board_id);
    });
    
    socket.on('status', (data) => createMessage(data)); 
    
    socket.on('transfer', (data) => announceTransfer(data))

    socket.on('task_update', () => populateTasks())

    socket.on('task_edit', (taskData) => reserveTask(taskData))
    
});

// emits leave chatroom event before user leaves the page
$(window).bind('beforeunload', () => {
    socket.emit('leaveChat', chatForm.dataset.board_id)
})


/**
 * creates a message in the chat based on message data received from socket event
 * @param  {{message: String, user: String}} data
 * @param  {Boolean} announcement=false whether or not the message should be treated as an announcement 
 */
const createMessage = (data, announcement=false) => {  
    let tag  = document.createElement("p");
    tag.classList.add(`${data['user'] === currUser ? 'mymsg' : 'usermsg'}`)
    let text = document
        .createTextNode(constructMessage(data['message'], data['user'], announcement));
    let element = document.getElementById("chat");
    tag.appendChild(text);
    element.appendChild(tag);
    $('#chat').scrollTop($('#chat')[0].scrollHeight);

}
/**
 * Create a message in the chat when a user enters  or leaves
 * @param  {{message: String, user: String}} data
 */
const announceTransfer = (data) => {
    createMessage(data, true)
}
/**
 * @param  {String} msg the text content of the message to construct
 * @param  {String} user the user sending the message
 * @param  {Boolean} isAnnouncement=false whether or not the message should be treated as an announcement
 * @return {String} the complete message
 */
const constructMessage = (msg, user, isAnnouncement=false) => {
    let finalMsg = ''
    if (!isAnnouncement && !(user === currUser))
        finalMsg += `${user}: `
    return finalMsg + msg
}

// Sets up listener for new task form submit that creates a new task in the database
newTaskForm.addEventListener('submit', (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    const data = Object.fromEntries(formData.entries())
    data['state'] = 0
    data['board_id'] = chatForm.dataset.board_id
    createTask(data)
    newTaskForm.reset()
    newTaskWindow.close()
})

/**
 * Sets up new task modal window
 */
const setUpNewTaskWindow = () => {
    newTaskWindow.addEventListener('keydown', (event) => {
        event.stopImmediatePropagation()
    })
    newTaskWindow.addEventListener('keyup', (event) => {
        event.stopImmediatePropagation()
    })

}
/**
 * sets up exit button to close the modal
 */
const setUpExitButton = () => {
    exitButton.addEventListener('click',  () => {
        newTaskWindow.close()
    })
}
/**
 * sets up the new task button to show new task modal form
 */
const setUpNewTaskButton = () => {
    newTaskButton.addEventListener('click', () => {
        newTaskWindow.showModal()
    })
}
/**
 * Pings server for updated task list and populates them in the UI
 */
const populateTasks = () => {
    jQuery.ajax({
        url: `/board/${chatForm.dataset.board_id}/tasks`,
        type: "GET",
        /**
         * @param  {Array<{task_id: Number, title: String, description: String, state: Number}>} taskList
         */
        success:function(taskList){
            tasks = JSON.parse(taskList);
            refreshTasks(todoList, tasks, 0)
            refreshTasks(doingList, tasks, 1)
            refreshTasks(completeList, tasks, 2)
            
                
            }
    });
}
/**
 * Updates a task on the server and emits a board update event for other clients
 * @param  {{task_id: Number, title: String, description: String, state: Number}} taskData
 */
const updateTask = (taskData) => {
    jQuery.ajax({
        url: "/updateTask",
        data: taskData,
        type: "POST",
        success: (returned_data) => {
            if ('success' in JSON.parse(returned_data)){
                socket.emit('boardUpdate', chatForm.dataset.board_id)
            }
        }
    });
}
/**
 * Clears the task lists for the three lists and refills them with updated information
 * @param  {HTMLDivElement} tasklist
 * @param  {Array<{task_id: Number, title: String, description: String, state: Number}>} tasks - list of tasks objects containing the task data for the given board
 * @param  {Number} state the statre of a task 0 = todo, 1 = doing, 2 = complete 
 */
const refreshTasks = (tasklist, tasks, state) => {
    removeAllChildNodes(tasklist)
    tasklist.append(...createTaskElements(tasks.filter(task => task.state === state)))
    if(state === 0) tasklist.appendChild(newTaskButton)
}
/**
 * Creates a new task on the server and emits a board update event for other clients
 * @param  {{title: String, description: String, state: Number}} taskData task object to create on the server
 */
const createTask = (taskData) => {
    jQuery.ajax({
        url: `/board/${chatForm.dataset.board_id}/tasks`,
        data: taskData,
        type: "POST",
        success:function(returned_data){
            if ('success' in JSON.parse(returned_data)){
                socket.emit('boardUpdate', chatForm.dataset.board_id)
            }          
        }
    });
}


/**
 * Creates an HTMl element representation for the given list of tasks and sets up
 * event listeners for UI functionality
 * @param  {Array<{task_id: Number, title: String, description: String, state: Number}>} tasks list of task objects to create elements for
 * @return {Array<HTMLElement>} the list of all the html elements representing the tasks
 */
const createTaskElements = (tasks) => {
    let taskElements = []
    tasks.forEach((task) => {
        

        const currElem = document.createElement('div')
        currElem.classList.add('task')
        currElem.dataset['id'] = task.task_id
        const heading = document.createElement('section')
        heading.classList.add('heading')
        const title = document.createElement('span')
        title.classList.add('title')
        title.textContent = task.title
        heading.append(title)
        
        const description = document.createElement('p')
        description.classList.add('description')
        description.textContent = task.description
        
        const controls = document.createElement('div')
        controls.classList.add('controls')

        if (task.state !== 2) {
            const submit = document.createElement('button')
            submit.classList.add('submit')
            submit.textContent = 'Submit'
    
            submit.addEventListener('click', () => {
                task.state += 1
                updateTask(task)
            })

    
            const edit = document.createElement('button')
            edit.classList.add('edit')
            edit.textContent = 'Edit'
    
            /**
             * Event handler for saving changes to a tasks description
             * @param  {Event} event keypress event
             */
            const handleSaveEdit = (event) => {
                if (event.key === "Enter"){
                    event.target.removeEventListener('keypress', handleSaveEdit)
                    event.target.contentEditable = false
                    event.target.blur()
                    currElem.classList.remove('editing')
                    task.description = event.target.textContent
                    socket.emit('releaseTask', {'editor': currUser, 'task': task.task_id, 'task_description': task.description})
                    updateTask(task)
                }
            }
    
            edit.addEventListener('click', () => {
                currElem.classList.add('editing')
                edit.classList.add('hide')
                edit.disabled = true
                description.contentEditable = true
                description.focus()
                socket.emit('lockTask', {'editor': currUser, 'task': task.task_id}, chatForm.dataset.board_id)
                description.addEventListener('keypress', handleSaveEdit)
            })

            controls.append(edit, submit)
        }


        currElem.append(heading, description, controls)
        taskElements.push(currElem)
    })
    return taskElements
}
/**
 * Prevents changes from being made to other tasks for clients that are not currently making an edit
 * @param  {{editor: String, task: Number, }} taskData
 */
const reserveTask = (taskData) => {
    if (taskData.editor === currUser) return
    const taskToLock = document.querySelector(`[data-id="${taskData.task}"]`)
    const allTasks = Array.from(document.querySelectorAll('[data-id]'))
    allTasks.forEach((task) => {
        if(task.lastElementChild.firstElementChild !== null){
            task.lastElementChild.firstElementChild.classList.add('hide')
            task.lastElementChild.lastElementChild.classList.add('hide')
            task.lastElementChild.firstElementChild.disabled = true
            task.lastElementChild.lastElementChild.disabled = true
        }
    })
    const taskChildren = Array.from(taskToLock.children)
    const taskDescription = taskChildren[1]
    taskDescription.textContent = `${taskData.editor} is making changes...`
    taskToLock.classList.add('reserved')
   
}


setUpNewTaskWindow()
setUpExitButton()
setUpNewTaskButton()
populateTasks()