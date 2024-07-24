import jdatetime


def split_persian_date(date):
    year = int(date.split('-')[0])
    month = int(date.split('-')[1])
    day = int(date.split('-')[2])

    return year, month, day


def is_member(user):
    return user.groups.filter(name='کاربر فنی').exists()


def to_gregorian(date):
    try:
        year, month, day = date.split('-')
        date = jdatetime.date(int(year), int(month), int(day)).togregorian()
        return date
    except (ValueError, AttributeError):
        # in case that one of start date or end date is empty
        return None


def gregorian_to_jalali(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if (gy > 1600):
        jy = 979
        gy -= 1600
    else:
        jy = 0
        gy -= 621
    if (gm > 2):
        gy2 = gy + 1
    else:
        gy2 = gy
    days = (365 * gy) + (int((gy2 + 3) / 4)) - (int((gy2 + 99) / 100)) + (int((gy2 + 399) / 400)) - 80 + gd + g_d_m[
        gm - 1]
    jy += 33 * (int(days / 12053))
    days %= 12053
    jy += 4 * (int(days / 1461))
    days %= 1461
    if (days > 365):
        jy += int((days - 1) / 365)
        days = (days - 1) % 365
    if (days < 186):
        jm = 1 + int(days / 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + int((days - 186) / 30)
        jd = 1 + ((days - 186) % 30)
    return [jy, jm, jd]


def date_jalali(value, mode=1):
    if value != None:
        if mode == 1:
            date_time = value.astimezone()
            if date_time.minute < 10:
                minute = '0' + str(date_time.minute)
            else:
                minute = str(date_time.minute)
            if date_time.second < 10:
                second = '0' + str(date_time.second)
            else:
                second = str(date_time.second)

            if date_time.hour < 10:
                hour = '0' + str(date_time.hour)
            else:
                hour = str(date_time.hour)
            shamsi = gregorian_to_jalali(date_time.year, date_time.month, date_time.day)
            return " {h}:{m}:{s} {year}/{month}/{day}".format(year=shamsi[0],
                                                              month=shamsi[1],
                                                              day=shamsi[2],
                                                              h=date_time.hour,
                                                              m=minute,
                                                              s=second)
        elif mode == 2:
            value = str(value)
            year, month, day = value.split('-')
            shamsi = gregorian_to_jalali(int(year), int(month), int(day))

            return "{year}/{month}/{day}".format(year=shamsi[0], month=shamsi[1], day=shamsi[2])

        elif mode == 3:
            return " {h}:{m}:{s}".format(h=0,
                                         m=0,
                                         s=0)
    else:
        return "بدون ثبت"


def full_name_extractor(name):
    if name:
        return name.split(' ')
    else:
        # in case the executor name does not provided
        # return firstname and lastname as none
        return None, None


def total_seconds_calculator(task, total_seconds):
    t_start = task.start_time
    t_end = task.end_time
    seconds_start = (t_start.hour * 60 + t_start.minute) * 60 + t_start.second
    seconds_end = (t_end.hour * 60 + t_end.minute) * 60 + t_end.second
    total_seconds += seconds_end - seconds_start
    return total_seconds


def find_longest_work(task, the_longest_work_seconds, the_longest_work_object):
    t_start = task.start_time
    t_end = task.end_time
    seconds_start = (t_start.hour * 60 + t_start.minute) * 60 + t_start.second
    seconds_end = (t_end.hour * 60 + t_end.minute) * 60 + t_end.second
    current_task_seconds = seconds_end - seconds_start
    if the_longest_work_seconds <= current_task_seconds:
        the_longest_work_object = task
        # return max(the_longest_work_seconds, current_task_seconds), the_longest_work
    return max(the_longest_work_seconds, current_task_seconds), the_longest_work_object
