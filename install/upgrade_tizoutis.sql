alter table auth_utilisateur add column nom varchar(100);
alter table auth_utilisateur add column prenom varchar(100);
alter table recr_agent_detail add column convention_signee integer(11);
alter table recr_agent_detail add column notif_list text not null default '';
alter table recr_agent_detail add column bureau varchar(50);
alter table ann_correspondant add column adresse2 varchar(255);
alter table ann_commune add column adresse2 varchar(255);
alter table ann_entreprise add column fonction_gerant varchar(255) default 'Gérant';
alter table ann_entreprise add column alt_email varchar(255);
alter table recr_agent add column intitule_poste varchar(255);
alter table intv_demande add column num_intv varchar(50);