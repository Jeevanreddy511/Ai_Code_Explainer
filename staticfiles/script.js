var currentChat = null;
// var previousCode = "";
// var codeChanged = true;

// console.log("{{chats|escapejs}}");
// var chats = JSON.parse("{{ chats|escapsejs }}");
console.log(chats);

document.getElementById("code-input").addEventListener("keydown", function(event) {
    if (event.key === "Tab") {
        event.preventDefault(); 
        // console.log("this is invoked");
        let start = this.selectionStart;
        let end = this.selectionEnd;
        
        // Insert tab character at cursor position
        this.value = this.value.substring(0, start) + "\ \ \ \ " + this.value.substring(end);
        
        // Move cursor after the inserted tab
        this.selectionStart = this.selectionEnd = start + 4;
    }
    // console.log("that is invoked");
});

document.getElementById("get-preview").addEventListener("click", async function() {
    let currentCode = document.getElementById("code-input").value.trim();
    // if (currentCode !== previousCode) {
    //     codeChanged = true; 
    //     previousCode = currentCode;
    // } else {
    //     codeChanged = false;
    // }
    // console.log(codeChanged);
    await get_preview("");
});

document.getElementById("ibbuu").addEventListener("click", function() {
    let currentCode = document.getElementById("code-input").value.trim();
    // if (currentCode != previousCode) {
    //     codeChanged = true;
    //     previousCode = currentCode;
    // } else {
    //     codeChanged = false;
    // }
    // // console.log(codeChanged);
    sendMessage();
});

document.getElementById("message-input").addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        if (!event.shiftKey) {  // If Enter is pressed without Shift
            event.preventDefault();  // Prevent new line
            // console.log(codeChanged);
            // sendMessage();  // Call send message function
            document.getElementById("ibbuu").click();
        }
        // If Shift + Enter is pressed, do nothing (default behavior)
    }
});

function createPanelBtn(sidePanel, chat, newChatName) {
    let chatBtn = document.createElement("button");
    chatBtn.className = "sidebar_button";
    if (chat.name.length < 20)
        chatBtn.textContent = chat.name;
    else{
        chatBtn.textContent = chat.name.substring(0,17)+"...";
        chatBtn.alt = chat.name;
    }
    chatBtn.onclick = () => change_chat(chat);
    if(newChatName && chat.id == newChatName.id)
        chatBtn.classList.add("active");
    else
        chatBtn.classList.add("inactive");

    chatBtn.style.display = "flex";
    chatBtn.style.alignItems = "center";
    chatBtn.style.justifyContent = "space-between"; 
    chatBtn.style.padding = "8px 12px"; 

    let editBtn = document.createElement("span");
    editBtn.textContent = "✏️";  // Pencil icon
    editBtn.className = "edit_button";
    editBtn.title = "Edit name";
    editBtn.onclick = (event) => {
        event.stopPropagation();  // Prevents chat opening on edit
        showEditNamePopup(chat);  // Call edit function
    };

    let deleteBtn = document.createElement("span");
    deleteBtn.textContent = "❌";  // Cross icon
    deleteBtn.className = "delete_button";
    deleteBtn.onclick = (event) => {
        event.stopPropagation();  // Prevents chat opening on delete
        destroy(chat);  // Call delete function
    };

    chatBtn.appendChild(editBtn);
    chatBtn.appendChild(deleteBtn);  
    sidePanel.appendChild(chatBtn);
}

function populateSidePanel(newChatName) {
    // console.log(chats);

    let sidePanel = document.getElementById("side_panel");
    sidePanel.innerHTML = ""; // Clear existing buttons

    let newChatBtn = document.createElement("button");
    newChatBtn.className = "sidebar_button";
    newChatBtn.textContent = "Create New Chat";
    newChatBtn.onclick = () => change_chat(null);
    if(!newChatName)
        newChatBtn.classList.add("active");
    else
        newChatBtn.classList.add("inactive");
    sidePanel.appendChild(newChatBtn);

    // Create chat buttons dynamically
    chats.forEach(chat => {
        if (chat.name){
            // console.log(name);
            createPanelBtn(sidePanel, chat, newChatName);
        }
    });
}

