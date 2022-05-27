CREATE TABLE YCSB(
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rg CHAR(50) NOT NULL,
    workers INT  NOT NULL,
    iteration  INT   NOT NULL,
    workloadtype CHAR(30) NOT NULL,
    workloadname   CHAR(30) NOT NULL,
    threads INT  NOT NULL,
    records INT  NOT NULL,
    operations  INT  NOT NULL,
    throughput FLOAT   NOT NULL,
    runtime  FLOAT NOT NULL
);
