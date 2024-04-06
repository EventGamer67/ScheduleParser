from typing import List, Optional

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Double, ForeignKeyConstraint, Identity, JSON, Numeric, PrimaryKeyConstraint, SmallInteger, Table, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import OID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime

class Base(DeclarativeBase):
    pass


class Difficults(Base):
    __tablename__ = 'Difficults'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='Difficults_pkey'),
    )

    id: Mapped[int] = mapped_column(SmallInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=32767, cycle=False, cache=1), primary_key=True)
    name: Mapped[str] = mapped_column(Text)

    Courses: Mapped[List['Courses']] = relationship('Courses', back_populates='Difficults_')


class LessonTypes(Base):
    __tablename__ = 'LessonTypes'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='LessonTypes_pkey'),
    )

    id: Mapped[int] = mapped_column(SmallInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=32767, cycle=False, cache=1), primary_key=True)
    name: Mapped[str] = mapped_column(Text)

    Lessons: Mapped[List['Lessons']] = relationship('Lessons', back_populates='LessonTypes_')


class Roles(Base):
    __tablename__ = 'Roles'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='Roles_pkey'),
    )

    id: Mapped[int] = mapped_column(SmallInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=32767, cycle=False, cache=1), primary_key=True)
    name: Mapped[str] = mapped_column(Text)

    Users: Mapped[List['Users']] = relationship('Users', back_populates='Roles_')


t_pg_stat_statements = Table(
    'pg_stat_statements', Base.metadata,
    Column('userid', OID),
    Column('dbid', OID),
    Column('toplevel', Boolean),
    Column('queryid', BigInteger),
    Column('query', Text),
    Column('plans', BigInteger),
    Column('total_plan_time', Double(53)),
    Column('min_plan_time', Double(53)),
    Column('max_plan_time', Double(53)),
    Column('mean_plan_time', Double(53)),
    Column('stddev_plan_time', Double(53)),
    Column('calls', BigInteger),
    Column('total_exec_time', Double(53)),
    Column('min_exec_time', Double(53)),
    Column('max_exec_time', Double(53)),
    Column('mean_exec_time', Double(53)),
    Column('stddev_exec_time', Double(53)),
    Column('rows', BigInteger),
    Column('shared_blks_hit', BigInteger),
    Column('shared_blks_read', BigInteger),
    Column('shared_blks_dirtied', BigInteger),
    Column('shared_blks_written', BigInteger),
    Column('local_blks_hit', BigInteger),
    Column('local_blks_read', BigInteger),
    Column('local_blks_dirtied', BigInteger),
    Column('local_blks_written', BigInteger),
    Column('temp_blks_read', BigInteger),
    Column('temp_blks_written', BigInteger),
    Column('blk_read_time', Double(53)),
    Column('blk_write_time', Double(53)),
    Column('temp_blk_read_time', Double(53)),
    Column('temp_blk_write_time', Double(53)),
    Column('wal_records', BigInteger),
    Column('wal_fpi', BigInteger),
    Column('wal_bytes', Numeric),
    Column('jit_functions', BigInteger),
    Column('jit_generation_time', Double(53)),
    Column('jit_inlining_count', BigInteger),
    Column('jit_inlining_time', Double(53)),
    Column('jit_optimization_count', BigInteger),
    Column('jit_optimization_time', Double(53)),
    Column('jit_emission_count', BigInteger),
    Column('jit_emission_time', Double(53))
)


t_pg_stat_statements_info = Table(
    'pg_stat_statements_info', Base.metadata,
    Column('dealloc', BigInteger),
    Column('stats_reset', DateTime(True))
)


