-- Oscar Ballart Vilella
-- emmagatzema informació sobre els usuaris del sistema de biblioteca. 
-- cada registre representa un usuari
CREATE TABLE Usuaris (
     id_usuari serial NOT NULL,
     nom_usuari character varying(32) NOT NULL,
     cognom_usuari character varying(64) NOT NULL,
     email_usuari TEXT NOT NULL,
     contrasenya_usuari TEXT NOT NULL,
     rol_usuari character varying(16) NOT NULL,
     CONSTRAINT pk_usuaris PRIMARY KEY (id_usuari)
);

-- Oscar Ballart Vilella
-- mmagatzema informació sobre els llibres disponibles a la biblioteca. 
-- cada registre representa un llibre
CREATE TABLE Llibres (
     id_llibre serial NOT NULL,
     titol_llibre character varying(64) NOT NULL,
     any_publicacio_llibre integer NOT NULL,
     ISBN_llibre TEXT NOT NULL,
     descripcio_llibre TEXT NOT NULL,
     nom_autor_llibre character varying(32) NOT NULL,
     cognom_autor_llibre character varying(64) NOT NULL,
     nom_editorial_llibre TEXT NOT NULL,
     nom_categoria_llibre TEXT NOT NULL,
     quantitat_total_llibre integer CHECK (quantitat_total_llibre >= 0),
     quantitat_disponible_llibre integer CHECK (quantitat_disponible_llibre >= 0),
     CONSTRAINT pk_llibres PRIMARY KEY (id_llibre)
);

-- Oscar Ballart Vilella
-- emmagatzema informació sobre les etiquetes que es poden assignar als llibres. 
-- cada registre representa una etiqueta
CREATE TABLE Etiquetes (
     id_etiqueta serial NOT NULL,
     nom_etiqueta_llibre character varying(48) NOT NULL,
     descripcio_etiqueta_llibre TEXT NOT NULL,
     CONSTRAINT pk_etiquetes PRIMARY KEY (id_etiqueta)
);

-- Oscar Ballart Vilella
-- és una taula de relació entre les taules Llibres i Etiquetes. 
-- cada registre representa l‟assignació d‟una etiqueta a un llibre.
CREATE TABLE Llibres_Etiquetes (
     id_llibre integer NOT NULL,
     id_etiqueta integer NOT NULL,
     CONSTRAINT fk_llibre_llibresEtiquetes FOREIGN KEY (id_llibre) REFERENCES Llibres (id_llibre),
     CONSTRAINT fk_etiqueta_llibresEtiquetes FOREIGN KEY (id_etiqueta) REFERENCES Etiquetes (id_etiqueta)
);

-- Oscar Ballart Vilella
-- emmagatzema informació sobre els préstecs de llibres realitzats pels usuaris. 
-- cada registre representa un préstec
CREATE TABLE Prestecs (
     id_prestec serial NOT NULL,
     id_llibre integer NOT NULL,
     id_usuari integer NOT NULL,
     data_prestec_llibre DATE NOT NULL,
     data_devolucio_llibre DATE NOT NULL,
     CONSTRAINT pk_prestecs PRIMARY KEY (id_prestec),
     CONSTRAINT fk_llibre_prestec FOREIGN KEY (id_llibre) REFERENCES Llibres (id_llibre),
     CONSTRAINT fk_usuari_prestec FOREIGN KEY (id_usuari) REFERENCES Usuaris (id_usuari)
);

-- Oscar Ballart Vilella
-- emmagatzema informació sobre les reserves de llibres realitzades pels usuaris.
-- cada registre representa una reserva 
CREATE TABLE Reserves (
     id_reserva serial NOT NULL,
     id_llibre integer NOT NULL,
     id_usuari integer NOT NULL,
     data_reserva_llibre DATE NOT NULL,
     CONSTRAINT pk_reserva PRIMARY KEY (id_reserva),
     CONSTRAINT fk_llibre_reserva FOREIGN KEY (id_llibre) REFERENCES Llibres (id_llibre),
     CONSTRAINT fk_usuari_reserva FOREIGN KEY (id_usuari) REFERENCES Usuaris (id_usuari)
);