async function get_preview(messageText) {
    let code = document.getElementById("code-input").value.trim();
    if (code) {
        if (!currentChat){
            currentChat = await getUnique(messageText);  // ✅ Wait for `getUnique()` to finish
            chats.push(currentChat);
            populateSidePanel(currentChat);
            // console.log("This is get_preview new chat"+currentChat);
        }
        // console.log("This is get_preview"+currentChat);
        
        var url = "./tree_parser";
        // console.log("this is preview");
        return fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code: code, chat_id: currentChat.id })
        })
        .then(response => response.text())
        .then(response => print_tree(response))
        .catch(error => console.log(error));
    }
}

function print_tree(code) {
    // if (code) {
        let tree_element = document.getElementById('preview');
        tree_element.innerHTML = "<pre style='font-size:14px;'>"+code+"</pre>";
        // console.log(code);
    // }
}

function createMessage(message){
    let messageContainer = document.getElementById("convo-container");
    let botMessageElement = document.createElement("p");
    botMessageElement.classList.add("message", "bot-message");
    botMessageElement.innerHTML = "<pre style='word-wrap: break-word; white-space: pre-wrap;'>"+message+"</pre>";
    messageContainer.appendChild(botMessageElement);
    return botMessageElement;
}

function createQuery(messageText){
    let messageContainer = document.getElementById("convo-container");
    let messageHolder = document.createElement("div");
    messageHolder.classList.add("message-wrapper");

    let newMessage = document.createElement('p');
    newMessage.classList.add("message", "user-message");
    newMessage.textContent = messageText;
    
    messageHolder.appendChild(newMessage);
    messageContainer.appendChild(messageHolder);
}

function fillText(data){
    let messageContainer = document.getElementById("convo-container");
    messageContainer.replaceChildren();
    code = data.code;
    tree = data.tree;
    coding_section = document.getElementById("code-input");
    coding_section.value = code;
    print_tree(tree);
    messages = data.messages 
    for (i in messages) {
        // console.log(messages[i].query);
        createQuery(messages[i].query);
        let botMessageElement = createMessage(messages[i].reply);
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }
}

function change_chat(clicked_chat) {
    if (clicked_chat){
        currentChat = clicked_chat;
        console.log(currentChat);

        var url = "?chat_id="+encodeURIComponent(currentChat.id);
        fetch(url)
        .then(response => response.json())
        .then(response => fillText(response))
        .catch(error => console.log(error));

        previousCode = "";
        populateSidePanel(currentChat);
    } else {
        window.location.href = "./";
        // console.log(chats);
    }
}

async function sendMessage() {
    let inputField = document.getElementById("message-input");
    let messageText = inputField.value.trim();

    if (messageText != "") { 
        let messageContainer = document.getElementById("convo-container");
        createQuery(messageText);

        inputField.value = "";
        
        let botMessageElement = createMessage("Thinking...");
        messageContainer.scrollTop = messageContainer.scrollHeight;

        await get_preview(messageText);
        
        // console.log("This is get_preview over "+currentChat);
        if (!currentChat){
            currentChat = await getUnique(messageText);  // ✅ Wait for `getUnique()` to finish
            chats.push(currentChat);
            populateSidePanel(currentChat);
            console.log("This is sendMessage new chat "+currentChat);
        }       
        console.log("This is sendMessage "+currentChat.id);
        fetch('./', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: messageText, chat_id: currentChat.id})
        })
        .then(response => response.body.getReader()) 
        .then(reader => printResponse(reader, botMessageElement))
        .catch(error => console.log(error));
        // console.log("This is sendMessage completed "+currentChat);
    }
}

