CREATE DATABASE IF NOT EXISTS Maraton;
use Maraton;
create table usuario(id int primary key auto_increment, email varchar(255) unique, password varchar(255)) collate utf8mb4_spanish2_ci;
create table grupo(id int primary key auto_increment, usuario_id integer, nombre varchar(255), fecha_inicio datetime default NOW(), fecha_fin datetime default null, foreign key (usuario_id) references usuario(id)) collate utf8mb4_spanish2_ci;
create table sesion(id int primary key auto_increment, grupo_id integer, fecha_inicio datetime default NOW(), fecha_fin datetime default null, foreign key (grupo_id) references grupo(id)) collate utf8mb4_spanish2_ci;
create table equipo(id int primary key auto_increment, nombre varchar(255), integrantes tinyint, grupo_id integer, foreign key (grupo_id) references grupo(id)) collate utf8mb4_spanish2_ci;
create table tema(id int primary key auto_increment, nombre varchar(100)) collate utf8mb4_spanish2_ci;
create table pregunta(id int primary key auto_increment, contenido varchar(500) unique, respuesta varchar(500), tema_id integer, foreign key (tema_id) references tema(id)) collate utf8mb4_spanish2_ci;
-- Si el resultado es -1 es ganada, si es -2 es perdida y si es >= 0 entonces es un id de equipo
create table historial(id int primary key auto_increment, sesion_id integer, pregunta_id integer, equipo_id integer, resultado integer, foreign key (sesion_id) references sesion(id), foreign key (pregunta_id) references pregunta(id), foreign key (equipo_id) references equipo(id)) collate utf8mb4_spanish2_ci;