-- Oscar Ballart Vilella
-- emmagatzema informació sobre les opinions que els usuaris han deixat sobre els llibres. 
-- cada registre representa una opinió
CREATE TABLE Opinions (
     id_opinio serial NOT NULL,
     id_llibre integer NOT NULL,
     id_usuari integer NOT NULL,
     opinio_usuari_llibre TEXT NOT NULL,
     qualificacio_usuari_llibre integer CHECK (qualificacio_usuari_llibre >= 1 AND qualificacio_usuari_llibre <= 5),
     CONSTRAINT fk_llibre_opinio FOREIGN KEY (id_llibre) REFERENCES Llibres (id_llibre),
     CONSTRAINT fk_usuari_opinio FOREIGN KEY (id_usuari) REFERENCES Usuaris (id_usuari)

);

-- Oscar Ballart Vilella
-- emmagatzema informació sobre les multes que s'han imposat als usuaris per tornar llibres fora de termini o en mal estat. 
-- cada registre representa una multa
CREATE TABLE Multes (
     id_multa serial NOT NULL,
     id_usuari integer NOT NULL,
     import_multa NUMERIC(10,2) NOT NULL,
     data_pagament_multa DATE NOT NULL,
     CONSTRAINT pk_multa PRIMARY KEY (id_multa),
     CONSTRAINT fk_usuari_multa FOREIGN KEY (id_usuari) REFERENCES Usuaris (id_usuari)
);

-- Oscar Ballart Vilella
-- Inserir dades en la taula Usuaris
INSERT INTO Usuaris (nom_usuari, cognom_usuari, email_usuari, contrasenya_usuari, rol_usuari) VALUES
('Oscar', 'Ballart', 'oscar.ballart@gmail.com', 'oballart&', 'administrador'),
('Valentina', 'Daniela', 'valentina.daniela@gmail.com', 'vdaniela&', 'administrador'),
('Juan', 'Gómez', 'juan.gomez@gmail.com', 'jgomez&', 'administrador'),
('Juan', 'Pérez', 'juan.perez@gmail.com', 'jp100000&', 'bibliotecario'),
('María', 'García', 'maria.garcia@gmail.com', 'mg110000&', 'bibliotecario'),
('Pedro', 'Rodríguez', 'pedro.rodriguez@gmail.com', 'pr120000&', 'bibliotecario'),
('Laura', 'Gómez', 'laura.gomez@hotmail.com', 'lg130000&', 'usuario'),
('Carlos', 'Hernández', 'carlos.hernandez@hotmail.com', 'ch140000&', 'usuario'),
('Carol', 'Díaz', 'carol.diaz@outlook.com', 'cd150000&', 'usuario'),
('Ana', 'Martínez', 'ana.martinez@hotmail.com', 'am160000&', 'usuario'),
('Jane', 'Smith', 'jane.smith@gmail.com', 'js170000&', 'usuario'),
('Bob', 'Johnson', 'bob.johnson@gmail.com', 'bj180000&', 'usuario'),
('Alice', 'Williams', 'alice.williams@hotmail.com', 'aw190000&', 'usuario'),
('David', 'Brown', 'david.brown@hotmail.com', 'db200000&', 'usuario'),
('Emma', 'Jones', 'emma.jones@hotmail.com', 'ej210000&', 'usuario'),
('Michael', 'Garcia', 'michael.garcia@hotmail.com', 'mg220000&', 'usuario'),
('Sarah', 'Miller', 'sarah.miller@hotmail.com', 'sm230000&', 'usuario'),
('James', 'Davis', 'james.davis@outlook.com', 'jd240000&', 'usuario'),
('Emily', 'Rodriguez', 'emily.rodriguez@outlook.com&', 'er250000', 'usuario');

