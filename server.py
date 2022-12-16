from aiohttp import web
import secrets
import accounts_database as db
app = web.Application()
COOKIES = []
    
COOKIE_NAME = 'gmaraton-cookie'
ADMIN_COOKIE_NAME = 'gmaraton-admin-cookie'
EMAILS = ['gmaraton']
ADMIN_COOKIE = None


def get_admin_cookie():
    global ADMIN_COOKIE, COOKIES
    with open('admin_cookie.txt') as f:
        ADMIN_COOKIE = f.read().strip()
    COOKIES.append(ADMIN_COOKIE)


def does_cookie_exist(cookie):
    return cookie in COOKIES


def create_cookie():
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
    if ADMIN_COOKIE_NAME in cookies:
        cookie = cookies[ADMIN_COOKIE_NAME]
        return cookie == ADMIN_COOKIE
    return False


async def game_page(request: web.Request):
    """Serve the client-side application."""
    print(request)
    if is_admin(request):
        with open('pages/admin.html') as f:
            return web.Response(text=f.read(), content_type='text/html')
    if is_valid_user(request):
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
    if is_valid_user(request) or is_admin(request):
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
    if not is_valid_user(request) and not is_admin(request):
        return web.json_response({'status': 'error'})
    if not await check_data(request):
        return web.json_response({'status': 'error'})
    data = await request.json()
    if data['column'] in db.BONUSES:
        db.update_bonus(data['grade'], int(data['class']), data['name'], data['column'], int(data['value']))
    elif data['column'] in db.TESTS:
        db.update_grade(data['grade'], int(data['class']), data['name'], data['column'], int(data['value']))
    print(f"{data['name'][::-1]} grade in {data['column']} was updated to {data['value']}")
    return web.json_response({'status': 'ok'})



async def admin_update(request: web.Request):
    print(request)
    if not is_admin(request):
        return web.json_response({'status': 'error'})
    if not request.can_read_body:
        return web.json_response({'status': 'error'})
    formating = ['grade', 'class', 'column', 'value']
    data = await request.json()
    if not formating == list(data):
        return web.json_response({'status': 'error'})
    if data['column'] in db.ATTENDS:
        db.set_attendents(data['grade'], data['class'], data['column'], int(data['value']))
    elif data['column'] == db.COMPETITION:
        db.set_competition(data['grade'], int(data['value']))
    return web.json_response({'status': 'ok'})


async def data(request: web.Request):
    # Auth
    if not is_valid_user(request) and not is_admin(request):
        return web.json_response({'status': 'error'})
    # Default is to give grades list and tests list
    if is_admin(request):
        grades = db.get_school_table()
        # return a dict of avreage for each test for each class, the test as the key and a dict as a value:
        # {test: {grade: {class: avreage}}}
        avreages = {}
        for test in db.TESTS:
            avreages[test] = {}
            for grade in db.TABLES_NAMES:
                avreages[test][grade] = {}
                for class_num in db.get_class_numbers_list(grade):
                    avreages[test][grade][class_num] = db.get_class_test_avg(grade, class_num, test)
        # same for bonusses
        bonusses = {}
        for bonus in db.BONUSES:
            bonusses[bonus] = {}
            for grade in db.TABLES_NAMES:
                bonusses[bonus][grade] = {}
                for class_num in db.get_class_numbers_list(grade):
                    bonusses[bonus][grade][class_num] = db.get_class_test_avg(grade, class_num, bonus)
        additional = db.get_additional_grading()
        for table in db.TABLES_NAMES:
            comp = additional[table][db.COMPETITION]
            comp_score = round((comp / 100) * 40, 1)
            grade_score = 0
            for classNum in db.get_class_numbers_list(table):
                grade_score += db.get_class_score(table, classNum)
            grade_score //= db.get_class_count(table)
            avg = grade_score
            grade_score *= 0.6
            grade_score = round(grade_score, 1)
            score = round(grade_score + comp_score, 1)
            additional[table][db.COMPETITION] = {'comp': comp, 'score': score, 'avg': avg}
        return web.json_response({'status': 'ok', 'grades': grades, 'bonusses': db.BONUSES,
         'tests': db.TESTS, 'competition': db.COMPETITION,
          'attendence': db.ATTENDS, 'additional': additional,
           'tests_avreages': avreages, 'bonusses_avreages': bonusses})
    else:
        grades = {}
        for grade in db.TABLES_NAMES:
            class_list = db.get_class_numbers_list(grade)
            class_dict = {}
            for class_num in class_list:
                class_dict[class_num] = db.get_class_names(grade, class_num)
            grades[grade] = class_dict
    return web.json_response({'status': 'ok', 'grades': grades, 'bonusses': db.BONUSES, 'tests': db.TESTS})
            

async def login_validation(request: web.Request):
    print(request)
    headers = request.headers
    if request.body_exists:
        data = await request.json()
        if 'username' in data and 'password' in data:
            if data['username'] == 'gmaraton' and data['password'] in EMAILS:
                cookie = create_cookie()
                response = web.json_response({'status': 'ok'})
                response.set_cookie(COOKIE_NAME, cookie)
                return response
    return web.json_response({'status': 'error'})


async def results(request: web.Request):
    # Auth
    if not is_valid_user(request) and not is_admin(request):
        return web.json_response({'status': 'error'})
    
    results = {}
    for grade in db.TABLES_NAMES:
        grade_results = {}
        for class_num in db.get_class_numbers_list(grade):
            score = db.get_class_score(grade, class_num)
            grade_results[class_num] = score
        results[grade] = grade_results

    return web.json_response({'status': 'ok', 'results': results})

async def reset(request: web.Request):
    # Auth
    if is_admin(request):
        db.reset_tables()


app.add_routes([web.get('/', game_page),
                web.get('/login', login),
                web.get('/display', display),
                web.get('/reset', reset),
                web.post('/validate', login_validation),
                web.post('/update', update),
                web.post('/admin_update', admin_update),
                web.post('/data', data),
                web.post('/results', results),
                web.static('/scripts', 'scripts'),
                web.static('/styles', 'styles'),
                web.static('/images', 'images')])


if __name__ == '__main__':
    print('Starting server...')
    get_admin_cookie()
    web.run_app(app, port=5678)