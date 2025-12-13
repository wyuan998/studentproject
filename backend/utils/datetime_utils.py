# ========================================
# 学生信息管理系统 - 时间工具类
# ========================================

import time
import calendar
from datetime import datetime, date, timedelta, timezone
from typing import Dict, List, Optional, Union, Tuple
from dateutil import relativedelta, parser
from dateutil.relativedelta import relativedelta as rdelta
import pytz
import holidays
import recurring_ical_events

from flask import current_app


class DateTimeUtils:
    """时间工具类"""

    # 中国时区
    CHINA_TIMEZONE = pytz.timezone('Asia/Shanghai')

    # 时间格式
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    DATE_FORMAT = '%Y-%m-%d'
    TIME_FORMAT = '%H:%M:%S'
    ISO_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
    ISO_DATE_FORMAT = '%Y-%m-%d'

    @staticmethod
    def now(timezone_str: str = 'Asia/Shanghai') -> datetime:
        """
        获取当前时间

        Args:
            timezone_str: 时区字符串

        Returns:
            datetime: 当前时间
        """
        tz = pytz.timezone(timezone_str)
        return datetime.now(tz)

    @staticmethod
    def utc_now() -> datetime:
        """
        获取UTC当前时间

        Returns:
            datetime: UTC当前时间
        """
        return datetime.now(timezone.utc)

    @staticmethod
    def parse_datetime(datetime_str: str, timezone_str: str = 'Asia/Shanghai') -> Optional[datetime]:
        """
        解析日期时间字符串

        Args:
            datetime_str: 日期时间字符串
            timezone_str: 时区字符串

        Returns:
            Optional[datetime]: 解析后的日期时间
        """
        try:
            # 尝试使用dateutil解析
            dt = parser.parse(datetime_str)

            # 如果没有时区信息，添加指定时区
            if dt.tzinfo is None:
                tz = pytz.timezone(timezone_str)
                dt = tz.localize(dt)

            return dt
        except Exception:
            return None

    @staticmethod
    def format_datetime(dt: datetime, format_str: str = None, timezone_str: str = 'Asia/Shanghai') -> str:
        """
        格式化日期时间

        Args:
            dt: 日期时间对象
            format_str: 格式字符串
            timezone_str: 时区字符串

        Returns:
            str: 格式化后的字符串
        """
        if format_str is None:
            format_str = DateTimeUtils.DATETIME_FORMAT

        # 转换时区
        if dt.tzinfo is not None:
            tz = pytz.timezone(timezone_str)
            dt = dt.astimezone(tz)

        return dt.strftime(format_str)

    @staticmethod
    def to_timezone(dt: datetime, timezone_str: str) -> datetime:
        """
        转换时区

        Args:
            dt: 日期时间对象
            timezone_str: 目标时区

        Returns:
            datetime: 转换时区后的日期时间
        """
        tz = pytz.timezone(timezone_str)

        if dt.tzinfo is None:
            # 假设是本地时间
            dt = tz.localize(dt)
        else:
            dt = dt.astimezone(tz)

        return dt

    @staticmethod
    def to_utc(dt: datetime) -> datetime:
        """
        转换为UTC时间

        Args:
            dt: 日期时间对象

        Returns:
            datetime: UTC时间
        """
        if dt.tzinfo is None:
            # 假设是系统本地时间
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)

        return dt

    @staticmethod
    def from_utc(dt: datetime, timezone_str: str = 'Asia/Shanghai') -> datetime:
        """
        从UTC时间转换

        Args:
            dt: UTC日期时间
            timezone_str: 目标时区

        Returns:
            datetime: 转换后的日期时间
        """
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        tz = pytz.timezone(timezone_str)
        return dt.astimezone(tz)

    @staticmethod
    def add_time(dt: datetime, **kwargs) -> datetime:
        """
        添加时间

        Args:
            dt: 日期时间对象
            **kwargs: 时间参数 (years, months, days, hours, minutes, seconds)

        Returns:
            datetime: 添加时间后的日期时间
        """
        return dt + relativedelta(**kwargs)

    @staticmethod
    def subtract_time(dt: datetime, **kwargs) -> datetime:
        """
        减去时间

        Args:
            dt: 日期时间对象
            **kwargs: 时间参数

        Returns:
            datetime: 减去时间后的日期时间
        """
        # 将所有值取负数
        kwargs = {k: -v for k, v in kwargs.items()}
        return dt + relativedelta(**kwargs)

    @staticmethod
    def time_difference(start: datetime, end: datetime) -> Dict[str, int]:
        """
        计算时间差

        Args:
            start: 开始时间
            end: 结束时间

        Returns:
            Dict[str, int]: 时间差信息
        """
        diff = relativedelta(end, start)

        return {
            'years': diff.years,
            'months': diff.months,
            'days': diff.days,
            'hours': diff.hours,
            'minutes': diff.minutes,
            'seconds': diff.seconds,
            'total_days': (end - start).days,
            'total_seconds': int((end - start).total_seconds())
        }

    @staticmethod
    def human_readable_time_difference(start: datetime, end: datetime = None, language: str = 'zh') -> str:
        """
        人类可读的时间差

        Args:
            start: 开始时间
            end: 结束时间（默认为当前时间）
            language: 语言

        Returns:
            str: 人类可读的时间差
        """
        if end is None:
            end = DateTimeUtils.now()

        diff = DateTimeUtils.time_difference(start, end)

        if language == 'zh':
            parts = []
            if diff['years'] > 0:
                parts.append(f"{diff['years']}年")
            if diff['months'] > 0:
                parts.append(f"{diff['months']}个月")
            if diff['days'] > 0:
                parts.append(f"{diff['days']}天")
            if diff['hours'] > 0:
                parts.append(f"{diff['hours']}小时")
            if diff['minutes'] > 0:
                parts.append(f"{diff['minutes']}分钟")
            if diff['seconds'] > 0:
                parts.append(f"{diff['seconds']}秒")

            if not parts:
                return "刚刚"

            return " ".join(parts) + "前"
        else:
            # 英文
            parts = []
            if diff['years'] > 0:
                parts.append(f"{diff['years']} years")
            if diff['months'] > 0:
                parts.append(f"{diff['months']} months")
            if diff['days'] > 0:
                parts.append(f"{diff['days']} days")
            if diff['hours'] > 0:
                parts.append(f"{diff['hours']} hours")
            if diff['minutes'] > 0:
                parts.append(f"{diff['minutes']} minutes")
            if diff['seconds'] > 0:
                parts.append(f"{diff['seconds']} seconds")

            if not parts:
                return "just now"

            return " ".join(parts) + " ago"

    @staticmethod
    def is_weekend(dt: datetime) -> bool:
        """
        判断是否为周末

        Args:
            dt: 日期时间对象

        Returns:
            bool: 是否为周末
        """
        return dt.weekday() in [5, 6]  # 周六、周日

    @staticmethod
    def is_business_day(dt: datetime, country: str = 'CN') -> bool:
        """
        判断是否为工作日

        Args:
            dt: 日期时间对象
            country: 国家代码

        Returns:
            bool: 是否为工作日
        """
        # 检查是否为周末
        if DateTimeUtils.is_weekend(dt):
            return False

        # 检查是否为公共假日
        country_holidays = holidays.country_holidays(country)
        if dt.date() in country_holidays:
            return False

        return True

    @staticmethod
    def add_business_days(dt: datetime, days: int, country: str = 'CN') -> datetime:
        """
        添加工作日

        Args:
            dt: 日期时间对象
            days: 要添加的工作日数
            country: 国家代码

        Returns:
            datetime: 添加工作日后的日期时间
        """
        current = dt
        added_days = 0

        while added_days < days:
            current += timedelta(days=1)
            if DateTimeUtils.is_business_day(current, country):
                added_days += 1

        return current

    @staticmethod
    def get_week_range(dt: datetime) -> Tuple[datetime, datetime]:
        """
        获取一周的范围

        Args:
            dt: 日期时间对象

        Returns:
            Tuple[datetime, datetime]: (周开始, 周结束)
        """
        # 获取周的开始（周一）
        week_start = dt - timedelta(days=dt.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

        # 获取周的结束（周日）
        week_end = week_start + timedelta(days=6)
        week_end = week_end.replace(hour=23, minute=59, second=59, microsecond=999999)

        return week_start, week_end

    @staticmethod
    def get_month_range(dt: datetime) -> Tuple[datetime, datetime]:
        """
        获取月份范围

        Args:
            dt: 日期时间对象

        Returns:
            Tuple[datetime, datetime]: (月开始, 月结束)
        """
        # 获取月份的第一天
        month_start = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # 获取月份的最后一天
        last_day = calendar.monthrange(dt.year, dt.month)[1]
        month_end = dt.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

        return month_start, month_end

    @staticmethod
    def get_year_range(dt: datetime) -> Tuple[datetime, datetime]:
        """
        获取年份范围

        Args:
            dt: 日期时间对象

        Returns:
            Tuple[datetime, datetime]: (年开始, 年结束)
        """
        year_start = dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        year_end = dt.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)

        return year_start, year_end

    @staticmethod
    def get_semester_range(year: int, semester: str) -> Tuple[datetime, datetime]:
        """
        获取学期范围

        Args:
            year: 年份
            semester: 学期 ('spring', 'summer', 'fall', 'winter')

        Returns:
            Tuple[datetime, datetime]: (学期开始, 学期结束)
        """
        semester_dates = {
            'spring': (f"{year}-02-01", f"{year}-06-30"),
            'summer': (f"{year}-07-01", f"{year}-08-31"),
            'fall': (f"{year}-09-01", f"{year}-12-31"),
            'winter': (f"{year}-01-01", f"{year}-01-31")
        }

        if semester not in semester_dates:
            raise ValueError(f"无效的学期: {semester}")

        start_date = datetime.strptime(semester_dates[semester][0], '%Y-%m-%d')
        end_date = datetime.strptime(semester_dates[semester][1], '%Y-%m-%d')

        # 设置时间
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        return start_date, end_date

    @staticmethod
    def get_age(birth_date: Union[date, datetime], reference_date: Union[date, datetime] = None) -> int:
        """
        计算年龄

        Args:
            birth_date: 出生日期
            reference_date: 参考日期（默认为当前日期）

        Returns:
            int: 年龄
        """
        if reference_date is None:
            reference_date = date.today()
        elif isinstance(reference_date, datetime):
            reference_date = reference_date.date()

        if isinstance(birth_date, datetime):
            birth_date = birth_date.date()

        age = reference_date.year - birth_date.year

        # 检查是否已过生日
        if (reference_date.month, reference_date.day) < (birth_date.month, birth_date.day):
            age -= 1

        return age

    @staticmethod
    def validate_date_range(start: Union[str, date, datetime], end: Union[str, date, datetime]) -> bool:
        """
        验证日期范围

        Args:
            start: 开始日期
            end: 结束日期

        Returns:
            bool: 是否有效
        """
        try:
            if isinstance(start, str):
                start = DateTimeUtils.parse_datetime(start).date()
            elif isinstance(start, datetime):
                start = start.date()

            if isinstance(end, str):
                end = DateTimeUtils.parse_datetime(end).date()
            elif isinstance(end, datetime):
                end = end.date()

            return start <= end
        except Exception:
            return False

    @staticmethod
    def get_time_periods() -> Dict[str, str]:
        """
        获取时间段定义

        Returns:
            Dict[str, str]: 时间段定义
        """
        return {
            'morning': '06:00-12:00',
            'afternoon': '12:00-18:00',
            'evening': '18:00-22:00',
            'night': '22:00-06:00'
        }

    @staticmethod
    def get_time_period(dt: datetime) -> str:
        """
        获取时间段

        Args:
            dt: 日期时间对象

        Returns:
            str: 时间段
        """
        hour = dt.hour

        if 6 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 18:
            return 'afternoon'
        elif 18 <= hour < 22:
            return 'evening'
        else:
            return 'night'

    @staticmethod
    def convert_timestamp(timestamp: Union[int, float], timezone_str: str = 'Asia/Shanghai') -> datetime:
        """
        转换时间戳

        Args:
            timestamp: 时间戳
            timezone_str: 时区

        Returns:
            datetime: 日期时间对象
        """
        dt = datetime.fromtimestamp(timestamp, tz=pytz.timezone(timezone_str))
        return dt

    @staticmethod
    def to_timestamp(dt: datetime) -> int:
        """
        转换为时间戳

        Args:
            dt: 日期时间对象

        Returns:
            int: 时间戳
        """
        return int(dt.timestamp())

    @staticmethod
    def is_same_day(dt1: datetime, dt2: datetime) -> bool:
        """
        判断是否为同一天

        Args:
            dt1: 日期时间1
            dt2: 日期时间2

        Returns:
            bool: 是否为同一天
        """
        return dt1.date() == dt2.date()

    @staticmethod
    def is_future(dt: datetime, reference: datetime = None) -> bool:
        """
        判断是否为未来时间

        Args:
            dt: 要判断的时间
            reference: 参考时间（默认为当前时间）

        Returns:
            bool: 是否为未来时间
        """
        if reference is None:
            reference = DateTimeUtils.now()
        return dt > reference

    @staticmethod
    def is_past(dt: datetime, reference: datetime = None) -> bool:
        """
        判断是否为过去时间

        Args:
            dt: 要判断的时间
            reference: 参考时间（默认为当前时间）

        Returns:
            bool: 是否为过去时间
        """
        if reference is None:
            reference = DateTimeUtils.now()
        return dt < reference

    @staticmethod
    def countdown(target: datetime) -> Dict[str, int]:
        """
        倒计时

        Args:
            target: 目标时间

        Returns:
            Dict[str, int]: 倒计时信息
        """
        now = DateTimeUtils.now()
        diff = target - now

        if diff.total_seconds() <= 0:
            return {'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 0, 'total_seconds': 0}

        total_seconds = int(diff.total_seconds())
        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        seconds = diff.seconds % 60

        return {
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'total_seconds': total_seconds
        }


class AcademicCalendar:
    """学术日历"""

    @staticmethod
    def get_current_semester() -> str:
        """
        获取当前学期

        Returns:
            str: 学期 (spring, summer, fall, winter)
        """
        now = DateTimeUtils.now()
        month = now.month

        if 2 <= month <= 6:
            return 'spring'
        elif 7 <= month <= 8:
            return 'summer'
        elif 9 <= month <= 12:
            return 'fall'
        else:
            return 'winter'

    @staticmethod
    def get_semester_start_end(year: int, semester: str) -> Tuple[datetime, datetime]:
        """
        获取学期开始结束时间

        Args:
            year: 年份
            semester: 学期

        Returns:
            Tuple[datetime, datetime]: (开始时间, 结束时间)
        """
        return DateTimeUtils.get_semester_range(year, semester)

    @staticmethod
    def get_academic_year(year: int) -> Tuple[datetime, datetime]:
        """
        获取学年时间范围

        Args:
            year: 学年开始年份

        Returns:
            Tuple[datetime, datetime]: (学年开始, 学年结束)
        """
        # 中国学年通常从9月开始
        start_date = datetime(year, 9, 1)
        end_date = datetime(year + 1, 8, 31, 23, 59, 59)
        return start_date, end_date

    @staticmethod
    def is_in_exam_period(dt: datetime = None) -> bool:
        """
        判断是否为考试期

        Args:
            dt: 日期时间（默认为当前时间）

        Returns:
            bool: 是否为考试期
        """
        if dt is None:
            dt = DateTimeUtils.now()

        month = dt.month
        # 通常考试期在6月和12月
        return month in [6, 12]

    @staticmethod
    def is_in_holiday(dt: datetime = None) -> bool:
        """
        判断是否为假期

        Args:
            dt: 日期时间（默认为当前时间）

        Returns:
            bool: 是否为假期
        """
        if dt is None:
            dt = DateTimeUtils.now()

        month = dt.month
        # 中国主要假期：1-2月寒假，7-8月暑假
        return month in [1, 2, 7, 8]


# 便捷函数
def now() -> datetime:
    """获取当前中国时间"""
    return DateTimeUtils.now('Asia/Shanghai')


def format_date(dt: datetime, format_str: str = None) -> str:
    """格式化日期"""
    return DateTimeUtils.format_datetime(dt, format_str or DateTimeUtils.DATE_FORMAT)


def parse_date(date_str: str) -> Optional[datetime]:
    """解析日期字符串"""
    return DateTimeUtils.parse_datetime(date_str)


def get_current_semester() -> str:
    """获取当前学期"""
    return AcademicCalendar.get_current_semester()


def is_business_day(dt: datetime = None) -> bool:
    """判断是否为工作日"""
    if dt is None:
        dt = now()
    return DateTimeUtils.is_business_day(dt, 'CN')


def add_business_days(dt: datetime, days: int) -> datetime:
    """添加工作日"""
    return DateTimeUtils.add_business_days(dt, days, 'CN')


def calculate_age(birth_date: Union[date, datetime]) -> int:
    """计算年龄"""
    return DateTimeUtils.get_age(birth_date)