from aiohttp import web
import secrets
import accounts_database as db
app = web.Application()
COOKIES = []
    
COOKIE_NAME = 'gmaraton-cookie'
EMAILS = ['chaimke2005@gmail.com']

ADMIN_EMAIL = 'chaimke2005@gmail.com'
ADMIN_COOKIES = []

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

def is_admin(request: web.Request):
    cookies = request.cookies
    if COOKIE_NAME in cookies:
        cookie = cookies[COOKIE_NAME]
        return cookie in ADMIN_COOKIES
    return False

async def game_page(request: web.Request):
    """Serve the client-side application."""
    print(request)
    if is_valid_user(request):
        if is_admin(request):
            with open('pages/admin.html') as f:
                return web.Response(text=f.read(), content_type='text/html')
        with open('pages/client.html') as f:
            return web.Response(text=f.read(), content_type='text/html')
    return web.Response(status=302, headers={'Location': '/login'})


async def login(request: web.Request):
    print(request)
    """Serve the client-side application."""
    with open('pages/login.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

async def display(request: web.Request):
    """Serve the client-side application."""
    print(request)
    if is_valid_user(request):
        with open('pages/display.html') as f:
            return web.Response(text=f.read(), content_type='text/html')
    return web.Response(status=302, headers={'Location': '/login'})


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
    print(request)
    if not is_valid_user(request):
        return web.json_response({'status': 'error'})
    if not await check_data(request):
        return web.json_response({'status': 'error'})
    data = await request.json()
    if data['column'] in db.BONUSES:
        db.update_bonus(data['grade'], int(data['class']), data['name'], data['column'], int(data['value']))
    else:
        db.update_grade(data['grade'], int(data['class']), data['name'], data['column'], int(data['value']))
    print(f"{data['name'][::-1]} grade in {data['column']} was updated to {data['value']}")
    return web.json_response({'status': 'ok'})


async def data(request: web.Request):
    # Auth
    if not is_valid_user(request):
        return web.json_response({'status': 'error'})
    
    # Default is to give grades list and tests list
    if not request.can_read_body:
        if is_admin(request):
            grades = db.get_school_table()
        else:
            grades = {}
            for grade in db.TABLES_NAMES:
                class_list = db.get_class_numbers_list(grade)
                class_dict = {}
                for class_num in class_list:
                    class_dict[class_num] = db.get_class_names(grade, class_num)
                grades[grade] = class_dict
        return web.json_response({'status': 'ok', 'grades': grades, 'bonusses': db.BONUSES, 'tests': db.TESTS})
    data = await request.json()
    if not data or 'reques' not in data:
        return web.json_response({'status': 'error'})
    if data['reques'] == 'subjects':
        # return a dict containing names as the keys and subjects as the values
        students = {}
        for grade in db.TABLES_NAMES:
            for class_num in db.get_class_numbers_list(grade):
                for name in db.get_class_names(grade, class_num):
                    students[name] = db.get_subjects(grade, class_num, name)
        return web.json_response({'status': 'ok', 'students': students})
            


async def login_validation(request: web.Request):
    print(request)
    headers = request.headers
    if request.body_exists:
        data = await request.json()
        if 'username' in data and 'password' in data:
            if data['username'] in EMAILS and data['password'] == 'gmaraton' or\
            data['username'] == 'test' and data['password'] == 'test' or\
            data['username'] == 'test1' and data['password'] == 'test1':
                if data['username'] == ADMIN_EMAIL or data['username'] == 'test':
                    global ADMIN_COOKIES
                    cookie = create_cookie(data['username'])
                    ADMIN_COOKIES.append(cookie)
                else:
                    cookie = create_cookie(data['username'])
                response = web.json_response({'status': 'ok'})
                response.set_cookie(COOKIE_NAME, cookie)
                return response
    return web.json_response({'status': 'error'})

async def results(request: web.Request):
    # Auth
    if not is_admin(request):
        return web.json_response({'status': 'error'})
    
    results = {}
    for grade in db.TABLES_NAMES:
        grade_results = {}
        for class_num in db.get_class_numbers_list(grade):
            score = db.get_class_score(grade, class_num)
            grade_results[class_num] = score
        results[grade] = grade_results

    return web.json_response({'status': 'ok', 'results': results})


app.add_routes([web.get('/', game_page),
                web.get('/login', login),
                web.get('/display', display),
                web.post('/validate', login_validation),
                web.post('/update', update),
                web.post('/data', data),
                web.post('/results', results),
                web.static('/scripts', 'scripts'),
                web.static('/styles', 'styles'),
                web.static('/images', 'images')])

if __name__ == '__main__':
    print('Starting server...')
    web.run_app(app, port=5678)