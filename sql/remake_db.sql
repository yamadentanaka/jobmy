drop database if exists JOBMY;
create database if not exists JOBMY character set utf8;
use JOBMY;
drop table if exists JOBS cascade;
create table if not exists JOBS (
  ID int auto_increment
  , TITLE varchar(200)
  , REMARKS varchar(2000)
  , COMMAND text
  , SCHEDULE varchar(200)
  , STATE boolean default false
  , LAST_EXEC_RESULT varchar(50)
  , LAST_EXEC_DATE datetime
  , IS_DELETED boolean default false
  , CREATE_DATETIME datetime not null default current_timestamp
  , UPDATE_DATETIME datetime not null default current_timestamp on update current_timestamp
  , index(ID)
) engine=InnoDB;
drop table if exists JOB_HISTORY cascade;
create table if not exists JOB_HISTORY (
  ID int auto_increment
  , JOB_ID int not null
  , EXEC_RESULT varchar(50)
  , EXEC_RESULT_DETAIL longtext
  , START_DATETIME datetime
  , END_DATETIME datetime
  , CREATE_DATETIME datetime not null default current_timestamp
  , UPDATE_DATETIME datetime not null default current_timestamp on update current_timestamp
  , index(ID)
) engine=InnoDB;
alter table JOB_HISTORY add index I_ID_JOB_ID(ID, JOB_ID);
alter table JOB_HISTORY engine=InnoDB ROW_FORMAT=compressed KEY_BLOCK_SIZE=8;
alter table JOB_HISTORY partition by hash(JOB_ID) partitions 8;
