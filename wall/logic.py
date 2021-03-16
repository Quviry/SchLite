import re

import requests
import bs4
from auth.models import User
from auth.logic import reauth
import logging
import datetime
from wall.models import TimeTable, DoneHomeworkNote

logger = logging.getLogger(__name__)
logger.debug('Logger in wall/logic.py loaded')

auth_headers_wordlist = {
    'Connection': 'close',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'DNT': '1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Student': '?1',
    'Sec-Fetch-Dest': 'document',
    'Referer': 'https://schools.school.mosreg.ru/marks.aspx',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en,ru;q=0.9',
}


def get_app_name(response_body):
    try:
        soup = bs4.BeautifulSoup(response_body.encode(), 'lxml')
        if soup.title:
            return soup.title.text.strip()
        else:
            tag: bs4.Tag = soup.find('meta', {'name': "application-name"})
            return tag.get('content').strip()
    except AttributeError as e:
        return 'AnonymousApplication'
    except Exception as e:
        logger.info(e)
        return 'UndefinedApplication'


def str_to_normal_date(str_date):
    months = {
        'января': 1,
        'февраля': 2,
        'марта': 3,
        'мая': 4,
        'апреля': 5,
        'июня': 6,
        'июля': 7,
        'августа': 8,
        'сентября': 9,
        'октября': 10,
        'ноября': 11,
        'декабря': 12,
    }
    periods = str_date.split()
    periods[1] = months[periods[1]]
    periods = [int(_) for _ in periods]
    periods.reverse()
    normal_date = datetime.date(*periods)
    return normal_date


def get_day(sch_form_date: str):
    src_date = sch_form_date.split(', ')[1]
    out_date = str_to_normal_date(src_date)
    return out_date.strftime('%Y-%m-%d')


def generate_browser_headers():
    return auth_headers_wordlist


class ApiClass:
    def __init__(self, user: User):
        self.response_code = 200
        self.user = user
        self.key = user.dairy_cookie
        self.errors = []

    def get_timetable_page(self):
        url = 'https://schools.school.mosreg.ru/schedules/'
        portal_response = self.get_portal_response(url)
        if (get_app_name(portal_response.text) == 'Войти') or ('scheduleWeekEditorParent' not in portal_response.text):
            if portal_response.status_code != 200:
                return portal_response.status_code, ''
            else:
                return 0, ''
        else:
            return 200, portal_response.text

    def get_portal_response(self, url):
        headers = generate_browser_headers()
        cookies = {'DnevnikLoadTestAuth_a': self.key}
        active_session = requests.Session()
        try:
            response = active_session.get(url=url, cookies=cookies, headers=headers)
        except requests.exceptions.ConnectionError:
            logger.warning(f'Portal connection fault')
            response = requests.models.Response()
        except Exception as e:
            logger.warning(f'Portal unresponding with error {e}')
            response = requests.models.Response()
        if get_app_name(response.text) == 'Войти':
            reauth(self.user)
            self.key = self.user.dairy_cookie
            cookies = {'DnevnikLoadTestAuth_a': self.key}
            response = active_session.get(url=url, cookies=cookies, headers=headers)
        return response

    def get(self):
        raise NotImplementedError


