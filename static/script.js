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
        var postContainer = event.target.closest('.box');
        var postId = postContainer.dataset.postId;

        fetch(`/requests/${postId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: 'rejected' })
        })
        .then(response => response.json())
        .then(data => {
            postContainer.classList.add('fadeOut');

            setTimeout(function() {
                postContainer.remove();
                console.log('Post removed!');
            }, 500);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred.');
        });
    }
});