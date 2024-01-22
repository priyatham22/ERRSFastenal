function unliked(post_id){
    fetch('/likefunction', ajaxcall(false,post_id))
    .then(response => response.json())
    .then(data => {
        console.log("disliked")
        console.log(data);
        location.reload();
    })
    .catch(error => console.error('Error:', error));
}

function liked(posts_id){
    fetch('/likefunction', ajaxcall(true,posts_id))
    .then(response => response.json())
    .then(data => {
        console.log("liked")
        console.log(data);
        location.reload();
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