CREATE TABLE rate_observations (
    id              SERIAL PRIMARY KEY,
    lane            VARCHAR(20)     NOT NULL DEFAULT 'SHA-LAX',
    observed_date   DATE            NOT NULL,
    rate_usd        DECIMAL(10,2)   NOT NULL,
    container_type  VARCHAR(10)     NOT NULL DEFAULT '40ft',
    rate_type       VARCHAR(20)     NOT NULL,
    source          VARCHAR(50)     NOT NULL,
    created_at      TIMESTAMP       DEFAULT NOW()
);

CREATE TABLE signal_events (
    id              SERIAL PRIMARY KEY,
    lane            VARCHAR(20)     NOT NULL DEFAULT 'SHA-LAX',
    event_date      DATE            NOT NULL,
    event_type      VARCHAR(50)     NOT NULL,
    description     TEXT,
    severity        VARCHAR(10)     NOT NULL,
    source          VARCHAR(100),
    created_at      TIMESTAMP       DEFAULT NOW()
);

CREATE TABLE forecasts (
    id              SERIAL PRIMARY KEY,
    lane            VARCHAR(20)     NOT NULL DEFAULT 'SHA-LAX',
    forecast_date   DATE            NOT NULL,
    target_date     DATE            NOT NULL,
    predicted_rate  DECIMAL(10,2)   NOT NULL,
    confidence      VARCHAR(10)     NOT NULL,
    signal          VARCHAR(10)     NOT NULL,
    model_version   VARCHAR(20),
    created_at      TIMESTAMP       DEFAULT NOW()
);

CREATE TABLE port_conditions (
    id              SERIAL PRIMARY KEY,
    port            VARCHAR(20)     NOT NULL DEFAULT 'USLAX',
    observed_date   DATE            NOT NULL,
    vessels_at_anchor INT,
    vessels_waiting   INT,
    avg_dwell_days  DECIMAL(5,2),
    throughput_teu  INT,
    source          VARCHAR(50),
    created_at      TIMESTAMP       DEFAULT NOW()
);

CREATE INDEX idx_rate_lane_date
    ON rate_observations(lane, observed_date DESC);
CREATE INDEX idx_signals_lane_date
    ON signal_events(lane, event_date DESC);
CREATE INDEX idx_forecasts_lane_date
    ON forecasts(lane, forecast_date DESC);

INSERT INTO rate_observations
(lane, observed_date, rate_usd, rate_type, source)
VALUES ('SHA-LAX', CURRENT_DATE, 2500.00, 'spot', 'test');
