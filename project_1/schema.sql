-- drop table person;
-- drop table skill;


-- create table person(
--   person_id SERIAL PRIMARY KEY,
--   name varchar(255)
-- );

-- create table skill(
--   skill_id SERIAL PRIMARY KEY,
--   person_id int references person,
--   skill varchar(255)
-- );
--
-- insert into person (name) values ('Yang He');
-- insert into person (name) values ('Daniel Kluver');

drop table survey;

create table survey(
  person_id SERIAL PRIMARY KEY,
  date_added timestamp DEFAULT CURRENT_TIMESTAMP,
  name varchar(255),
  fav_character varchar(255),
  season int,
  current varchar(255),
  justification text
);
