SET TIMEZONE = 'UTC';

CREATE TABLE IF NOT EXISTS users (
    tg_id   BIGINT PRIMARY KEY,
    tg_nick TEXT,
    vit     NUMERIC DEFAULT 0,
    kfc     NUMERIC DEFAULT 0,
    bk      NUMERIC DEFAULT 0,
    other   NUMERIC DEFAULT 0,
    summ    NUMERIC DEFAULT 0
);

CREATE TABLE IF NOT EXISTS transactions (

    id          SERIAL PRIMARY KEY,
    tg_id       BIGINT REFERENCES users(tg_id) ON DELETE CASCADE,
    category    TEXT NOT NULL,
    summ        NUMERIC NOT NULL,
    "date"      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS deleted_transactions (
    id          INTEGER,
    tg_id       BIGINT,
    category    TEXT,
    summ        NUMERIC DEFAULT 0,
    "date"      TIMESTAMPTZ,
    delete_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