class Users(Base):
    __tablename__ = 'Users'
    __table_args__ = (
        ForeignKeyConstraint(['RoleID'], ['Roles.id'], name='Users_RoleID_fkey'),
        PrimaryKeyConstraint('id', name='Users_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    email: Mapped[str] = mapped_column(Text, server_default=text("''::text"))
    registerDate: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    avatarURL: Mapped[Optional[str]] = mapped_column(Text)
    password: Mapped[Optional[str]] = mapped_column(Text)
    RoleID: Mapped[Optional[int]] = mapped_column(SmallInteger)
    name: Mapped[Optional[str]] = mapped_column(Text, server_default=text("''::text"))

    Roles_: Mapped['Roles'] = relationship('Roles', back_populates='Users')
    Courses: Mapped[List['Courses']] = relationship('Courses', back_populates='Users_')
    Messages: Mapped[List['Messages']] = relationship('Messages', foreign_keys='[Messages.senderID]', back_populates='Users_')
    Messages_: Mapped[List['Messages']] = relationship('Messages', foreign_keys='[Messages.takerID]', back_populates='Users1')
    UserCourses: Mapped[List['UserCourses']] = relationship('UserCourses', back_populates='Users_')
    LessonsProgress: Mapped[List['LessonsProgress']] = relationship('LessonsProgress', back_populates='Users_')
    UserPractices: Mapped[List['UserPractices']] = relationship('UserPractices', back_populates='Users_')


class Courses(Base):
    __tablename__ = 'Courses'
    __table_args__ = (
        ForeignKeyConstraint(['author'], ['Users.id'], name='Courses_author_fkey'),
        ForeignKeyConstraint(['difficultID'], ['Difficults.id'], name='Courses_difficultID_fkey'),
        PrimaryKeyConstraint('id', name='Courses_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    photo: Mapped[Optional[str]] = mapped_column(Text)
    difficultID: Mapped[Optional[int]] = mapped_column(SmallInteger)
    author: Mapped[Optional[int]] = mapped_column(BigInteger, server_default=text("'-1'::bigint"))

    Users_: Mapped['Users'] = relationship('Users', back_populates='Courses')
    Difficults_: Mapped['Difficults'] = relationship('Difficults', back_populates='Courses')
    ClosedCourses: Mapped[List['ClosedCourses']] = relationship('ClosedCourses', back_populates='Courses_')
    Modules: Mapped[List['Modules']] = relationship('Modules', back_populates='Courses_')
    UserCourses: Mapped[List['UserCourses']] = relationship('UserCourses', back_populates='Courses_')


class Messages(Base):
    __tablename__ = 'Messages'
    __table_args__ = (
        ForeignKeyConstraint(['senderID'], ['Users.id'], name='Messages_senderID_fkey'),
        ForeignKeyConstraint(['takerID'], ['Users.id'], name='Messages_takerID_fkey'),
        PrimaryKeyConstraint('id', name='Messages_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('now()'))
    senderID: Mapped[Optional[int]] = mapped_column(BigInteger)
    message: Mapped[Optional[str]] = mapped_column(Text)
    takerID: Mapped[Optional[int]] = mapped_column(BigInteger)

    Users_: Mapped['Users'] = relationship('Users', foreign_keys=[senderID], back_populates='Messages')
    Users1: Mapped['Users'] = relationship('Users', foreign_keys=[takerID], back_populates='Messages_')


class ClosedCourses(Base):
    __tablename__ = 'ClosedCourses'
    __table_args__ = (
        ForeignKeyConstraint(['closedcourse'], ['Courses.id'], name='ClosedCourses_closedcourse_fkey'),
        PrimaryKeyConstraint('id', name='ClosedCourses_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    closedcourse: Mapped[int] = mapped_column(BigInteger, server_default=text("'20'::bigint"))

    Courses_: Mapped['Courses'] = relationship('Courses', back_populates='ClosedCourses')


class Modules(Base):
    __tablename__ = 'Modules'
    __table_args__ = (
        ForeignKeyConstraint(['courseID'], ['Courses.id'], name='Modules_courseID_fkey'),
        PrimaryKeyConstraint('id', name='Modules_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    courseID: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[Optional[str]] = mapped_column(Text)

    Courses_: Mapped['Courses'] = relationship('Courses', back_populates='Modules')
    Lessons: Mapped[List['Lessons']] = relationship('Lessons', back_populates='Modules_')


class UserCourses(Base):
    __tablename__ = 'UserCourses'
    __table_args__ = (
        ForeignKeyConstraint(['CourseID'], ['Courses.id'], name='UserCourses_CourseID_fkey'),
        ForeignKeyConstraint(['UserID'], ['Users.id'], name='UserCourses_UserID_fkey'),
        PrimaryKeyConstraint('id', name='UserCourses_pkey'),
        UniqueConstraint('id', name='UserCourses_id_key')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    UserID: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1))
    CourseID: Mapped[int] = mapped_column(BigInteger)

    Courses_: Mapped['Courses'] = relationship('Courses', back_populates='UserCourses')
    Users_: Mapped['Users'] = relationship('Users', back_populates='UserCourses')


class Lessons(Base):
    __tablename__ = 'Lessons'
    __table_args__ = (
        ForeignKeyConstraint(['moduleID'], ['Modules.id'], name='Lessons_moduleID_fkey'),
        ForeignKeyConstraint(['type'], ['LessonTypes.id'], name='Lessons_type_fkey'),
        PrimaryKeyConstraint('id', name='Lessons_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    moduleID: Mapped[int] = mapped_column(BigInteger)
    media: Mapped[str] = mapped_column(Text, server_default=text("'empty'::text"))
    text_: Mapped[str] = mapped_column('text', Text, server_default=text("'empty'::text"))
    name: Mapped[Optional[str]] = mapped_column(Text)
    type: Mapped[Optional[int]] = mapped_column(SmallInteger)

    Modules_: Mapped['Modules'] = relationship('Modules', back_populates='Lessons')
    LessonTypes_: Mapped['LessonTypes'] = relationship('LessonTypes', back_populates='Lessons')
    LessonTests: Mapped[List['LessonTests']] = relationship('LessonTests', back_populates='Lessons_')
    LessonsProgress: Mapped[List['LessonsProgress']] = relationship('LessonsProgress', back_populates='Lessons_')
    Practices: Mapped[List['Practices']] = relationship('Practices', back_populates='Lessons_')
    UserPractices: Mapped[List['UserPractices']] = relationship('UserPractices', back_populates='Lessons_')
    pdfLesson: Mapped[List['PdfLesson']] = relationship('PdfLesson', back_populates='Lessons_')


class LessonTests(Base):
    __tablename__ = 'LessonTests'
    __table_args__ = (
        ForeignKeyConstraint(['lesson'], ['Lessons.id'], name='LessonTests_lesson_fkey'),
        PrimaryKeyConstraint('id', name='LessonTests_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    lesson: Mapped[int] = mapped_column(BigInteger)
    data: Mapped[str] = mapped_column(Text)

    Lessons_: Mapped['Lessons'] = relationship('Lessons', back_populates='LessonTests')


class LessonsProgress(Base):
    __tablename__ = 'LessonsProgress'
    __table_args__ = (
        ForeignKeyConstraint(['LessonID'], ['Lessons.id'], name='LessonsProgress_LessonID_fkey'),
        ForeignKeyConstraint(['UserID'], ['Users.id'], name='LessonsProgress_UserID_fkey'),
        PrimaryKeyConstraint('id', name='LessonsProgress_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    LessonID: Mapped[int] = mapped_column(BigInteger)
    UserID: Mapped[int] = mapped_column(BigInteger)

    Lessons_: Mapped['Lessons'] = relationship('Lessons', back_populates='LessonsProgress')
    Users_: Mapped['Users'] = relationship('Users', back_populates='LessonsProgress')


class Practices(Base):
    __tablename__ = 'Practices'
    __table_args__ = (
        ForeignKeyConstraint(['lesson'], ['Lessons.id'], name='Practices_lesson_fkey'),
        PrimaryKeyConstraint('id', name='practices_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    lesson: Mapped[int] = mapped_column(BigInteger)
    active: Mapped[bool] = mapped_column(Boolean, server_default=text('false'))
    flags: Mapped[dict] = mapped_column(JSON, server_default=text("'[]'::json"))

    Lessons_: Mapped['Lessons'] = relationship('Lessons', back_populates='Practices')


class UserPractices(Base):
    __tablename__ = 'UserPractices'
    __table_args__ = (
        ForeignKeyConstraint(['lesson'], ['Lessons.id'], name='UserPractices_lesson_fkey'),
        ForeignKeyConstraint(['user'], ['Users.id'], name='UserPractices_user_fkey'),
        PrimaryKeyConstraint('id', name='UserPractices_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    user: Mapped[int] = mapped_column(BigInteger)
    lesson: Mapped[Optional[int]] = mapped_column(BigInteger)
    text_: Mapped[Optional[str]] = mapped_column('text', Text, server_default=text("''::text"))
    fileLinks: Mapped[Optional[str]] = mapped_column(Text, server_default=text("''::text"))

    Lessons_: Mapped['Lessons'] = relationship('Lessons', back_populates='UserPractices')
    Users_: Mapped['Users'] = relationship('Users', back_populates='UserPractices')


class PdfLesson(Base):
    __tablename__ = 'pdfLesson'
    __table_args__ = (
        ForeignKeyConstraint(['idLesson'], ['Lessons.id'], name='pdfLesson_idLesson_fkey'),
        PrimaryKeyConstraint('id', name='pdfLesson_pkey')
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True)
    pdfLink: Mapped[str] = mapped_column(Text)
    idLesson: Mapped[Optional[int]] = mapped_column(BigInteger)
    nameFile: Mapped[Optional[str]] = mapped_column(Text)

    Lessons_: Mapped['Lessons'] = relationship('Lessons', back_populates='pdfLesson')