class Schedule(ApiClass):
    def __init__(self, user: User):
        logger.debug('Schedule inited')
        super().__init__(user)
        self.homework = []
        self.timetable = []
        self.load_timetable()
        self.init_weeks()

    def get(self):
        """
        return schedule in format
        {
            'response_code': '%d'
            'content': {
                            'timetable':[
                                [order, starts, ends]...
                            ]
                            'homework': [
                                ['day', [{
                                        'ordering': '%d',
                                        'class': '%s',
                                        'homework': '%s'
                                    }]...
                                ]
                            ]
                        }
            'errors': [
                '%s',...
            ]
        }
        """
        data = {
            'code': self.response_code,
            'content': {
                'timetable': self.timetable,
                'homework': self.homework,
            },
            'errors': self.errors
        }
        logger.debug('Schedule reported')
        return data

    def load_timetable(self):
        logger.debug('Trying to load timetable')
        db_timetable = TimeTable.objects.filter(user=self.user)
        if len(db_timetable) != 0:
            logger.debug('Timetable data was found')
            for timemark in db_timetable:
                self.timetable.append([timemark.order, timemark.starts, timemark.ends])
            logger.debug('Timetable loaded from db')
        else:
            logger.debug('Timetable not found in db')
            self.upload_timetable()

    def init_weeks(self):
        url = 'https://schools.school.mosreg.ru/marks.aspx'
        current_week = self.get_portal_response(url)
        if get_app_name(current_week.text) == 'Войти':
            self.response_code = 304
            self.errors.append('ERROR ON AUTHENTICATION')
            return
        elif current_week.status_code != 200:
            self.response_code = current_week.status_code
            self.errors.append('Mosreg portal error')
            return
        else:
            next_week_url = bs4.BeautifulSoup(current_week.text, features='lxml').find('a', title='Следующая неделя')[
                'href']
            next_week = self.get_portal_response(next_week_url)
            [self.homework.append(day) for day in self.parse_week(current_week.text)]
            [self.homework.append(day) for day in self.parse_week(next_week.text)]
        if self.user.is_parent:
            logger.error('Parent user is active')
            current_week = None
            return current_week
        return

    def upload_timetable(self):
        logger.debug('Start timetable loading')
        code, timetable_page = self.get_timetable_page()
        if code != 200:
            logger.warning(f'Uploading timetable fault with response_code {code}')
            self.errors.append(f'Failed timetable loading')
            return False
        else:
            logger.debug(f'Timetable loaded from portal')
            self.load_timetable_to_db(timetable_page)

    def load_timetable_to_db(self, timetable_page):
        logger.debug('Timetable loading to db...')
        time_soup = bs4.BeautifulSoup(timetable_page, features='lxml')
        weeks = time_soup.find_all('tr', {'class': 'wWeek'})
        for week in weeks:
            order = int(week.find('strong').text)
            time = week.find_all('p', {'title': re.compile('Время: ')})
            if len(time) != 0:
                time = time[0].text
                starts, ends = map(lambda x: datetime.time(int(x.split(":")[0]), int(x.split(':')[1])),
                                   time.split(' - '))
                time_mark = TimeTable(user=self.user, order=order, starts=starts, ends=ends)
                time_mark.save()
                self.timetable.append([order, starts, ends])
            else:
                continue
        logger.debug('Timetable loaded to db')

    def parse_week(self, week_html):
        """
        html week -> [{'day', [{'ordering': '%d','class': '%s','homework': '%s' }]}, ...]
        :param week_html:
        :return:
        """
        week_soup = bs4.BeautifulSoup(week_html, features='lxml')
        days = week_soup.find_all('div', class_='panel blue2 clear')
        week = []
        for day in days:
            date = get_day(day.h3.text)
            day_lessons = {date: []}
            for lessons in day.find_all('tr'):
                lesson_src = lessons.find('td', class_='s2')
                order = int(lesson_src.div.text.split()[0])
                lesson = lesson_src.a.text
                homework_list = []
                for homework_point in lessons.find_all('div', class_='breakword'):
                    homework_list.append(homework_point.text.strip().replace('\n', '<br>'))
                    if homework_point.find_all('span', class_='additional-homework-file'):
                        homework_list.append('<br>' + self.get_homework_file(homework_point.find('a')['href']))
                homework = '<br>'.join(homework_list)

                if re.search(r'[A-Za-zа-яА-Я]', homework.replace('<br>', '')) is not None:
                    lesson_data = {
                        'order': order,
                        'lesson': lesson,
                        'homework': homework,
                    }
                    day_lessons[date].append(lesson_data)
            week.append(day_lessons)
        return week

    def get_homework_file(self, url) -> str:
        logger.debug(f'Getting additional files link from {url}')
        response = self.get_portal_response(url)
        files = []
        if response.status_code != 200:  # or not 'homework-file-block' in response.text:
            logger.warning('Additional file can\'t be added')
            return ''
        else:
            source_soup = bs4.BeautifulSoup(response.text, features='lxml')
            for file in source_soup.find_all('tr', class_='homework-file-block'):
                files.append(f'<a href="{file.find("a")["href"]}" target="_blank" '
                             f'rel="noreferrer">Прикреплённый файл</a>')
            logger.debug(f'found files {" ".join(files)}')
            return '<br>'.join(files)


