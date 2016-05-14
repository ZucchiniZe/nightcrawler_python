drop table if exists titles;
drop table if exists issues;
drop table if exists titlesearch;

create table titles (
       id integer primary key,
       title text not null,
       startyear integer not null,
       endyear integer,
       scraped boolean not null default 0
);

create virtual table titlesearch using fts4(id, title, startyear, endyear, scraped default 0);

create table issues (
       id integer primary key,
       title text not null,
       link text not null,
       series integer not null,
       foreign key(series) references titles(id)
);