-- Oscar Ballart Vilella
-- Inserir dades en la taula Llibres
INSERT INTO Llibres (titol_llibre, any_publicacio_llibre, ISBN_llibre, descripcio_llibre, nom_autor_llibre, cognom_autor_llibre, nom_editorial_llibre, nom_categoria_llibre, quantitat_total_llibre, quantitat_disponible_llibre) VALUES 
('Don Quijote de la Mancha', 1605, '978-84-376-0494-9', 'Novela escrita por Miguel de Cervantes que cuenta las aventuras del caballero andante Don Quijote y su escudero Sancho Panza.', 'Miguel', 'de Cervantes Saavedra', 'Cátedra', 'Novela', 3, 2),
('Cien años de soledad', 1967, '978-84-376-0494-9', 'Novela escrita por Gabriel García Márquez que cuenta la historia de la familia Buendía a lo largo de varias generaciones en el pueblo ficticio de Macondo.', 'Gabriel', 'García Márquez', 'Sudamericana', 'Novela', 2, 1),
('La Odisea', 800, '978-84-376-0494-9', 'Poema épico atribuido a Homero que narra las aventuras del héroe griego Odiseo durante su viaje de regreso a casa después de la guerra de Troya.', 'Homero', ' ', 'Gredos', 'Poesía épica', 1, 0),
('Don Juan Tenorio', 1844, '978-84-376-0494-9', 'Drama romántico en dos partes escrito por José Zorrilla que cuenta la historia del famoso seductor Don Juan Tenorio.', 'José', 'Zorrilla', 'Cátedra', 'Teatro', 2, 2),
('La casa de Bernarda Alba', 1936, '978-84-376-0494-9', 'Drama en tres actos escrito por Federico García Lorca que cuenta la historia de Bernarda Alba y sus cinco hijas después de la muerte de su segundo marido.', 'Federico', 'García Lorca', 'Cátedra', 'Teatro', 3, 3),
('El Conde Lucanor', 1335, '978-84-376-0494-9', 'Colección de cuentos escrita por Don Juan Manuel que narra las aventuras y enseñanzas del Conde Lucanor y su consejero Patronio.', 'Don Juan', 'Manuel', 'Cátedra', 'Narrativa breve', 1, 0),
('La casa de los espíritus', 1982, '978-84-376-0494-9', 'Novela realismo mágico', 'Isabel', 'Allende', 'Editorial Sudamericana', 'Literatura Latinoamericana', 3, 3),
('Rayuela', 1963, '978-84-376-0494-9', 'Novela realismo mágico', 'Julio', 'Cortázar', 'Editorial Sudamericana', 'Literatura Latinoamericana', 1, 1),
('Pedro Páramo', 1955, '978-84-204-8290-3', 'Novela realismo mágico','Juan', 'Rulfo', 'Editorial Fondo de Cultura Económica', 'Literatura Latinoamericana', 2, 2),
('La ciudad y los perros', 1963, '978-84-204-8290-3', 'Novela realismo mágico', 'Mario', 'Vargas Llosa', 'Editorial Seix Barral', 'Literatura Latinoamericana', 1, 1),
('El otoño del patriarca', 1975, '978-84-204-8290-3', 'Novela realismo mágico', 'Gabriel','García Márquez', 'Editorial Plaza & Janés', 'Literatura Latinoamericana', 5, 5),
('La tía Julia y el escribidor', 1977, '978-84-204-8290-3', 'Novela realismo mágico', 'Mario', 'Vargas Llosa', 'Editorial Seix Barral', 'Literatura Latinoamericana', 8, 8),
('El amor en los tiempos del cólera', 1985, '978-84-204-8290-3', 'Novela realismo mágico', 'Gabriel', 'García Márquez', 'Editorial Oveja Negra', 'Literatura Latinoamericana', 4, 4),
('La Celestina', 1499, '978-84-376-0495-0', 'Obra atribuida a Fernando de Rojas que cuenta la historia de amor entre Calisto y Melibea y cómo la alcahueta Celestina interviene en su relación.', 'Fernando', 'de Rojas', 'Cátedra', 'Teatro', 1, 1),
('Lazarillo de Tormes', 1554, '978-84-376-0496-7', 'Novela picaresca anónima que narra las aventuras del joven Lázaro de Tormes y sobre diferentes dueños.', 'Anónimo', ' ', 'Cátedra ', 'Narrativa breve', 1, 1),
('La vida se sueño', 1635, '978-84-376-0498-1','Obra teatral escrita por Pedro Calderón de la Barca que reflexiona sobre el libro albedrío y el destino a través del personaje Segismundo.', ' Pedro', 'Calderón de la Barca', 'Cátedra', 'Teatro', 1, 1),
('El sí de las niñas', 1806, '978 -84 -376 -0499 -8', 'Comedia escrita por Leandro Fernández Moratín que critica a los matrimonios forzados y defiende el derecho a elegir pareja.', 'Leandro', 'Fernández Moratín', 'Cátedra', 'Teatro', 1, 1),
('El Buscón', 1626, '978-84-376-0500-1', 'Novela picaresca escrita por Francisco de Quevedo que narra las aventuras del joven Pablos y su búsqueda de fortuna.', 'Francisco', 'de Quevedo ', 'Cátedra', 'Narrativa breve', 1, 1),
('Fuenteovejuna', 1619, '978-84-376-0501-8', 'Obra teatral escrita por Lope de Vega que cuenta la historia de la rebelión del pueblo de Fuenteovejuna contra su señor.', 'Lope', 'de Vega', 'Cátedra', 'Teatro', 1, 1),
('La Regenta' ,1884 ,'978 -84 -376 -0502 -5', 'Novela escrita por Leopoldo Alas “Clarín” que narra la vida de Ana Ozores y su relación con el Magistral Fermín de Paso y Álvaro Mesía.', 'Leopoldo', 'Alas Clarín', 'Cátedra', 'Novela', 1, 1),
('Tirant lo Blanc' ,1490 ,'978 -84 -376 -0503 -2', 'Novela caballeresca escrita por Joanot Martorell que cuenta las aventuras del caballero Tirant lo Blanc.', 'Joanot', 'Martorell', 'Cátedra ', 'Novela caballeresca', 1, 1);