function printResponse(reader, botMessageElement) {
    const decoder = new TextDecoder();
    botMessageElement.innerHTML = "";
    let preElement = document.createElement("pre");
    preElement.style.wordBreak = "break-word";
    preElement.style.whiteSpace = "pre-wrap";
    botMessageElement.appendChild(preElement);

    function readChunk() {
        reader.read().then(({ done, value }) => {
            if (done) return; // Stop when done
            
            let textChunk = decoder.decode(value);
            preElement.textContent += textChunk; 
            
            document.getElementById("convo-container").scrollTop = document.getElementById("convo-container").scrollHeight;
            readChunk(); 
        });
    }

    readChunk();
}

function w3_open() {
    let sidebar = document.getElementById("mySidebar");

    if (sidebar) {
        sidebar.style.width = "250px";
        sidebar.style.display = "block";
    } else {
        console.log("Element with ID 'mySidebar' not found.");
    }
}

function w3_close() {
    let sidebar = document.getElementById("mySidebar");

    if (sidebar) {
        sidebar.style.display = "none";
    } else {
        console.log("Element with ID 'mySidebar' not found.");
    }
}

async function getUnique(messageText) {
    const url = './unique_chat?name=' + encodeURIComponent(messageText);
    const response = await fetch(url);
    // console.log("getUnique"+ response);
    return await response.json();
}

function destroy(chat) {
    const url = "./delete_chat?chat_id="+chat.id;
    console.log(url)
    fetch(url)
    .then(response => response.text())
    .then(response => {
        let index = chats.indexOf(chat);
        chats.splice(index, 1);
    })
    .then(response => change_chat(null))
    .catch(error => console.error("Error deleting chat:", error));
}

populateSidePanel(currentChat);

function openTab(evt, tabName) {
    let i, tabcontent, tablinks;
    
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";

    if (tabName == "CodeTab") 
        document.getElementById("get-preview").style.display = "none";
    else
        document.getElementById("get-preview").style.display = "block";
}

// Open the default tab on page load
document.getElementById("defaultTab").click();

function showEditNamePopup(chat) {
    // Create popup container
    const popup = document.createElement("div");
    popup.className = "edit-name-popup";
    
    // Create popup title
    const title = document.createElement("h3");
    title.textContent = "Edit Chat Name";
    title.className = "popup-title";
    
    // Create input field 
    const input = document.createElement("input");
    input.type = "text";
    input.value = chat.name;
    input.className = "popup-input";
    
    // Create buttons container
    const btnContainer = document.createElement("div");
    btnContainer.className = "popup-buttons";
    
    // Create cancel button
    const cancelBtn = document.createElement("button");
    cancelBtn.textContent = "Cancel";
    cancelBtn.className = "popup-button cancel-button";
    
    // Create save button
    const saveBtn = document.createElement("button");
    saveBtn.textContent = "Save";
    saveBtn.className = "popup-button save-button";
    
    // Create overlay
    const overlay = document.createElement("div");
    overlay.className = "popup-overlay";
    
    // Add event listeners
    cancelBtn.onclick = () => {
        document.body.removeChild(popup);
        document.body.removeChild(overlay);
    };
    
    saveBtn.onclick = () => {
        const newName = input.value.trim();
        if (newName && newName !== chat.name) {
            const url = "./change_name";
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ new_name: newName, chat_id: chat.id})
            });

            chat.name = newName;
            populateSidePanel(currentChat);
        }
        
        document.body.removeChild(popup);
        document.body.removeChild(overlay);
    };
    
    // Assemble popup
    popup.appendChild(title);
    popup.appendChild(input);
    btnContainer.appendChild(cancelBtn);
    btnContainer.appendChild(saveBtn);
    popup.appendChild(btnContainer);
    
    // Add to document
    document.body.appendChild(overlay);
    document.body.appendChild(popup);
    
    // Focus the input
    input.focus();
    
    // Allow Enter key to save
    input.addEventListener("keyup", function(event) {
        if (event.key === "Enter") {
            saveBtn.click();
        } else if (event.key === "Escape") {
            cancelBtn.click();
        }
    });
}