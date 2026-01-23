-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: restaurant_db
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=87 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',3,'add_permission'),(6,'Can change permission',3,'change_permission'),(7,'Can delete permission',3,'delete_permission'),(8,'Can view permission',3,'view_permission'),(9,'Can add group',2,'add_group'),(10,'Can change group',2,'change_group'),(11,'Can delete group',2,'delete_group'),(12,'Can view group',2,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add Utilisateur',6,'add_customuser'),(22,'Can change Utilisateur',6,'change_customuser'),(23,'Can delete Utilisateur',6,'delete_customuser'),(24,'Can view Utilisateur',6,'view_customuser'),(25,'Can add Table',7,'add_tablerestaurant'),(26,'Can change Table',7,'change_tablerestaurant'),(27,'Can delete Table',7,'delete_tablerestaurant'),(28,'Can view Table',7,'view_tablerestaurant'),(29,'Can add Plat',8,'add_plat'),(30,'Can change Plat',8,'change_plat'),(31,'Can delete Plat',8,'delete_plat'),(32,'Can view Plat',8,'view_plat'),(33,'Can add Panier',11,'add_panier'),(34,'Can change Panier',11,'change_panier'),(35,'Can delete Panier',11,'delete_panier'),(36,'Can view Panier',11,'view_panier'),(37,'Can add Article du panier',12,'add_panieritem'),(38,'Can change Article du panier',12,'change_panieritem'),(39,'Can delete Article du panier',12,'delete_panieritem'),(40,'Can view Article du panier',12,'view_panieritem'),(41,'Can add Commande',9,'add_commande'),(42,'Can change Commande',9,'change_commande'),(43,'Can delete Commande',9,'delete_commande'),(44,'Can view Commande',9,'view_commande'),(45,'Peut voir toutes les commandes',9,'can_view_all_orders'),(46,'Peut marquer une commande comme servie',9,'can_serve_order'),(47,'Peut enregistrer un paiement',9,'can_pay_order'),(48,'Can add Article de commande',10,'add_commandeitem'),(49,'Can change Article de commande',10,'change_commandeitem'),(50,'Can delete Article de commande',10,'delete_commandeitem'),(51,'Can view Article de commande',10,'view_commandeitem'),(52,'Can add Caisse',13,'add_caisse'),(53,'Can change Caisse',13,'change_caisse'),(54,'Can delete Caisse',13,'delete_caisse'),(55,'Can view Caisse',13,'view_caisse'),(56,'Peut ouvrir la caisse',13,'can_open_register'),(57,'Peut fermer la caisse',13,'can_close_register'),(58,'Peut voir les détails de la caisse',13,'can_view_register'),(59,'Can add Paiement',14,'add_paiement'),(60,'Can change Paiement',14,'change_paiement'),(61,'Can delete Paiement',14,'delete_paiement'),(62,'Can view Paiement',14,'view_paiement'),(63,'Peut enregistrer un paiement',14,'can_register_payment'),(64,'Peut voir les détails des paiements',14,'can_view_payment'),(65,'Can add Type de dépense',16,'add_typedepense'),(66,'Can change Type de dépense',16,'change_typedepense'),(67,'Can delete Type de dépense',16,'delete_typedepense'),(68,'Can view Type de dépense',16,'view_typedepense'),(69,'Can add Sortie de caisse',15,'add_sortiecaisse'),(70,'Can change Sortie de caisse',15,'change_sortiecaisse'),(71,'Can delete Sortie de caisse',15,'delete_sortiecaisse'),(72,'Can view Sortie de caisse',15,'view_sortiecaisse'),(73,'Peut enregistrer une dépense',15,'can_register_expense'),(74,'Peut voir les détails des dépenses',15,'can_view_expense'),(75,'Can add Dépense',17,'add_depense'),(76,'Can change Dépense',17,'change_depense'),(77,'Can delete Dépense',17,'delete_depense'),(78,'Can view Dépense',17,'view_depense'),(79,'Can add dummy dashboard model',18,'add_dummydashboardmodel'),(80,'Can change dummy dashboard model',18,'change_dummydashboardmodel'),(81,'Can delete dummy dashboard model',18,'delete_dummydashboardmodel'),(82,'Can view dummy dashboard model',18,'view_dummydashboardmodel'),(83,'Can add Catégorie',19,'add_categorieplat'),(84,'Can change Catégorie',19,'change_categorieplat'),(85,'Can delete Catégorie',19,'delete_categorieplat'),(86,'Can view Catégorie',19,'view_categorieplat');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `caisse`
--

