# Signup{
    {{Domain}}/App/signup/
    POST
    
    input(string):
        npass,
        nemail,
        ndispn,
    
    output(JSON):
        Status,
}

# Login{
    {{Domain}}/App/login/
    POST
    
    input(string):
        email,
        npass,
    
    output(JSON):
        Status,
        Token (optional),
}

# Check Mail Availability{
    {{Domain}}/App/check/mail/
    POST

    input(string):
        email,

    output(JSON):
        Status,
}

# Forget PassWord{
    {{Domain}}/App/user/profile/ForgetPass/
    POST

    input(string):
        email,

    output(JSON):
        Status,
}


# Check Forget PassWord Code{
    {{Domain}}/App/check/ForgetCode/
    POST

    input(string):
        email,
        code,

    output(JSON):
        Status,
}


# resend veriffication Mail{
    {{Domain}}/App/user/profile/reactivate/
    POST

    input(string):
        email,

    output(JSON):
        Status,
}

##GET

# Get Member Profile{
    {{Domain}}/App/user/profile/member/
    
    input(string):
        postid,
        
    output(JSON):
        propic,
        Email,
        dispun,
        AccessLevel,
        Groups[
            Name,
        ]        
}


# Get Personal Profile{
    {{Domain}}/App/user/profile/get/
    
    input(string):
        Token,
        
    output(JSON):
        propic,
        Email,
        dispun,
        AccessLevel, 
}

# Get user groups{
    {{Domain}}/App/user/groups/get/
    
    input(string):
        Email,
        
    output(JSON):
        Groups[
            Name,
            Logo,
        ]
}

# Get Post Comments{
    {{Domain}}/App/Comments/get/
    POST

    input(string):
        id  #id of Post to get comments,
    
    output(JSON): #this could return a list of output  
        
        Comments{
            authorImg, 
            Name,   
            Text,
            Date,
            Time,
        }
}

# Get Group names{
    {{Domain}}/App/Group/get/

    output(JSON):
        Groups{
            Name,
            logo,
        }
}


# Get Group Posts{
    {{Domain}}/App/PostView/
    
    input(string):
        Group,

    output(JSON):
        Posts{
            profile,
            Id,
            Image,
            Title,
            author,
            Text,
            Date,
            Time,
        }
}





##SET

# Set Personal Profile{
    {{Domain}}/App/user/profile/set/
    
    input(string):
        Token,
        propic (optional),
        email (optional),
        dispun (optional),
        OldPass (optional),
        NewPass (optional),
        
    output(JSON):
        Status (optional),
        PassWord (optional)[
            Status,
        ],
        DisplayUName (optional) [
            Status,
        ],
        Email (optional) [
            Status,
        ],
        ProfilePicture (optional) [
            Status,
        ],
}
     

# Set New Post{
    {{Domain}}/App/Post/set/
    
    input(string):
        Token,
        Title,
        Text,
        status (draft/published),
        Group,
        Image,

    output(JSON):
        status,
}

# Set New Comment{
    {{Domain}}/App/Comments/set/
    
    input(string):
        Token,
        Text,
        PostId,
        
    output(JSON):
        status,
}


# Set user groups{
    {{Domain}}/App/user/groups/set/
    
    input(string):
        Token,
        email,
        group,
        action('add'/'remove'), 

    output(JSON):
        Status,
}

# Set new Group{
    {{Domain}}/App/Group/add/
    
    input(image , string):
        Token,
        pic (optional),
        Name,
        description,

    output(JSON):
        Status,
}

# Edit Group{
    {{Domain}}/App/Group/set/
    
    input(image , string):
        Token,
        Name,
        pic (optional),
        description (optional),
        NewName (optional)

    output(JSON):
        Status,
}

# Set new Password{
    {{Domain}}/App/user/profile/ChangeForgetPass/
    
    input(string):
        email,
        code,
        password,

    output(JSON):
        Status,
}

