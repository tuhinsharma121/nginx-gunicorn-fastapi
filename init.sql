drop table if exists users;

create table if not exists users
(
    user_id          varchar(100) not null primary key,
    full_name          varchar(100) not null,
    company_name       varchar(100) not null,
    hashed_password    varchar(100) not null,
    disabled           boolean      not null
);