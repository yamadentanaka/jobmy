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
  , LAST_EXEC_DATETIME datetime
  , IS_DELETED boolean default false
  , CREATE_DATETIME timestamp not null default current_timestamp
  , UPDATE_DATETIME timestamp not null default current_timestamp on update current_timestamp
  , index(ID)
) engine=InnoDB;
drop table if exists JOB_HISTORY cascade;
create table if not exists JOB_HISTORY (
  ID int auto_increment
  , JOB_ID int not null
  , JOB_KEY varchar(72)
  , HOST varchar(50)
  , PID int
  , EXEC_RESULT varchar(50)
  , STD_OUT longtext
  , STD_ERR longtext
  , START_DATETIME datetime
  , END_DATETIME datetime
  , CREATE_DATETIME timestamp not null default current_timestamp
  , UPDATE_DATETIME timestamp not null default current_timestamp on update current_timestamp
  , index(ID)
) engine=InnoDB;
alter table JOB_HISTORY add index I_ID_JOB_ID(ID, JOB_ID);
alter table JOB_HISTORY add index I_ID_JOB_KEY(ID, JOB_KEY);
alter table JOB_HISTORY engine=InnoDB ROW_FORMAT=compressed KEY_BLOCK_SIZE=8;
alter table JOB_HISTORY partition by hash(JOB_ID) partitions 8;