-- Oscar Ballart Vilella
-- Inserir dades en la taula Etiquetes
INSERT INTO Etiquetes (nom_etiqueta_llibre, descripcio_etiqueta_llibre) VALUES 
('Aventuras', 'Libros que cuentan historias emocionantes y llenas de acción'),
('Amor', 'Libros que exploran el tema del amor y las relaciones románticas'),
('Historia', 'Libros que se basan en hechos históricos o que exploran temas históricos'),
('Misterio', 'Libros que cuentan historias llenas de intriga y suspense'),
('Ciencia ficción', 'Libros que exploran temas relacionados con la ciencia y la tecnología en un futuro imaginario o alternativo'),
('Fantasía', 'Libros que se desarrollan en mundos imaginarios y que incluyen elementos mágicos o sobrenaturales'),
('Realismo mágico' ,'Libros que contienen elementos de realismo mágico'),
('Familia' ,'Libros que tratan sobre relaciones familiares'),
('Romance', 'Libros que exploran relaciones amorosas y románticas'),
('Terror', 'Libros que buscan asustar o inquietar al lector con historias de miedo'),
('Histórico', 'Libros que recrean eventos históricos o épocas pasadas'),
('Biográfico', 'Libros que cuentan la vida de una persona real'),
('Autoayuda', 'Libros que ofrecen consejos y estrategias para mejorar la vida del lector'),
('Poesía', 'Libros que contienen poemas y versos'),
('Drama', 'Libros que exploran conflictos emocionales y relaciones humanas'),
('Comedia', 'Libros que buscan hacer reír al lector con situaciones divertidas'),
('Ciencia', 'Libros que explican conceptos científicos de manera accesible'),
('Política', 'Libros que analizan sistemas políticos y eventos históricos'),
('Filosofía', 'Libros que exploran ideas y conceptos filosóficos'),
('Religión', 'Libros que tratan temas relacionados con la fe y la espiritualidad'),
('Cocina', 'Libros que contienen receptas e información sobre gastronomía'),
('Negocios', 'Libros que ofrecen consejos y estrategias para el mundo empresarial'),
('Deportes', 'Libros que cuentan historias y anécdotas sobre deportes y atletas'),
('Viajes', 'Libros que relatan experiencias de viaje y ofrecen información sobre destinos turísticos'),
('Arte', 'Libros que exploran diferentes formas de expresión artística'),
('Música', 'Libros que cuentan la historia de la música y sus diferentes géneros'),
('Cine', 'Libros que analizan películas y la industria cinematográfica'),
('Teatro', 'Libros que contienen obras teatrales o exploran el mundo del teatro'),
('Moda', 'Libros que ofrecen información sobre tendencias y diseñadoras de moda');

