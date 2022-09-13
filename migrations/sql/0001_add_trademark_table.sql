--liquibase formatted sql

--changeset r.chushkin:create-schema-data
CREATE SCHEMA IF NOT EXISTS data;

--changeset r.chushkin:create-extension-trgm
CREATE EXTENSION IF NOT EXISTS pg_trgm;

--changeset r.chushkin:create-data-trademark-table
CREATE TABLE IF NOT EXISTS data.trademark (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    application_number TEXT NOT NULL,
    application_date DATE NOT NULL,
    registration_date DATE NOT NULL,
    expiry_date DATE NOT NULL
);