class OfflineSchedule:
    """
    Return minimally correct Schedule page
    """

    def __init__(self, user: User):
        logger.info('Offline schedule requested')
        self.user = user
        self.head = '<!DOCTYPE html>'
        self.src = self.get_content()

    def get(self) -> str:
        """
        :return: HTML page with minimal Schedule content
        """
        logger.info('Offline schedule received')
        return self.head + self.src

    def get_content(self):
        logger.info('Uglifing Offline Schedule...')
        out = bs4.BeautifulSoup('<div id="app" style="color:white; font-width:700"></div>', features='lxml')
        src = Schedule(self.user).get()['content']['homework']
        for day in src:
            date, lessons = day.popitem()
            if len(lessons) != 0:
                day_tag = out.new_tag('h3')
                day_tag.string = date
                out.div.append(day_tag)
                for lesson in lessons:
                    lesson_tag = out.new_tag('p')
                    lesson_tag.string = f'{lesson["lesson"]}: {lesson["homework"]}'
                    out.div.append(lesson_tag)
            else:
                pass  # no homework today
        logger.info('Offline schedule uglified')
        return out.prettify()


class Done(ApiClass):
    def __init__(self, user):
        logger.debug('Done inited')
        super().__init__(user)
        self.done_list = []
        self.set_up()
        self.rejection()

    def get(self):
        logger.info('Getting Done ...')
        data = {
            'code': 200,
            'content': self.done_list,
            'errors': [],
        }
        logger.info('Done received')
        return data

    def set(self, new_done_list):
        logger.debug('Setting up new Done list...')
        try:
            for note in new_done_list:
                if note not in self.done_list:
                    new_note = DoneHomeworkNote(user=self.user,
                                                date=datetime.datetime.fromisoformat(note[0]).date(),
                                                homework_hash=note[1])
                    new_note.save()
                else:
                    pass
            logger.debug('Done data placed to db successful')
            return 200
        except Exception as e:
            logger.error(e)
            return 500

    def set_up(self):
        logger.debug('Setting up Done list')
        db_done_list = DoneHomeworkNote.objects.filter(user=self.user)
        if len(db_done_list) != 0:
            for done_homework in db_done_list:
                done_homework: DoneHomeworkNote
                self.done_list.append([done_homework.date, done_homework.homework_hash])
        else:
            return

    def rejection(self):
        logger.debug('Rejecting Done')
        expired = DoneHomeworkNote.objects.filter(user=self.user)
        expired = expired.filter(date__lt=(datetime.date.today() - datetime.timedelta(days=14)))
        return expired.delete()


class Backpack(ApiClass):
    def __init__(self, user):
        logger.debug('Backpack initing...')
        super().__init__(user)
        self.backpack = {}
        self.date = self.get_date()
        self.set_up()
        if self.response_code == 200:
            logger.debug('Backpack inited successful')
        else:
            logger.info(f'Backpack initing fault with response_code {self.response_code}')

    def set_up(self):
        logger.debug('Setting up Backpack ...')
        code, src_page = self.get_timetable_page()
        if code != 200:
            self.response_code = code
            logger.debug(f'Setting up Backpack fault in data loading with response_code {code}')
            return False
        else:
            soup = bs4.BeautifulSoup(src_page, features='lxml')
            for lesson_slice in soup.find_all('tr', class_='wWeek'):
                order = int(lesson_slice.find('strong').text)
                lesson_cell = lesson_slice.find_all('td')[self.date]
                try:
                    lesson_name = lesson_cell.find('a').get('title')
                    self.backpack[order] = lesson_name
                except AttributeError:
                    pass
            logger.debug(f'Setting up Backpack successful')
            return True

    def get(self):
        logger.debug('Getting Backpack...')
        data = {
            'code': self.response_code,
            'content': self.backpack,
            'errors': self.errors
        }
        logger.debug('Backpack received')
        return data

    def get_date(self) -> int:
        """
        Returning weekday for correct day pick \n
        WARN : only five-days workweek supported
        :return: int Weekday
        """
        logger.debug('Setting up Backpack date')
        today = datetime.date.today().weekday() + 1
        current_time = datetime.datetime.now().time()
        try:
            shift_time = TimeTable.objects.filter(user=self.user).order_by('order').last().starts
        except TimeTable.DoesNotExist:  # We have a times where that's no yet timetable but we need Backpack
            shift_time = current_time
        if today > 5:  # if its Saturday or Sunday -> return Monday automatically
            return 1
        if current_time <= shift_time:  # if its previous last lesson -> return today
            return today
        else:  # if its after last lesson -> return next day for each except Fri that's return Mon
            return (today + 1) % 5 + 1


logger.debug('File wall/logic.py loaded')
