$(document).ready(function() {

    $('.followButton').on('click', function() {
        $button = $(this);
        var blog_id = $(this).attr('blog_id');

        req = $.ajax({
            url : '/follow',
            type : 'POST',
            data : { id : blog_id }
        });

        req.done(function(data) {
            if( $button.hasClass('following')){
          
                $button.removeClass('following');
                $button.removeClass('unfollow');
                $button.text('Follow');
            } else {
                
                $button.addClass('following');
                $button.text('Unfollow');
            }
        });
    

    });

});

$(document).ready(function() {

    $('.unfollowButton').on('click', function() {
    
        $button = $(this);
        var blog_id = $(this).attr('blog_id');

        req = $.ajax({
            url : '/follow',
            type : 'POST',
            data : { id : blog_id }
        });

        req.done(function(data) {
            if( $button.hasClass('unfollowed')){
          
                $button.removeClass('unfollowed');
                $button.removeClass('follow');
                $button.text('Follow');
            } else {
                
                $button.addClass('unfollowed');
                $button.text('Follow');
            }
        });
    

    });

});

$(document).ready(function() {

    $('.delete_Button').on('click', function() {
        $button = $(this);
        var post_id = $(this).attr('post_id');
    if(confirm("Are you sure you want to delete this?")){
        req = $.ajax({
            url : '/delete_post',
            type : 'POST',
            data : { id : post_id }
        });


        req.done(function(data) {

            $('#rem_post'+post_id).fadeOut(1000);

        });
    }
    else{
        return false;
    }


    });

});

$(document).ready(function() {

    $('.likeButton').on('click', function() {
        $button = $(this);
        var post_id = $(this).attr('post_id');

        req = $.ajax({
            url : '/like',
            type : 'POST',
            data : { id : post_id }
        });

        req.done(function(data) {
            if( $button.hasClass('like')){
          
                $button.removeClass('like');
                $button.removeClass('unlike');
                $button.text('Like');
            } else {
                
                $button.addClass('like');
                $button.text('Unlike');
            }
        });
    

    });

});

$(document).ready(function() {

    $('.unlikeButton').on('click', function() {
    
        $button = $(this);
        var post_id = $(this).attr('post_id');

        req = $.ajax({
            url : '/like',
            type : 'POST',
            data : { id : post_id }
        });

        req.done(function(data) {
            if( $button.hasClass('unlike')){
          
                $button.removeClass('unlike');
                $button.removeClass('like');
                $button.text('Like');
            } else {
                
                $button.addClass('unlike');
                $button.text('Unlike');
            }
        });
    

    });

});