DROP TABLE IF EXISTS `caisse`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `caisse` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `solde_initial` decimal(12,2) NOT NULL,
  `solde_actuel` decimal(12,2) NOT NULL,
  `notes` longtext NOT NULL,
  `notes_fermeture` longtext NOT NULL,
  `date_ouverture` datetime(6) NOT NULL,
  `date_fermeture` datetime(6) DEFAULT NULL,
  `est_ouverte` tinyint(1) NOT NULL,
  `utilisateur_fermeture_id` bigint DEFAULT NULL,
  `utilisateur_ouverture_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `caisse_utilisateur_fermeture_id_b8224932_fk_users_id` (`utilisateur_fermeture_id`),
  KEY `caisse_utilisateur_ouverture_id_2fc54c64_fk_users_id` (`utilisateur_ouverture_id`),
  CONSTRAINT `caisse_utilisateur_fermeture_id_b8224932_fk_users_id` FOREIGN KEY (`utilisateur_fermeture_id`) REFERENCES `users` (`id`),
  CONSTRAINT `caisse_utilisateur_ouverture_id_2fc54c64_fk_users_id` FOREIGN KEY (`utilisateur_ouverture_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `caisse`
--

LOCK TABLES `caisse` WRITE;
/*!40000 ALTER TABLE `caisse` DISABLE KEYS */;
INSERT INTO `caisse` VALUES (1,5000.00,5000.00,'PAS DE PIMENT','','2025-12-25 16:03:55.559044','2025-12-27 12:17:18.440679',0,1,3),(2,0.00,0.00,'','','2025-12-27 12:42:01.780213','2025-12-27 14:02:45.316483',0,1,1),(3,0.00,1932.00,'','','2025-12-27 14:03:13.244508',NULL,1,NULL,1);
/*!40000 ALTER TABLE `caisse` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories_plats`
--

DROP TABLE IF EXISTS `categories_plats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories_plats` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) NOT NULL,
  `ordre` int unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nom` (`nom`),
  CONSTRAINT `categories_plats_chk_1` CHECK ((`ordre` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories_plats`
--

LOCK TABLES `categories_plats` WRITE;
/*!40000 ALTER TABLE `categories_plats` DISABLE KEYS */;
INSERT INTO `categories_plats` VALUES (1,'Poulet',0),(2,'Jus',1),(3,'Viande',2),(4,'Poisson',3),(5,'Chawarma',4);
/*!40000 ALTER TABLE `categories_plats` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `commande_items`
--

DROP TABLE IF EXISTS `commande_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `commande_items` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `quantite` int unsigned NOT NULL,
  `prix_unitaire` decimal(10,2) NOT NULL,
  `notes` longtext NOT NULL,
  `commande_id` bigint NOT NULL,
  `plat_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `commande_items_commande_id_12469e12_fk_commandes_id` (`commande_id`),
  KEY `commande_items_plat_id_5b0f5bc4_fk_plats_id` (`plat_id`),
  CONSTRAINT `commande_items_commande_id_12469e12_fk_commandes_id` FOREIGN KEY (`commande_id`) REFERENCES `commandes` (`id`),
  CONSTRAINT `commande_items_plat_id_5b0f5bc4_fk_plats_id` FOREIGN KEY (`plat_id`) REFERENCES `plats` (`id`),
  CONSTRAINT `commande_items_chk_1` CHECK ((`quantite` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `commande_items`
--

LOCK TABLES `commande_items` WRITE;
/*!40000 ALTER TABLE `commande_items` DISABLE KEYS */;
INSERT INTO `commande_items` VALUES (1,1,22.00,'beaucoup de frommage',1,2),(2,1,22.00,'',2,2),(3,2,300.00,'',2,3),(4,1,22.00,'',3,2),(5,1,300.00,'',3,3);
/*!40000 ALTER TABLE `commande_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `commandes`
--

DROP TABLE IF EXISTS `commandes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `commandes` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `numero_commande` varchar(50) NOT NULL,
  `montant_total` decimal(10,2) NOT NULL,
  `statut` varchar(20) NOT NULL,
  `date_commande` datetime(6) NOT NULL,
  `date_service` datetime(6) DEFAULT NULL,
  `date_paiement` datetime(6) DEFAULT NULL,
  `notes` longtext NOT NULL,
  `table_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `numero_commande` (`numero_commande`),
  KEY `commandes_table_id_b34575b3_fk_tables_restaurant_id` (`table_id`),
  CONSTRAINT `commandes_table_id_b34575b3_fk_tables_restaurant_id` FOREIGN KEY (`table_id`) REFERENCES `tables_restaurant` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `commandes`
--

LOCK TABLES `commandes` WRITE;
/*!40000 ALTER TABLE `commandes` DISABLE KEYS */;
INSERT INTO `commandes` VALUES (1,'CMD-20251227-0001',22.00,'payee','2025-12-27 16:11:30.319504','2025-12-27 16:14:26.328590','2025-12-30 10:44:48.600816','pas d\'oignons',2),(2,'CMD-20251230-0001',622.00,'payee','2025-12-30 10:26:59.878222','2025-12-30 10:39:28.882518','2025-12-30 10:51:58.852380','',3),(3,'CMD-20251230-0002',322.00,'payee','2025-12-30 10:27:48.779310','2025-12-30 10:29:56.063433','2025-12-30 10:44:18.319125','',3);
/*!40000 ALTER TABLE `commandes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `depenses`
--

DROP TABLE IF EXISTS `depenses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `depenses` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `montant` decimal(10,2) NOT NULL,
  `motif` varchar(255) NOT NULL,
  `date_depense` datetime(6) NOT NULL,
  `justificatif` varchar(100) DEFAULT NULL,
  `notes` longtext NOT NULL,
  `caisse_id` bigint NOT NULL,
  `type_depense_id` bigint NOT NULL,
  `utilisateur_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `depenses_caisse_id_4d6e9eed_fk_caisse_id` (`caisse_id`),
  KEY `depenses_type_depense_id_f0e1971c_fk_types_depense_id` (`type_depense_id`),
  KEY `depenses_utilisateur_id_28e8a2f6_fk_users_id` (`utilisateur_id`),
  CONSTRAINT `depenses_caisse_id_4d6e9eed_fk_caisse_id` FOREIGN KEY (`caisse_id`) REFERENCES `caisse` (`id`),
  CONSTRAINT `depenses_type_depense_id_f0e1971c_fk_types_depense_id` FOREIGN KEY (`type_depense_id`) REFERENCES `types_depense` (`id`),
  CONSTRAINT `depenses_utilisateur_id_28e8a2f6_fk_users_id` FOREIGN KEY (`utilisateur_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `depenses`
--

LOCK TABLES `depenses` WRITE;
/*!40000 ALTER TABLE `depenses` DISABLE KEYS */;
/*!40000 ALTER TABLE `depenses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_users_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(2,'auth','group'),(3,'auth','permission'),(6,'authentication','customuser'),(4,'contenttypes','contenttype'),(18,'dashboard','dummydashboardmodel'),(17,'expenses','depense'),(19,'menu','categorieplat'),(8,'menu','plat'),(9,'orders','commande'),(10,'orders','commandeitem'),(11,'orders','panier'),(12,'orders','panieritem'),(13,'payments','caisse'),(14,'payments','paiement'),(15,'payments','sortiecaisse'),(16,'payments','typedepense'),(5,'sessions','session'),(7,'tables','tablerestaurant');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-12-25 15:44:03.344360'),(2,'contenttypes','0002_remove_content_type_name','2025-12-25 15:44:03.474459'),(3,'auth','0001_initial','2025-12-25 15:44:03.759663'),(4,'auth','0002_alter_permission_name_max_length','2025-12-25 15:44:03.819225'),(5,'auth','0003_alter_user_email_max_length','2025-12-25 15:44:03.821736'),(6,'auth','0004_alter_user_username_opts','2025-12-25 15:44:03.828416'),(7,'auth','0005_alter_user_last_login_null','2025-12-25 15:44:03.833119'),(8,'auth','0006_require_contenttypes_0002','2025-12-25 15:44:03.836019'),(9,'auth','0007_alter_validators_add_error_messages','2025-12-25 15:44:03.841086'),(10,'auth','0008_alter_user_username_max_length','2025-12-25 15:44:03.845479'),(11,'auth','0009_alter_user_last_name_max_length','2025-12-25 15:44:03.850029'),(12,'auth','0010_alter_group_name_max_length','2025-12-25 15:44:03.864733'),(13,'auth','0011_update_proxy_permissions','2025-12-25 15:44:03.874561'),(14,'auth','0012_alter_user_first_name_max_length','2025-12-25 15:44:03.881503'),(15,'authentication','0001_initial','2025-12-25 15:44:04.163237'),(16,'admin','0001_initial','2025-12-25 15:44:04.290441'),(17,'admin','0002_logentry_remove_auto_add','2025-12-25 15:44:04.294550'),(18,'admin','0003_logentry_add_action_flag_choices','2025-12-25 15:44:04.302868'),(19,'sessions','0001_initial','2025-12-25 15:44:04.363111'),(20,'dashboard','0001_initial','2025-12-25 15:58:03.312323'),(21,'tables','0001_initial','2025-12-25 15:58:03.415604'),(22,'menu','0001_initial','2025-12-25 15:58:03.432075'),(23,'orders','0001_initial','2025-12-25 15:58:03.887081'),(24,'payments','0001_initial','2025-12-25 15:58:04.437046'),(25,'expenses','0001_initial','2025-12-25 15:58:04.636747'),(26,'payments','0002_paiement_est_valide','2025-12-30 10:38:42.885642'),(27,'tables','0002_alter_tablerestaurant_user','2025-12-30 10:38:43.251991'),(28,'orders','0002_panier_created_by','2025-12-30 11:01:50.053045'),(29,'authentication','0002_alter_customuser_role','2026-01-05 14:52:55.266939'),(30,'menu','0002_plat_categorie_plat_description','2026-01-05 14:52:55.354753'),(31,'menu','0003_plat_categorie_choices','2026-01-05 14:52:55.379273'),(32,'menu','0004_categories_plats','2026-01-05 14:52:55.450168'),(33,'tables','0003_tablerestaurant_nombre_clients_actuels','2026-01-05 14:52:55.628417');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('3sgokp2lmvpbfdg1ufbtqoq91d9m7i7f','.eJxVjEEOwiAQRe_C2hCmdKbUpXvPQAYGpGpoUtqV8e7apAvd_vfefynP21r81tLiJ1Fn5dTpdwscH6nuQO5cb7OOc12XKehd0Qdt-jpLel4O9--gcCvfOkiINg8OrO3IJMoggAAwWGOIESSMwSHgKMwZGYl7cLETIbK9JafeH9Y0NzU:1vaa8l:yERb4QPhoCtR9_BL7ruT6y4aNghzeGdwrx9fA0iz0tg','2025-12-30 14:21:59.318108'),('gxzcljv0o9gb5bv7b96e549pmorpktxt','.eJxVjMEOwiAQRP-FsyG7WKF49N5vIAvLStXQpLQn47_bJj3oZQ7z3sxbBVqXEtaW5zCyuiqnTr9dpPTMdQf8oHqfdJrqMo9R74o-aNPDxPl1O9y_g0KtbOsuGehdNgbonCwIxYgIiWIvGcSDvzhBRnLYWTGJLaLdwkfO7ERAfb7pWThN:1vbepv:355717sJQOrJrNNZmcWbCG8lqMZDfPqi-q41Qjd8z9M','2026-01-02 13:34:59.550498'),('mr7gchzoggkvevkieqgup8equ2jy5bcs','.eJxVjMEOwiAQRP-FsyG7WKF49N5vIAvLStXQpLQn47_bJj3oZQ7z3sxbBVqXEtaW5zCyuiqnTr9dpPTMdQf8oHqfdJrqMo9R74o-aNPDxPl1O9y_g0KtbOsuGehdNgbonCwIxYgIiWIvGcSDvzhBRnLYWTGJLaLdwkfO7ERAfb7pWThN:1vabOn:r0QwCR7Rs-yLr6tFq-IEq7nIvtoAb0cn9dvkgbQ_fMA','2025-12-30 15:42:37.990292'),('paa947v3vltnmkj2e99fh4ux7wtisnkl','.eJxVjMEOwiAQRP-FsyG7WKF49N5vIAvLStXQpLQn47_bJj3oZQ7z3sxbBVqXEtaW5zCyuiqnTr9dpPTMdQf8oHqfdJrqMo9R74o-aNPDxPl1O9y_g0KtbOsuGehdNgbonCwIxYgIiWIvGcSDvzhBRnLYWTGJLaLdwkfO7ERAfb7pWThN:1vaeIQ:-7anfn-3etUocOGT6uA4iz2d7I2dZDXTJPid3tUlm9A','2025-12-30 18:48:14.177253'),('wttl3zrsxs3nm7rpx7hq9r7ttuj74cwv','.eJxVjMEOwiAQRP-FsyG7WKF49N5vIAvLStXQpLQn47_bJj3oZQ7z3sxbBVqXEtaW5zCyuiqnTr9dpPTMdQf8oHqfdJrqMo9R74o-aNPDxPl1O9y_g0KtbOsuGehdNgbonCwIxYgIiWIvGcSDvzhBRnLYWTGJLaLdwkfO7ERAfb7pWThN:1vafHT:KN9CWwSge2zpJVWvIoczs8mAJEoLHYlO4p0evAvrFJ4','2025-12-30 19:51:19.742855');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `paiements`
--

DROP TABLE IF EXISTS `paiements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `paiements` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `montant` decimal(10,2) NOT NULL,
  `mode_paiement` varchar(10) NOT NULL,
  `reference` varchar(100) NOT NULL,
  `date_paiement` datetime(6) NOT NULL,
  `notes` longtext NOT NULL,
  `caisse_id` bigint NOT NULL,
  `commande_id` bigint NOT NULL,
  `utilisateur_id` bigint NOT NULL,
  `est_valide` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `commande_id` (`commande_id`),
  KEY `paiements_caisse_id_2d59870f_fk_caisse_id` (`caisse_id`),
  KEY `paiements_utilisateur_id_d09c2f9f_fk_users_id` (`utilisateur_id`),
  CONSTRAINT `paiements_caisse_id_2d59870f_fk_caisse_id` FOREIGN KEY (`caisse_id`) REFERENCES `caisse` (`id`),
  CONSTRAINT `paiements_commande_id_2c6f25fc_fk_commandes_id` FOREIGN KEY (`commande_id`) REFERENCES `commandes` (`id`),
  CONSTRAINT `paiements_utilisateur_id_d09c2f9f_fk_users_id` FOREIGN KEY (`utilisateur_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `paiements`
--

LOCK TABLES `paiements` WRITE;
/*!40000 ALTER TABLE `paiements` DISABLE KEYS */;
INSERT INTO `paiements` VALUES (1,322.00,'especes','','2025-12-30 10:44:18.324217','',3,3,8,1),(2,22.00,'especes','','2025-12-30 10:44:48.605339','',3,1,8,1),(3,622.00,'especes','','2025-12-30 10:51:58.859045','',3,2,8,1);
/*!40000 ALTER TABLE `paiements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `panier_items`
--

DROP TABLE IF EXISTS `panier_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `panier_items` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `quantite` int unsigned NOT NULL,
  `prix_unitaire` decimal(10,2) NOT NULL,
  `notes` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `panier_id` bigint NOT NULL,
  `plat_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `panier_items_panier_id_plat_id_9b17b512_uniq` (`panier_id`,`plat_id`),
  KEY `panier_items_plat_id_9e041d0b_fk_plats_id` (`plat_id`),
  CONSTRAINT `panier_items_panier_id_a25aaddf_fk_paniers_id` FOREIGN KEY (`panier_id`) REFERENCES `paniers` (`id`),
  CONSTRAINT `panier_items_plat_id_9e041d0b_fk_plats_id` FOREIGN KEY (`plat_id`) REFERENCES `plats` (`id`),
  CONSTRAINT `panier_items_chk_1` CHECK ((`quantite` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `panier_items`
--

LOCK TABLES `panier_items` WRITE;
/*!40000 ALTER TABLE `panier_items` DISABLE KEYS */;
INSERT INTO `panier_items` VALUES (1,1,22.00,'beaucoup de frommage','2025-12-27 16:10:45.161981',1,2),(2,2,300.00,'','2025-12-30 10:22:11.417299',2,3),(3,1,22.00,'','2025-12-30 10:25:08.350291',2,2),(4,1,300.00,'','2025-12-30 10:27:27.240231',3,3),(5,1,22.00,'','2025-12-30 10:27:33.321589',3,2);
/*!40000 ALTER TABLE `panier_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `paniers`
--

DROP TABLE IF EXISTS `paniers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `paniers` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `table_id` bigint NOT NULL,
  `created_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `paniers_table_id_a5c475dd_fk_tables_restaurant_id` (`table_id`),
  KEY `paniers_created_by_id_14f7957b_fk_users_id` (`created_by_id`),
  CONSTRAINT `paniers_created_by_id_14f7957b_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `paniers_table_id_a5c475dd_fk_tables_restaurant_id` FOREIGN KEY (`table_id`) REFERENCES `tables_restaurant` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `paniers`
--

LOCK TABLES `paniers` WRITE;
/*!40000 ALTER TABLE `paniers` DISABLE KEYS */;
INSERT INTO `paniers` VALUES (1,0,'2025-12-27 16:10:45.158239','2025-12-27 16:11:30.323704',2,NULL),(2,0,'2025-12-30 10:22:11.410209','2025-12-30 10:26:59.886815',3,NULL),(3,0,'2025-12-30 10:26:59.887816','2025-12-30 10:27:48.782930',3,NULL),(4,0,'2025-12-30 10:27:48.782930','2025-12-30 10:27:48.782930',3,NULL),(5,0,'2025-12-30 10:44:18.328940','2025-12-30 10:44:18.328940',3,NULL),(6,1,'2025-12-30 10:44:48.611629','2025-12-30 10:44:48.611629',2,NULL),(7,1,'2025-12-30 10:51:58.864518','2025-12-30 10:51:58.864518',3,NULL);
/*!40000 ALTER TABLE `paniers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `plats`
--

DROP TABLE IF EXISTS `plats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `plats` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nom` varchar(200) NOT NULL,
  `prix_unitaire` decimal(10,2) NOT NULL,
  `image` varchar(100) NOT NULL,
  `disponible` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `categorie` varchar(100) NOT NULL,
  `description` longtext NOT NULL DEFAULT (_utf8mb4''),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `plats`
--

LOCK TABLES `plats` WRITE;
/*!40000 ALTER TABLE `plats` DISABLE KEYS */;
INSERT INTO `plats` VALUES (2,'pizza',22.00,'plats/134099780150277525.jpg',1,'2025-12-27 16:03:23.182095','2025-12-27 16:03:23.182095','Poulet',''),(3,'chawarma',300.00,'plats/img1.jpg',1,'2025-12-30 10:13:35.677259','2025-12-30 10:13:35.677259','Poulet','');
/*!40000 ALTER TABLE `plats` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sorties_caisse`
--

DROP TABLE IF EXISTS `sorties_caisse`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sorties_caisse` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `montant` decimal(10,2) NOT NULL,
  `date_sortie` datetime(6) NOT NULL,
  `motif` varchar(255) NOT NULL,
  `justificatif` varchar(100) DEFAULT NULL,
  `notes` longtext NOT NULL,
  `caisse_id` bigint NOT NULL,
  `utilisateur_id` bigint NOT NULL,
  `type_depense_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `sorties_caisse_caisse_id_c8981a87_fk_caisse_id` (`caisse_id`),
  KEY `sorties_caisse_utilisateur_id_5c7be3ef_fk_users_id` (`utilisateur_id`),
  KEY `sorties_caisse_type_depense_id_a17a252d_fk_types_depense_id` (`type_depense_id`),
  CONSTRAINT `sorties_caisse_caisse_id_c8981a87_fk_caisse_id` FOREIGN KEY (`caisse_id`) REFERENCES `caisse` (`id`),
  CONSTRAINT `sorties_caisse_type_depense_id_a17a252d_fk_types_depense_id` FOREIGN KEY (`type_depense_id`) REFERENCES `types_depense` (`id`),
  CONSTRAINT `sorties_caisse_utilisateur_id_5c7be3ef_fk_users_id` FOREIGN KEY (`utilisateur_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sorties_caisse`
--

LOCK TABLES `sorties_caisse` WRITE;
/*!40000 ALTER TABLE `sorties_caisse` DISABLE KEYS */;
/*!40000 ALTER TABLE `sorties_caisse` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tables_restaurant`
--

DROP TABLE IF EXISTS `tables_restaurant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tables_restaurant` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `numero_table` varchar(50) NOT NULL,
  `nombre_places` int unsigned NOT NULL,
  `current_status` varchar(30) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` bigint DEFAULT NULL,
  `nombre_clients_actuels` int unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `numero_table` (`numero_table`),
  KEY `tables_restaurant_user_id_a4e739d0` (`user_id`),
  CONSTRAINT `tables_restaurant_user_id_a4e739d0_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `tables_restaurant_chk_1` CHECK ((`nombre_places` >= 0)),
  CONSTRAINT `tables_restaurant_chk_2` CHECK ((`nombre_clients_actuels` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tables_restaurant`
--

LOCK TABLES `tables_restaurant` WRITE;
/*!40000 ALTER TABLE `tables_restaurant` DISABLE KEYS */;
INSERT INTO `tables_restaurant` VALUES (2,'T002',8,'libre','2025-12-27 16:02:13.092562','2025-12-30 13:51:55.228563',5,0),(3,'T001',3,'libre','2025-12-30 08:42:19.060219','2025-12-30 13:51:55.220593',7,0);
/*!40000 ALTER TABLE `tables_restaurant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `types_depense`
--

DROP TABLE IF EXISTS `types_depense`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `types_depense` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) NOT NULL,
  `description` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `types_depense`
--

LOCK TABLES `types_depense` WRITE;
/*!40000 ALTER TABLE `types_depense` DISABLE KEYS */;
/*!40000 ALTER TABLE `types_depense` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `login` varchar(50) NOT NULL,
  `role` varchar(20) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `login` (`login`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'pbkdf2_sha256$1200000$ew5MezEfqW6FgFiKklM89s$lGTQOmU5Mk++ZqvX5C0AIvLHS4983kxh6chQlmpEGBA=','2025-12-30 08:30:54.102507',1,'cherif','Radmin',1,1,'2025-12-25 15:55:42.606032'),(3,'!12goQdCQENrS9Bet0PSZPo7c1Bc4VM7Vjo3dlNa7',NULL,0,'system00','Radmin',0,0,'2025-12-27 15:08:47.138259'),(5,'pbkdf2_sha256$1200000$y9GBNNrA6gHuwSblL5D6Us$UuVrI9KC7tSnwCNU8d01Pul6CNp5x7UC9xFrjsRjP4Q=','2025-12-27 16:09:45.066498',0,'TAB001','Rtable',1,0,'2025-12-27 16:02:11.477379'),(7,'pbkdf2_sha256$1200000$wGcK0x7cH1yFXwcl0ZwxYJ$Msniw68IXfu/4zm1duduMDmn0SkRBYr6eA3kWHMQplY=','2026-01-02 13:04:30.639008',0,'TAB002','Rtable',1,0,'2025-12-30 08:42:16.789806'),(8,'pbkdf2_sha256$1200000$Z6C8NwyAAksX7gk63wmHBP$wy1nADbXHv3JoczCgL1MbaNFPos7lMKJwmAYS+E8NCU=','2025-12-30 13:22:09.536644',0,'SER002','Rservent',1,0,'2025-12-30 08:43:50.345672'),(9,'pbkdf2_sha256$1200000$EValxvaPG8VDt3TXLdtTSB$e7fyWZREo53eHsN/4XqlqKH89Dtz2A87/iw6eLTRglY=','2025-12-30 10:12:48.486923',0,'Cuisinier001','Rcuisinier',1,0,'2025-12-30 08:46:53.717927'),(10,'pbkdf2_sha256$1200000$vxNxsiBo79BFoONh88eUh0$ay2GCmlHUlaM5jHwsxxE55v/EfDCDUSshYZqntiFiYU=','2025-12-30 10:41:08.930801',0,'comptable001','Rcomptable',1,0,'2025-12-30 08:49:23.873197'),(11,'pbkdf2_sha256$600000$RiLIMvxpafU3TnGFa2Uh7X$OrS3xs6Fztcih1qkycFj5mAUapydncqqsSSFU9EYbXw=','2026-01-10 06:28:43.340129',1,'boubacar','Radmin',1,1,'2026-01-10 06:28:32.867103');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_groups`
--

DROP TABLE IF EXISTS `users_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `customuser_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_groups_customuser_id_group_id_927de924_uniq` (`customuser_id`,`group_id`),
  KEY `users_groups_group_id_2f3517aa_fk_auth_group_id` (`group_id`),
  CONSTRAINT `users_groups_customuser_id_4bd991a9_fk_users_id` FOREIGN KEY (`customuser_id`) REFERENCES `users` (`id`),
  CONSTRAINT `users_groups_group_id_2f3517aa_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_groups`
--

LOCK TABLES `users_groups` WRITE;
/*!40000 ALTER TABLE `users_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `users_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_user_permissions`
--

DROP TABLE IF EXISTS `users_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `customuser_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_user_permissions_customuser_id_permission_id_2b4e4e39_uniq` (`customuser_id`,`permission_id`),
  KEY `users_user_permissio_permission_id_6d08dcd2_fk_auth_perm` (`permission_id`),
  CONSTRAINT `users_user_permissio_permission_id_6d08dcd2_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `users_user_permissions_customuser_id_efdb305c_fk_users_id` FOREIGN KEY (`customuser_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_user_permissions`
--

LOCK TABLES `users_user_permissions` WRITE;
/*!40000 ALTER TABLE `users_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `users_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-23 15:57:42
