drop table users;
drop table posts;

create table users (
  user_id SERIAL PRIMARY KEY,
  email text,
  username varchar(255),
  newuser boolean,
  data bytea
);

create table posts (
  post_id SERIAL PRIMARY KEY,
  username text,
  filename text,
  data bytea,
  rgb_1 text DEFAULT '0',
  rgb_2 text DEFAULT '0',
  rgb_3 text DEFAULT '0',
  average_rgb text DEFAULT '0',
  metadata text DEFAULT 'none'
);
