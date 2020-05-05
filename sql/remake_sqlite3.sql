drop table if exists JOBS;
create table if not exists JOBS (
  ID integer primary key autoincrement
  , TITLE text
  , REMARKS text
  , COMMAND text
  , SCHEDULE text
  , MAX_EXEC_TIME integer default 0
  , NEXT_JOB_IDS text
  , HOST text
  , IS_DELETED integer default 0
  , CREATE_DATETIME text not null default (datetime('now', 'localtime'))
  , UPDATE_DATETIME text not null default (datetime('now', 'localtime'))
);
create trigger TRIGGER_JOBS_UPDATED after update on JOBS
begin
    update JOBS set UPDATE_DATETIME = datetime('now', 'localtime') where rowid == new.rowid; end;
drop table if exists JOB_HISTORY;
create table if not exists JOB_HISTORY (
  ID integer primary key autoincrement
  , JOB_ID integer not null
  , JOB_KEY text
  , COMMAND text
  , CALLER_JOB_KEY text
  , HOST text
  , IP_ADDRESS text
  , PID integer
  , RETURN_CODE integer
  , EXEC_RESULT text -- running, successed, failed, killed, skipped
  , STD_OUT text
  , STD_ERR text
  , START_DATETIME datetime
  , END_DATETIME datetime
  , CREATE_DATETIME text not null default (DATETIME('now', 'localtime'))
  , UPDATE_DATETIME text not null default (DATETIME('now', 'localtime'))
);
create trigger TRIGGER_JOB_HISTORY_UPDATED after update on JOB_HISTORY
begin
    update JOB_HISTORY set UPDATE_DATETIME = datetime('now', 'localtime') where rowid == new.rowid; end;
create index I_ID_JOB_ID on JOB_HISTORY(ID, JOB_ID);
create index I_ID_JOB_KEY on JOB_HISTORY(ID, JOB_KEY);
create index I_ID_EXEC_RESULT on JOB_HISTORY(ID, EXEC_RESULT);
