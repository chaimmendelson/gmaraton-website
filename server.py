from aiohttp import web
import secrets
import accounts_database as db
app = web.Application()
COOKIES = []
    
COOKIE_NAME = 'gmaraton-cookie'
EMAILS = ['chaimke2005@gmail.com']

def does_cookie_exist(cookie):
    return cookie in COOKIES

def create_cookie(email):
    cookie = secrets.token_hex(16)
    while does_cookie_exist(cookie):
        cookie = secrets.token_hex(16)
    COOKIES.append(cookie)
    return cookie


def is_valid_user(request: web.Request):
    cookies = request.cookies
    if COOKIE_NAME in cookies:
        cookie = cookies[COOKIE_NAME]
        return does_cookie_exist(cookie)
    return False


async def game_page(request: web.Request):
    """Serve the client-side application."""
    if is_valid_user(request):
        with open('pages/client.html') as f:
            return web.Response(text=f.read(), content_type='text/html')
    return web.Response(status=302, headers={'Location': '/login'})

async def login(request: web.Request):
    """Serve the client-side application."""
    with open('pages/login.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


async def check_data(request: web.Request):
    if not request.can_read_body:
        return False
    data = await request.json()
    if not data:
        return False
    keys_format = ['grade', 'class', 'name', 'column', 'value']
    if keys_format != list(data.keys()):
        return False
    if not db.check_data(data['grade'], data['class'], data['name'], data['column'], data['value']):
        return False
    return True

async def update(request: web.Request):
    if not is_valid_user(request):
        return web.json_response({'status': 'error'})
    if not await check_data(request):
        return web.json_response({'status': 'error'})
    data = await request.json()
    if data['column'] == db.BONUS:
        db.update_bonus(data['grade'], int(data['class']), data['name'], int(data['value']))
    else:
        db.update_grade(data['grade'], int(data['class']), data['name'], data['column'], int(data['value']))
    print(f"{data['name']} grade in {data['column']} was updated to {data['value']}")
    return web.json_response({'status': 'ok'})


async def data(request: web.Request):
    # Auth
    if not is_valid_user(request):
        return web.json_response({'status': 'error'})
    
    # Default is to give grades list and tests list
    if not request.can_read_body:
        grades = {}
        for grade in db.TABLES_NAMES:
            class_list = db.get_class_list(grade)
            class_dict = {}
            for class_num in class_list:
                class_dict[class_num] = db.get_class_names(grade, class_num)
            grades[grade] = class_dict
        return web.json_response({'status': 'ok', 'grades': grades, 'tests': db.TESTS + [db.BONUS]})
    
    data = await request.json()


async def login_validation(request: web.Request):
    headers = request.headers
    if request.body_exists:
        data = await request.json()
        if 'username' in data and 'password' in data:
            if data['username'] in EMAILS and data['password'] == 'gmaraton' or\
            data['username'] == 'test' and data['password'] == 'test':
                cookie = create_cookie(data['username'])
                response = web.json_response({'status': 'ok'})
                response.set_cookie(COOKIE_NAME, cookie)
                return response
    return web.json_response({'status': 'error'})

app.add_routes([web.get('/', game_page),
                web.get('/login', login),
                web.post('/validate', login_validation),
                web.post('/update', update),
                web.post('/data', data),
                web.static('/scripts', 'scripts'),
                web.static('/styles', 'styles'),
                web.static('/images', 'images')])

if __name__ == '__main__':
    web.run_app(app, port=8000)