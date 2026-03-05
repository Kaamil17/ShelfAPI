CREATE DATABASE  verkko;
CREATE USER verkko WITH PASSWORD 'verkko';
GRANT ALL PRIVILEGES ON DATABASE  verkko TO verkko;
ALTER ROLE  verkko SET client_encoding TO 'utf8';
ALTER ROLE  verkko SET default_transaction_isolation TO 'read committed';
ALTER ROLE  verkko SET timezone TO 'UTC';
CREATE EXTENSION IF NOT EXISTS pg_trgm;
\c verkko
GRANT ALL ON SCHEMA public TO  verkko;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO  verkko;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO  verkko;
