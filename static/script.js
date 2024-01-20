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