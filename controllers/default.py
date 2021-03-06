def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    images = []
    comments = []
    followers = []
    if auth.user_id:
        if hasattr(db(db.auth_user.username == auth.user.username).select(db.auth_user.follow_list).first(), 'follow_list'):
            followers = db(db.auth_user.username == auth.user.username).select(db.auth_user.follow_list).first().follow_list
        images = db((db.image.author.belongs(followers)) | (db.image.author == auth.user.username)).select(db.image.ALL, orderby=~db.image.posted_on,limitby=(0, 20))

        comments = db().select(db.image_comment.ALL)
    return dict(get_username_from_email=get_username_from_email, get_firstname_from_email=get_firstname_from_email,
                images=images, comments=comments)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """

    return dict(form=auth())

def edit_profile():
    return dict(form=auth.profile())

def get_username_from_email(email):
    u = db(db.auth_user.email == email).select().first()
    if u is None:
        return 'None'
    else:
        return ' '.join([u.first_name, u.last_name])

def get_firstname_from_email(email):
    u = db(db.auth_user.email == email).select().first()
    if u is None:
        return 'None'
    else:
        return u.first_name

def serve_file():
    filename = request.args(0)
    path = os.path.join(request.folder, 'static', 'images', filename)
    return response.stream(path)


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

@auth.requires_login()
def profile():
    if request.args(0) is not None:
        query = db.image.author == request.args(0)
        user = request.args(0)
        bio_query = db.auth_user.username == request.args(0)
        bio = db(bio_query).select(db.auth_user.bio).first().bio
    else:
        query = db.image.author == auth.user.username
        user = auth.user.username
        bio = auth.user.bio

    images = db(query).select(orderby=~db.image.posted_on, limitby=(0, 20))
    user_profile = db(db.auth_user.username == user).select().first()

    audience_list = db(db.auth_user.username == user).select().first().audience_list
    follow_list = db(db.auth_user.username == user).select().first().follow_list
    audience_count = len(db(db.auth_user.username == user).select().first().audience_list)
    follower_count = len(db(db.auth_user.username == user).select().first().follow_list)

    return dict(get_firstname_from_email=get_firstname_from_email,
                images=images, user=user, bio=bio, user_profile = user_profile,
                audience_count=audience_count, follower_count = follower_count,
                audience_list = audience_list, follow_list = follow_list)

@auth.requires_login()
def upload():
    form = SQLFORM(db.image)
    if form.process().accepted:
        session.flash = T('Image Posted.')
        redirect(URL('default','index'))
    return dict(form=form)


def upload_image():
    p_id = db.image.insert(
        image_content = request.vars.image,
        caption = request.vars.caption
    )
    print p_id
    return "ok"