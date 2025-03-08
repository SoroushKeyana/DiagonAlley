document.addEventListener("DOMContentLoaded", function () {
    const createPost = document.querySelector("#create-post");
    const createPostPopup = document.querySelector("#create-post-popup");
    const profileUpload = document.querySelector("#profile-picture-upload-button");
    const profileUploadForm = document.querySelector("#upload-picture");
    const editPost = document.querySelectorAll("#edit-button");
    const likeButton = document.querySelectorAll(".like-button");
    const commentButton = document.querySelectorAll(".comment-button");
    const deleteButtons = document.querySelectorAll(".delete-button");
    const following = document.querySelector("#following");
    const followers = document.querySelector("#followers");
    const profilePosts = document.querySelector("#profile-posts");
    const profilePostsButton = document.querySelector("#profile-posts-button");
    const profileFollowingButton = document.querySelector("#profile-following-button");
    const profileFollowersButton = document.querySelector("#profile-followers-button");
    const comment = document.querySelectorAll(".add-comment")
    const profile_buttons = document.querySelectorAll(".tab-button");
    

 function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    commentButton.forEach(button => {
        button.addEventListener("click", function () {
            const postId = this.getAttribute("data-post-id");
            const commentsContainer = document.querySelector(`#comments-${postId}`);

        if (commentsContainer.style.display === "block") {
            commentsContainer.style.display = "none";
        } else {
            commentsContainer.style.display = "block";
        }
            
        });
    });


    deleteButtons.forEach(button => {
        button.addEventListener("click", function () {
            const postId = this.getAttribute("data-post-id");
            const postElement = document.querySelector(`#post-${postId}`);
            
            fetch(`/delete/${postId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                }
            })
            .then(response => response.json()) 
            .then(data => {
                postElement.remove()
            });
        });
    });

    likeButton.forEach(button => {
        button.addEventListener("click", function () {
            const postId = this.getAttribute("data-post-id");
            const likeCount = document.querySelector(`#like-count-${postId}`);
            
            fetch(`/like/${postId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                }
            })
            .then(response => response.json()) 
            .then(data => {
                likeCount.innerText = data.likes;
                const heartIcon = document.createElement('i');
                heartIcon.className = data.liked ? 'fa-solid fa-heart colored-heart' : 'fa-regular fa-heart';
                this.innerHTML = '';
                this.appendChild(heartIcon);
            });
        });
    });


    comment.forEach(form => {
        form.addEventListener("submit", function(event) {
            event.preventDefault();

            let formData = new FormData(this);

            fetch(this.action, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }

                let newComment = document.createElement("div");
                newComment.classList.add("comment", "mt-2", "p-2", "d-flex");

                newComment.innerHTML = `
                    <img src="${data.profile_picture}" alt="Profile Picture" class="profile-picture picture-comment">
                    <div class="bg-primary rounded ml-3 p-2">
                        <h5 class="m-0 p-0">${data.user}</h5> 
                        <p class="m-0 p-0">${data.content}</p> 
                        <p class="m-0 p-0">${data.time_stamp}</p>
                    </div>
                `;

                let postComments = document.querySelector(`#post-${data.post_id} .comments`);
                const commentForm = postComments.querySelector(".add-comment");
                
                postComments.insertBefore(newComment, commentForm);

                this.querySelector("textarea").value = "";
            })

            .catch(error => console.error("Error:", error));
        });
    });


    editPost.forEach(button => { 
        button.addEventListener("click", function () {
            const postId = this.getAttribute("data-post-id");
            const textareaContent = document.querySelector(`#textarea-${postId}`).value;
            const postContent = document.querySelector(`#content-${postId}`);
            const modal = document.querySelector(`#edit-post-${postId}`);
            const removeImage = document.querySelector(`#remove-image-${postId}`)?.checked || false;
            const imageFileInput = document.querySelector(`#image-upload-${postId}`);
            
            const formData = new FormData();
            formData.append('content', textareaContent);
            formData.append('remove_image', removeImage);
            if (imageFileInput.files[0]) {
                formData.append('image', imageFileInput.files[0]);
            }

            fetch(`/edit/${postId}`, {
                method: "POST",
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            })
            .then(response => response.json())
            .then(result => {
                postContent.innerHTML = result.content;
                if (removeImage) {
                    const imageElements = document.querySelectorAll(`.post-image-${postId}`);
                    imageElements.forEach(imageElement => imageElement.remove());
                }
                
                if (result.image) {
                    const imageElements = document.querySelectorAll(`.post-image-${postId}`);
                    imageElements.forEach(imageElement => imageElement.remove());  

                    const imgContainer = document.querySelector(`#post-img-container-${postId}`);
                    const postContentContainer = document.querySelector(`.post-content-container-${postId}`)
                    
                    const imageElement = document.createElement('img');
                    imageElement.src = result.image;
                    imageElement.alt = "Post Image";
                    imageElement.classList.add('img-thumbnail', `post-image-${postId}`);
                    postContentContainer.appendChild(imageElement); 
                    imgContainer.appendChild(imageElement.cloneNode(true));
                    
                }
                $(modal).modal('hide'); 
            
            });
        });
    });     


    if (createPost && createPostPopup) {
        const textarea = createPostPopup.querySelector("textarea"); 
        createPost.addEventListener("click", function () {
            createPostPopup.style.display = "flex";
            if(textarea){
            textarea.focus();
            }
        });

        createPostPopup.addEventListener("click", function (event) {
            if (event.target === this) {
                this.style.display = "none";
            }
        });
    }

    if (profileUpload && profileUploadForm) {
        profileUpload.addEventListener("click", function () {
            profileUploadForm.style.display = "flex"; 
        });

        profileUploadForm.addEventListener("click", function (event) {
            if (event.target === this) {
                this.style.display = "none";
            }
        });
    }

    if (profileFollowingButton) {
    profileFollowingButton.addEventListener("click", function() {
        followers.style.display="none"
        following.style.display="block"
        profilePosts.style.display="none"
    })
    }

    if (profileFollowersButton) {
    profileFollowersButton.addEventListener("click", function() {
        followers.style.display="block"
        following.style.display="none"
        profilePosts.style.display="none"
    })
    }

    if (profilePostsButton) {
    profilePostsButton.addEventListener("click", function() {
        followers.style.display="none"
        following.style.display="none"
        profilePosts.style.display="block"
    })
    }
    
    profile_buttons.forEach(button => {
        button.addEventListener("click", function () {
            profile_buttons.forEach(btn => btn.classList.remove("active"));
                this.classList.add("active");
        });
    });

});


