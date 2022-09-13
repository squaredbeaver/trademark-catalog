--liquibase formatted sql

--changeset r.chushkin:create-index-by-title
CREATE INDEX IF NOT EXISTS trademark_trgm_idx ON data.trademark USING GIN (title gin_trgm_ops);
