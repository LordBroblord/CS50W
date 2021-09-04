document.addEventListener('DOMContentLoaded', function() {

    // Use buttons to toggle between views
    document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
    document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
    document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
    document.querySelector('#compose').addEventListener('click', compose_email);

    // By default, load the inbox
    load_mailbox('inbox');

    // Add functionality to new mail form
    document.querySelector('#compose-form').onsubmit = function () {
        fetch('/emails', {
            method: 'POST',
            body: JSON.stringify({
                recipients: document.querySelector('#compose-recipients').value,
                subject: document.querySelector('#compose-subject').value,
                body: document.querySelector('#compose-body').value,
            })
        })
        .then(load_mailbox('sent'))
        return false;
    }

});



function compose_email() {

    // Show compose view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#read-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';

    // Clear out composition fields
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';
}



function load_mailbox(mailbox) {

    // Show the mailbox and hide other views
    document.querySelector('#emails-view').style.display = 'block';
    document.querySelector('#read-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';

    // Show the mailbox name (capitalizing first character)
    document.querySelector('#emails-view').innerHTML =
        `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>
        <div id="emails-list"></div>`;

    // fetch emails from correct mailbox and show them in a list
    fetch(`/emails/${mailbox}`)
        .then(response => response.json())
        .then(emails => {
            emails.forEach(email => email_preview(email, mailbox));
        });

}



function email_preview(email, mailbox) {

    // Create the element to show
    const element = document.createElement('div');
    element.className = 'email-preview';

    // Fill the element depending on which mailbox is selected
    if (mailbox === 'inbox' || mailbox === 'archive') {

        // Set a flag (true -> put in archive, false -> extract from archive) and a message for the archive/unarchive button
        archive_flag = true;
        archive_message = "Archive";
        if (mailbox === 'archive') { archive_flag = false; archive_message = "Unarchive"; }         // Only in archive mailbox, switch flag to false

        // Set the HTML of the element
        element.innerHTML =
        `<h5>${email.subject}</h5>
        <div>${email.sender}</div>
        <div>${email.timestamp}</div>`;
        element.addEventListener('click', () => { show_email(email) });

        // Create button
        const archive_button = document.createElement("button");
        archive_button.className = "archive-button";
        archive_button.innerHTML = archive_message;
        archive_button.onclick = function () { archive_email(email, archive_flag) };
        element.append(archive_button);
    }

    if (mailbox === 'sent') {
        element.innerHTML =
        `<h5>${email.subject}</h5>
        <div>${email.recipients}</div>
        <div>${email.timestamp}</div>`;
        element.addEventListener('click', () => { show_email(email) });
    }

    // Add style
    if (email.read === false) { element.style.background = 'white' }
    else { element.style.background = '#e6e6e6' }

    // Add to page
    document.querySelector('#emails-list').append(element);
}



function show_email(email) {

    // Show the mail and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#read-view').style.display = 'block';
    document.querySelector('#compose-view').style.display = 'none';

    // Set the content of the page
    document.querySelector('#read-view').innerHTML =
        `<div class="email">
        <button class="btn btn-sm btn-outline-primary" id="reply-button">Reply</button>
        <h4 class="email-subject">${email.subject}</h4>
        <div class="email-address">From: ${email.sender}</div>
        <div class="email-address">To: ${email.recipients}</div><hr>
        <div class="email-body">${email.body}</div>
        <div class="email-timestamp">${email.timestamp}</div>
        </div>`;

    document.querySelector('#reply-button').addEventListener('click', () => reply_email(email));

    // Mark the email as read
    fetch(`/emails/${email.id}`, {
        method: 'PUT',
        body: JSON.stringify({
            read: true
        })
    })
}



function archive_email(email, flag) {
    event.stopPropagation();            // prevents the button from triggering the clickable div
    fetch(`/emails/${email.id}`, {
        method: 'PUT',
        body: JSON.stringify({
            archived: flag
        })
    })
    .then(load_mailbox('inbox'));
}



function reply_email(email) {
    compose_email();

    // Pre fill form
    document.querySelector('#compose-recipients').value = email.sender;
    if (email.subject.startsWith("Re: ")) { document.querySelector('#compose-subject').value = email.subject; }
    else { document.querySelector('#compose-subject').value = `Re: ${email.subject}`; }
    document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote:\n${email.body}`;
}