-- Oscar Ballart Vilella
-- Inserir dades en la taula LlibresEtiquetes
INSERT INTO Llibres_Etiquetes (id_llibre, id_etiqueta) VALUES 
(1, 1),
(1, 3),
(2, 2),
(2, 3),
(3, 1),
(3, 3),
(11, 3),
(4, 2),
(4, 3),
(5, 2),
(5, 3),
(6, 1),
(6, 3);

-- Oscar Ballart Vilella
-- Inserir dades en la taula Prestecs
INSERT INTO Prestecs (id_llibre, id_usuari, data_prestec_llibre, data_devolucio_llibre) VALUES 
(6, 7, '2023-03-20', '2023-04-05'),
(11, 8, '2023-03-01', '2023-03-15'),
(1, 8, '2023-03-25', '2023-04-10'),
(2, 9, '2023-03-16', '2023-04-16'),
(3, 10, '2023-03-30', '2023-04-15');

-- Oscar Ballart Vilella
-- Inserir dades en la taula Reserves
INSERT INTO Reserves (id_llibre, id_usuari, data_reserva_llibre) VALUES 
(6, 7, '2023-03-01'),
(1, 8, '2023-03-05'),
(4, 8, '2023-03-05'),
(4, 9, '2023-03-10'),
(2, 9, '2023-03-16'),
(3, 10, '2023-03-10');

-- Oscar Ballart Vilella
-- Inserir dades en la taula Opinions
INSERT INTO Opinions (id_llibre, id_usuari, opinio_usuari_llibre, qualificacio_usuari_llibre) VALUES 
(1, 7, 'Me encantó este libro. La historia es emocionante y los personajes son muy interesantes.', 5),
(2, 9, 'Este libro es una obra maestra. La prosa es hermosa y la historia es conmovedora.', 5),
(7, 8, 'Me encantó esta novela. La recomiendo ampliamente.', 5),
(3, 8, 'Este libro es un poco difícil de seguir al principio pero una vez que te acostumbras al estilo es muy entretenido.', 4),
(6, 10, 'Una historia conmovedora', 4),
(4, 11, 'Un libro muy original', 5);

-- Oscar Ballart Vilella
-- Inserir dades en la taula Multes
INSERT INTO Multes (id_usuari, import_multa, data_pagament_multa) VALUES 
(5, 15.00, '2023-03-25'),
(6, 20.00, '2023-03-30'),
(7 ,20.00 ,'2023-04-17'),
(10, 25.00, '2023-04-05');