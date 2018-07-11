DROP TABLE IF EXISTS `bati_travaux`;
CREATE TABLE `bati_travaux` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dmdr_service` int(11) DEFAULT NULL,
  `dmdr_contact_nom` varchar(100) DEFAULT NULL,
  `dmdr_contact_email` varchar(255) DEFAULT NULL,
  `dem_date` date DEFAULT NULL,
  `dem_importance_travaux` int(11) DEFAULT NULL,
  `dem_type_travaux` int(11) DEFAULT NULL,
  `dem_description_travaux` text,
  `dem_commune` int(11) DEFAULT NULL,
  `dem_designation` int(11) DEFAULT NULL,
  `plan_service` int(11) DEFAULT NULL,
  `plan_entreprise` varchar(255) DEFAULT NULL,
  `plan_date` varchar(100) DEFAULT NULL,
  `plan_commentaire` text,
  `rea_date` date DEFAULT NULL,
  `rea_duree` int(11) DEFAULT NULL,
  `rea_commentaire` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `bati_rel_plan_fichier`;
CREATE TABLE `bati_rel_plan_fichier` (
  `id_demande` int(11) NOT NULL,
  `id_fichier` int(11) NOT NULL,
  PRIMARY KEY (`id_demande`,`id_fichier`),
  KEY `id_fichier` (`id_fichier`),
  CONSTRAINT `bati_rel_plan_fichier_ibfk_1` FOREIGN KEY (`id_demande`) REFERENCES `bati_travaux` (`id`) ON DELETE CASCADE,
  CONSTRAINT `bati_rel_plan_fichier_ibfk_2` FOREIGN KEY (`id_fichier`) REFERENCES `commons_fichier` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `bati_rel_rea_fichier`;
CREATE TABLE `bati_rel_rea_fichier` (
  `id_demande` int(11) NOT NULL,
  `id_fichier` int(11) NOT NULL,
  PRIMARY KEY (`id_demande`,`id_fichier`),
  KEY `id_fichier` (`id_fichier`),
  CONSTRAINT `bati_rel_rea_fichier_ibfk_1` FOREIGN KEY (`id_demande`) REFERENCES `bati_travaux` (`id`) ON DELETE CASCADE,
  CONSTRAINT `bati_rel_rea_fichier_ibfk_2` FOREIGN KEY (`id_fichier`) REFERENCES `commons_fichier` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `bati_rel_travaux_fichier`;
CREATE TABLE `bati_rel_travaux_fichier` (
  `id_demande` int(11) NOT NULL,
  `id_fichier` int(11) NOT NULL,
  PRIMARY KEY (`id_demande`,`id_fichier`),
  KEY `id_fichier` (`id_fichier`),
  CONSTRAINT `bati_rel_travaux_fichier_ibfk_1` FOREIGN KEY (`id_demande`) REFERENCES `bati_travaux` (`id`) ON DELETE CASCADE,
  CONSTRAINT `bati_rel_travaux_fichier_ibfk_2` FOREIGN KEY (`id_fichier`) REFERENCES `commons_fichier` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `ref_geo_batiment`;
CREATE TABLE `ref_geo_batiment` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `ref_commune` int(11) DEFAULT NULL,
      `reference` varchar(10) DEFAULT NULL,
      `lieu_dit` varchar(255) DEFAULT NULL,
      `designation` varchar(255) DEFAULT NULL,
      PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `ref_geo_commune`;
CREATE TABLE `ref_geo_commune` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `nom_commune` varchar(255) DEFAULT NULL,
      PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


INSERT INTO th_thesaurus (id_ref, label) VALUES (0, 'services_travaux');
INSERT INTO th_thesaurus (id_ref, label) VALUES (0, 'types_travaux');
INSERT INTO th_thesaurus (id_ref, label) VALUES (0, 'charges_travaux');

INSERT INTO th_thesaurus (id_ref, label) VALUES (74, 'Direction');
INSERT INTO th_thesaurus (id_ref, label) VALUES (74, 'SAS');
INSERT INTO th_thesaurus (id_ref, label) VALUES (74, 'SCVT');
INSERT INTO th_thesaurus (id_ref, label) VALUES (74, 'SDD');
INSERT INTO th_thesaurus (id_ref, label) VALUES (74, 'SG');
INSERT INTO th_thesaurus (id_ref, label) VALUES (74, 'PAUP');
INSERT INTO th_thesaurus (id_ref, label) VALUES (74, 'RT');

INSERT INTO th_thesaurus (id_ref, label) VALUES (75, 'autres');
INSERT INTO th_thesaurus (id_ref, label) VALUES (75, 'chauffage');
INSERT INTO th_thesaurus (id_ref, label) VALUES (75, 'clôture');
INSERT INTO th_thesaurus (id_ref, label) VALUES (75, 'électricité');
INSERT INTO th_thesaurus (id_ref, label) VALUES (75, 'escalier');
INSERT INTO th_thesaurus (id_ref, label) VALUES (75, 'étanchéité');
INSERT INTO th_thesaurus (id_ref, label) VALUES (75, 'fosse septique');
INSERT INTO th_thesaurus (id_ref, label) VALUES (75, 'isolation');
INSERT INTO th_thesaurus (id_ref, label) VALUES (75, 'menuiseries');
INSERT INTO th_thesaurus (id_ref, label) VALUES (75, 'mise aux normes électriques');
INSERT INTO th_thesaurus (id_ref, label) VALUES (75, 'mise aux normes incendie');
INSERT INTO th_thesaurus (id_ref, label) VALUES (75, 'mur');
INSERT INTO th_thesaurus (id_ref, label) VALUES (75, 'mur soutènement');
INSERT INTO th_thesaurus (id_ref, label) VALUES (75, 'peinture');
INSERT INTO th_thesaurus (id_ref, label) VALUES (75, 'plafond');
INSERT INTO th_thesaurus (id_ref, label) VALUES (75, 'plancher, sol, carrelage');
INSERT INTO th_thesaurus (id_ref, label) VALUES (75, 'plomberie');
INSERT INTO th_thesaurus (id_ref, label) VALUES (75, 'sanitaires');
INSERT INTO th_thesaurus (id_ref, label) VALUES (75, 'toiture');

INSERT INTO th_thesaurus (id_ref, label) VALUES (76, 'PAUP (Chargé mission architecture)');
INSERT INTO th_thesaurus (id_ref, label) VALUES (76, 'PAUP (Chargé mission urbanisme-paysage)');
INSERT INTO th_thesaurus (id_ref, label) VALUES (76, 'PAUP (technicien Massifs Aigoual et Causses Gorges)');
INSERT INTO th_thesaurus (id_ref, label) VALUES (76, 'PAUP (technicien Massifs Mont Lozère et Vallées Cévenoles)');
INSERT INTO th_thesaurus (id_ref, label) VALUES (76, 'Régie technique');


INSERT INTO ref_geo_commune (nom_commune) VALUES ('Aumessas'),
('Alès'),
('Barre des Cévennes'),
('Bassurels'),
('Cans et Cévennes'),
('Cassagnas'), 
('Dourbies'),
('Florac Trois Rivières'),
('Génolhac'),
('Hures la Parade'),
('Lanuéjols'),
('Le Vigan'),
('Molezon'),
('Mont Lozère et Goulet'),
('Pont de Montvert-Sud Mont Lozère'),
('Rousses'),
('Saint André de Lancize'),
('Saint Martin de Lansuscle'),
('Sainte Croix Vallée Française'),
('Vallerauge'),
('Ventalon en Cévennes'),
('Vialas');


INSERT INTO ref_geo_batiment (ref_commune, reference, lieu_dit, designation) VALUES (1,'1','le Lingas','logement de berger'),
(2,'L1','21 rue Soubeyranne','bureau'),
(3,'12','le Bourg','logement'),
(3,'13','le Bramadou','ferme sans affectation'),
(4,'14','Aire de Côtes','Maison forestière d''Aire de Côte'),
(5,'15','Mijavols, Saint Julien d''Arpaon','logement de berger'),
(5,'16','Ventajols, Saint Julien d''Arpaon','logement'),
(5,'17','Las Parets, Saint Julien d''Arpaon','jas d''estive'),
(6,'18','les Crozes Bas','bureaux et logement'),
(6,'19','Roche Courbade','bergerie d''estive'),
(6,'20','La Baume','ruines'),
(6,'21','la Loubière','logement berger'),
(7,'2a','les Pises ','observatoire astronomique'),
(7,'2b','les Pises','gîte'),
(7,'3','Les Pises ','barrage'),
(7,'4a','les Laupies-village','logement de berger '),
(7,'4b','les Laupies-village',' grange'),
(7,'5','les Laupies','logement de berger'),
(7,'6','les Laupies-Pradinas','ferme d\'estive désaffectée'),
(7,'7a','la Borie du Pont','logement de berger'),
(7,'7b','la Borie du Pont','logement vacant'),
(7,'7c','la Borie du Pont','grange'),
(7,'7d','la Borie du Pont','écurie (toit chaume)'),
(8,'22','24 rue du lotissement la Grézotière','logement de la Grézotière Bleue'),
(8,'23','20 rue du lotissement la Grézotière','logement de la Grézotière Verte'),
(8,'24a','6 bis place du Palais','centre administratif (direction)'),
(8,'24b','6 bis place du Palais','centre administratif (château)'),
(8,'24c','6 bis place du Palais','centre info'),
(8,'25','rue des Aires','atelier'),
(8,'26','Place du Palais','bureau ancien tribunal'),
(8,'27','51 av Jean Monestier','garage'),
(8,'L4','1 rue de la Serve','garage Gleize'),
(9,'8','Village','Maison de l''Arceau'),
(9,'9','Grand Rue','Maison Fontvive'),
(10,'28a','Drigas','logement'),
(10,'28b','Drigas','grange'),
(10,'29a','le Villaret','bureau'),
(10,'29b','le Villaret','four à pain et atelier'),
(11,'10','Aiguebonne-Randavel','emphytéote : M.JAILLET'),
(12,'L3','2 rue du Maquis','bureau'),
(13,'30','Lou Poux','tour de Canourgue'),
(13,'L6','la Roque','magnanerie '),
(14,'L5','Mas d''Oricères, Finiels','logement de berger'),
(15,'31','la Paro','Maison du Mont Lozère'),
(15,'32','l''Estournal','bureau'),
(15,'33','Mas Camargue','ferme, grange et moulin'),
(15,'34','Bellecoste','logement de berger'),
(15,'35','Mas Camargue ','logement de berger'),
(16,'36','Massevaques','logement de berger'),
(17,'37','la Roche','logement vacant'),
(18,'38','Saint Clément ','vestige villa romaine'),
(18,'39','Saint Clément ','ancien mas'),
(19,'40a','Ségalières','logement vacant'),
(19,'40b','Ségalières','bergerie et clède'),
(20,'11','Col de la Serreyrède','boutique, office de tourisme, bureaux'),
(20,'L2','Aigoual','logement de berger'),
(21,'41','Clerguemort','logement'),
(22,'42','Bayard','logement de berger'),
(22,'43','Gourdouze ','refuge'),
(22,'44','Gourdouze ','ferme en ruine'),
(22,'45','Gourdouze ','Maisons');
