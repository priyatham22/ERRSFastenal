function changeOnclickFunction(newOnclickFunction,parameter,obj) {
    obj.onclick = function() {
        newOnclickFunction(parameter);
    };
}

function unliked(posts_id){
    fetch('/likefunction', ajaxcall(false,posts_id))
    .then(response => response.json())
    .then(data => {

        let value=document.getElementById(posts_id+"points");
        console.log("disliked")
        value.innerHTML=parseInt(value.innerHTML)-5;
        let button=document.getElementById(posts_id+"button");
        button.classList.remove("liked");
        button.classList.add("unliked");
        changeOnclickFunction(liked,posts_id,button);
    })
    .catch(error => console.error('Error:', error));
}

function liked(posts_id){
    fetch('/likefunction', ajaxcall(true,posts_id))
    .then(response => response.json())
    .then(data => {
        let value=document.getElementById(posts_id+"points");
        console.log("liked")
        value.innerHTML=parseInt(value.innerHTML)+5;
        let button=document.getElementById(posts_id+"button");
        button.classList.remove("unliked");
        button.classList.add("liked");
        changeOnclickFunction(unliked,posts_id,button);
    })
    .catch(error => console.error('Error:', error));
}

function ajaxcall(liked,posts_id){
    return{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            'post_id': posts_id,
            'liked': liked
        }),
    }
}

document.addEventListener('click', function(event) {
    if (event.target.classList.contains('declineBtn')) {
        var requestContainer = event.target.closest('.box');
        var requestID = requestContainer.dataset.postId;

        fetch(`/requests/${requestID}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: 'rejected' })
        })
        .then(response => response.json())
        .then(data => {
            requestContainer.classList.add('fadeOut');

            setTimeout(function() {
                requestContainer.remove();
                console.log('Post removed!');

                if (document.querySelectorAll('.box').length === 0) {
                    var noRequestsDiv = document.createElement('div');
                    noRequestsDiv.classList.add('no-requests-message');
                    noRequestsDiv.innerHTML = '<h1><b>There are no new requests</b></h1>';
                    
                    document.querySelector('.manager').innerHTML = '';
                    document.querySelector('.manager').appendChild(noRequestsDiv);
                }
            }, 500);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred.');
        });
    }
});
